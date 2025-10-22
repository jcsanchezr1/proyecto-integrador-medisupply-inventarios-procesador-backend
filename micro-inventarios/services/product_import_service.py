"""
Servicio para la importación masiva de productos
"""
import os
import uuid
import logging
from typing import Tuple, Optional
from werkzeug.datastructures import FileStorage
import pandas as pd
from io import BytesIO

from ..config.settings import Config
from ..models.product_processed_history import ProductProcessedHistory
from ..repositories.product_processed_history_repository import ProductProcessedHistoryRepository
from ..services.cloud_storage_service import CloudStorageService
from ..services.pubsub_service import PubSubService
from ..exceptions.validation_error import ValidationError
from ..exceptions.business_logic_error import BusinessLogicError

logger = logging.getLogger(__name__)


class ProductImportService:
    """
    Servicio para la lógica de negocio de importación masiva de productos
    """
    
    def __init__(self, history_repository=None, cloud_storage_service=None, 
                 pubsub_service=None, config=None):
        self.config = config or Config()
        self.history_repository = history_repository or ProductProcessedHistoryRepository()
        self.cloud_storage_service = cloud_storage_service or CloudStorageService(self.config)
        self.pubsub_service = pubsub_service or PubSubService(self.config)
    
    def import_products_file(self, file: FileStorage, user_id: str) -> Tuple[str, str]:
        """
        Importa un archivo de productos (CSV/Excel) y procesa la carga masiva
        
        Args:
            file: Archivo de productos
            user_id: ID del usuario que realiza la carga
            
        Returns:
            Tuple[str, str]: (history_id, mensaje de éxito)
            
        Raises:
            ValidationError: Si hay errores de validación
            BusinessLogicError: Si hay errores de lógica de negocio
        """
        try:
            # 1. Validar campos obligatorios
            self._validate_required_fields(file, user_id)
            
            # 2. Validar tipo de archivo
            self._validate_file_type(file)
            
            # 3. Validar número de registros (máximo 100)
            self._validate_records_count(file)
            
            # 4. Generar nuevo nombre del archivo con UUID
            new_filename = self._generate_new_filename(file.filename)
            
            # 5. Subir archivo a Cloud Storage
            file.seek(0)  # Volver al inicio del archivo
            self._upload_file_to_storage(file, new_filename)
            
            # 6. Crear registro en la base de datos
            history = self._create_history_record(new_filename, user_id)
            
            # 7. Enviar evento a Pub/Sub
            self._publish_import_event(history.id)
            
            logger.info(f"Importación de productos iniciada - History ID: {history.id}, File: {new_filename}")
            
            return history.id, "Archivo cargado exitosamente"
            
        except ValidationError:
            raise
        except BusinessLogicError:
            raise
        except Exception as e:
            logger.error(f"Error en importación de productos: {str(e)}")
            raise BusinessLogicError(f"Error al procesar importación de productos: {str(e)}")
    
    def _validate_required_fields(self, file: FileStorage, user_id: str) -> None:
        """
        Valida que los campos requeridos estén presentes
        
        Args:
            file: Archivo de productos
            user_id: ID del usuario
            
        Raises:
            ValidationError: Si faltan campos requeridos
        """
        if not file or not file.filename:
            raise ValidationError("El archivo es obligatorio")
        
        if not user_id or user_id.strip() == "":
            raise ValidationError("El userId es obligatorio")
    
    def _validate_file_type(self, file: FileStorage) -> None:
        """
        Valida que el archivo sea CSV o Excel
        
        Args:
            file: Archivo a validar
            
        Raises:
            ValidationError: Si el tipo de archivo no es válido
        """
        if not file.filename or '.' not in file.filename:
            raise ValidationError("El archivo no tiene extensión")
        
        extension = file.filename.lower().split('.')[-1]
        allowed_extensions = {'csv', 'xls', 'xlsx'}
        
        if extension not in allowed_extensions:
            raise ValidationError("Solo se permiten archivos CSV/Excel")
    
    def _validate_records_count(self, file: FileStorage) -> None:
        """
        Valida que el archivo no contenga más de 100 registros
        
        Args:
            file: Archivo a validar
            
        Raises:
            ValidationError: Si el archivo tiene más de 100 registros
        """
        try:
            # Leer el archivo según su extensión
            file.seek(0)
            extension = file.filename.lower().split('.')[-1]
            
            if extension == 'csv':
                df = pd.read_csv(file)
            elif extension in ['xls', 'xlsx']:
                df = pd.read_excel(file)
            else:
                raise ValidationError("Formato de archivo no soportado")
            
            # Validar número de registros
            records_count = len(df)
            
            if records_count > self.config.MAX_IMPORT_PRODUCTS:
                raise ValidationError(
                    f"Solo se permiten cargar {self.config.MAX_IMPORT_PRODUCTS} productos. "
                    f"El archivo contiene {records_count} registros"
                )
            
            logger.info(f"Archivo validado - Registros: {records_count}")
            
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Error al validar el archivo: {str(e)}")
    
    def _generate_new_filename(self, original_filename: str) -> str:
        """
        Genera un nuevo nombre de archivo con UUID
        
        Args:
            original_filename: Nombre original del archivo
            
        Returns:
            str: Nuevo nombre del archivo
        """
        # Obtener nombre base y extensión
        if '.' in original_filename:
            name_parts = original_filename.rsplit('.', 1)
            base_name = name_parts[0]
            extension = name_parts[1]
        else:
            base_name = original_filename
            extension = ''
        
        # Generar UUID
        file_uuid = str(uuid.uuid4())
        
        # Construir nuevo nombre
        if extension:
            new_filename = f"{base_name}_{file_uuid}.{extension}"
        else:
            new_filename = f"{base_name}_{file_uuid}"
        
        return new_filename
    
    def _upload_file_to_storage(self, file: FileStorage, filename: str) -> None:
        """
        Sube el archivo a Google Cloud Storage
        
        Args:
            file: Archivo a subir
            filename: Nombre del archivo en el bucket
            
        Raises:
            BusinessLogicError: Si hay error al subir el archivo
        """
        try:
            # Crear ruta completa con carpeta
            full_path = f"{self.config.BUCKET_FOLDER_PROCESSED_PRODUCTS}/{filename}"
            
            # Obtener bucket
            bucket = self.cloud_storage_service.bucket
            
            # Crear blob en el bucket
            blob = bucket.blob(full_path)
            
            # Configurar metadatos
            blob.metadata = {
                'original_filename': file.filename,
                'uploaded_by': 'medisupply-inventories',
                'folder': self.config.BUCKET_FOLDER_PROCESSED_PRODUCTS
            }
            
            # Subir archivo
            file.seek(0)
            blob.upload_from_file(file)
            
            logger.info(f"Archivo subido exitosamente - Filename: {filename}")
            
        except Exception as e:
            raise BusinessLogicError(f"Error al subir archivo a Cloud Storage: {str(e)}")
    
    def _create_history_record(self, filename: str, user_id: str) -> ProductProcessedHistory:
        """
        Crea un registro en la tabla de historial
        
        Args:
            filename: Nombre del archivo
            user_id: ID del usuario
            
        Returns:
            ProductProcessedHistory: Registro creado
            
        Raises:
            BusinessLogicError: Si hay error al crear el registro
        """
        try:
            # Crear instancia del modelo
            history = ProductProcessedHistory(
                file_name=filename,
                user_id=user_id,
                status="En curso",
                result=None
            )
            
            # Guardar en la base de datos
            created_history = self.history_repository.create(history)
            
            logger.info(f"Registro de historial creado - ID: {created_history.id}")
            
            return created_history
            
        except Exception as e:
            raise BusinessLogicError(f"Error al crear registro de historial: {str(e)}")
    
    def _publish_import_event(self, history_id: str) -> None:
        """
        Publica un evento de importación en Pub/Sub
        
        Args:
            history_id: ID del registro de historial
            
        Raises:
            BusinessLogicError: Si hay error al publicar el evento
        """
        try:
            message_id = self.pubsub_service.publish_product_import_event(history_id)
            logger.info(f"Evento de importación publicado - History ID: {history_id}, Message ID: {message_id}")
            
        except Exception as e:
            raise BusinessLogicError(f"Error al publicar evento de importación: {str(e)}")


"""
Servicio para procesar archivos de productos desde Cloud Storage
"""
import logging
from typing import Tuple, Dict, Any
from datetime import datetime
import pandas as pd
from io import BytesIO

from app.config.settings import Config
from app.models.product import Product
from app.models.product_processed_history import ProductProcessedHistory
from app.repositories.product_repository import ProductRepository
from app.repositories.product_processed_history_repository import ProductProcessedHistoryRepository
from app.services.cloud_storage_service import CloudStorageService

logger = logging.getLogger(__name__)


class ProductFileProcessorService:
    """
    Servicio para procesar archivos de productos desde Cloud Storage
    """
    
    def __init__(self, product_repository=None, history_repository=None, 
                 cloud_storage_service=None, config=None):
        self.config = config or Config()
        self.product_repository = product_repository or ProductRepository(self.config)
        self.history_repository = history_repository or ProductProcessedHistoryRepository(self.config)
        self.cloud_storage_service = cloud_storage_service or CloudStorageService(self.config)
    
    def process_file_by_history_id(self, history_id: str) -> Dict[str, Any]:
        """
        Procesa un archivo de productos usando el history_id
        
        Args:
            history_id: ID del registro de historial
            
        Returns:
            Dict[str, Any]: Resultado del procesamiento con estadísticas
            
        Raises:
            Exception: Si hay errores en el procesamiento
        """
        try:
            logger.info(f"Iniciando procesamiento de archivo - History ID: {history_id}")
            
            # 1. Obtener el registro de historial
            history = self.history_repository.get_by_id(history_id)
            if not history:
                raise Exception(f"No se encontró registro de historial con ID: {history_id}")
            
            logger.info(f"Registro de historial encontrado - File: {history.file_name}")
            
            # 2. Descargar el archivo desde Cloud Storage
            file_content = self.cloud_storage_service.download_file(
                history.file_name, 
                self.config.BUCKET_FOLDER_PROCESSED_PRODUCTS
            )
            
            # 3. Procesar el archivo
            total_records, successful_records, failed_records, errors = self._process_file_content(
                file_content, 
                history.file_name
            )
            
            # 4. Actualizar el registro de historial
            result_message = f"{successful_records}/{total_records} productos registrados"
            history.status = "Finalizado"
            history.result = result_message
            history.updated_at = datetime.utcnow()
            
            self.history_repository.update(history)
            
            logger.info(f"Procesamiento completado - {result_message}")
            
            return {
                "history_id": history_id,
                "file_name": history.file_name,
                "total_records": total_records,
                "successful_records": successful_records,
                "failed_records": failed_records,
                "result": result_message,
                "errors": errors
            }
            
        except Exception as e:
            logger.error(f"Error en procesamiento de archivo: {str(e)}")
            
            # Actualizar el historial con error si existe
            try:
                history = self.history_repository.get_by_id(history_id)
                if history:
                    history.status = "Error"
                    history.result = f"Error: {str(e)}"
                    history.updated_at = datetime.utcnow()
                    self.history_repository.update(history)
            except Exception as update_error:
                logger.error(f"Error al actualizar historial con error: {str(update_error)}")
            
            raise Exception(f"Error al procesar archivo: {str(e)}")
    
    def _process_file_content(self, file_content: BytesIO, filename: str) -> Tuple[int, int, int, list]:
        """
        Procesa el contenido del archivo y registra los productos
        
        Args:
            file_content: Contenido del archivo en memoria
            filename: Nombre del archivo
            
        Returns:
            Tuple[int, int, int, list]: (total_records, successful_records, failed_records, errors)
        """
        try:
            # Determinar el tipo de archivo
            extension = filename.lower().split('.')[-1]
            
            # Leer el archivo con pandas
            if extension == 'csv':
                df = pd.read_csv(file_content)
            elif extension in ['xls', 'xlsx']:
                df = pd.read_excel(file_content)
            else:
                raise Exception(f"Formato de archivo no soportado: {extension}")
            
            logger.info(f"Archivo leído - Total registros: {len(df)}")
            
            # Procesar cada registro (sin contar el encabezado)
            total_records = len(df)
            successful_records = 0
            failed_records = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Crear producto desde la fila
                    product = self._create_product_from_row(row)
                    
                    # Intentar guardar el producto
                    self.product_repository.create(product)
                    successful_records += 1
                    
                    logger.debug(f"Producto registrado - SKU: {product.sku}, Fila: {index + 2}")
                    
                except Exception as e:
                    failed_records += 1
                    error_message = f"Fila {index + 2}: {str(e)}"
                    errors.append(error_message)
                    logger.warning(f"Error al procesar registro - {error_message}")
            
            logger.info(f"Procesamiento completado - Exitosos: {successful_records}, Fallidos: {failed_records}")
            
            return total_records, successful_records, failed_records, errors
            
        except Exception as e:
            logger.error(f"Error al procesar contenido del archivo: {str(e)}")
            raise Exception(f"Error al leer archivo: {str(e)}")
    
    def _create_product_from_row(self, row: pd.Series) -> Product:
        """
        Crea un producto desde una fila del archivo
        
        Args:
            row: Fila del DataFrame
            
        Returns:
            Product: Producto creado
            
        Raises:
            ValueError: Si hay errores de validación
        """
        try:
            # Mapear las columnas del archivo a los campos del producto
            # Se esperan las siguientes columnas en el archivo:
            # sku, name, expiration_date, quantity, price, location, 
            # description, product_type, provider_id, photo_filename, photo_url
            
            # Convertir la fecha de vencimiento
            expiration_date_str = str(row['expiration_date'])
            try:
                expiration_date = datetime.fromisoformat(expiration_date_str.replace('Z', '+00:00'))
            except:
                # Intentar otros formatos comunes
                try:
                    expiration_date = pd.to_datetime(row['expiration_date']).to_pydatetime()
                except:
                    raise ValueError(f"Formato de fecha inválido: {expiration_date_str}")
            
            # Crear el producto
            product = Product(
                sku=str(row['sku']).strip(),
                name=str(row['name']).strip(),
                expiration_date=expiration_date,
                quantity=int(row['quantity']),
                price=float(row['price']),
                location=str(row['location']).strip(),
                description=str(row['description']).strip() if pd.notna(row.get('description')) else '',
                product_type=str(row['product_type']).strip(),
                provider_id=str(row['provider_id']).strip(),
                photo_filename=str(row['photo_filename']).strip() if pd.notna(row.get('photo_filename')) and row.get('photo_filename') != '' else None,
                photo_url=str(row['photo_url']).strip() if pd.notna(row.get('photo_url')) and row.get('photo_url') != '' else None
            )
            
            return product
            
        except KeyError as e:
            raise ValueError(f"Columna requerida no encontrada: {str(e)}")
        except ValueError as e:
            raise ValueError(f"Error de validación: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error al crear producto: {str(e)}")


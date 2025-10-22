"""
Servicio de Google Cloud Storage para manejo de imágenes
"""
import os
import uuid
import logging
from typing import Optional, Tuple
from werkzeug.datastructures import FileStorage
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from PIL import Image
import io

from ..config.settings import Config

logger = logging.getLogger(__name__)


class CloudStorageService:
    """Servicio para manejar operaciones con Google Cloud Storage"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self._client = None
        self._bucket = None
        
        logger.info(f"CloudStorageService inicializado - Bucket: {self.config.BUCKET_NAME}, Folder: {self.config.BUCKET_FOLDER}")
    
    @property
    def client(self) -> storage.Client:
        """Obtiene el cliente de Google Cloud Storage"""
        if self._client is None:
            try:
                # Configurar credenciales si están disponibles
                if self.config.GOOGLE_APPLICATION_CREDENTIALS:
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.config.GOOGLE_APPLICATION_CREDENTIALS
                
                self._client = storage.Client(project=self.config.GCP_PROJECT_ID)
            except Exception as e:
                raise GoogleCloudError(f"Error al inicializar cliente de GCS: {str(e)}")
        
        return self._client
    
    @property
    def bucket(self) -> storage.Bucket:
        """Obtiene el bucket de Google Cloud Storage"""
        if self._bucket is None:
            try:
                self._bucket = self.client.bucket(self.config.BUCKET_NAME)
            except Exception as e:
                raise GoogleCloudError(f"Error al obtener bucket '{self.config.BUCKET_NAME}': {str(e)}")
        
        return self._bucket
    
    def validate_image_file(self, file: FileStorage) -> Tuple[bool, str]:
        """
        Valida un archivo de imagen
        
        Args:
            file: Archivo a validar
            
        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        if not file or not file.filename:
            return False, "No se proporcionó archivo"
        
        # Verificar extensión
        if '.' not in file.filename:
            return False, "El archivo no tiene extensión"
        
        extension = file.filename.lower().split('.')[-1]
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
        
        if extension not in allowed_extensions:
            return False, f"Extensión no permitida. Use: {', '.join(allowed_extensions)}"
        
        # Verificar tamaño
        file.seek(0, 2)  # Ir al final del archivo
        file_size = file.tell()
        file.seek(0)  # Volver al inicio
        
        max_size = self.config.MAX_CONTENT_LENGTH
        if file_size > max_size:
            return False, f"El archivo es demasiado grande. Máximo: {max_size // (1024*1024)}MB"
        
        # Verificar que sea una imagen válida
        try:
            file.seek(0)
            with Image.open(file) as img:
                img.verify()
            file.seek(0)
        except Exception:
            return False, "El archivo no es una imagen válida"
        
        return True, "Archivo válido"
    
    def upload_image(self, file: FileStorage, filename: str) -> Tuple[bool, str, Optional[str]]:
        """
        Sube una imagen al bucket de Google Cloud Storage en la carpeta específica
        
        Args:
            file: Archivo de imagen
            filename: Nombre del archivo en el bucket
            
        Returns:
            Tuple[bool, str, Optional[str]]: (éxito, mensaje, url_pública)
        """
        try:
            # Validar archivo
            is_valid, error_message = self.validate_image_file(file)
            if not is_valid:
                return False, error_message, None
            
            # Crear ruta completa con carpeta
            full_path = f"{self.config.BUCKET_FOLDER}/{filename}"
            
            # Crear blob en el bucket
            blob = self.bucket.blob(full_path)
            
            # Configurar metadatos
            blob.metadata = {
                'original_filename': file.filename,
                'content_type': f'image/{filename.split(".")[-1].lower()}',
                'uploaded_by': 'medisupply-inventories',
                'folder': self.config.BUCKET_FOLDER
            }
            
            # Subir archivo
            file.seek(0)
            blob.upload_from_file(file, content_type=blob.metadata['content_type'])
            
            # Generar URL firmada
            signed_url = self.get_image_url(filename)
            
            logger.info(f"Imagen subida exitosamente - Filename: {filename}, URL firmada generada")
            
            return True, "Imagen subida exitosamente", signed_url
            
        except GoogleCloudError as e:
            return False, f"Error de Google Cloud Storage: {str(e)}", None
        except Exception as e:
            return False, f"Error al subir imagen: {str(e)}", None
    
    def delete_image(self, filename: str) -> Tuple[bool, str]:
        """
        Elimina una imagen del bucket
        
        Args:
            filename: Nombre del archivo a eliminar
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            full_path = f"{self.config.BUCKET_FOLDER}/{filename}"
            blob = self.bucket.blob(full_path)
            
            if blob.exists():
                blob.delete()
                return True, "Imagen eliminada exitosamente"
            else:
                return False, "La imagen no existe"
                
        except GoogleCloudError as e:
            return False, f"Error de Google Cloud Storage: {str(e)}"
        except Exception as e:
            return False, f"Error al eliminar imagen: {str(e)}"
    
    def get_image_url(self, filename: str, expiration_hours: int = 168) -> str:
        """
        Genera una URL firmada de una imagen en Cloud Storage usando impersonated credentials (Cloud Run safe)
        
        Args:
            filename: Nombre del archivo
            expiration_hours: Horas de validez de la URL (default: 168 = 7 días, máximo permitido)
            
        Returns:
            str: URL firmada de la imagen
        """
        try:
            from datetime import datetime, timedelta, timezone
            from google.auth import default, impersonated_credentials
            
            full_path = f"{self.config.BUCKET_FOLDER}/{filename}"
            blob = self.bucket.blob(full_path)

            if not blob.exists():
                logger.warning(f"El archivo {filename} no existe en el bucket")
                return ""

            expiration = datetime.now(timezone.utc) + timedelta(hours=expiration_hours)

            source_credentials, _ = default()

            target_credentials = impersonated_credentials.Credentials(
                source_credentials=source_credentials,
                target_principal=self.config.SIGNING_SERVICE_ACCOUNT_EMAIL,
                target_scopes=["https://www.googleapis.com/auth/devstorage.read_only"],
                lifetime=300,
            )

            signed_url = blob.generate_signed_url(
                expiration=expiration,
                method="GET",
                version="v4",
                credentials=target_credentials,
            )

            logger.info(f"URL firmada generada para {filename}")
            return signed_url

        except Exception as e:
            logger.error(f"Error al generar URL firmada para {filename}: {e}")
            return f"https://storage.googleapis.com/{self.config.BUCKET_NAME}/{self.config.BUCKET_FOLDER}/{filename}"

"""
Servicio de Google Cloud Storage para manejo de archivos
"""
import os
import logging
from typing import Optional
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from io import BytesIO

from app.config.settings import Config

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
    
    def download_file(self, filename: str, folder: Optional[str] = None) -> BytesIO:
        """
        Descarga un archivo desde Google Cloud Storage
        
        Args:
            filename: Nombre del archivo a descargar
            folder: Carpeta donde se encuentra el archivo (opcional)
            
        Returns:
            BytesIO: Contenido del archivo en memoria
            
        Raises:
            GoogleCloudError: Si hay error al descargar el archivo
        """
        try:
            # Crear ruta completa con carpeta
            if folder:
                full_path = f"{folder}/{filename}"
            else:
                full_path = filename
            
            # Obtener blob del bucket
            blob = self.bucket.blob(full_path)
            
            # Verificar que el archivo existe
            if not blob.exists():
                raise GoogleCloudError(f"El archivo {full_path} no existe en el bucket")
            
            # Descargar archivo a memoria
            file_content = BytesIO()
            blob.download_to_file(file_content)
            file_content.seek(0)  # Volver al inicio del archivo
            
            logger.info(f"Archivo descargado exitosamente - Filename: {filename}")
            
            return file_content
            
        except GoogleCloudError as e:
            logger.error(f"Error de Google Cloud Storage: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error al descargar archivo: {str(e)}")
            raise GoogleCloudError(f"Error al descargar archivo desde Cloud Storage: {str(e)}")
    
    def file_exists(self, filename: str, folder: Optional[str] = None) -> bool:
        """
        Verifica si un archivo existe en Cloud Storage
        
        Args:
            filename: Nombre del archivo
            folder: Carpeta donde se encuentra el archivo (opcional)
            
        Returns:
            bool: True si el archivo existe, False en caso contrario
        """
        try:
            # Crear ruta completa con carpeta
            if folder:
                full_path = f"{folder}/{filename}"
            else:
                full_path = filename
            
            # Obtener blob del bucket
            blob = self.bucket.blob(full_path)
            
            return blob.exists()
            
        except Exception as e:
            logger.error(f"Error al verificar existencia del archivo: {str(e)}")
            return False
    
    def delete_file(self, filename: str, folder: Optional[str] = None) -> bool:
        """
        Elimina un archivo de Cloud Storage
        
        Args:
            filename: Nombre del archivo a eliminar
            folder: Carpeta donde se encuentra el archivo (opcional)
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            # Crear ruta completa con carpeta
            if folder:
                full_path = f"{folder}/{filename}"
            else:
                full_path = filename
            
            # Obtener blob del bucket
            blob = self.bucket.blob(full_path)
            
            if blob.exists():
                blob.delete()
                logger.info(f"Archivo eliminado exitosamente - Filename: {filename}")
                return True
            else:
                logger.warning(f"El archivo {full_path} no existe")
                return False
                
        except GoogleCloudError as e:
            logger.error(f"Error de Google Cloud Storage: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error al eliminar archivo: {str(e)}")
            return False


"""
Servicio de Google Cloud Pub/Sub para envío de eventos
"""
import os
import json
import logging
from typing import Dict, Any
from google.cloud import pubsub_v1
from google.cloud.exceptions import GoogleCloudError

from ..config.settings import Config

logger = logging.getLogger(__name__)


class PubSubService:
    """Servicio para manejar operaciones con Google Cloud Pub/Sub"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self._publisher = None
        
        logger.info(f"PubSubService inicializado - Project: {self.config.GCP_PROJECT_ID}")
    
    @property
    def publisher(self) -> pubsub_v1.PublisherClient:
        """Obtiene el cliente de Pub/Sub Publisher"""
        if self._publisher is None:
            try:
                # Configurar credenciales si están disponibles
                if self.config.GOOGLE_APPLICATION_CREDENTIALS:
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.config.GOOGLE_APPLICATION_CREDENTIALS
                
                self._publisher = pubsub_v1.PublisherClient()
            except Exception as e:
                raise GoogleCloudError(f"Error al inicializar cliente de Pub/Sub: {str(e)}")
        
        return self._publisher
    
    def publish_message(self, topic_name: str, message_data: Dict[str, Any]) -> str:
        """
        Publica un mensaje en un tópico de Pub/Sub
        
        Args:
            topic_name: Nombre del tópico (sin incluir el path completo)
            message_data: Datos del mensaje a publicar
            
        Returns:
            str: ID del mensaje publicado
            
        Raises:
            GoogleCloudError: Si hay error al publicar el mensaje
        """
        try:
            # Construir el path completo del tópico
            topic_path = self.publisher.topic_path(self.config.GCP_PROJECT_ID, topic_name)
            
            # Convertir el mensaje a JSON y codificar en bytes
            message_json = json.dumps(message_data)
            message_bytes = message_json.encode('utf-8')
            
            # Publicar mensaje
            future = self.publisher.publish(topic_path, message_bytes)
            message_id = future.result()
            
            logger.info(f"Mensaje publicado exitosamente - Topic: {topic_name}, Message ID: {message_id}")
            
            return message_id
            
        except GoogleCloudError as e:
            logger.error(f"Error de Google Cloud Pub/Sub: {str(e)}")
            raise GoogleCloudError(f"Error al publicar mensaje en Pub/Sub: {str(e)}")
        except Exception as e:
            logger.error(f"Error al publicar mensaje: {str(e)}")
            raise Exception(f"Error al publicar mensaje en Pub/Sub: {str(e)}")
    
    def publish_product_import_event(self, history_id: str) -> str:
        """
        Publica un evento de importación de productos
        
        Args:
            history_id: ID del registro de historial de productos procesados
            
        Returns:
            str: ID del mensaje publicado
            
        Raises:
            GoogleCloudError: Si hay error al publicar el evento
        """
        try:
            message_data = {
                'history_id': history_id,
                'event_type': 'product_import',
                'timestamp': str(datetime.utcnow().isoformat())
            }
            
            return self.publish_message(
                self.config.PUBSUB_TOPIC_PRODUCTS_IMPORT,
                message_data
            )
            
        except Exception as e:
            logger.error(f"Error al publicar evento de importación de productos: {str(e)}")
            raise


# Importar datetime para el timestamp
from datetime import datetime


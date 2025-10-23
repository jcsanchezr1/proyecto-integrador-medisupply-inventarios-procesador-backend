"""
Controlador para procesar archivos de productos desde eventos de Pub/Sub
"""
import logging
import json
import base64
from flask import Blueprint, request, jsonify
from app.controllers.base_controller import BaseController
from app.services.product_file_processor_service import ProductFileProcessorService

logger = logging.getLogger(__name__)

# Crear Blueprint para el controlador
product_processor_bp = Blueprint('product_processor', __name__, url_prefix='/inventory-procesor')


class ProductProcessorController(BaseController):
    """
    Controlador para procesar archivos de productos desde Cloud Storage
    """
    
    def __init__(self, processor_service=None):
        self.processor_service = processor_service or ProductFileProcessorService()
    
    def process_products_file(self):
        """
        Endpoint POST para procesar archivos de productos desde eventos Pub/Sub push
        
        Recibe un evento de Pub/Sub con el formato:
        {
            "message": {
                "data": "base64_encoded_data",
                "messageId": "message_id",
                "publishTime": "timestamp"
            },
            "subscription": "subscription_name"
        }
        
        El data decodificado contiene:
        {
            "history_id": "uuid",
            "event_type": "product_import",
            "timestamp": "timestamp"
        }
        
        Returns:
            Response: Respuesta HTTP con resultado del procesamiento
        """
        try:
            # Validar que la petición tenga contenido
            try:
                pubsub_message = request.get_json(force=True)
                if not pubsub_message:
                    logger.warning("Petición sin contenido JSON")
                    return jsonify({
                        "success": False,
                        "message": "Petición sin contenido JSON"
                    }), 400
            except Exception:
                logger.warning("Petición sin contenido JSON válido")
                return jsonify({
                    "success": False,
                    "message": "Petición sin contenido JSON"
                }), 400
            
            if 'message' not in pubsub_message:
                logger.warning("Mensaje de Pub/Sub sin campo 'message'")
                return jsonify({
                    "success": False,
                    "message": "Formato de mensaje Pub/Sub inválido"
                }), 400
            
            message = pubsub_message['message']
            
            # Decodificar el data del mensaje
            if 'data' not in message:
                logger.warning("Mensaje de Pub/Sub sin campo 'data'")
                return jsonify({
                    "success": False,
                    "message": "Mensaje sin data"
                }), 400
            
            # Decodificar base64
            try:
                data_decoded = base64.b64decode(message['data']).decode('utf-8')
                event_data = json.loads(data_decoded)
            except Exception as e:
                logger.error(f"Error al decodificar mensaje: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": f"Error al decodificar mensaje: {str(e)}"
                }), 400
            
            # Extraer history_id del evento
            history_id = event_data.get('history_id')
            if not history_id:
                logger.warning("Evento sin history_id")
                return jsonify({
                    "success": False,
                    "message": "Evento sin history_id"
                }), 400
            
            logger.info(f"Procesando archivo - History ID: {history_id}, Event Type: {event_data.get('event_type')}")
            
            # Procesar el archivo
            result = self.processor_service.process_file_by_history_id(history_id)
            
            logger.info(f"Archivo procesado exitosamente - {result['result']}")
            
            return jsonify({
                "success": True,
                "message": "Archivo procesado exitosamente",
                "data": result
            }), 200
            
        except Exception as e:
            logger.error(f"Error al procesar archivo: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"Error al procesar archivo: {str(e)}"
            }), 500


# Instanciar el controlador
controller = ProductProcessorController()


# Registrar las rutas
@product_processor_bp.route('/products/files', methods=['POST'])
def process_products_file():
    """
    Endpoint POST /inventory-procesor/products/files
    
    Procesa archivos de productos desde eventos Pub/Sub push
    """
    return controller.process_products_file()


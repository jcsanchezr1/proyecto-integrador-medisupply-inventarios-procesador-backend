"""
Pruebas unitarias para el controlador ProductProcessorController
"""
import unittest
import json
import base64
from unittest.mock import Mock, patch
from flask import Flask
from app.controllers.product_processor_controller import ProductProcessorController, product_processor_bp
from app.services.product_file_processor_service import ProductFileProcessorService


class TestProductProcessorController(unittest.TestCase):
    """Pruebas para el controlador ProductProcessorController"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.app = Flask(__name__)
        self.app.register_blueprint(product_processor_bp)
        self.client = self.app.test_client()
        self.mock_processor_service = Mock()
    
    def _create_pubsub_message(self, history_id: str) -> dict:
        """Crea un mensaje de Pub/Sub de prueba"""
        event_data = {
            'history_id': history_id,
            'event_type': 'product_import',
            'timestamp': '2024-01-01T00:00:00.000Z'
        }
        
        # Codificar en base64
        data_encoded = base64.b64encode(json.dumps(event_data).encode('utf-8')).decode('utf-8')
        
        return {
            'message': {
                'data': data_encoded,
                'messageId': 'test-message-id',
                'publishTime': '2024-01-01T00:00:00.000Z'
            },
            'subscription': 'projects/test-project/subscriptions/test-subscription'
        }
    
    def test_process_products_file_success(self):
        """Prueba procesar archivo exitosamente"""
        # Mock del método process_file_by_history_id del servicio
        with patch.object(ProductFileProcessorService, 'process_file_by_history_id') as mock_process:
            mock_process.return_value = {
                'history_id': '123e4567-e89b-12d3-a456-426614174000',
                'file_name': 'test_products.csv',
                'total_records': 1,
                'successful_records': 1,
                'failed_records': 0,
                'result': '1/1 productos registrados',
                'errors': []
            }
            
            # Crear mensaje de prueba
            pubsub_message = self._create_pubsub_message('123e4567-e89b-12d3-a456-426614174000')
            
            # Ejecutar
            response = self.client.post(
                '/inventory-procesor/products/files',
                json=pubsub_message,
                content_type='application/json'
            )
            
            # Verificar
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertTrue(response_data['success'])
            self.assertIn('Archivo procesado exitosamente', response_data['message'])
    
    def test_process_products_file_without_json(self):
        """Prueba procesar sin contenido JSON"""
        response = self.client.post(
            '/inventory-procesor/products/files',
            data=None,
            content_type='application/json'
        )
        
        # Verificar
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
        self.assertIn('sin contenido JSON', response_data['message'])
    
    @patch('app.controllers.product_processor_controller.ProductFileProcessorService')
    def test_process_products_file_without_message(self, mock_service_class):
        """Prueba procesar sin campo 'message'"""
        response = self.client.post(
            '/inventory-procesor/products/files',
            json={'invalid': 'data'},
            content_type='application/json'
        )
        
        # Verificar
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
        self.assertIn('Formato de mensaje Pub/Sub inválido', response_data['message'])
    
    @patch('app.controllers.product_processor_controller.ProductFileProcessorService')
    def test_process_products_file_without_data(self, mock_service_class):
        """Prueba procesar sin campo 'data'"""
        response = self.client.post(
            '/inventory-procesor/products/files',
            json={
                'message': {
                    'messageId': 'test-id',
                    'publishTime': '2024-01-01T00:00:00.000Z'
                }
            },
            content_type='application/json'
        )
        
        # Verificar
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
        self.assertIn('Mensaje sin data', response_data['message'])
    
    @patch('app.controllers.product_processor_controller.ProductFileProcessorService')
    def test_process_products_file_invalid_base64(self, mock_service_class):
        """Prueba procesar con base64 inválido"""
        response = self.client.post(
            '/inventory-procesor/products/files',
            json={
                'message': {
                    'data': 'invalid-base64!!!',
                    'messageId': 'test-id',
                    'publishTime': '2024-01-01T00:00:00.000Z'
                }
            },
            content_type='application/json'
        )
        
        # Verificar
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
        self.assertIn('Error al decodificar', response_data['message'])
    
    @patch('app.controllers.product_processor_controller.ProductFileProcessorService')
    def test_process_products_file_without_history_id(self, mock_service_class):
        """Prueba procesar sin history_id"""
        event_data = {
            'event_type': 'product_import',
            'timestamp': '2024-01-01T00:00:00.000Z'
            # Falta history_id
        }
        
        data_encoded = base64.b64encode(json.dumps(event_data).encode('utf-8')).decode('utf-8')
        
        response = self.client.post(
            '/inventory-procesor/products/files',
            json={
                'message': {
                    'data': data_encoded,
                    'messageId': 'test-id',
                    'publishTime': '2024-01-01T00:00:00.000Z'
                }
            },
            content_type='application/json'
        )
        
        # Verificar
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
        self.assertIn('sin history_id', response_data['message'])
    
    @patch('app.controllers.product_processor_controller.ProductFileProcessorService')
    def test_process_products_file_service_error(self, mock_service_class):
        """Prueba procesar cuando el servicio lanza error"""
        # Configurar mocks
        mock_service = Mock()
        mock_service.process_file_by_history_id.side_effect = Exception("Error en el servicio")
        mock_service_class.return_value = mock_service
        
        # Crear mensaje de prueba
        pubsub_message = self._create_pubsub_message('123e4567-e89b-12d3-a456-426614174000')
        
        # Ejecutar
        response = self.client.post(
            '/inventory-procesor/products/files',
            json=pubsub_message,
            content_type='application/json'
        )
        
        # Verificar
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
        self.assertIn('Error al procesar archivo', response_data['message'])
    
    def test_process_products_file_with_partial_success(self):
        """Prueba procesar archivo con éxito parcial"""
        # Mock del método process_file_by_history_id del servicio
        with patch.object(ProductFileProcessorService, 'process_file_by_history_id') as mock_process:
            mock_process.return_value = {
                'history_id': '123e4567-e89b-12d3-a456-426614174000',
                'file_name': 'test_products.csv',
                'total_records': 2,
                'successful_records': 1,
                'failed_records': 1,
                'result': '1/2 productos registrados',
                'errors': ['Fila 3: El SKU debe seguir el formato MED-XXXX']
            }
            
            # Crear mensaje de prueba
            pubsub_message = self._create_pubsub_message('123e4567-e89b-12d3-a456-426614174000')
            
            # Ejecutar
            response = self.client.post(
                '/inventory-procesor/products/files',
                json=pubsub_message,
                content_type='application/json'
            )
            
            # Verificar
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertTrue(response_data['success'])
            self.assertEqual(response_data['data']['successful_records'], 1)
            self.assertEqual(response_data['data']['failed_records'], 1)
    
    def test_controller_initialization(self):
        """Prueba la inicialización del controlador"""
        controller = ProductProcessorController(processor_service=self.mock_processor_service)
        self.assertIsNotNone(controller)
        self.assertEqual(controller.processor_service, self.mock_processor_service)
    
    def test_controller_initialization_without_service(self):
        """Prueba la inicialización del controlador sin servicio"""
        controller = ProductProcessorController()
        self.assertIsNotNone(controller)
        self.assertIsNotNone(controller.processor_service)


if __name__ == '__main__':
    unittest.main()


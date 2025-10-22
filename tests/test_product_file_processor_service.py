"""
Pruebas unitarias para el servicio ProductFileProcessorService
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from datetime import datetime, timedelta
import pandas as pd
from app.services.product_file_processor_service import ProductFileProcessorService
from app.models.product_processed_history import ProductProcessedHistory
from app.config.settings import Config


class TestProductFileProcessorService(unittest.TestCase):
    """Pruebas para el servicio ProductFileProcessorService"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.config = Config()
        self.mock_product_repo = Mock()
        self.mock_history_repo = Mock()
        self.mock_cloud_storage = Mock()
        
        self.service = ProductFileProcessorService(
            product_repository=self.mock_product_repo,
            history_repository=self.mock_history_repo,
            cloud_storage_service=self.mock_cloud_storage,
            config=self.config
        )
    
    def _create_test_csv_content(self):
        """Crea contenido de archivo CSV de prueba"""
        csv_content = """sku,name,expiration_date,quantity,price,location,description,product_type,provider_id,photo_filename,photo_url
MED-1234,Paracetamol 500mg,2025-12-31,100,5000.50,A-01-01,Analgésico,Alto valor,550e8400-e29b-41d4-a716-446655440000,photo.jpg,https://example.com/photo.jpg
MED-5678,Ibuprofeno 400mg,2025-11-30,50,3500.00,B-02-03,Antiinflamatorio,Seguridad,650e8400-e29b-41d4-a716-446655440001,photo2.jpg,https://example.com/photo2.jpg"""
        
        return BytesIO(csv_content.encode('utf-8'))
    
    def test_process_file_by_history_id_success(self):
        """Prueba procesar archivo exitosamente"""
        # Configurar mocks
        history_id = '123e4567-e89b-12d3-a456-426614174000'
        mock_history = ProductProcessedHistory(
            id=history_id,
            file_name='test_products.csv',
            user_id='user-123',
            status='En curso'
        )
        
        self.mock_history_repo.get_by_id.return_value = mock_history
        self.mock_cloud_storage.download_file.return_value = self._create_test_csv_content()
        self.mock_product_repo.create.return_value = Mock(id=1)
        
        # Ejecutar
        result = self.service.process_file_by_history_id(history_id)
        
        # Verificar
        self.assertEqual(result['history_id'], history_id)
        self.assertEqual(result['total_records'], 2)
        self.assertEqual(result['successful_records'], 2)
        self.assertEqual(result['failed_records'], 0)
        self.assertIn('2/2', result['result'])
        
        # Verificar que se llamaron los métodos esperados
        self.mock_history_repo.get_by_id.assert_called_once_with(history_id)
        self.mock_cloud_storage.download_file.assert_called_once()
        self.assertEqual(self.mock_product_repo.create.call_count, 2)
        self.mock_history_repo.update.assert_called_once()
    
    def test_process_file_by_history_id_not_found(self):
        """Prueba procesar archivo cuando historial no existe"""
        # Configurar mocks
        history_id = 'non-existent-id'
        self.mock_history_repo.get_by_id.return_value = None
        
        # Ejecutar y verificar
        with self.assertRaises(Exception) as context:
            self.service.process_file_by_history_id(history_id)
        
        self.assertIn('No se encontró', str(context.exception))
    
    def test_process_file_with_partial_errors(self):
        """Prueba procesar archivo con algunos errores"""
        # Configurar mocks
        history_id = '123e4567-e89b-12d3-a456-426614174000'
        mock_history = ProductProcessedHistory(
            id=history_id,
            file_name='test_products.csv',
            user_id='user-123',
            status='En curso'
        )
        
        self.mock_history_repo.get_by_id.return_value = mock_history
        self.mock_cloud_storage.download_file.return_value = self._create_test_csv_content()
        
        # Simular que el segundo producto falla
        self.mock_product_repo.create.side_effect = [
            Mock(id=1),  # Primer producto exitoso
            Exception("Error de validación")  # Segundo producto falla
        ]
        
        # Ejecutar
        result = self.service.process_file_by_history_id(history_id)
        
        # Verificar
        self.assertEqual(result['total_records'], 2)
        self.assertEqual(result['successful_records'], 1)
        self.assertEqual(result['failed_records'], 1)
        self.assertIn('1/2', result['result'])
        self.assertEqual(len(result['errors']), 1)
    
    def test_process_file_excel_format(self):
        """Prueba procesar archivo en formato Excel"""
        # Crear contenido Excel de prueba
        df = pd.DataFrame({
            'sku': ['MED-1234'],
            'name': ['Paracetamol 500mg'],
            'expiration_date': ['2025-12-31'],
            'quantity': [100],
            'price': [5000.50],
            'location': ['A-01-01'],
            'description': ['Analgésico'],
            'product_type': ['Alto valor'],
            'provider_id': ['550e8400-e29b-41d4-a716-446655440000'],
            'photo_filename': ['photo.jpg'],
            'photo_url': ['https://example.com/photo.jpg']
        })
        
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        # Configurar mocks
        history_id = '123e4567-e89b-12d3-a456-426614174000'
        mock_history = ProductProcessedHistory(
            id=history_id,
            file_name='test_products.xlsx',
            user_id='user-123',
            status='En curso'
        )
        
        self.mock_history_repo.get_by_id.return_value = mock_history
        self.mock_cloud_storage.download_file.return_value = excel_buffer
        self.mock_product_repo.create.return_value = Mock(id=1)
        
        # Ejecutar
        result = self.service.process_file_by_history_id(history_id)
        
        # Verificar
        self.assertEqual(result['total_records'], 1)
        self.assertEqual(result['successful_records'], 1)
        self.assertEqual(result['failed_records'], 0)
    
    def test_process_file_invalid_format(self):
        """Prueba procesar archivo con formato inválido"""
        # Configurar mocks
        history_id = '123e4567-e89b-12d3-a456-426614174000'
        mock_history = ProductProcessedHistory(
            id=history_id,
            file_name='test_products.txt',  # Formato no soportado
            user_id='user-123',
            status='En curso'
        )
        
        self.mock_history_repo.get_by_id.return_value = mock_history
        self.mock_cloud_storage.download_file.return_value = BytesIO(b'invalid content')
        
        # Ejecutar y verificar
        with self.assertRaises(Exception):
            self.service.process_file_by_history_id(history_id)
        
        # Verificar que se actualizó el historial con error
        self.mock_history_repo.update.assert_called()
        updated_history = self.mock_history_repo.update.call_args[0][0]
        self.assertEqual(updated_history.status, 'Error')
    
    def test_create_product_from_row_valid(self):
        """Prueba crear producto desde una fila válida"""
        # Crear fila de prueba
        row = pd.Series({
            'sku': 'MED-1234',
            'name': 'Paracetamol 500mg',
            'expiration_date': '2025-12-31',
            'quantity': 100,
            'price': 5000.50,
            'location': 'A-01-01',
            'description': 'Analgésico',
            'product_type': 'Alto valor',
            'provider_id': '550e8400-e29b-41d4-a716-446655440000',
            'photo_filename': 'photo.jpg',
            'photo_url': 'https://example.com/photo.jpg'
        })
        
        # Ejecutar
        product = self.service._create_product_from_row(row)
        
        # Verificar
        self.assertEqual(product.sku, 'MED-1234')
        self.assertEqual(product.name, 'Paracetamol 500mg')
        self.assertEqual(product.quantity, 100)
        self.assertEqual(product.price, 5000.50)
        self.assertEqual(product.location, 'A-01-01')
    
    def test_create_product_from_row_missing_column(self):
        """Prueba crear producto desde fila con columna faltante"""
        # Crear fila incompleta
        row = pd.Series({
            'sku': 'MED-1234',
            'name': 'Paracetamol 500mg'
            # Faltan otras columnas requeridas
        })
        
        # Ejecutar y verificar
        with self.assertRaises(ValueError) as context:
            self.service._create_product_from_row(row)
        
        self.assertIn('no encontrada', str(context.exception))
    
    def test_create_product_from_row_with_optional_fields_empty(self):
        """Prueba crear producto con campos opcionales vacíos"""
        # Crear fila con campos opcionales vacíos
        row = pd.Series({
            'sku': 'MED-1234',
            'name': 'Paracetamol 500mg',
            'expiration_date': '2025-12-31',
            'quantity': 100,
            'price': 5000.50,
            'location': 'A-01-01',
            'description': 'Analgésico',
            'product_type': 'Alto valor',
            'provider_id': '550e8400-e29b-41d4-a716-446655440000',
            'photo_filename': '',  # Campo vacío
            'photo_url': None      # Campo None
        })
        
        # Ejecutar
        product = self.service._create_product_from_row(row)
        
        # Verificar
        self.assertIsNone(product.photo_filename)
        self.assertIsNone(product.photo_url)


if __name__ == '__main__':
    unittest.main()


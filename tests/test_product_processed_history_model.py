"""
Pruebas unitarias para el modelo ProductProcessedHistory
"""
import unittest
from datetime import datetime
from app.models.product_processed_history import ProductProcessedHistory


class TestProductProcessedHistoryModel(unittest.TestCase):
    """Pruebas para el modelo ProductProcessedHistory"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.valid_history_data = {
            'file_name': 'products_20240101.csv',
            'user_id': '550e8400-e29b-41d4-a716-446655440000',
            'status': 'En curso',
            'result': None
        }
    
    def test_create_history_with_valid_data(self):
        """Prueba crear un historial con datos válidos"""
        history = ProductProcessedHistory(**self.valid_history_data)
        self.assertEqual(history.file_name, 'products_20240101.csv')
        self.assertEqual(history.user_id, '550e8400-e29b-41d4-a716-446655440000')
        self.assertEqual(history.status, 'En curso')
        self.assertIsNone(history.result)
        self.assertIsNotNone(history.created_at)
        self.assertIsNone(history.updated_at)
    
    def test_create_history_with_default_status(self):
        """Prueba crear historial con estado por defecto"""
        data = {
            'file_name': 'products.csv',
            'user_id': '550e8400-e29b-41d4-a716-446655440000'
        }
        history = ProductProcessedHistory(**data)
        self.assertEqual(history.status, 'En curso')
    
    def test_validate_valid_history(self):
        """Prueba validar un historial con datos válidos"""
        history = ProductProcessedHistory(**self.valid_history_data)
        try:
            history.validate()
        except Exception as e:
            self.fail(f"Validación falló con datos válidos: {str(e)}")
    
    def test_validate_file_name_required(self):
        """Prueba que nombre de archivo sea obligatorio"""
        invalid_data = self.valid_history_data.copy()
        invalid_data['file_name'] = ''
        history = ProductProcessedHistory(**invalid_data)
        
        with self.assertRaises(ValueError) as context:
            history.validate()
        self.assertIn('nombre del archivo', str(context.exception))
    
    def test_validate_user_id_required(self):
        """Prueba que ID de usuario sea obligatorio"""
        invalid_data = self.valid_history_data.copy()
        invalid_data['user_id'] = ''
        history = ProductProcessedHistory(**invalid_data)
        
        with self.assertRaises(ValueError) as context:
            history.validate()
        self.assertIn('ID del usuario', str(context.exception))
    
    def test_validate_status_required(self):
        """Prueba que estado sea obligatorio"""
        invalid_data = self.valid_history_data.copy()
        invalid_data['status'] = ''
        history = ProductProcessedHistory(**invalid_data)
        
        with self.assertRaises(ValueError) as context:
            history.validate()
        self.assertIn('estado', str(context.exception))
    
    def test_validate_file_name_length(self):
        """Prueba que nombre de archivo no exceda el límite"""
        invalid_data = self.valid_history_data.copy()
        invalid_data['file_name'] = 'a' * 101  # Más de 100 caracteres
        history = ProductProcessedHistory(**invalid_data)
        
        with self.assertRaises(ValueError) as context:
            history.validate()
        self.assertIn('nombre del archivo', str(context.exception))
    
    def test_validate_user_id_length(self):
        """Prueba que ID de usuario no exceda el límite"""
        invalid_data = self.valid_history_data.copy()
        invalid_data['user_id'] = 'a' * 37  # Más de 36 caracteres
        history = ProductProcessedHistory(**invalid_data)
        
        with self.assertRaises(ValueError) as context:
            history.validate()
        self.assertIn('ID del usuario', str(context.exception))
    
    def test_validate_status_length(self):
        """Prueba que estado no exceda el límite"""
        invalid_data = self.valid_history_data.copy()
        invalid_data['status'] = 'a' * 21  # Más de 20 caracteres
        history = ProductProcessedHistory(**invalid_data)
        
        with self.assertRaises(ValueError) as context:
            history.validate()
        self.assertIn('estado', str(context.exception))
    
    def test_to_dict(self):
        """Prueba convertir historial a diccionario"""
        history = ProductProcessedHistory(**self.valid_history_data)
        history_dict = history.to_dict()
        
        self.assertIsInstance(history_dict, dict)
        self.assertEqual(history_dict['file_name'], 'products_20240101.csv')
        self.assertEqual(history_dict['user_id'], '550e8400-e29b-41d4-a716-446655440000')
        self.assertEqual(history_dict['status'], 'En curso')
        self.assertIsNone(history_dict['result'])
        self.assertIn('created_at', history_dict)
        self.assertIn('updated_at', history_dict)
    
    def test_to_dict_with_result(self):
        """Prueba convertir historial con resultado a diccionario"""
        data = self.valid_history_data.copy()
        data['result'] = '10/10 productos registrados'
        history = ProductProcessedHistory(**data)
        history_dict = history.to_dict()
        
        self.assertEqual(history_dict['result'], '10/10 productos registrados')
    
    def test_repr(self):
        """Prueba representación del historial"""
        history = ProductProcessedHistory(**self.valid_history_data)
        repr_str = repr(history)
        
        self.assertIn('ProductProcessedHistory', repr_str)
        self.assertIn('products_20240101.csv', repr_str)
        self.assertIn('En curso', repr_str)
    
    def test_update_status_and_result(self):
        """Prueba actualizar estado y resultado"""
        history = ProductProcessedHistory(**self.valid_history_data)
        history.status = 'Finalizado'
        history.result = '10/15 productos registrados'
        history.updated_at = datetime.utcnow()
        
        self.assertEqual(history.status, 'Finalizado')
        self.assertEqual(history.result, '10/15 productos registrados')
        self.assertIsNotNone(history.updated_at)
        
        # Validar que sigue siendo válido
        try:
            history.validate()
        except Exception as e:
            self.fail(f"Validación falló después de actualización: {str(e)}")


if __name__ == '__main__':
    unittest.main()


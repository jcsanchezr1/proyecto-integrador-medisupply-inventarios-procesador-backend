"""
Pruebas unitarias para el modelo Product
"""
import unittest
from datetime import datetime, timedelta
from app.models.product import Product


class TestProductModel(unittest.TestCase):
    """Pruebas para el modelo Product"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.valid_product_data = {
            'sku': 'MED-1234',
            'name': 'Paracetamol 500mg',
            'expiration_date': datetime.utcnow() + timedelta(days=365),
            'quantity': 100,
            'price': 5000.50,
            'location': 'A-01-01',
            'description': 'Analgésico y antipirético',
            'product_type': 'Alto valor',
            'provider_id': '550e8400-e29b-41d4-a716-446655440000',
            'photo_filename': 'photo.jpg',
            'photo_url': 'https://example.com/photo.jpg'
        }
    
    def test_create_product_with_valid_data(self):
        """Prueba crear un producto con datos válidos"""
        product = Product(**self.valid_product_data)
        self.assertEqual(product.sku, 'MED-1234')
        self.assertEqual(product.name, 'Paracetamol 500mg')
        self.assertEqual(product.quantity, 100)
        self.assertEqual(product.price, 5000.50)
        self.assertEqual(product.location, 'A-01-01')
        self.assertEqual(product.product_type, 'Alto valor')
        self.assertIsNotNone(product.created_at)
        self.assertIsNotNone(product.updated_at)
    
    def test_validate_valid_product(self):
        """Prueba validar un producto con datos válidos"""
        product = Product(**self.valid_product_data)
        try:
            product.validate()
        except Exception as e:
            self.fail(f"Validación falló con datos válidos: {str(e)}")
    
    def test_validate_sku_format(self):
        """Prueba validar formato de SKU"""
        # SKU inválido
        invalid_data = self.valid_product_data.copy()
        invalid_data['sku'] = 'INVALID'
        product = Product(**invalid_data)
        
        with self.assertRaises(ValueError) as context:
            product.validate()
        self.assertIn('SKU', str(context.exception))
    
    def test_validate_sku_required(self):
        """Prueba que SKU sea obligatorio"""
        invalid_data = self.valid_product_data.copy()
        invalid_data['sku'] = ''
        product = Product(**invalid_data)
        
        with self.assertRaises(ValueError) as context:
            product.validate()
        self.assertIn('SKU', str(context.exception))
    
    def test_validate_name_required(self):
        """Prueba que nombre sea obligatorio"""
        invalid_data = self.valid_product_data.copy()
        invalid_data['name'] = ''
        product = Product(**invalid_data)
        
        with self.assertRaises(ValueError) as context:
            product.validate()
        self.assertIn('nombre', str(context.exception))
    
    def test_validate_name_min_length(self):
        """Prueba que nombre tenga mínimo 3 caracteres"""
        invalid_data = self.valid_product_data.copy()
        invalid_data['name'] = 'AB'
        product = Product(**invalid_data)
        
        with self.assertRaises(ValueError) as context:
            product.validate()
        self.assertIn('3 caracteres', str(context.exception))
    
    def test_validate_expiration_date_required(self):
        """Prueba que fecha de vencimiento sea obligatoria"""
        invalid_data = self.valid_product_data.copy()
        invalid_data['expiration_date'] = None
        product = Product(**invalid_data)
        
        with self.assertRaises(ValueError) as context:
            product.validate()
        self.assertIn('vencimiento', str(context.exception))
    
    def test_validate_expiration_date_future(self):
        """Prueba que fecha de vencimiento sea futura"""
        invalid_data = self.valid_product_data.copy()
        invalid_data['expiration_date'] = datetime.utcnow() - timedelta(days=1)
        product = Product(**invalid_data)
        
        with self.assertRaises(ValueError) as context:
            product.validate()
        self.assertIn('posterior', str(context.exception))
    
    def test_validate_quantity_range(self):
        """Prueba que cantidad esté en rango válido"""
        # Cantidad menor a 1
        invalid_data = self.valid_product_data.copy()
        invalid_data['quantity'] = 0
        product = Product(**invalid_data)
        
        with self.assertRaises(ValueError) as context:
            product.validate()
        self.assertIn('cantidad', str(context.exception))
        
        # Cantidad mayor a 9999
        invalid_data['quantity'] = 10000
        product = Product(**invalid_data)
        
        with self.assertRaises(ValueError) as context:
            product.validate()
        self.assertIn('cantidad', str(context.exception))
    
    def test_validate_price_positive(self):
        """Prueba que precio sea positivo"""
        invalid_data = self.valid_product_data.copy()
        invalid_data['price'] = -100
        product = Product(**invalid_data)
        
        with self.assertRaises(ValueError) as context:
            product.validate()
        self.assertIn('precio', str(context.exception))
    
    def test_validate_location_format(self):
        """Prueba validar formato de ubicación"""
        # Ubicación inválida
        invalid_data = self.valid_product_data.copy()
        invalid_data['location'] = 'INVALID'
        product = Product(**invalid_data)
        
        with self.assertRaises(ValueError) as context:
            product.validate()
        self.assertIn('ubicación', str(context.exception))
    
    def test_validate_product_type_valid(self):
        """Prueba que tipo de producto sea válido"""
        invalid_data = self.valid_product_data.copy()
        invalid_data['product_type'] = 'Tipo Inválido'
        product = Product(**invalid_data)
        
        with self.assertRaises(ValueError) as context:
            product.validate()
        self.assertIn('tipo de producto', str(context.exception))
    
    def test_validate_product_type_valid_options(self):
        """Prueba tipos de producto válidos"""
        valid_types = ["Alto valor", "Seguridad", "Cadena fría"]
        
        for product_type in valid_types:
            data = self.valid_product_data.copy()
            data['product_type'] = product_type
            product = Product(**data)
            try:
                product.validate()
            except Exception as e:
                self.fail(f"Validación falló para tipo válido '{product_type}': {str(e)}")
    
    def test_validate_provider_id_format(self):
        """Prueba validar formato UUID de provider_id"""
        invalid_data = self.valid_product_data.copy()
        invalid_data['provider_id'] = 'invalid-uuid'
        product = Product(**invalid_data)
        
        with self.assertRaises(ValueError) as context:
            product.validate()
        self.assertIn('proveedor', str(context.exception))
    
    def test_to_dict(self):
        """Prueba convertir producto a diccionario"""
        product = Product(**self.valid_product_data)
        product_dict = product.to_dict()
        
        self.assertIsInstance(product_dict, dict)
        self.assertEqual(product_dict['sku'], 'MED-1234')
        self.assertEqual(product_dict['name'], 'Paracetamol 500mg')
        self.assertEqual(product_dict['quantity'], 100)
        self.assertEqual(product_dict['price'], 5000.50)
        self.assertIn('created_at', product_dict)
        self.assertIn('updated_at', product_dict)
    
    def test_repr(self):
        """Prueba representación del producto"""
        product = Product(**self.valid_product_data)
        repr_str = repr(product)
        
        self.assertIn('Product', repr_str)
        self.assertIn('MED-1234', repr_str)
        self.assertIn('Paracetamol 500mg', repr_str)


if __name__ == '__main__':
    unittest.main()


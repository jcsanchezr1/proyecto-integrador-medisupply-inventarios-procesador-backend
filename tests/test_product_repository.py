"""
Pruebas unitarias para el repositorio ProductRepository
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from app.models.product import Product
from app.repositories.product_repository import ProductRepository, ProductDB


class TestProductRepository(unittest.TestCase):
    """Pruebas para el repositorio ProductRepository"""
    
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
    
    @patch('app.repositories.product_repository.create_engine')
    @patch('app.repositories.product_repository.sessionmaker')
    def test_repository_initialization(self, mock_sessionmaker, mock_create_engine):
        """Prueba la inicialización del repositorio"""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_session_class = Mock()
        mock_sessionmaker.return_value = mock_session_class
        
        repository = ProductRepository()
        
        self.assertIsNotNone(repository)
        mock_create_engine.assert_called_once()
        mock_sessionmaker.assert_called_once_with(bind=mock_engine)
    
    @patch('app.repositories.product_repository.create_engine')
    @patch('app.repositories.product_repository.sessionmaker')
    def test_create_product(self, mock_sessionmaker, mock_create_engine):
        """Prueba crear un producto"""
        # Configurar mocks
        mock_session = Mock()
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        # Crear repositorio y producto
        repository = ProductRepository()
        product = Product(**self.valid_product_data)
        
        # Simular que el producto se crea con ID
        def add_side_effect(db_product):
            db_product.id = 1
        mock_session.add.side_effect = add_side_effect
        
        # Ejecutar
        created_product = repository.create(product)
        
        # Verificar
        self.assertIsNotNone(created_product.id)
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_repository.create_engine')
    @patch('app.repositories.product_repository.sessionmaker')
    def test_get_by_id_found(self, mock_sessionmaker, mock_create_engine):
        """Prueba obtener producto por ID cuando existe"""
        # Configurar mocks
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        # Crear producto de BD mock
        mock_db_product = ProductDB(
            id=1,
            sku='MED-1234',
            name='Paracetamol 500mg',
            expiration_date=datetime.utcnow() + timedelta(days=365),
            quantity=100,
            price=5000.50,
            location='A-01-01',
            description='Analgésico',
            product_type='Alto valor',
            provider_id='550e8400-e29b-41d4-a716-446655440000',
            photo_filename='photo.jpg',
            photo_url='https://example.com/photo.jpg'
        )
        
        mock_filter.first.return_value = mock_db_product
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        # Ejecutar
        repository = ProductRepository()
        product = repository.get_by_id(1)
        
        # Verificar
        self.assertIsNotNone(product)
        self.assertEqual(product.sku, 'MED-1234')
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_repository.create_engine')
    @patch('app.repositories.product_repository.sessionmaker')
    def test_get_by_id_not_found(self, mock_sessionmaker, mock_create_engine):
        """Prueba obtener producto por ID cuando no existe"""
        # Configurar mocks
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        # Ejecutar
        repository = ProductRepository()
        product = repository.get_by_id(999)
        
        # Verificar
        self.assertIsNone(product)
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_repository.create_engine')
    @patch('app.repositories.product_repository.sessionmaker')
    def test_get_by_sku_found(self, mock_sessionmaker, mock_create_engine):
        """Prueba obtener producto por SKU cuando existe"""
        # Configurar mocks
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_db_product = ProductDB(
            id=1,
            sku='MED-1234',
            name='Paracetamol 500mg',
            expiration_date=datetime.utcnow() + timedelta(days=365),
            quantity=100,
            price=5000.50,
            location='A-01-01',
            description='Analgésico',
            product_type='Alto valor',
            provider_id='550e8400-e29b-41d4-a716-446655440000',
            photo_filename=None,
            photo_url=None
        )
        
        mock_filter.first.return_value = mock_db_product
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        # Ejecutar
        repository = ProductRepository()
        product = repository.get_by_sku('MED-1234')
        
        # Verificar
        self.assertIsNotNone(product)
        self.assertEqual(product.sku, 'MED-1234')
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_repository.create_engine')
    @patch('app.repositories.product_repository.sessionmaker')
    def test_delete_product(self, mock_sessionmaker, mock_create_engine):
        """Prueba eliminar un producto"""
        # Configurar mocks
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_db_product = Mock()
        
        mock_filter.first.return_value = mock_db_product
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        # Ejecutar
        repository = ProductRepository()
        result = repository.delete(1)
        
        # Verificar
        self.assertTrue(result)
        mock_session.delete.assert_called_once_with(mock_db_product)
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_repository.create_engine')
    @patch('app.repositories.product_repository.sessionmaker')
    def test_delete_product_not_found(self, mock_sessionmaker, mock_create_engine):
        """Prueba eliminar producto que no existe"""
        # Configurar mocks
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        # Ejecutar
        repository = ProductRepository()
        result = repository.delete(999)
        
        # Verificar
        self.assertFalse(result)
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_repository.create_engine')
    @patch('app.repositories.product_repository.sessionmaker')
    def test_update_stock_add(self, mock_sessionmaker, mock_create_engine):
        """Prueba actualizar stock agregando cantidad"""
        # Configurar mocks
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_db_product = Mock()
        mock_db_product.quantity = 100
        
        mock_filter.first.return_value = mock_db_product
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        # Ejecutar
        repository = ProductRepository()
        result = repository.update_stock(1, "add", 50)
        
        # Verificar
        self.assertEqual(result['previous_quantity'], 100)
        self.assertEqual(result['new_quantity'], 150)
        self.assertEqual(mock_db_product.quantity, 150)
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_repository.create_engine')
    @patch('app.repositories.product_repository.sessionmaker')
    def test_update_stock_subtract(self, mock_sessionmaker, mock_create_engine):
        """Prueba actualizar stock restando cantidad"""
        # Configurar mocks
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_db_product = Mock()
        mock_db_product.quantity = 100
        
        mock_filter.first.return_value = mock_db_product
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        # Ejecutar
        repository = ProductRepository()
        result = repository.update_stock(1, "subtract", 30)
        
        # Verificar
        self.assertEqual(result['previous_quantity'], 100)
        self.assertEqual(result['new_quantity'], 70)
        self.assertEqual(mock_db_product.quantity, 70)
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_repository.create_engine')
    @patch('app.repositories.product_repository.sessionmaker')
    def test_update_stock_insufficient(self, mock_sessionmaker, mock_create_engine):
        """Prueba actualizar stock con cantidad insuficiente"""
        # Configurar mocks
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_db_product = Mock()
        mock_db_product.quantity = 50
        
        mock_filter.first.return_value = mock_db_product
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        # Ejecutar y verificar
        repository = ProductRepository()
        with self.assertRaises(ValueError) as context:
            repository.update_stock(1, "subtract", 100)
        
        self.assertIn('insuficiente', str(context.exception))
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_repository.create_engine')
    @patch('app.repositories.product_repository.sessionmaker')
    def test_update_stock_invalid_operation(self, mock_sessionmaker, mock_create_engine):
        """Prueba actualizar stock con operación inválida"""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_db_product = Mock()
        mock_db_product.quantity = 50
        
        mock_filter.first.return_value = mock_db_product
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        repository = ProductRepository()
        with self.assertRaises(ValueError) as context:
            repository.update_stock(1, "invalid", 50)
        
        self.assertIn("debe ser 'add' o 'subtract'", str(context.exception))
    
    @patch('app.repositories.product_repository.create_engine')
    @patch('app.repositories.product_repository.sessionmaker')
    def test_update_stock_invalid_quantity(self, mock_sessionmaker, mock_create_engine):
        """Prueba actualizar stock con cantidad inválida"""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_db_product = Mock()
        mock_db_product.quantity = 50
        
        mock_filter.first.return_value = mock_db_product
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        repository = ProductRepository()
        with self.assertRaises(ValueError) as context:
            repository.update_stock(1, "add", 0)
        
        self.assertIn("cantidad debe ser mayor a 0", str(context.exception))
    
    @patch('app.repositories.product_repository.create_engine')
    @patch('app.repositories.product_repository.sessionmaker')
    def test_update_stock_product_not_found(self, mock_sessionmaker, mock_create_engine):
        """Prueba actualizar stock de producto no existente"""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        repository = ProductRepository()
        with self.assertRaises(ValueError) as context:
            repository.update_stock(999, "add", 50)
        
        self.assertIn("no encontrado", str(context.exception))
    
    @patch('app.repositories.product_repository.create_engine')
    @patch('app.repositories.product_repository.sessionmaker')
    def test_get_all_with_filters(self, mock_sessionmaker, mock_create_engine):
        """Prueba obtener productos con filtros"""
        mock_session = Mock()
        mock_query = Mock()
        
        mock_db_products = [
            ProductDB(
                id=1,
                sku='MED-1234',
                name='Test Product',
                expiration_date=datetime.utcnow() + timedelta(days=365),
                quantity=100,
                price=5000.50,
                location='A-01-01',
                description='Test',
                product_type='Alto valor',
                provider_id='550e8400-e29b-41d4-a716-446655440000',
                photo_filename=None,
                photo_url=None
            )
        ]
        
        mock_query.all.return_value = mock_db_products
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        repository = ProductRepository()
        products = repository.get_all(
            sku='MED',
            name='Test',
            quantity=100,
            price=5000.50,
            location='A-01',
            limit=10,
            offset=0
        )
        
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].sku, 'MED-1234')
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_repository.create_engine')
    @patch('app.repositories.product_repository.sessionmaker')
    def test_count_with_filters(self, mock_sessionmaker, mock_create_engine):
        """Prueba contar productos con filtros"""
        mock_session = Mock()
        mock_query = Mock()
        
        mock_query.count.return_value = 5
        mock_query.filter.return_value = mock_query
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        repository = ProductRepository()
        count = repository.count(
            sku='MED',
            name='Test',
            quantity=100
        )
        
        self.assertEqual(count, 5)
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_repository.create_engine')
    @patch('app.repositories.product_repository.sessionmaker')
    def test_delete_all(self, mock_sessionmaker, mock_create_engine):
        """Prueba eliminar todos los productos"""
        mock_session = Mock()
        mock_query = Mock()
        
        mock_query.count.return_value = 10
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        repository = ProductRepository()
        count = repository.delete_all()
        
        self.assertEqual(count, 10)
        mock_query.delete.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_repository.create_engine')
    @patch('app.repositories.product_repository.sessionmaker')
    def test_update_product(self, mock_sessionmaker, mock_create_engine):
        """Prueba actualizar un producto"""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_db_product = ProductDB(
            id=1,
            sku='MED-1234',
            name='Old Name',
            expiration_date=datetime.utcnow() + timedelta(days=365),
            quantity=100,
            price=5000.50,
            location='A-01-01',
            description='Test',
            product_type='Alto valor',
            provider_id='550e8400-e29b-41d4-a716-446655440000',
            photo_filename=None,
            photo_url=None
        )
        
        mock_filter.first.return_value = mock_db_product
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        product = Product(**self.valid_product_data)
        product.id = 1
        product.name = 'New Name'
        
        repository = ProductRepository()
        updated_product = repository.update(product)
        
        self.assertEqual(updated_product.name, 'New Name')
        self.assertEqual(mock_db_product.name, 'New Name')
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()


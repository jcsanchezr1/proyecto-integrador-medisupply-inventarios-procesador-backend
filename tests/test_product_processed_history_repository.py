"""
Pruebas unitarias para el repositorio ProductProcessedHistoryRepository
"""
import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from app.models.product_processed_history import ProductProcessedHistory
from app.repositories.product_processed_history_repository import ProductProcessedHistoryRepository, ProductProcessedHistoryDB


class TestProductProcessedHistoryRepository(unittest.TestCase):
    """Pruebas para el repositorio ProductProcessedHistoryRepository"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        self.valid_history_data = {
            'file_name': 'products_20240101.csv',
            'user_id': '550e8400-e29b-41d4-a716-446655440000',
            'status': 'En curso',
            'result': None
        }
    
    @patch('app.repositories.product_processed_history_repository.create_engine')
    @patch('app.repositories.product_processed_history_repository.sessionmaker')
    def test_repository_initialization(self, mock_sessionmaker, mock_create_engine):
        """Prueba la inicialización del repositorio"""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_session_class = Mock()
        mock_sessionmaker.return_value = mock_session_class
        
        repository = ProductProcessedHistoryRepository()
        
        self.assertIsNotNone(repository)
        mock_create_engine.assert_called_once()
        mock_sessionmaker.assert_called_once_with(bind=mock_engine)
    
    @patch('app.repositories.product_processed_history_repository.create_engine')
    @patch('app.repositories.product_processed_history_repository.sessionmaker')
    @patch('app.repositories.product_processed_history_repository.uuid')
    def test_create_history(self, mock_uuid, mock_sessionmaker, mock_create_engine):
        """Prueba crear un registro de historial"""
        # Configurar mocks
        mock_session = Mock()
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        mock_uuid.uuid4.return_value = Mock(hex='123e4567-e89b-12d3-a456-426614174000')
        
        # Crear repositorio y historial
        repository = ProductProcessedHistoryRepository()
        history = ProductProcessedHistory(**self.valid_history_data)
        
        # Ejecutar
        created_history = repository.create(history)
        
        # Verificar
        self.assertIsNotNone(created_history.id)
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_processed_history_repository.create_engine')
    @patch('app.repositories.product_processed_history_repository.sessionmaker')
    def test_get_by_id_found(self, mock_sessionmaker, mock_create_engine):
        """Prueba obtener historial por ID cuando existe"""
        # Configurar mocks
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        # Crear historial de BD mock
        mock_db_history = ProductProcessedHistoryDB(
            id='123e4567-e89b-12d3-a456-426614174000',
            file_name='products_20240101.csv',
            user_id='550e8400-e29b-41d4-a716-446655440000',
            status='En curso',
            result=None,
            created_at=datetime.utcnow(),
            updated_at=None
        )
        
        mock_filter.first.return_value = mock_db_history
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        # Ejecutar
        repository = ProductProcessedHistoryRepository()
        history = repository.get_by_id('123e4567-e89b-12d3-a456-426614174000')
        
        # Verificar
        self.assertIsNotNone(history)
        self.assertEqual(history.file_name, 'products_20240101.csv')
        self.assertEqual(history.status, 'En curso')
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_processed_history_repository.create_engine')
    @patch('app.repositories.product_processed_history_repository.sessionmaker')
    def test_get_by_id_not_found(self, mock_sessionmaker, mock_create_engine):
        """Prueba obtener historial por ID cuando no existe"""
        # Configurar mocks
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        # Ejecutar
        repository = ProductProcessedHistoryRepository()
        history = repository.get_by_id('non-existent-id')
        
        # Verificar
        self.assertIsNone(history)
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_processed_history_repository.create_engine')
    @patch('app.repositories.product_processed_history_repository.sessionmaker')
    def test_update_history(self, mock_sessionmaker, mock_create_engine):
        """Prueba actualizar un registro de historial"""
        # Configurar mocks
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_db_history = ProductProcessedHistoryDB(
            id='123e4567-e89b-12d3-a456-426614174000',
            file_name='products_20240101.csv',
            user_id='550e8400-e29b-41d4-a716-446655440000',
            status='En curso',
            result=None,
            created_at=datetime.utcnow(),
            updated_at=None
        )
        
        mock_filter.first.return_value = mock_db_history
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        # Crear historial para actualizar
        history = ProductProcessedHistory(
            id='123e4567-e89b-12d3-a456-426614174000',
            file_name='products_20240101.csv',
            user_id='550e8400-e29b-41d4-a716-446655440000',
            status='Finalizado',
            result='10/10 productos registrados'
        )
        
        # Ejecutar
        repository = ProductProcessedHistoryRepository()
        updated_history = repository.update(history)
        
        # Verificar
        self.assertEqual(updated_history.status, 'Finalizado')
        self.assertEqual(updated_history.result, '10/10 productos registrados')
        self.assertEqual(mock_db_history.status, 'Finalizado')
        self.assertEqual(mock_db_history.result, '10/10 productos registrados')
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_processed_history_repository.create_engine')
    @patch('app.repositories.product_processed_history_repository.sessionmaker')
    def test_delete_history(self, mock_sessionmaker, mock_create_engine):
        """Prueba eliminar un registro de historial"""
        # Configurar mocks
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_db_history = Mock()
        
        mock_filter.first.return_value = mock_db_history
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        # Ejecutar
        repository = ProductProcessedHistoryRepository()
        result = repository.delete('123e4567-e89b-12d3-a456-426614174000')
        
        # Verificar
        self.assertTrue(result)
        mock_session.delete.assert_called_once_with(mock_db_history)
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_processed_history_repository.create_engine')
    @patch('app.repositories.product_processed_history_repository.sessionmaker')
    def test_delete_history_not_found(self, mock_sessionmaker, mock_create_engine):
        """Prueba eliminar registro que no existe"""
        # Configurar mocks
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        # Ejecutar
        repository = ProductProcessedHistoryRepository()
        result = repository.delete('non-existent-id')
        
        # Verificar
        self.assertFalse(result)
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_processed_history_repository.create_engine')
    @patch('app.repositories.product_processed_history_repository.sessionmaker')
    def test_get_by_user_id(self, mock_sessionmaker, mock_create_engine):
        """Prueba obtener registros por ID de usuario"""
        # Configurar mocks
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_order_by = Mock()
        
        mock_db_history1 = ProductProcessedHistoryDB(
            id='123e4567-e89b-12d3-a456-426614174000',
            file_name='products1.csv',
            user_id='550e8400-e29b-41d4-a716-446655440000',
            status='Finalizado',
            result='10/10 productos',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        mock_db_history2 = ProductProcessedHistoryDB(
            id='223e4567-e89b-12d3-a456-426614174001',
            file_name='products2.csv',
            user_id='550e8400-e29b-41d4-a716-446655440000',
            status='En curso',
            result=None,
            created_at=datetime.utcnow(),
            updated_at=None
        )
        
        mock_order_by.all.return_value = [mock_db_history1, mock_db_history2]
        mock_filter.order_by.return_value = mock_order_by
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        # Ejecutar
        repository = ProductProcessedHistoryRepository()
        histories = repository.get_by_user_id('550e8400-e29b-41d4-a716-446655440000')
        
        # Verificar
        self.assertEqual(len(histories), 2)
        self.assertEqual(histories[0].file_name, 'products1.csv')
        self.assertEqual(histories[1].file_name, 'products2.csv')
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_processed_history_repository.create_engine')
    @patch('app.repositories.product_processed_history_repository.sessionmaker')
    def test_get_by_user_id_with_limit(self, mock_sessionmaker, mock_create_engine):
        """Prueba obtener registros por ID de usuario con límite"""
        mock_session = Mock()
        mock_query = Mock()
        mock_filter = Mock()
        mock_order_by = Mock()
        mock_limit = Mock()
        
        mock_db_history = ProductProcessedHistoryDB(
            id='123e4567-e89b-12d3-a456-426614174000',
            file_name='products1.csv',
            user_id='550e8400-e29b-41d4-a716-446655440000',
            status='Finalizado',
            result='10/10 productos',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        mock_limit.all.return_value = [mock_db_history]
        mock_order_by.limit.return_value = mock_limit
        mock_filter.order_by.return_value = mock_order_by
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        repository = ProductProcessedHistoryRepository()
        histories = repository.get_by_user_id('550e8400-e29b-41d4-a716-446655440000', limit=1)
        
        self.assertEqual(len(histories), 1)
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_processed_history_repository.create_engine')
    @patch('app.repositories.product_processed_history_repository.sessionmaker')
    def test_get_all_with_pagination(self, mock_sessionmaker, mock_create_engine):
        """Prueba obtener todos los registros con paginación"""
        mock_session = Mock()
        mock_query = Mock()
        mock_order_by = Mock()
        mock_limit = Mock()
        mock_offset = Mock()
        
        mock_db_history = ProductProcessedHistoryDB(
            id='123e4567-e89b-12d3-a456-426614174000',
            file_name='products.csv',
            user_id='550e8400-e29b-41d4-a716-446655440000',
            status='Finalizado',
            result='10/10 productos',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        mock_offset.all.return_value = [mock_db_history]
        mock_limit.offset.return_value = mock_offset
        mock_order_by.limit.return_value = mock_limit
        mock_query.order_by.return_value = mock_order_by
        mock_session.query.return_value = mock_query
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        repository = ProductProcessedHistoryRepository()
        histories = repository.get_all(limit=10, offset=5)
        
        self.assertEqual(len(histories), 1)
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_processed_history_repository.create_engine')
    @patch('app.repositories.product_processed_history_repository.sessionmaker')
    def test_create_with_existing_id(self, mock_sessionmaker, mock_create_engine):
        """Prueba crear historial con ID existente"""
        mock_session = Mock()
        mock_sessionmaker.return_value = Mock(return_value=mock_session)
        
        history = ProductProcessedHistory(
            id='existing-id',
            file_name='products.csv',
            user_id='user-123',
            status='En curso'
        )
        
        repository = ProductProcessedHistoryRepository()
        created_history = repository.create(history)
        
        self.assertEqual(created_history.id, 'existing-id')
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    


if __name__ == '__main__':
    unittest.main()


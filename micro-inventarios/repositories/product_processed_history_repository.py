"""
Repositorio de Historial de Productos Procesados - Implementación con SQLAlchemy
"""
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import uuid

from .base_repository import BaseRepository
from ..models.product_processed_history import ProductProcessedHistory
from ..config.settings import Config

# Configuración de SQLAlchemy
Base = declarative_base()


class ProductProcessedHistoryDB(Base):
    """Modelo de base de datos para historial de productos procesados"""
    __tablename__ = 'products_processed_history'
    
    id = Column(String(36), primary_key=True)
    file_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    user_id = Column(String(36), nullable=False)
    status = Column(String(20), nullable=False)
    result = Column(Text, nullable=True)


class ProductProcessedHistoryRepository(BaseRepository):
    """
    Repositorio para operaciones del historial de productos procesados en la base de datos
    """
    
    def __init__(self):
        # Configuración de la base de datos
        self.engine = create_engine(Config.DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        
        # Crear tablas si no existen
        try:
            Base.metadata.create_all(self.engine)
        except Exception as e:
            print(f"Error creando tablas: {e}")
    
    def _get_session(self) -> Session:
        """Obtiene una sesión de base de datos"""
        return self.Session()
    
    def _db_to_model(self, db_history: ProductProcessedHistoryDB) -> ProductProcessedHistory:
        """Convierte un objeto de base de datos a modelo de dominio"""
        return ProductProcessedHistory(
            id=db_history.id,
            file_name=db_history.file_name,
            user_id=db_history.user_id,
            status=db_history.status,
            result=db_history.result,
            created_at=db_history.created_at,
            updated_at=db_history.updated_at
        )
    
    def _model_to_db(self, history: ProductProcessedHistory) -> ProductProcessedHistoryDB:
        """Convierte un modelo de dominio a objeto de base de datos"""
        return ProductProcessedHistoryDB(
            id=history.id,
            file_name=history.file_name,
            user_id=history.user_id,
            status=history.status,
            result=history.result,
            created_at=history.created_at,
            updated_at=history.updated_at
        )
    
    def create(self, history: ProductProcessedHistory) -> ProductProcessedHistory:
        """
        Crea un nuevo registro de historial en la base de datos
        
        Args:
            history: Instancia del historial a crear
            
        Returns:
            ProductProcessedHistory: Historial creado con ID asignado
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        session = self._get_session()
        try:
            # Validar que el historial sea válido
            history.validate()
            
            # Generar UUID si no existe
            if not history.id:
                history.id = str(uuid.uuid4())
            
            # Convertir a objeto de base de datos
            db_history = self._model_to_db(history)
            
            # Guardar en base de datos
            session.add(db_history)
            session.commit()
            
            return history
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al crear registro de historial: {str(e)}")
        finally:
            session.close()
    
    def get_by_id(self, history_id: str) -> Optional[ProductProcessedHistory]:
        """
        Obtiene un registro de historial por su ID
        
        Args:
            history_id: ID del registro (UUID)
            
        Returns:
            Optional[ProductProcessedHistory]: Historial encontrado o None
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        session = self._get_session()
        try:
            db_history = session.query(ProductProcessedHistoryDB).filter(
                ProductProcessedHistoryDB.id == history_id
            ).first()
            if db_history:
                return self._db_to_model(db_history)
            return None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener registro de historial por ID: {str(e)}")
        finally:
            session.close()
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[ProductProcessedHistory]:
        """
        Obtiene todos los registros de historial con paginación
        
        Args:
            limit: Límite de registros a obtener (opcional)
            offset: Desplazamiento para paginación
            
        Returns:
            List[ProductProcessedHistory]: Lista de registros de historial
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        session = self._get_session()
        try:
            query = session.query(ProductProcessedHistoryDB).order_by(
                ProductProcessedHistoryDB.created_at.desc()
            )
            
            # Aplicar paginación
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            db_histories = query.all()
            return [self._db_to_model(db_history) for db_history in db_histories]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener registros de historial: {str(e)}")
        finally:
            session.close()
    
    def update(self, history: ProductProcessedHistory) -> ProductProcessedHistory:
        """
        Actualiza un registro de historial existente
        
        Args:
            history: Historial con datos actualizados
            
        Returns:
            ProductProcessedHistory: Historial actualizado
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        session = self._get_session()
        try:
            # Validar que el historial sea válido
            history.validate()
            
            # Buscar el registro existente
            db_history = session.query(ProductProcessedHistoryDB).filter(
                ProductProcessedHistoryDB.id == history.id
            ).first()
            
            if db_history:
                # Actualizar campos
                db_history.file_name = history.file_name
                db_history.user_id = history.user_id
                db_history.status = history.status
                db_history.result = history.result
                db_history.updated_at = datetime.utcnow()
                
                session.commit()
            
            return history
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al actualizar registro de historial: {str(e)}")
        finally:
            session.close()
    
    def delete(self, history_id: str) -> bool:
        """
        Elimina un registro de historial por su ID
        
        Args:
            history_id: ID del registro a eliminar (UUID)
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        session = self._get_session()
        try:
            db_history = session.query(ProductProcessedHistoryDB).filter(
                ProductProcessedHistoryDB.id == history_id
            ).first()
            if db_history:
                session.delete(db_history)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al eliminar registro de historial: {str(e)}")
        finally:
            session.close()
    
    def get_by_user_id(self, user_id: str, limit: Optional[int] = None) -> List[ProductProcessedHistory]:
        """
        Obtiene registros de historial por ID de usuario
        
        Args:
            user_id: ID del usuario
            limit: Límite de registros a obtener (opcional)
            
        Returns:
            List[ProductProcessedHistory]: Lista de registros de historial del usuario
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        session = self._get_session()
        try:
            query = session.query(ProductProcessedHistoryDB).filter(
                ProductProcessedHistoryDB.user_id == user_id
            ).order_by(ProductProcessedHistoryDB.created_at.desc())
            
            if limit:
                query = query.limit(limit)
            
            db_histories = query.all()
            return [self._db_to_model(db_history) for db_history in db_histories]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener registros de historial por usuario: {str(e)}")
        finally:
            session.close()


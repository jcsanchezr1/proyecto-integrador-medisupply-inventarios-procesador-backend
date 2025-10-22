"""
Repositorio de Productos - Implementación con SQLAlchemy
"""
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import uuid

from .base_repository import BaseRepository
from ..models.product import Product
from ..config.settings import Config

Base = declarative_base()


class ProductDB(Base):
    """Modelo de base de datos para productos"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String(20), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    location = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    product_type = Column(String(50), nullable=False)
    provider_id = Column(String(36), nullable=False)
    photo_filename = Column(String(255), nullable=True)
    photo_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProductRepository(BaseRepository):
    """
    Repositorio para operaciones de productos en la base de datos
    """
    
    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        
        try:
            Base.metadata.create_all(self.engine)
        except Exception as e:
            print(f"Error creando tablas: {e}")
    
    def _get_session(self) -> Session:
        """Obtiene una sesión de base de datos"""
        return self.Session()
    
    def _db_to_model(self, db_product: ProductDB) -> Product:
        """Convierte un objeto de base de datos a modelo de dominio"""
        return Product(
            id=db_product.id,
            sku=db_product.sku,
            name=db_product.name,
            expiration_date=db_product.expiration_date.isoformat() if db_product.expiration_date else None,
            quantity=db_product.quantity,
            price=db_product.price,
            location=db_product.location,
            description=db_product.description,
            product_type=db_product.product_type,
            provider_id=db_product.provider_id,
            photo_filename=db_product.photo_filename,
            photo_url=db_product.photo_url
        )
    
    def _model_to_db(self, product: Product) -> ProductDB:
        """Convierte un modelo de dominio a objeto de base de datos"""
        return ProductDB(
            sku=product.sku,
            name=product.name,
            expiration_date=product.expiration_date if isinstance(product.expiration_date, datetime) else datetime.fromisoformat(product.expiration_date.replace('Z', '+00:00')) if product.expiration_date else None,
            quantity=product.quantity,
            price=product.price,
            location=product.location,
            description=product.description,
            product_type=product.product_type,
            provider_id=product.provider_id,
            photo_filename=product.photo_filename,
            photo_url=product.photo_url
        )
    
    def create(self, product: Product) -> Product:
        """
        Crea un nuevo producto en la base de datos
        
        Args:
            product: Instancia del producto a crear
            
        Returns:
            Product: Producto creado con ID asignado
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        session = self._get_session()
        try:
            # Validar que el producto sea válido
            product.validate()
            
            # Convertir a objeto de base de datos
            db_product = self._model_to_db(product)
            
            # Guardar en base de datos
            session.add(db_product)
            session.commit()
            
            # Asignar ID al producto original
            product.id = db_product.id
            
            return product
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al crear producto: {str(e)}")
        finally:
            session.close()
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Obtiene un producto por su ID
        
        Args:
            product_id: ID del producto
            
        Returns:
            Optional[Product]: Producto encontrado o None
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        session = self._get_session()
        try:
            db_product = session.query(ProductDB).filter(ProductDB.id == product_id).first()
            if db_product:
                return self._db_to_model(db_product)
            return None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener producto por ID: {str(e)}")
        finally:
            session.close()
    
    def get_by_sku(self, sku: str) -> Optional[Product]:
        """
        Obtiene un producto por su SKU
        
        Args:
            sku: SKU del producto
            
        Returns:
            Optional[Product]: Producto encontrado o None
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        session = self._get_session()
        try:
            db_product = session.query(ProductDB).filter(ProductDB.sku == sku).first()
            if db_product:
                return self._db_to_model(db_product)
            return None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener producto por SKU: {str(e)}")
        finally:
            session.close()
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0, 
                sku: Optional[str] = None, name: Optional[str] = None, 
                expiration_date: Optional[str] = None, quantity: Optional[int] = None,
                price: Optional[float] = None, location: Optional[str] = None) -> List[Product]:
        """
        Obtiene todos los productos con paginación y filtros opcionales
        
        Args:
            limit: Límite de productos a obtener (opcional)
            offset: Desplazamiento para paginación
            sku: Filtrar por SKU (búsqueda parcial, case-insensitive)
            name: Filtrar por nombre (búsqueda parcial, case-insensitive)
            expiration_date: Filtrar por fecha de vencimiento (formato YYYY-MM-DD)
            quantity: Filtrar por cantidad exacta
            price: Filtrar por precio exacto
            location: Filtrar por ubicación (búsqueda parcial, case-insensitive)
            
        Returns:
            List[Product]: Lista de productos
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        session = self._get_session()
        try:
            query = session.query(ProductDB)
            
            # Aplicar filtros
            if sku:
                query = query.filter(ProductDB.sku.ilike(f'%{sku}%'))
            if name:
                query = query.filter(ProductDB.name.ilike(f'%{name}%'))
            if expiration_date:
                query = query.filter(ProductDB.expiration_date == expiration_date)
            if quantity is not None:
                query = query.filter(ProductDB.quantity == quantity)
            if price is not None:
                query = query.filter(ProductDB.price == price)
            if location:
                query = query.filter(ProductDB.location.ilike(f'%{location}%'))
            
            # Aplicar paginación
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            db_products = query.all()
            return [self._db_to_model(db_product) for db_product in db_products]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener productos: {str(e)}")
        finally:
            session.close()
    
    def update(self, product: Product) -> Product:
        """
        Actualiza un producto existente
        
        Args:
            product: Producto con datos actualizados
            
        Returns:
            Product: Producto actualizado
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        session = self._get_session()
        try:
            # Validar que el producto sea válido
            product.validate()
            
            # Buscar el producto existente
            db_product = session.query(ProductDB).filter(ProductDB.id == product.id).first()
            if db_product:
                # Actualizar campos
                db_product.sku = product.sku
                db_product.name = product.name
                db_product.expiration_date = product.expiration_date if isinstance(product.expiration_date, datetime) else datetime.fromisoformat(product.expiration_date.replace('Z', '+00:00')) if product.expiration_date else None
                db_product.quantity = product.quantity
                db_product.price = product.price
                db_product.location = product.location
                db_product.description = product.description
                db_product.product_type = product.product_type
                db_product.photo_filename = product.photo_filename
                db_product.updated_at = datetime.utcnow()
                
                session.commit()
            
            return product
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al actualizar producto: {str(e)}")
        finally:
            session.close()
    
    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto por su ID
        
        Args:
            product_id: ID del producto a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        session = self._get_session()
        try:
            db_product = session.query(ProductDB).filter(ProductDB.id == product_id).first()
            if db_product:
                session.delete(db_product)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al eliminar producto: {str(e)}")
        finally:
            session.close()
    
    def delete_all(self) -> int:
        """
        Elimina todos los productos
        
        Returns:
            int: Número de productos eliminados
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        session = self._get_session()
        try:
            count = session.query(ProductDB).count()
            session.query(ProductDB).delete()
            session.commit()
            return count
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al eliminar todos los productos: {str(e)}")
        finally:
            session.close()
    
    def count(self, sku: Optional[str] = None, name: Optional[str] = None, 
              expiration_date: Optional[str] = None, quantity: Optional[int] = None,
              price: Optional[float] = None, location: Optional[str] = None) -> int:
        """
        Cuenta el total de productos con filtros opcionales
        
        Args:
            sku: Filtrar por SKU (búsqueda parcial, case-insensitive)
            name: Filtrar por nombre (búsqueda parcial, case-insensitive)
            expiration_date: Filtrar por fecha de vencimiento (formato YYYY-MM-DD)
            quantity: Filtrar por cantidad exacta
            price: Filtrar por precio exacto
            location: Filtrar por ubicación (búsqueda parcial, case-insensitive)
            
        Returns:
            int: Número total de productos
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        session = self._get_session()
        try:
            query = session.query(ProductDB)
            
            # Aplicar filtros
            if sku:
                query = query.filter(ProductDB.sku.ilike(f'%{sku}%'))
            if name:
                query = query.filter(ProductDB.name.ilike(f'%{name}%'))
            if expiration_date:
                query = query.filter(ProductDB.expiration_date == expiration_date)
            if quantity is not None:
                query = query.filter(ProductDB.quantity == quantity)
            if price is not None:
                query = query.filter(ProductDB.price == price)
            if location:
                query = query.filter(ProductDB.location.ilike(f'%{location}%'))
            
            return query.count()
        except SQLAlchemyError as e:
            raise Exception(f"Error al contar productos: {str(e)}")
        finally:
            session.close()
    
    def update_stock(self, product_id: int, operation: str, quantity: int) -> dict:
        """
        Actualiza el stock de un producto
        
        Args:
            product_id: ID del producto a actualizar
            operation: Operación a realizar ("add" o "subtract")
            quantity: Cantidad a sumar o restar
            
        Returns:
            dict: Información de la actualización realizada
            
        Raises:
            ValueError: Si el producto no existe o no hay stock suficiente
            Exception: Si hay error en la base de datos
        """
        session = self._get_session()
        try:
            db_product = session.query(ProductDB).filter(ProductDB.id == product_id).first()
            if not db_product:
                raise ValueError(f"Producto con ID {product_id} no encontrado")

            if operation not in ["add", "subtract"]:
                raise ValueError("La operación debe ser 'add' o 'subtract'")

            if quantity <= 0:
                raise ValueError("La cantidad debe ser mayor a 0")

            current_quantity = db_product.quantity

            if operation == "add":
                new_quantity = current_quantity + quantity
            else:
                new_quantity = current_quantity - quantity
                if new_quantity < 0:
                    raise ValueError(f"Stock insuficiente. Disponible: {current_quantity}, Solicitado: {quantity}")

            db_product.quantity = new_quantity
            db_product.updated_at = datetime.utcnow()
            
            session.commit()
            
            return {
                "product_id": product_id,
                "previous_quantity": current_quantity,
                "new_quantity": new_quantity,
                "operation": operation,
                "quantity_changed": quantity
            }
            
        except ValueError:
            session.rollback()
            raise
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al actualizar stock del producto: {str(e)}")
        finally:
            session.close()
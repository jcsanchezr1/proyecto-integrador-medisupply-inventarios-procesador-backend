from typing import List, Optional, Dict, Any
from datetime import datetime
from werkzeug.datastructures import FileStorage
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.services.cloud_storage_service import CloudStorageService
from app.config.settings import Config
from app.exceptions.validation_error import ValidationError
from app.exceptions.business_logic_error import BusinessLogicError


class ProductService:
    """
    Servicio para la lógica de negocio de productos
    """
    
    def __init__(self, product_repository=None, cloud_storage_service=None, config=None):
        self.product_repository = product_repository or ProductRepository()
        self.config = config or Config()
        self.cloud_storage_service = cloud_storage_service or CloudStorageService(self.config)
    
    def create_product(self, product_data: Dict[str, Any], photo_file: Optional[FileStorage] = None) -> Product:
        """
        Crea un nuevo producto con validaciones de negocio
        
        Args:
            product_data: Diccionario con los datos del producto
            photo_file: Archivo de foto del producto (opcional)
            
        Returns:
            Product: Producto creado
            
        Raises:
            ValidationError: Si hay errores de validación
            BusinessLogicError: Si hay errores de lógica de negocio
        """
        try:
            self._validate_required_fields(product_data)
            if photo_file is not None:
                photo_filename, photo_url = self._process_photo_file(photo_file)
                if photo_filename:
                    product_data['photo_filename'] = photo_filename
                    product_data['photo_url'] = photo_url
            
            product = self._create_product_instance(product_data)
            self._validate_business_rules(product)
            created_product = self.product_repository.create(product)
            
            if created_product.photo_filename:
                created_product.photo_url = self.cloud_storage_service.get_image_url(created_product.photo_filename)
            
            return created_product
            
        except ValidationError:
            raise
        except BusinessLogicError:
            raise
        except Exception as e:
            raise BusinessLogicError(f"Error al crear producto: {str(e)}")
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """
        Obtiene un producto por su ID
        
        Args:
            product_id: ID del producto
            
        Returns:
            Optional[Product]: Producto encontrado o None
            
        Raises:
            BusinessLogicError: Si hay error en la operación
        """
        try:
            product = self.product_repository.get_by_id(product_id)
            if product and product.photo_filename:
                product.photo_url = self.cloud_storage_service.get_image_url(product.photo_filename)
            return product
        except Exception as e:
            raise BusinessLogicError(f"Error al obtener producto: {str(e)}")
    
    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """
        Obtiene un producto por su SKU
        
        Args:
            sku: SKU del producto
            
        Returns:
            Optional[Product]: Producto encontrado o None
            
        Raises:
            BusinessLogicError: Si hay error en la operación
        """
        try:
            return self.product_repository.get_by_sku(sku)
        except Exception as e:
            raise BusinessLogicError(f"Error al obtener producto por SKU: {str(e)}")
    
    def get_all_products(self, limit: Optional[int] = None, offset: int = 0,
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
            BusinessLogicError: Si hay error en la operación
        """
        try:
            products = self.product_repository.get_all(
                limit=limit, offset=offset, sku=sku, name=name,
                expiration_date=expiration_date, quantity=quantity,
                price=price, location=location
            )
            for product in products:
                if product.photo_filename:
                    product.photo_url = self.cloud_storage_service.get_image_url(product.photo_filename)
            return products
        except Exception as e:
            raise BusinessLogicError(f"Error al obtener productos: {str(e)}")
    
    def get_products_summary(self, limit: Optional[int] = None, offset: int = 0,
                            sku: Optional[str] = None, name: Optional[str] = None,
                            expiration_date: Optional[str] = None, quantity: Optional[int] = None,
                            price: Optional[float] = None, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtiene un resumen de productos para listado con paginación y filtros opcionales
        
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
            List[Dict[str, Any]]: Lista de diccionarios con datos básicos de productos
            
        Raises:
            BusinessLogicError: Si hay error en la operación
        """
        try:
            products = self.get_all_products(
                limit=limit, offset=offset, sku=sku, name=name,
                expiration_date=expiration_date, quantity=quantity,
                price=price, location=location
            )
            return [product.to_dict() for product in products]
        except Exception as e:
            raise BusinessLogicError(f"Error al obtener resumen de productos: {str(e)}")
    
    def get_products_count(self, sku: Optional[str] = None, name: Optional[str] = None,
                          expiration_date: Optional[str] = None, quantity: Optional[int] = None,
                          price: Optional[float] = None, location: Optional[str] = None) -> int:
        """
        Obtiene el total de productos con filtros opcionales
        
        Args:
            sku: Filtrar por SKU (búsqueda parcial, case-insensitive)
            name: Filtrar por nombre (búsqueda parcial, case-insensitive)
            expiration_date: Filtrar por fecha de vencimiento (formato YYYY-MM-DD)
            quantity: Filtrar por cantidad exacta
            price: Filtrar por precio exacto
            location: Filtrar por ubicación (búsqueda parcial, case-insensitive)
            
        Returns:
            int: Total de productos
            
        Raises:
            BusinessLogicError: Si hay error en la operación
        """
        try:
            return self.product_repository.count(
                sku=sku, name=name, expiration_date=expiration_date,
                quantity=quantity, price=price, location=location
            )
        except Exception as e:
            raise BusinessLogicError(f"Error al contar productos: {str(e)}")
    
    def delete_product(self, product_id: int) -> bool:
        """
        Elimina un producto por su ID
        
        Args:
            product_id: ID del producto a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            BusinessLogicError: Si hay error en la operación
        """
        try:
            product = self.product_repository.get_by_id(product_id)
            if not product:
                raise BusinessLogicError("Producto no encontrado")
            
            return self.product_repository.delete(product_id)
        except BusinessLogicError:
            raise
        except Exception as e:
            raise BusinessLogicError(f"Error al eliminar producto: {str(e)}")
    
    def delete_all_products(self) -> int:
        """
        Elimina todos los productos
        
        Returns:
            int: Número de productos eliminados
            
        Raises:
            BusinessLogicError: Si hay error en la operación
        """
        try:
            return self.product_repository.delete_all()
        except Exception as e:
            raise BusinessLogicError(f"Error al eliminar todos los productos: {str(e)}")
    
    
    def _validate_required_fields(self, product_data: Dict[str, Any]) -> None:
        """
        Valida que todos los campos requeridos estén presentes
        
        Args:
            product_data: Diccionario con los datos del producto
            
        Raises:
            ValidationError: Si faltan campos requeridos
        """
        required_fields = [
            'sku', 'name', 'expiration_date', 'quantity', 
            'price', 'location', 'description', 'product_type', 'provider_id'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in product_data or product_data[field] is None or product_data[field] == '':
                missing_fields.append(field)
        
        if missing_fields:
            raise ValidationError(f"Campos requeridos faltantes: {', '.join(missing_fields)}")
    
    def _create_product_instance(self, product_data: Dict[str, Any]) -> Product:
        """
        Crea una instancia de Product a partir de los datos
        
        Args:
            product_data: Diccionario con los datos del producto
            
        Returns:
            Product: Instancia del producto
            
        Raises:
            ValidationError: Si hay error en la conversión de datos
        """
        try:
            sku = str(product_data['sku'])
            name = str(product_data['name'])
            expiration_date = product_data['expiration_date']
            if isinstance(expiration_date, str):
                try:
                    expiration_date = datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
                except ValueError:
                    raise ValidationError("Formato de fecha de vencimiento inválido")
            elif not isinstance(expiration_date, datetime):
                raise ValidationError("La fecha de vencimiento debe ser un datetime o string válido")
            
            try:
                quantity = int(product_data['quantity'])
                price = float(product_data['price'])
                provider_id = str(product_data['provider_id'])
            except (ValueError, TypeError) as e:
                raise ValidationError(f"Error en conversión de tipos numéricos: {str(e)}")
            
            location = str(product_data['location'])
            description = str(product_data['description'])
            product_type = str(product_data['product_type'])
            photo_filename = str(product_data.get('photo_filename')) if product_data.get('photo_filename') else None
            
            return Product(
                sku=sku,
                name=name,
                expiration_date=expiration_date,
                quantity=quantity,
                price=price,
                location=location,
                description=description,
                product_type=product_type,
                provider_id=provider_id,
                photo_filename=photo_filename
            )
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Error en formato de datos: {str(e)}")
    
    def _validate_business_rules(self, product: Product) -> None:
        """
        Valida reglas de negocio específicas
        
        Args:
            product: Instancia del producto a validar
            
        Raises:
            BusinessLogicError: Si hay violación de reglas de negocio
        """
        existing_product = self.product_repository.get_by_sku(product.sku)
        if existing_product:
            raise BusinessLogicError("El SKU ya existe en el sistema. Utilice un SKU único.")
        
        product.validate()
    
    def _process_photo_file(self, photo_file: Optional[FileStorage]) -> tuple[Optional[str], Optional[str]]:
        """
        Procesa el archivo de foto y lo sube a Google Cloud Storage
        
        Args:
            photo_file: Archivo de foto del producto
            
        Returns:
            tuple[Optional[str], Optional[str]]: (filename, url_pública)
            
        Raises:
            ValidationError: Si hay error en el archivo
        """
        if not photo_file or not photo_file.filename:
            return None, None
        

        photo_file.seek(0, 2)
        file_size = photo_file.tell()
        photo_file.seek(0)
        
        if file_size == 0:
            raise ValidationError("El archivo está vacío")
        
        try:
            import uuid
            if not photo_file.filename or '.' not in photo_file.filename:
                unique_filename = f"product_{uuid.uuid4()}.jpg"
            else:
                extension = photo_file.filename.lower().split('.')[-1]
                unique_filename = f"product_{uuid.uuid4()}.{extension}"

            success, message, _ = self.cloud_storage_service.upload_image(
                photo_file, unique_filename
            )
            
            if not success:
                raise ValidationError(f"Error al subir imagen: {message}")
            
            signed_url = self.cloud_storage_service.get_image_url(unique_filename)
            
            return unique_filename, signed_url
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f"Error al procesar archivo de foto: {str(e)}")
    
    def _is_allowed_file(self, filename: str) -> bool:
        """
        Verifica si el archivo está permitido
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            bool: True si el archivo está permitido
        """
        if not filename or '.' not in filename:
            return False
        
        extension = filename.lower().split('.')[-1]
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
        
        return extension in allowed_extensions
    
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
            ValidationError: Si hay errores de validación
            BusinessLogicError: Si hay errores de lógica de negocio
        """
        try:
            if not product_id or product_id <= 0:
                raise ValidationError("El ID del producto debe ser válido")
            
            if not operation or operation not in ["add", "subtract"]:
                raise ValidationError("La operación debe ser 'add' o 'subtract'")
            
            if not quantity or quantity <= 0:
                raise ValidationError("La cantidad debe ser mayor a 0")

            result = self.product_repository.update_stock(product_id, operation, quantity)
            
            return result
            
        except ValueError as e:
            raise BusinessLogicError(str(e))
        except Exception as e:
            if isinstance(e, (ValidationError, BusinessLogicError)):
                raise
            raise BusinessLogicError(f"Error al actualizar stock del producto: {str(e)}")

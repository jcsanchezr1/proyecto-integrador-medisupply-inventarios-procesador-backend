from datetime import datetime
from typing import Optional
import re
from app.models.base_model import BaseModel


class Product(BaseModel):
    """
    Modelo para productos del inventario
    """
    
    def __init__(self, sku: str, name: str, expiration_date: datetime, 
                 quantity: int, price: float, location: str, 
                 description: str, product_type: str, provider_id: str,
                 photo_filename: Optional[str] = None, 
                 photo_url: Optional[str] = None,
                 id: Optional[int] = None):
        """
        Inicializa un producto con validaciones
        
        Args:
            sku: Código único del producto (formato MED-XXXX)
            name: Nombre del producto (alfanumérico, espacios y tildes)
            expiration_date: Fecha de vencimiento
            quantity: Cantidad disponible
            price: Precio unitario en COP
            location: Ubicación en almacén (formato P-EE-NN)
            description: Descripción del producto
            product_type: Tipo de producto (Alto valor, Seguridad, Cadena fría)
            provider_id: ID del proveedor (UUID string)
            photo_filename: Nombre del archivo de foto (opcional)
            photo_url: URL de la foto (opcional)
            id: ID del producto (opcional)
        """
        self.id = id
        self.sku = sku
        self.name = name
        self.expiration_date = expiration_date
        self.quantity = quantity
        self.price = price
        self.location = location
        self.description = description
        self.product_type = product_type
        self.provider_id = provider_id
        self.photo_filename = photo_filename
        self.photo_url = photo_url
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def validate(self) -> None:
        """
        Valida todos los campos del producto según los criterios de negocio
        """
        self._validate_sku()
        self._validate_name()
        self._validate_expiration_date()
        self._validate_quantity()
        self._validate_price()
        self._validate_location()
        self._validate_product_type()
        self._validate_provider_id()
        self._validate_photo_filename()
    
    def _validate_sku(self) -> None:
        """Valida formato SKU: MED-XXXX (4 dígitos numéricos)"""
        if not self.sku:
            raise ValueError("El SKU es obligatorio")
        
        sku_pattern = r'^MED-\d{4}$'
        if not re.match(sku_pattern, self.sku):
            raise ValueError("El SKU debe seguir el formato MED-XXXX (4 dígitos numéricos)")
    
    def _validate_name(self) -> None:
        """Valida nombre: alfanumérico, espacios y tildes, mínimo 3 caracteres"""
        if not self.name:
            raise ValueError("El nombre es obligatorio")
        
        if len(self.name.strip()) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres")
        
        name_pattern = r'^[a-zA-Z0-9\sáéíóúÁÉÍÓÚñÑüÜ]+$'
        if not re.match(name_pattern, self.name):
            raise ValueError("El nombre debe contener únicamente caracteres alfanuméricos, espacios y tildes")
    
    def _validate_expiration_date(self) -> None:
        """Valida fecha de vencimiento: debe ser futura"""
        if not self.expiration_date:
            raise ValueError("La fecha de vencimiento es obligatoria")
        
        if isinstance(self.expiration_date, str):
            try:
                self.expiration_date = datetime.fromisoformat(self.expiration_date.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError("Formato de fecha inválido")
        
        # Convertir a UTC naive para comparar con datetime.utcnow()
        if self.expiration_date.tzinfo is not None:
            expiration_utc = self.expiration_date.replace(tzinfo=None)
        else:
            expiration_utc = self.expiration_date
            
        if expiration_utc <= datetime.utcnow():
            raise ValueError("La fecha de vencimiento debe ser posterior a la fecha actual")
    
    def _validate_quantity(self) -> None:
        """Valida cantidad: entero positivo entre 1-9999"""
        if not isinstance(self.quantity, int):
            raise ValueError("La cantidad debe ser un número entero")
        
        if self.quantity < 1 or self.quantity > 9999:
            raise ValueError("La cantidad debe estar entre 1 y 9999")
    
    def _validate_price(self) -> None:
        """Valida precio: numérico positivo"""
        if not isinstance(self.price, (int, float)):
            raise ValueError("El precio debe ser un valor numérico")
        
        if self.price <= 0:
            raise ValueError("El precio debe ser un valor positivo")
    
    def _validate_location(self) -> None:
        """Valida ubicación: formato P-EE-NN (Pasillo: A-Z, Estante: 01-99, Nivel: 01-99)"""
        if not self.location:
            raise ValueError("La ubicación es obligatoria")
        
        location_pattern = r'^[A-Z]-\d{2}-\d{2}$'
        if not re.match(location_pattern, self.location):
            raise ValueError("La ubicación debe seguir el formato P-EE-NN (Pasillo: A-Z, Estante: 01-99, Nivel: 01-99)")
    
    def _validate_product_type(self) -> None:
        """Valida tipo de producto: Alto valor, Seguridad, Cadena fría"""
        if not self.product_type:
            raise ValueError("El tipo de producto es obligatorio")
        
        valid_types = ["Alto valor", "Seguridad", "Cadena fría"]
        if self.product_type not in valid_types:
            raise ValueError("El tipo de producto debe ser: Alto valor, Seguridad o Cadena fría")
    
    def _validate_provider_id(self) -> None:
        """Valida ID del proveedor: UUID string válido"""
        if not self.provider_id:
            raise ValueError("El ID del proveedor es obligatorio")
        
        if not isinstance(self.provider_id, str):
            raise ValueError("El ID del proveedor debe ser un string")
        
        # Validar formato UUID (8-4-4-4-12 caracteres hexadecimales)
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, self.provider_id.lower()):
            raise ValueError("El ID del proveedor debe ser un UUID válido")
    
    def _validate_photo_filename(self) -> None:
        """Valida archivo de foto: JPG, PNG, GIF, máximo 2MB"""
        if self.photo_filename:
            # Validar extensión
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            file_extension = self.photo_filename.lower()
            
            if not any(file_extension.endswith(ext) for ext in valid_extensions):
                raise ValueError("La foto debe ser un archivo JPG, PNG o GIF")
    
    def to_dict(self) -> dict:
        """
        Convierte el producto a diccionario
        """
        return {
            'id': getattr(self, 'id', None),
            'sku': self.sku,
            'name': self.name,
            'expiration_date': self.expiration_date.isoformat() if isinstance(self.expiration_date, datetime) else self.expiration_date,
            'quantity': self.quantity,
            'price': self.price,
            'location': self.location,
            'description': self.description,
            'product_type': self.product_type,
            'provider_id': self.provider_id,
            'photo_filename': self.photo_filename,
            'photo_url': self.photo_url,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    def __repr__(self) -> str:
        return f"Product(sku='{self.sku}', name='{self.name}', quantity={self.quantity})"

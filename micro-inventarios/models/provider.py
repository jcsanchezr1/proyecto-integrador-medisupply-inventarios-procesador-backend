from datetime import datetime
from typing import Optional


class Provider:
    """
    Modelo para representar un proveedor obtenido del servicio externo
    """
    
    def __init__(self, id: str, name: str, email: str, phone: str, 
                 logo_filename: str = "", logo_url: str = "",
                 created_at: Optional[str] = None, updated_at: Optional[str] = None):
        """
        Inicializa un proveedor
        
        Args:
            id: ID único del proveedor (UUID)
            name: Nombre del proveedor
            email: Email del proveedor
            phone: Teléfono del proveedor
            logo_filename: Nombre del archivo del logo (opcional)
            logo_url: URL del logo (opcional)
            created_at: Fecha de creación (opcional)
            updated_at: Fecha de actualización (opcional)
        """
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.logo_filename = logo_filename
        self.logo_url = logo_url
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Provider':
        """
        Crea una instancia de Provider desde un diccionario
        
        Args:
            data: Diccionario con los datos del proveedor
            
        Returns:
            Provider: Instancia del proveedor
        """
        return cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            logo_filename=data.get('logo_filename', ''),
            logo_url=data.get('logo_url', ''),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self) -> dict:
        """
        Convierte el proveedor a diccionario
        
        Returns:
            dict: Diccionario con los datos del proveedor
        """
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'logo_filename': self.logo_filename,
            'logo_url': self.logo_url,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def __repr__(self) -> str:
        return f"Provider(id='{self.id}', name='{self.name}')"

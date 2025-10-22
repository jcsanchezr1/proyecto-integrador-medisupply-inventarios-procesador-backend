"""
Modelo para el historial de productos procesados
"""
from datetime import datetime
from typing import Optional
from app.models.base_model import BaseModel


class ProductProcessedHistory(BaseModel):
    """
    Modelo para el historial de productos procesados mediante carga masiva
    """
    
    def __init__(self, file_name: str, user_id: str, status: str = "En curso",
                 result: Optional[str] = None, id: Optional[str] = None,
                 created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None):
        """
        Inicializa un registro de historial de productos procesados
        
        Args:
            file_name: Nombre del archivo procesado
            user_id: ID del usuario que realizó la carga
            status: Estado del procesamiento (default: "En curso")
            result: Resultado del procesamiento (opcional)
            id: ID del registro (UUID, opcional)
            created_at: Fecha de creación (opcional)
            updated_at: Fecha de última actualización (opcional)
        """
        self.id = id
        self.file_name = file_name
        self.user_id = user_id
        self.status = status
        self.result = result
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at
    
    def validate(self) -> None:
        """
        Valida los datos del registro según las reglas de negocio
        """
        if not self.file_name:
            raise ValueError("El nombre del archivo es obligatorio")
        
        if not self.user_id:
            raise ValueError("El ID del usuario es obligatorio")
        
        if not self.status:
            raise ValueError("El estado es obligatorio")
        
        # Validar longitud de campos
        if len(self.file_name) > 100:
            raise ValueError("El nombre del archivo no puede exceder 100 caracteres")
        
        if len(self.user_id) > 36:
            raise ValueError("El ID del usuario no puede exceder 36 caracteres")
        
        if len(self.status) > 20:
            raise ValueError("El estado no puede exceder 20 caracteres")
    
    def to_dict(self) -> dict:
        """
        Convierte el modelo a diccionario
        """
        return {
            'id': self.id,
            'file_name': self.file_name,
            'user_id': self.user_id,
            'status': self.status,
            'result': self.result,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) and self.updated_at else None
        }
    
    def __repr__(self) -> str:
        return f"ProductProcessedHistory(id='{self.id}', file_name='{self.file_name}', status='{self.status}')"


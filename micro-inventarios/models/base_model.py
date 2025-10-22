from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseModel(ABC):
    """
    Clase base abstracta para todos los modelos
    """
    
    def __init__(self):
        self.id: Optional[int] = None
    
    @abstractmethod
    def validate(self) -> None:
        """
        Valida los datos del modelo según las reglas de negocio
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el modelo a diccionario
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"

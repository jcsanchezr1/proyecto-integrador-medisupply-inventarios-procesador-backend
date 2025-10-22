from abc import ABC, abstractmethod
from typing import Any


class BaseService(ABC):
    """
    Clase base abstracta para todos los servicios
    """
    
    @abstractmethod
    def create(self, entity_data: dict) -> Any:
        """
        Crea una nueva entidad
        """
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: int) -> Any:
        """
        Obtiene una entidad por su ID
        """
        pass
    
    @abstractmethod
    def get_all(self) -> list:
        """
        Obtiene todas las entidades
        """
        pass

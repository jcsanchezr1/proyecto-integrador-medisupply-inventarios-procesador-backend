from abc import ABC, abstractmethod
from typing import Any, List, Optional


class BaseRepository(ABC):
    """
    Clase base abstracta para todos los repositorios
    """
    
    @abstractmethod
    def create(self, entity: Any) -> Any:
        """
        Crea una nueva entidad en la base de datos
        """
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[Any]:
        """
        Obtiene una entidad por su ID
        """
        pass
    
    @abstractmethod
    def get_all(self) -> List[Any]:
        """
        Obtiene todas las entidades
        """
        pass
    
    @abstractmethod
    def update(self, entity: Any) -> Any:
        """
        Actualiza una entidad existente
        """
        pass
    
    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """
        Elimina una entidad por su ID
        """
        pass

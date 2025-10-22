import requests
import logging
from typing import Dict, Optional, List
from app.config.settings import get_config
from app.models.provider import Provider
from app.exceptions.business_logic_error import BusinessLogicError

logger = logging.getLogger(__name__)


class ProviderService:
    """
    Servicio para comunicación con el microservicio de proveedores
    """
    
    def __init__(self):
        self.config = get_config()
        self.base_url = self.config.PROVIDERS_SERVICE_URL
        self.timeout = 10  # Timeout en segundos
    
    def get_provider_by_id(self, provider_id: str) -> Optional[Provider]:
        """
        Obtiene un proveedor por su ID desde el servicio externo
        
        Args:
            provider_id: ID del proveedor
            
        Returns:
            Optional[Provider]: Proveedor encontrado o None si no existe
            
        Raises:
            BusinessLogicError: Si hay error en la comunicación con el servicio
        """
        try:
            url = f"{self.base_url}/providers/{provider_id}"
            
            logger.info(f"Consultando proveedor: {url}")
            
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('message') == 'Proveedor obtenido exitosamente' and 'data' in data:
                    return Provider.from_dict(data['data'])
                else:
                    logger.warning(f"Respuesta inesperada del servicio de proveedores: {data}")
                    return None
            elif response.status_code == 404:
                logger.warning(f"Proveedor no encontrado: {provider_id}")
                return None
            else:
                logger.error(f"Error en servicio de proveedores: {response.status_code} - {response.text}")
                raise BusinessLogicError(f"Error en servicio de proveedores: {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout al consultar proveedor {provider_id}")
            raise BusinessLogicError("Timeout al consultar el servicio de proveedores")
        except requests.exceptions.ConnectionError:
            logger.error(f"Error de conexión al consultar proveedor {provider_id}")
            raise BusinessLogicError("Error de conexión con el servicio de proveedores")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición al servicio de proveedores: {str(e)}")
            raise BusinessLogicError(f"Error al consultar proveedor: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado al consultar proveedor {provider_id}: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al consultar proveedor: {str(e)}")
    
    def get_providers_batch(self, provider_ids: List[str]) -> Dict[str, Optional[Provider]]:
        """
        Obtiene múltiples proveedores de manera eficiente
        
        Args:
            provider_ids: Lista de IDs de proveedores únicos
            
        Returns:
            Dict[str, Optional[Provider]]: Diccionario con provider_id como clave y Provider como valor
        """
        providers = {}
        
        for provider_id in provider_ids:
            try:
                provider = self.get_provider_by_id(provider_id)
                providers[provider_id] = provider
            except BusinessLogicError as e:
                logger.error(f"Error al consultar proveedor {provider_id}: {str(e)}")
                providers[provider_id] = None
        
        return providers
    
    def get_provider_name(self, provider_id: str) -> str:
        """
        Obtiene el nombre de un proveedor, retornando "Proveedor no asociado" si falla
        
        Args:
            provider_id: ID del proveedor
            
        Returns:
            str: Nombre del proveedor o "Proveedor no asociado" si falla
        """
        try:
            provider = self.get_provider_by_id(provider_id)
            if provider:
                return provider.name
            else:
                return "Proveedor no asociado"
        except Exception as e:
            logger.error(f"Error al obtener nombre del proveedor {provider_id}: {str(e)}")
            return "Proveedor no asociado"

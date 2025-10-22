from flask_restful import Resource
from typing import Dict, Any, Tuple
from app.controllers.base_controller import BaseController
from app.services.provider_products_service import ProviderProductsService
from app.exceptions.business_logic_error import BusinessLogicError


class ProviderProductsController(BaseController, Resource):
    """
    Controlador para obtener productos agrupados por proveedor
    """
    
    def __init__(self, provider_products_service=None):
        self.provider_products_service = provider_products_service or ProviderProductsService()
    
    def get(self) -> Tuple[Dict[str, Any], int]:
        """
        Obtiene todos los productos agrupados por proveedor
        
        Returns:
            Tuple[Dict[str, Any], int]: Respuesta y código de estado
        """
        try:
            result = self.provider_products_service.get_products_grouped_by_provider()
            
            return self.success_response(
                data={"groups": result["groups"]},
                message=result["message"]
            )
            
        except BusinessLogicError as e:
            return self.handle_exception(e)
        except Exception as e:
            return self.handle_exception(e)

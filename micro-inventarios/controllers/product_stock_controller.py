"""
Controlador para actualización de stock de productos
"""
from flask import request
from flask_restful import Resource
from typing import Dict, Any, Tuple

from .base_controller import BaseController
from ..services.product_service import ProductService
from ..exceptions.validation_error import ValidationError
from ..exceptions.business_logic_error import BusinessLogicError


class ProductStockController(BaseController, Resource):
    """Controlador para operaciones de actualización de stock de productos"""
    
    def __init__(self, product_service=None):
        self.product_service = product_service or ProductService()
    
    def put(self, product_id: int) -> Tuple[Dict[str, Any], int]:
        """PUT /inventory/products/{product_id}/stock - Actualizar stock de un producto"""
        try:
            try:
                data = request.get_json()
            except Exception:
                return self.error_response("Error de validación", "Se requiere un cuerpo JSON válido", 400)
            
            if not data:
                return self.error_response("Error de validación", "Se requiere un cuerpo JSON", 400)

            operation = data.get('operation')
            quantity = data.get('quantity')
            reason = data.get('reason', 'stock_update')
            

            if not operation:
                return self.error_response("Error de validación", "El campo 'operation' es obligatorio", 400)
            
            if quantity is None:
                return self.error_response("Error de validación", "El campo 'quantity' es obligatorio", 400)

            if not isinstance(quantity, (int, float)) or quantity <= 0:
                return self.error_response("Error de validación", "La cantidad debe ser un número mayor a 0", 400)

            quantity = int(quantity)
            result = self.product_service.update_stock(product_id, operation, quantity)
            
            return self.success_response(
                data=result,
                message="Stock actualizado exitosamente"
            )
            
        except ValidationError as e:
            return self.error_response("Error de validación", str(e), 400)
        except BusinessLogicError as e:
            return self.error_response("Error de lógica de negocio", str(e), 422)
        except Exception as e:
            return self.error_response("Error interno del servidor", str(e), 500)

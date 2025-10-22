"""
Controlador para la importación masiva de productos
"""
from flask import request
from flask_restful import Resource
from typing import Dict, Any, Tuple

from app.controllers.base_controller import BaseController
from app.services.product_import_service import ProductImportService
from app.exceptions.validation_error import ValidationError
from app.exceptions.business_logic_error import BusinessLogicError


class ProductImportController(BaseController, Resource):
    """
    Controlador para operaciones de importación masiva de productos
    """
    
    def __init__(self, product_import_service=None):
        self.product_import_service = product_import_service or ProductImportService()
    
    def post(self) -> Tuple[Dict[str, Any], int]:
        """
        Importa productos de manera masiva desde archivo CSV/Excel
        POST /inventory/products/import
        Form Data:
            - file: Archivo CSV/Excel con los productos (obligatorio)
            - userId: ID del usuario que realiza la carga (obligatorio)
        
        Returns:
            Tuple[Dict[str, Any], int]: Respuesta y código de estado 201
        """
        try:
            # Intentar obtener los campos del request
            file = None
            user_id = None
            
            # Verificar si el Content-Type es adecuado para acceder a files/form
            if request.content_type and 'multipart/form-data' in request.content_type:
                file = request.files.get('file')
                user_id = request.form.get('userId')
            
            # Validar campos obligatorios primero (da mejor feedback al usuario)
            if not file:
                # Si no hay archivo, verificar si es porque el Content-Type es incorrecto
                if not request.content_type or 'multipart/form-data' not in request.content_type:
                    return self.error_response(
                        "El campo 'file' es obligatorio",
                        "Asegúrate de usar Content-Type: multipart/form-data para enviar archivos",
                        400
                    )
                return self.error_response("El campo 'file' es obligatorio", None, 400)
            
            if not user_id:
                return self.error_response("El campo 'userId' es obligatorio", None, 400)
            
            # Procesar importación
            history_id, message = self.product_import_service.import_products_file(file, user_id)
            
            return self.created_response(
                data={
                    'history_id': history_id
                },
                message=message
            )
            
        except ValidationError as e:
            return self.handle_exception(e)
        except BusinessLogicError as e:
            return self.handle_exception(e)
        except Exception as e:
            return self.handle_exception(e)


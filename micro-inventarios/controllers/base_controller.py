from flask import request
from typing import Any, Dict, Tuple, Optional
import traceback


class BaseController:
    """
    Clase base para todos los controladores
    """
    
    def success_response(self, data: Any = None, message: str = "Operación exitosa") -> Tuple[Dict[str, Any], int]:
        """
        Crea una respuesta de éxito
        
        Args:
            data: Datos a retornar
            message: Mensaje de éxito
            
        Returns:
            Tuple[Dict[str, Any], int]: Respuesta y código de estado
        """
        response = {
            "success": True,
            "message": message
        }
        
        if data is not None:
            response["data"] = data
            
        return response, 200
    
    def created_response(self, data: Any, message: str = "Recurso creado exitosamente") -> Tuple[Dict[str, Any], int]:
        """
        Crea una respuesta de éxito para creación de recursos (201)
        
        Args:
            data: Datos a retornar
            message: Mensaje de éxito
            
        Returns:
            Tuple[Dict[str, Any], int]: Respuesta y código de estado 201
        """
        response = {
            "success": True,
            "message": message
        }
        
        if data is not None:
            response["data"] = data
            
        return response, 201
    
    def error_response(self, message: str, details: Optional[str] = None, status_code: int = 400) -> Tuple[Dict[str, Any], int]:
        """
        Crea una respuesta de error
        
        Args:
            message: Mensaje de error
            details: Detalles adicionales del error
            status_code: Código de estado HTTP
            
        Returns:
            Tuple[Dict[str, Any], int]: Respuesta y código de estado
        """
        response = {
            "success": False,
            "error": message
        }
        
        if details:
            response["details"] = details
            
        return response, status_code
    
    def handle_exception(self, e: Exception) -> Tuple[Dict[str, Any], int]:
        """
        Maneja excepciones genéricas
        
        Args:
            e: Excepción capturada
            
        Returns:
            Tuple[Dict[str, Any], int]: Respuesta de error y código de estado
        """
        from app.exceptions.validation_error import ValidationError
        from app.exceptions.business_logic_error import BusinessLogicError
        
        if isinstance(e, ValidationError):
            return self.error_response("Error de validación", str(e), 400)
        elif isinstance(e, BusinessLogicError):
            return self.error_response("Error de lógica de negocio", str(e), 422)
        else:
            return self.error_response("Error temporal del sistema. Contacte soporte técnico si persiste", None, 500)

from flask import request
from flask_restful import Resource
from typing import Dict, Any, Tuple, Optional
from app.controllers.base_controller import BaseController
from app.services.product_service import ProductService
from app.exceptions.validation_error import ValidationError
from app.exceptions.business_logic_error import BusinessLogicError


class ProductController(BaseController, Resource):
    """
    Controlador para operaciones de productos
    """
    
    def __init__(self, product_service=None):
        self.product_service = product_service or ProductService()
    
    def post(self) -> Tuple[Dict[str, Any], int]:
        """
        Crea un nuevo producto
        
        Returns:
            Tuple[Dict[str, Any], int]: Respuesta y código de estado
        """
        try:
            # Determinar el tipo de contenido
            if request.is_json:
                product_data = request.get_json()
                photo_file = None
            elif request.content_type and 'multipart/form-data' in request.content_type:
                product_data, photo_file = self._extract_multipart_data()
            else:
                return self.error_response("Content-Type no soportado", "Se requiere application/json o multipart/form-data", 415)
            
            # Crear producto
            product = self.product_service.create_product(product_data, photo_file)
            
            return self.created_response(
                data=product.to_dict(),
                message="Producto registrado exitosamente"
            )
            
        except ValidationError as e:
            return self.handle_exception(e)
        except BusinessLogicError as e:
            return self.handle_exception(e)
        except Exception as e:
            return self.handle_exception(e)
    
    def get(self, product_id: int = None) -> Tuple[Dict[str, Any], int]:
        """
        Obtiene productos
        
        Args:
            product_id: ID del producto (opcional)
            
        Returns:
            Tuple[Dict[str, Any], int]: Respuesta y código de estado
        """
        try:
            if product_id:
                # Obtener producto específico
                product = self.product_service.get_product_by_id(product_id)
                if not product:
                    return self.error_response("Producto no encontrado", None, 404)
                
                return self.success_response(data=product.to_dict())
            else:
                # Obtener lista de productos con paginación y filtros
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)

                sku = request.args.get('sku', type=str)
                name = request.args.get('name', type=str)
                expiration_date = request.args.get('expiration_date', type=str)
                quantity = request.args.get('quantity', type=int)
                price = request.args.get('price', type=float)
                location = request.args.get('location', type=str)

                if page < 1:
                    return self.error_response("El parámetro 'page' debe ser mayor a 0", 400)
                
                if per_page < 1 or per_page > 100:
                    return self.error_response("El parámetro 'per_page' debe estar entre 1 y 100", 400)

                if expiration_date:
                    try:
                        from datetime import datetime
                        datetime.strptime(expiration_date, '%Y-%m-%d')
                    except ValueError:
                        return self.error_response("El formato de 'expiration_date' debe ser YYYY-MM-DD", 400)
                
                offset = (page - 1) * per_page

                products = self.product_service.get_products_summary(
                    limit=per_page,
                    offset=offset,
                    sku=sku,
                    name=name,
                    expiration_date=expiration_date,
                    quantity=quantity,
                    price=price,
                    location=location
                )
                total = self.product_service.get_products_count(
                    sku=sku,
                    name=name,
                    expiration_date=expiration_date,
                    quantity=quantity,
                    price=price,
                    location=location
                )

                total_pages = (total + per_page - 1) // per_page
                has_next = page < total_pages
                has_prev = page > 1
                
                return self.success_response(
                    data={
                        'products': products,
                        'pagination': {
                            'page': page,
                            'per_page': per_page,
                            'total': total,
                            'total_pages': total_pages,
                            'has_next': has_next,
                            'has_prev': has_prev,
                            'next_page': page + 1 if has_next else None,
                            'prev_page': page - 1 if has_prev else None
                        }
                    },
                    message="Lista de productos obtenida exitosamente"
                )
                
        except BusinessLogicError as e:
            return self.handle_exception(e)
        except Exception as e:
            return self.handle_exception(e)
    
    def delete(self, product_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Elimina un producto
        
        Args:
            product_id: ID del producto a eliminar
            
        Returns:
            Tuple[Dict[str, Any], int]: Respuesta y código de estado
        """
        try:
            success = self.product_service.delete_product(product_id)
            if success:
                return self.success_response(message="Producto eliminado exitosamente")
            else:
                return self.error_response("No se pudo eliminar el producto", None, 500)
                
        except BusinessLogicError as e:
            return self.handle_exception(e)
        except Exception as e:
            return self.handle_exception(e)
    
    def _extract_multipart_data(self) -> Tuple[Dict[str, Any], Optional[Any]]:
        """
        Extrae datos de una petición multipart/form-data
        
        Returns:
            Tuple[Dict[str, Any], Optional[Any]]: Datos extraídos y archivo de foto
            
        Raises:
            ValidationError: Si hay error en el formato de datos
        """
        try:
            # Obtener datos del formulario
            form_data = request.form.to_dict()
            
            # Obtener archivo de foto si existe
            photo_file = request.files.get('photo')
            
            return form_data, photo_file
            
        except Exception as e:
            raise ValidationError(f"Error al procesar datos multipart: {str(e)}")


class ProductDeleteAllController(BaseController, Resource):
    """
    Controlador para eliminar todos los productos
    """
    
    def __init__(self, product_service=None):
        self.product_service = product_service or ProductService()
    
    def delete(self) -> Tuple[Dict[str, Any], int]:
        """
        Elimina todos los productos
        
        Returns:
            Tuple[Dict[str, Any], int]: Respuesta y código de estado
        """
        try:
            deleted_count = self.product_service.delete_all_products()
            return self.success_response(
                data={"deleted_count": deleted_count},
                message=f"Se eliminaron {deleted_count} productos"
            )
            
        except BusinessLogicError as e:
            return self.handle_exception(e)
        except Exception as e:
            return self.handle_exception(e)

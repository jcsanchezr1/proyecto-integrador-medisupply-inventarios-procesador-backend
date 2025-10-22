"""
Controlador de Filtros de Productos - Endpoints REST para filtrado avanzado
"""
from flask import request
from flask_restful import Resource
from typing import Dict, Any, Tuple

from .base_controller import BaseController
from ..services.product_service import ProductService
from ..exceptions.business_logic_error import BusinessLogicError


class ProductFilterController(BaseController, Resource):
    """Controlador para operaciones de filtrado de productos"""
    
    def __init__(self, product_service=None):
        self.product_service = product_service or ProductService()
    
    def get(self) -> Tuple[Dict[str, Any], int]:
        """
        GET /inventory/products/filter - Obtener productos con filtros avanzados
        
        Query Parameters:
            page: Número de página (default: 1)
            per_page: Elementos por página (default: 10, max: 100)
            sku: Filtrar por SKU (búsqueda parcial, case-insensitive)
            name: Filtrar por nombre (búsqueda parcial, case-insensitive)
            expiration_date: Filtrar por fecha de vencimiento (formato YYYY-MM-DD)
            quantity: Filtrar por cantidad exacta
            price: Filtrar por precio exacto
            location: Filtrar por ubicación (búsqueda parcial, case-insensitive)
        
        Returns:
            Tuple[Dict[str, Any], int]: Respuesta y código de estado
        """
        try:
            # Obtener parámetros de paginación
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

            filters_present = any([sku, name, expiration_date, quantity is not None, price is not None, location])
            if not filters_present:
                return self.error_response("Debe proporcionar al menos un filtro de búsqueda", 400)
            
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
                    'filters_applied': {
                        'sku': sku,
                        'name': name,
                        'expiration_date': expiration_date,
                        'quantity': quantity,
                        'price': price,
                        'location': location
                    },
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
                message="Productos filtrados obtenidos exitosamente"
            )
            
        except BusinessLogicError as e:
            return self.handle_exception(e)
        except Exception as e:
            return self.handle_exception(e)

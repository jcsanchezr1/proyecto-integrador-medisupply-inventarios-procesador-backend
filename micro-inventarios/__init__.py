"""
Aplicación principal del sistema de inventarios MediSupply
"""
import os
from flask import Flask
from flask_restful import Api
from flask_cors import CORS


def create_app():
    """Factory function para crear la aplicación Flask"""
    
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Configurar CORS
    cors = CORS(app)
    
    # Configurar rutas
    configure_routes(app)
    
    return app


def configure_routes(app):
    """Configura las rutas de la aplicación"""
    from .controllers.health_controller import HealthCheckView
    from .controllers.product_controller import ProductController, ProductDeleteAllController
    from .controllers.product_filter_controller import ProductFilterController
    from .controllers.product_stock_controller import ProductStockController
    from .controllers.provider_products_controller import ProviderProductsController
    from .controllers.product_import_controller import ProductImportController
    
    api = Api(app)
    
    # Health check endpoint
    api.add_resource(HealthCheckView, '/inventory/ping')
    
    # Product endpoints
    api.add_resource(ProductController, '/inventory/products', '/inventory/products/<int:product_id>')
    api.add_resource(ProductFilterController, '/inventory/products/filter')
    api.add_resource(ProductStockController, '/inventory/products/<int:product_id>/stock')
    api.add_resource(ProductDeleteAllController, '/inventory/products/delete-all')
    api.add_resource(ProductImportController, '/inventory/products/import')
    
    # Provider products endpoint
    api.add_resource(ProviderProductsController, '/inventory/providers/products')


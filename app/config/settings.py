"""
Configuración de la aplicación - Estructura para manejar configuraciones
"""
import os


class Config:
    """Configuración base de la aplicación"""
    
    # Configuración básica
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '8080'))
    
    # Configuración de la aplicación
    APP_NAME = 'MediSupply Inventory Processor Backend'
    APP_VERSION = '1.0.0'
    
    # Configuración de Google Cloud Platform
    GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'project-id')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', None)
    
    # Configuración de Google Cloud Storage
    BUCKET_NAME = os.getenv('BUCKET_NAME', 'medisupply-bucket')
    BUCKET_FOLDER = os.getenv('BUCKET_FOLDER', 'products')
    BUCKET_FOLDER_PROCESSED_PRODUCTS = os.getenv('BUCKET_FOLDER_PROCESSED_PRODUCTS', 'processed_products')
    SIGNING_SERVICE_ACCOUNT_EMAIL = os.getenv('SIGNING_SERVICE_ACCOUNT_EMAIL', '')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 2 * 1024 * 1024))  # 2MB
    
    # Configuración de Google Cloud Pub/Sub
    PUBSUB_TOPIC_PRODUCTS_IMPORT = os.getenv('PUBSUB_TOPIC_PRODUCTS_IMPORT', 'products-import')
    
    # Configuración de la base de datos
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/medisupply')
    
    # Configuración de importación de productos
    MAX_IMPORT_PRODUCTS = int(os.getenv('MAX_IMPORT_PRODUCTS', 100))


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False


def get_config():
    """Retorna la configuración según el entorno"""
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig()
    else:
        return DevelopmentConfig()
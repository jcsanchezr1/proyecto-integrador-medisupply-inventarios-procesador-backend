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
    APP_NAME = 'MediSupply Inventory Backend'
    APP_VERSION = '1.0.0'
    
    # Configuración de base de datos
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://medisupply_local_user:medisupply_local_password@localhost:5432/medisupply_local_db')
    
    # Configuración de Google Cloud Storage
    GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'soluciones-cloud-2024-02')
    BUCKET_NAME = os.getenv('BUCKET_NAME', 'medisupply-images-bucket')
    BUCKET_FOLDER = os.getenv('BUCKET_FOLDER', 'products')
    BUCKET_FOLDER_PROCESSED_PRODUCTS = os.getenv('BUCKET_FOLDER_PROCESSED_PRODUCTS', 'processed-products')
    BUCKET_LOCATION = os.getenv('BUCKET_LOCATION', 'us-central1')
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    SIGNING_SERVICE_ACCOUNT_EMAIL = os.getenv('SIGNING_SERVICE_ACCOUNT_EMAIL', '')

    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    PROVIDERS_SERVICE_URL = os.getenv('PROVIDERS_SERVICE_URL', 'http://localhost:8083')
    
    # Configuración de Pub/Sub
    PUBSUB_TOPIC_PRODUCTS_IMPORT = os.getenv('PUBSUB_TOPIC_PRODUCTS_IMPORT', 'inventory.processing.products')
    
    # Configuración de importación de productos
    MAX_IMPORT_PRODUCTS = 100


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


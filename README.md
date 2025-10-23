# MediSupply Inventory Processor Backend

Sistema procesador de inventarios backend para el proyecto integrador MediSupply.

## Arquitectura

Estructura básica preparada para escalar:

```
├── app/
│   ├── config/          # Configuración
│   ├── controllers/     # Controladores REST
│   │   └── health_controller.py  # Healthcheck funcional
│   ├── services/        # Lógica de negocio (estructura)
│   ├── repositories/    # Acceso a datos (estructura)
│   ├── models/          # Modelos de datos (estructura)
│   ├── exceptions/      # Excepciones (estructura)
│   └── utils/           # Utilidades (estructura)
├── tests/               # Tests (estructura)
├── app.py              # Punto de entrada
├── requirements.txt    # Mismas versiones del proyecto sample
├── Dockerfile         # Containerización
├── docker-compose.yml # Orquestación
└── README.md          # Documentación
```

## Características

- **Health Check**: Endpoint de monitoreo del servicio en `/inventory-procesor/ping`
- **Docker**: Containerización para local y Cloud Run
- **Flask**: Framework web minimalista
- **CORS**: Habilitado para desarrollo

## Tecnologías

- Python 3.9
- Flask 3.0.3
- Gunicorn 21.2.0
- Docker

## Instalación

### Desarrollo Local

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecutar la aplicación:
   ```bash
   python app.py
   ```

### Con Docker

1. Construir y ejecutar:
   ```bash
   docker-compose up --build
   ```

2. La aplicación estará disponible en `http://localhost:8080`

## Endpoints

### Health Check
- `GET /inventory-procesor/ping` - Retorna "pong" para verificar el estado del servicio

## Cloud Run

Para desplegar en Google Cloud Run:

1. Construir imagen:
   ```bash
   docker build -t gcr.io/PROJECT_ID/medisupply-inventory-processor .
   ```

2. Subir imagen:
   ```bash
   docker push gcr.io/PROJECT_ID/medisupply-inventory-processor
   ```

3. Desplegar:
   ```bash
   gcloud run deploy medisupply-inventory-processor \
     --image gcr.io/PROJECT_ID/medisupply-inventory-processor \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## Variables de Entorno

- `FLASK_ENV`: Entorno (development/production)
- `PORT`: Puerto del servicio (default: 8080)
- `HOST`: Host del servicio (default: 0.0.0.0)
- `DEBUG`: Modo debug (default: True)

## Testing

### Ejecutar Tests

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con información detallada
pytest -v

# Ejecutar pruebas específicas
pytest tests/test_health_controller.py

# Ejecutar pruebas de un módulo específico
pytest tests/test_product_service.py -v
```

### Ejecutar con Coverage

```bash
# Ejecutar pruebas con coverage
pytest --cov=app --cov-report=term-missing

# Generar reporte HTML de coverage
pytest --cov=app --cov-report=html

# Verificar coverage mínimo del 95%
pytest --cov=app --cov-fail-under=95

# Ejecutar solo tests que fallan
pytest --lf
```
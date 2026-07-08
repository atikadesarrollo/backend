from flask import Flask, request, g
from flask import render_template
from odoo_api.routes import odoo_bp
from datalake_api.routes import datalake_bp
from datalake_api.analytics_routes import analytics_bp
from waitress import serve
from flask_cors import CORS
import logging
import os
import time
from datetime import datetime
import json
import pandas as pd
import numpy as np

def setup_logging():
    """Configurar logging para la aplicación"""
    # Crear directorio de logs si no existe
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar formato de logging
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configurar logging básico
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            # Handler para archivo
            logging.FileHandler(f'{log_dir}/app.log', encoding='utf-8'),
            # Handler para consola
            logging.StreamHandler()
        ]
    )
    
    # Configurar logger específico para requests
    request_logger = logging.getLogger('requests')
    request_handler = logging.FileHandler(f'{log_dir}/requests.log', encoding='utf-8')
    request_handler.setFormatter(logging.Formatter(log_format))
    request_logger.addHandler(request_handler)
    request_logger.setLevel(logging.INFO)
    
    return logging.getLogger(__name__)

class CustomJSONEncoder(json.JSONEncoder):
    """JSON encoder personalizado para tipos pandas/numpy"""
    def default(self, obj):
        if pd.isna(obj):
            return None
        elif isinstance(obj, (pd.Timestamp, datetime)):
            return obj.isoformat() if obj else None
        elif isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif hasattr(obj, 'item'):
            try:
                return obj.item()
            except:
                return str(obj)
        return super().default(obj)

def create_app():
    logger = setup_logging()

    app = Flask(__name__)

    # Configurar JSON encoder personalizado
    app.json_encoder = CustomJSONEncoder

    # Configurar CORS
    CORS(app, origins=[
        "http://localhost:8080",
        "https://app.atika.cl",
        "http://localhost:3000",
        "http://127.0.0.1:5500",  # Live Server
        "http://localhost:5500",  # Live Server alternativo
        "file://"  # Para archivos HTML locales
    ])

    # Middleware para logging de requests
    @app.before_request
    def log_request_info():
        g.start_time = time.time()
        request_logger = logging.getLogger('requests')
        request_logger.info(f"REQUEST: {request.method} {request.url} - IP: {request.remote_addr} - User-Agent: {request.headers.get('User-Agent', 'N/A')}")
        # Log del body para requests POST/PUT (solo primeros 500 caracteres)
        if request.method in ['POST', 'PUT'] and request.content_length and request.content_length < 5000:
            try:
                body = request.get_data(as_text=True)
                if body:
                    body_preview = body[:500] + "..." if len(body) > 500 else body
                    request_logger.info(f"REQUEST BODY: {body_preview}")
            except:
                request_logger.info("REQUEST BODY: [No se pudo leer el body]")

    # Ruta para la interfaz web de ficha técnica
    @app.route('/ficha-form')
    def ficha_form():
        return render_template('ficha_form.html')

    @app.after_request
    def log_response_info(response):
        duration = time.time() - g.start_time if hasattr(g, 'start_time') else 0
        request_logger = logging.getLogger('requests')
        
        # Log de respuesta
        request_logger.info(f"RESPONSE: {response.status_code} - {request.method} {request.url} - Duration: {duration:.3f}s")
        
        # Log de errores con más detalle
        if response.status_code >= 400:
            logger.warning(f"ERROR RESPONSE: {response.status_code} - {request.method} {request.url} - Duration: {duration:.3f}s")
            
        return response
    
    # Handler para errores no capturados
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"404 Error: {request.method} {request.url} - IP: {request.remote_addr}")
        return {"error": "Endpoint not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 Error: {request.method} {request.url} - IP: {request.remote_addr} - Error: {str(error)}")
        return {"error": "Internal server error"}, 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled Exception: {request.method} {request.url} - IP: {request.remote_addr} - Exception: {str(e)}", exc_info=True)
        return {"error": "An unexpected error occurred"}, 500
    
    # Endpoint de salud para monitoreo
    @app.route('/health', methods=['GET'])
    def health_check():
        logger.info("Health check requested")
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }, 200
    
    # Registrar blueprints
    logger.info("Registrando blueprints...")
    app.register_blueprint(odoo_bp, url_prefix='/odoo')
    logger.info("Blueprint 'odoo_bp' registrado en /odoo")
    
    app.register_blueprint(datalake_bp, url_prefix='/datalake')
    logger.info("Blueprint 'datalake_bp' registrado en /datalake")
    
    app.register_blueprint(analytics_bp)
    logger.info("Blueprint 'analytics_bp' registrado en /api/analytics")
    
    from analisis_venta.periodos import analisis_venta_bp
    app.register_blueprint(analisis_venta_bp, url_prefix='/analisis_venta')
    logger.info("Blueprint 'analisis_venta_bp' registrado en /analisis_venta")

    # Registrar el blueprint de facturación
    from facturacion.periodos import bp_facturacion
    app.register_blueprint(bp_facturacion, url_prefix='/facturacion')
    logger.info("Blueprint 'bp_facturacion' registrado en /facturacion")

    # Registrar el dashboard de administración
    from admin.views import admin_bp
    app.register_blueprint(admin_bp)
    logger.info("Blueprint 'admin_bp' registrado en /admin")

    # Registrar el middleware Atika × ConceptHome (proyecto Cocinas)
    from middleware.router import middleware_bp
    app.register_blueprint(middleware_bp, url_prefix='/middleware')
    logger.info("Blueprint 'middleware_bp' registrado en /middleware")

    # Cron in-process: sincroniza periódicamente los proyectos externos activos
    from middleware.cron import iniciar_cron
    iniciar_cron()

    return app


if __name__ == '__main__':
    app = create_app()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 50)
    logger.info("INICIANDO SERVIDOR BACKEND ATIKA")
    logger.info("=" * 50)
    logger.info("Configuración:")
    logger.info("- Host: 0.0.0.0")
    logger.info("- Puerto: 5000")
    logger.info("- CORS habilitado para: http://localhost:8080, https://app.atika.cl, http://localhost:3000, http://127.0.0.1:5500, http://localhost:5500, file://")
    logger.info("- Endpoints disponibles:")
    logger.info("  - /health (GET) - Health check")
    logger.info("  - /odoo/* - API de Odoo")
    logger.info("  - /datalake/* - API de Datalake")
    logger.info("  - /api/analytics/* - API de Analytics ETL")
    logger.info("  - /analisis_venta/* - API de Análisis de Venta")
    logger.info("  - /facturacion/* - API de Facturación")
    logger.info("  - /admin - Dashboard de Administración")
    logger.info("  - /middleware/* - Sync Atika x ConceptHome (Cocinas)")
    logger.info("- Logs guardados en: logs/app.log y logs/requests.log")
    logger.info("=" * 50)
    
    try:
        logger.info("Servidor iniciado exitosamente en http://0.0.0.0:5000")
        serve(app, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        logger.info("Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"Error al iniciar servidor: {str(e)}", exc_info=True)
    finally:
        logger.info("Servidor finalizado")
        logger.info("=" * 50)
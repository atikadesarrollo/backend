from flask import Flask
from odoo_api.routes import odoo_bp
from datalake_api.routes import datalake_bp
from waitress import serve
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:8080", "https://app.atika.cl","http://localhost:3000"])  # Habilitar CORS para toda la aplicación

    # Registrar blueprints
    app.register_blueprint(odoo_bp, url_prefix='/odoo')
    app.register_blueprint(datalake_bp, url_prefix='/datalake')

    return app

if __name__ == '__main__':
    app = create_app()
    serve(app,  host='0.0.0.0', port=5000) 

#commit control 06-10-25
#dev control 
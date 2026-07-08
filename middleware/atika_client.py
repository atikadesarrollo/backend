# Cliente XML-RPC a Odoo Atika para el middleware. Independiente del que usa
# odoo_api/routes.py (ese hardcodea producción vía variables de módulo). Este
# permite elegir producción o staging vía MIDDLEWARE_ATIKA_ENV, para poder probar
# el flujo de notificaciones (F1b/F3) contra un proyecto de prueba en staging sin
# tocar producción. Cambiar a 'production' (o quitar la variable) cuando termine
# la prueba.
import os
import xmlrpc.client

from dotenv import load_dotenv

load_dotenv()

ATIKA_ENV = os.getenv('MIDDLEWARE_ATIKA_ENV', 'production')


class AtikaOdooClient:
    def __init__(self, models_proxy, uid, db, password):
        self.models_proxy = models_proxy
        self.uid = uid
        self.db = db
        self.password = password

    def execute_kw(self, model, method, args=None, kwargs=None):
        return self.models_proxy.execute_kw(
            self.db, self.uid, self.password, model, method, args or [], kwargs or {})


def get_atika_client() -> AtikaOdooClient:
    if ATIKA_ENV == 'staging':
        url = os.getenv('ODOO_STAGING_URL')
        db = os.getenv('ODOO_STAGING_DB')
        username = os.getenv('ODOO_STAGING_USERNAME')
        password = os.getenv('ODOO_STAGING_PASSWORD')
    else:
        url = os.getenv('ODOO_URL')
        db = os.getenv('ODOO_DB')
        username = os.getenv('ODOO_USERNAME')
        password = os.getenv('ODOO_PASSWORD')

    if not all([url, db, username, password]):
        raise RuntimeError(f"Faltan credenciales ODOO_* ({ATIKA_ENV}) en el .env")

    common = xmlrpc.client.ServerProxy(f"{url.rstrip('/')}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(db, username, password, {})
    if not uid:
        raise RuntimeError(f"No se pudo autenticar en Odoo Atika ({ATIKA_ENV})")
    models = xmlrpc.client.ServerProxy(f"{url.rstrip('/')}/xmlrpc/2/object", allow_none=True)
    return AtikaOdooClient(models, uid, db, password)

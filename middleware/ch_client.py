# Cliente XML-RPC al Odoo de ConceptHome (CH). Mismo mecanismo que odoo_api/routes.py
# usa para Atika, pero con las credenciales propias de CH (ver README.md).
import os
import xmlrpc.client

from dotenv import load_dotenv

load_dotenv()

CH_URL = os.getenv('CH_ODOO_URL')
CH_DB = os.getenv('CH_ODOO_DB')
CH_USERNAME = os.getenv('CH_ODOO_USERNAME')
CH_PASSWORD = os.getenv('CH_ODOO_PASSWORD')


class ChOdooClient:
    def __init__(self, models_proxy, uid):
        self.models_proxy = models_proxy
        self.uid = uid

    def execute_kw(self, model, method, args=None, kwargs=None):
        return self.models_proxy.execute_kw(
            CH_DB, self.uid, CH_PASSWORD, model, method, args or [], kwargs or {})


def get_ch_client() -> ChOdooClient:
    if not all([CH_URL, CH_DB, CH_USERNAME, CH_PASSWORD]):
        raise RuntimeError(
            "Faltan credenciales CH_ODOO_* en el .env (ver middleware/README.md)")
    common = xmlrpc.client.ServerProxy(f'{CH_URL}/xmlrpc/2/common', allow_none=True)
    uid = common.authenticate(CH_DB, CH_USERNAME, CH_PASSWORD, {})
    if not uid:
        raise RuntimeError("No se pudo autenticar en el Odoo de ConceptHome")
    models = xmlrpc.client.ServerProxy(f'{CH_URL}/xmlrpc/2/object', allow_none=True)
    return ChOdooClient(models, uid)

# Envío de notificaciones por correo del middleware (Resend), independiente del
# mail.mail de Odoo. Templates en middleware/templates/.
import os

import requests
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

load_dotenv()

RESEND_API_KEY = os.getenv('Resend_Api_key')
RESEND_FROM = 'proyectos@atika.cl'

_jinja_env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))


def render_template(nombre_archivo: str, **contexto) -> str:
    return _jinja_env.get_template(nombre_archivo).render(**contexto)


def enviar_email(destinatarios: list, asunto: str, html: str, adjuntos: list = None) -> None:
    if not RESEND_API_KEY:
        raise RuntimeError("Falta Resend_Api_key en el .env")
    cuerpo = {'from': RESEND_FROM, 'to': destinatarios, 'subject': asunto, 'html': html}
    if adjuntos:
        # Resend espera [{'filename': ..., 'content': <base64>}]. Odoo manda el
        # Binary ya codificado, así que no hay nada que convertir acá.
        cuerpo['attachments'] = adjuntos
    resp = requests.post(
        'https://api.resend.com/emails',
        headers={'Authorization': f'Bearer {RESEND_API_KEY}'},
        json=cuerpo,
        timeout=60 if adjuntos else 10,
    )
    resp.raise_for_status()

# Detecta transiciones comparando el estado ya guardado en Odoo Atika contra los
# datos frescos que acaba de traer sync.py desde CH, y dispara avisos por correo
# (Resend) ANTES de que Odoo sobreescriba el estado con su propio upsert. No hay
# base de datos propia: el "antes" se lee en vivo de Atika en cada sync.
import logging

from middleware.atika_client import get_atika_client
from middleware.mailer import enviar_email, render_template

logger = logging.getLogger(__name__)

# Modo prueba — luego se reemplaza por el responsable dinámico del proyecto.
DESTINATARIOS_INTERNOS = ['alegonfern@gmail.com', 'a.gonzalez@atika.cl']


def detectar_y_notificar(name_proyecto: str, tareas: list) -> None:
    """tareas: lista ya traducida (misma que arma obtener_estructura_proyecto).
    No propaga excepciones: un fallo de correo no debe romper el sync."""
    try:
        client = get_atika_client()
        proyectos = client.execute_kw(
            'custom.projects', 'search_read',
            [[['name', '=', name_proyecto]]],
            {'fields': ['id', 'proyecto_creado_proveedor', 'project_name'], 'limit': 1})
        if not proyectos:
            return
        proyecto = proyectos[0]

        if not proyecto['proyecto_creado_proveedor']:
            _notificar_proyecto_vinculado(name_proyecto, proyecto.get('project_name') or name_proyecto)

        tareas_actuales = client.execute_kw(
            'proyecto.tarea.externa', 'search_read',
            [[['proyecto_id', '=', proyecto['id']]]],
            {'fields': ['id_externo', 'estado_pago']})
        estado_previo = {t['id_externo']: t['estado_pago'] for t in tareas_actuales}

        for t in tareas:
            if t.get('tipo_tarea') != 'hito' or not t.get('completada'):
                continue
            previo = estado_previo.get(t['id_externo'])
            if previo in (None, 'pendiente'):
                _notificar_hito_completado(name_proyecto, t.get('name'), t.get('monto'))
    except Exception:
        logger.exception("Error detectando/notificando cambios para %s", name_proyecto)


def _notificar_proyecto_vinculado(codigo, nombre_proyecto):
    html = render_template('proyecto_vinculado.html', codigo=codigo, nombre_proyecto=nombre_proyecto)
    enviar_email(DESTINATARIOS_INTERNOS, f"Proyecto vinculado por ConceptHome: {codigo}", html)


def _notificar_hito_completado(codigo, tarea_nombre, monto):
    html = render_template('hito_completado.html', codigo=codigo, tarea_nombre=tarea_nombre, monto=monto)
    enviar_email(DESTINATARIOS_INTERNOS, f"Hito completado, pendiente de pago: {codigo}", html)

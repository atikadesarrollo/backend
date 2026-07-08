# Endpoints del apartado middleware (spec: ESPECIFICACION_TECNICA_Cocinas.md).
# MVP: sin auth/firma (se refuerza en una fase posterior).
import logging

from flask import Blueprint, jsonify, request

from middleware.sync import ProyectoNoEncontradoEnCH, obtener_estructura_proyecto

logger = logging.getLogger(__name__)
middleware_bp = Blueprint('middleware', __name__)


@middleware_bp.route('/sync/<name_proyecto>', methods=['GET'])
def sync_proyecto(name_proyecto):
    """Odoo (botón 'Actualizar proyecto' o el cron diario) llama esto para obtener
    el snapshot completo de etapas/tareas de CH y ejecutar localmente el upsert."""
    try:
        data = obtener_estructura_proyecto(name_proyecto)
        return jsonify(data), 200
    except ProyectoNoEncontradoEnCH:
        return jsonify({'error': 'proyecto_no_encontrado_en_ch'}), 404
    except Exception as e:
        logger.exception("Error sincronizando proyecto %s", name_proyecto)
        return jsonify({'error': str(e)}), 500


@middleware_bp.route('/webhook/concepthome', methods=['POST'])
def webhook_concepthome():
    """CH dispara esto desde una Automatización de su Odoo cuando una tarea
    cambia. Solo necesita el código de proyecto (name de Atika); el middleware
    gatilla la resincronización llamando a Odoo Atika vía API."""
    payload = request.get_json(force=True, silent=True) or {}
    name_proyecto = payload.get('codigo_proyecto')
    if not name_proyecto:
        return jsonify({'error': "falta 'codigo_proyecto' en el body"}), 400

    from odoo_api.routes import get_odoo_client
    try:
        client = get_odoo_client()
        ids = client.execute_kw(
            'custom.projects', 'search',
            [[['name', '=', name_proyecto], ['es_proyecto_externo', '=', True]]],
            {'limit': 1})
        if not ids:
            return jsonify({'error': 'proyecto_no_encontrado_en_atika'}), 404
        client.execute_kw('custom.projects', 'action_actualizar_proyecto', [ids])
        return jsonify({'ok': True}), 200
    except Exception as e:
        logger.exception("Error en webhook CH para %s", name_proyecto)
        return jsonify({'error': str(e)}), 500

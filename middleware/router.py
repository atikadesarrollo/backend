# Endpoints del apartado middleware (spec: ESPECIFICACION_TECNICA_Cocinas.md).
# MVP: sin auth/firma (se refuerza en una fase posterior).
import logging

from flask import Blueprint, jsonify, request

from middleware.sync import ProyectoNoEncontradoEnCH, marcar_hito_pagado, obtener_estructura_proyecto

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


@middleware_bp.route('/pago-hito/<id_externo>', methods=['POST'])
def pago_hito(id_externo):
    """Atika llama esto al confirmar el wizard de pago de un hito, para que el
    middleware refleje en CH (x_studio_estado_de_pago='Pagado') que ya se pagó."""
    try:
        marcar_hito_pagado(id_externo)
        return jsonify({'ok': True}), 200
    except Exception as e:
        logger.exception("Error marcando hito pagado en CH (id_externo=%s)", id_externo)
        return jsonify({'error': str(e)}), 500


@middleware_bp.route('/notify/<tipo>', methods=['POST'])
def notify(tipo):
    """Odoo llama esto para despachar los correos migrados de mail.mail (2026-07-13):
    alta-proyecto (F1), pago-hito (F4) y cotizacion-confirmada. El body trae los
    destinatarios (opción A: Odoo es la fuente de verdad de a quién se envía) más
    los datos del template. Devuelve 500 si el envío falla — Odoo decide qué hacer."""
    from middleware import notificaciones

    payload = request.get_json(force=True, silent=True) or {}
    destinatarios = payload.get('destinatarios') or []
    if not destinatarios:
        return jsonify({'error': "falta 'destinatarios' en el body"}), 400

    try:
        if tipo == 'alta-proyecto':
            notificaciones.notificar_alta_proyecto(
                destinatarios, payload.get('codigo', ''),
                payload.get('nombre_proyecto', ''), payload.get('proveedor', ''),
                payload.get('cliente_nombre', ''), payload.get('cliente_rut', ''),
                payload.get('valor_contrato', ''))
        elif tipo == 'pago-hito':
            notificaciones.notificar_pago_hito(
                destinatarios, payload.get('codigo', ''), payload.get('proveedor', ''),
                payload.get('hito', ''), payload.get('monto', ''),
                payload.get('fecha', ''), payload.get('referencia', ''))
        elif tipo == 'cotizacion-confirmada':
            notificaciones.notificar_cotizacion_confirmada(
                destinatarios, payload.get('codigo', ''),
                payload.get('pedido', ''), payload.get('lineas') or [])
        else:
            return jsonify({'error': f"tipo de notificación desconocido: {tipo}"}), 404
        return jsonify({'ok': True}), 200
    except Exception as e:
        logger.exception("Error enviando notificación '%s'", tipo)
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

# Cron in-process: sincroniza periódicamente todos los proyectos externos activos,
# sin depender de que alguien apriete el botón en Odoo ni de que CH configure nada
# de su lado. Reutiliza la misma llamada que ya usa el webhook de CH
# (action_actualizar_proyecto), en loop sobre todos los proyectos activos. Sin base
# de datos propia: cada corrida vuelve a leer el estado actual de Atika y CH.
import logging
import os
import threading
import time

from middleware.atika_client import get_atika_client

logger = logging.getLogger(__name__)

INTERVALO_SEGUNDOS = int(os.getenv('CRON_SYNC_INTERVALO_SEGUNDOS', '1800'))

_hilo_iniciado = False
_lock = threading.Lock()


def sincronizar_todos():
    """Recorre todos los proyectos externos activos en Atika y dispara
    action_actualizar_proyecto en cada uno (misma llamada que usa el webhook)."""
    try:
        client = get_atika_client()
    except Exception:
        logger.exception("Cron: no se pudo conectar a Atika, se salta esta corrida")
        return

    try:
        proyecto_ids = client.execute_kw(
            'custom.projects', 'search',
            [[['es_proyecto_externo', '=', True]]], {})
    except Exception:
        logger.exception("Cron: error buscando proyectos externos activos")
        return

    logger.info("Cron: sincronizando %d proyecto(s) externo(s)", len(proyecto_ids))
    for proyecto_id in proyecto_ids:
        try:
            client.execute_kw('custom.projects', 'action_actualizar_proyecto', [[proyecto_id]])
        except Exception:
            logger.exception("Cron: error sincronizando proyecto id=%s", proyecto_id)


def _loop():
    while True:
        time.sleep(INTERVALO_SEGUNDOS)
        sincronizar_todos()


def iniciar_cron():
    """Arranca el hilo de background una sola vez por proceso."""
    global _hilo_iniciado
    with _lock:
        if _hilo_iniciado:
            return
        _hilo_iniciado = True
    hilo = threading.Thread(target=_loop, daemon=True)
    hilo.start()
    logger.info("Cron de sincronización iniciado (cada %d segundos)", INTERVALO_SEGUNDOS)

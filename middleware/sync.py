# Lee las tareas del proyecto en el Odoo de ConceptHome y las traduce al formato
# que espera `_upsert_externo` del módulo Odoo `proyectos_externos`
# (proyecto.tarea.externa). Sin etapas: el disparador de avisos/pagos es el
# booleano `completada`, no una agrupación por etapa/stage.
from middleware.ch_client import get_ch_client
from middleware.field_map import (
    CH_ESTADO_PAGO_PAGADO,
    CH_FIELD_CODIGO_PROYECTO,
    CH_FIELD_ESTADO_PAGO,
    CH_FIELD_STATE,
    CH_FIELD_TIPO_TAREA,
    CH_FIELD_VISIBLE,
    CH_PROJECT_MODEL,
    CH_STATE_COMPLETADA,
    CH_STATE_LABELS,
    CH_TASK_MODEL,
    FIELD_MAP_TASK,
    TIPO_TAREA_MAP,
)
from middleware.notificaciones import detectar_y_notificar


class ProyectoNoEncontradoEnCH(Exception):
    """El proyecto aún no existe en CH (no lo han creado desde la oportunidad, F1b)."""


def obtener_estructura_proyecto(name_proyecto: str) -> dict:
    client = get_ch_client()

    # Relación 1:N — un mismo código Atika puede vivir en VARIOS proyectos de CH;
    # el espejo en Atika junta las tareas de todos.
    proyectos = client.execute_kw(
        CH_PROJECT_MODEL, 'search_read',
        [[[CH_FIELD_CODIGO_PROYECTO, '=', name_proyecto]]],
        {'fields': ['id', 'name']})
    if not proyectos:
        raise ProyectoNoEncontradoEnCH(name_proyecto)
    ch_project_ids = [p['id'] for p in proyectos]

    campos = list(FIELD_MAP_TASK.keys()) + [CH_FIELD_TIPO_TAREA, CH_FIELD_STATE, CH_FIELD_VISIBLE]
    tareas_ch = client.execute_kw(
        CH_TASK_MODEL, 'search_read',
        [[['project_id', 'in', ch_project_ids], [CH_FIELD_VISIBLE, '=', True]]],
        {'fields': campos})

    tareas = []
    for t in tareas_ch:
        tarea = {canon: t.get(real) for real, canon in FIELD_MAP_TASK.items()}
        tarea['id_externo'] = str(tarea['id_externo'])
        tarea['tipo_tarea'] = TIPO_TAREA_MAP.get(t.get(CH_FIELD_TIPO_TAREA), 'normal')
        estado_ch = t.get(CH_FIELD_STATE)
        tarea['status_tarea'] = CH_STATE_LABELS.get(estado_ch, estado_ch or None)
        tarea['completada'] = estado_ch == CH_STATE_COMPLETADA  # ÚNICO disparador de avisos/pagos
        tareas.append(tarea)

    detectar_y_notificar(name_proyecto, tareas)

    return {'tareas': tareas}


def marcar_hito_pagado(id_externo: str) -> None:
    """Único write del middleware sobre CH: refleja que Atika registró el pago
    de un hito. Se llama desde el wizard de pago de Atika (junto con F4)."""
    client = get_ch_client()
    client.execute_kw(
        CH_TASK_MODEL, 'write',
        [[int(id_externo)], {CH_FIELD_ESTADO_PAGO: CH_ESTADO_PAGO_PAGADO}])

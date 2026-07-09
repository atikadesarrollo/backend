# >>> ÚNICO ARCHIVO QUE CAMBIA CUANDO CONCEPTHOME CONFIRME SUS NOMBRES REALES <<<
#
# CH usa Odoo Studio, así que sus campos custom son `x_studio_*`. Nombres confirmados
# el 2026-07-07 escaneando en vivo el Odoo real de CH vía XML-RPC (ver
# "Información de CH.txt" en Claude Proyects/Atika).

CH_PROJECT_MODEL = 'project.project'
CH_TASK_MODEL = 'project.task'

# Campo en project.project donde CH guarda nuestro código de proyecto (= name de Atika).
# Se crea primero en crm.lead (Studio) y se hereda al convertir a proyecto — mismo
# nombre técnico en ambos modelos. Reemplazó a x_studio_id_proyecto_externo (ya no existe).
CH_FIELD_CODIGO_PROYECTO = 'x_studio_id_proyecto_atika'

# Campo booleano de CH (project.task): solo las tareas visibles=True llegan a Atika.
CH_FIELD_VISIBLE = 'x_studio_visible'

# Campo de CH (project.task) con el tipo de tarea.
CH_FIELD_TIPO_TAREA = 'x_studio_tipo_tarea'

# Campo ESTÁNDAR de Odoo (no es custom de CH) en project.task. Sirve doble propósito:
# informativo (status_tarea) y disparador real de avisos/pagos (completada).
CH_FIELD_STATE = 'state'

# Traduce el valor real de x_studio_tipo_tarea (CH) al valor interno esperado por
# proyecto.tarea.externa.tipo_tarea. Sin valor / no mapeado → 'normal'.
TIPO_TAREA_MAP = {
    'Hito': 'hito',
    'Entrega': 'entregable',
    'Gestión Interna': 'normal',
}

# Valor de `state` que CH usa para marcar una tarea terminada. Es el ÚNICO
# disparador de avisos/pagos (ver custom_projects.py::_upsert_externo).
CH_STATE_COMPLETADA = '1_done'

# Etiquetas legibles del `state` estándar de Odoo, solo para mostrar en
# 'status_tarea' (columna "Estado CH" — informativo, no dispara nada).
CH_STATE_LABELS = {
    '01_in_progress': 'En progreso',
    '02_changes_requested': 'Cambios solicitados',
    '03_approved': 'Aprobado',
    '1_done': 'Terminado',
    '1_canceled': 'Cancelado',
    '04_waiting_normal': 'Esperando',
}

# Campos de mapeo directo 1:1 (mismo valor, solo cambia el nombre). tipo_tarea,
# status_tarea y completada se arman aparte en sync.py porque requieren traducción.
FIELD_MAP_TASK = {
    'id': 'id_externo',
    'name': 'name',
    'sequence': 'secuencia',
    'x_studio_monto_hito': 'monto',
}

# Campo de CH (project.task) donde se refleja el estado de pago del hito. Único
# campo que el middleware ESCRIBE en CH (todo lo demás arriba es solo lectura):
# Atika lo actualiza cuando registra el pago de un hito (wizard de pago → F4).
# Confirmado con el usuario 2026-07-08: CH solo tiene 2 valores ('Pendiente de
# Pago' / 'Pagado'), Atika maneja 3 ('notificado'/'pendiente'/'pagado') — solo
# se escribe cuando Atika llega a 'pagado'.
CH_FIELD_ESTADO_PAGO = 'x_studio_estado_de_pago'
CH_ESTADO_PAGO_PAGADO = 'Pagado'

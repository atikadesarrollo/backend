# Middleware — Atika × ConceptHome (proyecto Cocinas)

Apartado dentro del servicio backend existente. Sincroniza el proyecto de
Odoo Atika (módulo `proyectos_externos`) con el Odoo del proveedor
ConceptHome (CH), todo vía API (XML-RPC). Las notificaciones **F1** (alta de
proyecto) y **F4** (aviso de pago) van por correo — ya implementadas en el
módulo Odoo — y no pasan por aquí.

MVP: sin auth/firma entre servicios. Se refuerza en una fase posterior.

## Variables de entorno (agregar al `.env` existente del servicio)

El servicio ya tiene las credenciales de Odoo **Atika** (`ODOO_URL`,
`ODOO_DB`, `ODOO_USERNAME`, `ODOO_PASSWORD` — las usa `odoo_api/`); el
middleware las reutiliza vía `odoo_api.routes.get_odoo_client`, no se
duplican.

Agregar el bloque de **ConceptHome**:

```bash
CH_ODOO_URL=          # URL del Odoo de ConceptHome (ej. https://odoo.concepthome.cl)
CH_ODOO_DB=           # nombre de su base de datos
CH_ODOO_USERNAME=     # usuario que entregó ConceptHome
CH_ODOO_PASSWORD=     # contraseña / API key que entregó ConceptHome
```

## Endpoints

- `GET /middleware/sync/<name_proyecto>` — devuelve `{tareas}` leídas de CH
  (contrato interno que consume `_upsert_externo` en Odoo; sin etapas — el
  disparador de avisos/pagos es el booleano `completada` de cada tarea, no
  una agrupación por etapa). Lo llama Odoo (botón *Actualizar proyecto* o el
  cron diario). 404 si el proyecto aún no existe en CH.
- `POST /middleware/webhook/concepthome` — lo llama la Automatización del
  Odoo de CH cuando una tarea cambia. Body: `{"codigo_proyecto": "PY007598"}`.
  El middleware busca ese proyecto en Atika y gatilla
  `action_actualizar_proyecto` (mismo flujo que el botón).

## Conexión con CH real

`field_map.py` ya tiene los nombres reales, confirmados el 2026-07-07
escaneando en vivo el Odoo de CH vía XML-RPC (ver "Información de CH.txt",
Claude Proyects/Atika): `x_studio_id_proyecto_externo`, `x_studio_tipo_tarea`
(valores `'Hito'`/`'Entrega'`/`'Gestión Interna'`), `x_studio_monto_hito`,
`x_studio_visible`. El disparador de "completada" es el campo **estándar**
de Odoo `state` (no un campo custom de CH) cuando vale `'1_done'`.

## Probar

```bash
curl http://localhost:5000/middleware/sync/PY007598
curl -X POST http://localhost:5000/middleware/webhook/concepthome \
  -H "Content-Type: application/json" \
  -d '{"codigo_proyecto": "PY007598"}'
```

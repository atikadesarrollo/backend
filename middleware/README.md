# Middleware — Atika × ConceptHome (proyecto Cocinas)

Apartado dentro del servicio backend existente. Sincroniza el proyecto de
Odoo Atika (módulo `proyectos_externos`) con el Odoo del proveedor
ConceptHome (CH), todo vía API (XML-RPC), y maneja las notificaciones que no
dependen de Odoo nativo (F1b, F3).

MVP: sin auth/firma entre servicios. Se refuerza en una fase posterior.

## Variables de entorno (agregar al `.env` existente del servicio)

El servicio ya tiene las credenciales de Odoo **Atika** (`ODOO_URL`,
`ODOO_DB`, `ODOO_USERNAME`, `ODOO_PASSWORD` — las usa `odoo_api/`); el
middleware las reutiliza vía `odoo_api.routes.get_odoo_client` (producción) o
`middleware.atika_client` (permite apuntar a `ODOO_STAGING_*` con
`MIDDLEWARE_ATIKA_ENV=staging`, no se duplican credenciales).

Agregar el bloque de **ConceptHome**:

```bash
CH_ODOO_URL=          # URL del Odoo de ConceptHome (ej. https://concepthome.odoo.com)
CH_ODOO_DB=           # nombre de su base de datos
CH_ODOO_USERNAME=     # usuario que entregó ConceptHome
CH_ODOO_PASSWORD=     # contraseña / API key que entregó ConceptHome
Resend_Api_key=       # API key de Resend, para F1b/F3 (mailer.py)
```

## Endpoints

- `GET /middleware/sync/<name_proyecto>` — devuelve `{tareas}` leídas de CH
  (contrato interno que consume `_upsert_externo` en Odoo; sin etapas — el
  disparador de avisos/pagos es el booleano `completada` de cada tarea, no
  una agrupación por etapa). Lo llama Odoo (botón *Actualizar proyecto* o el
  cron periódico). 404 si el proyecto aún no existe en CH. De paso, detecta y
  dispara F1b/F3 (ver `notificaciones.py`) comparando el estado "antes" (leído
  de Atika) contra el "después" (fresco de CH).
- `POST /middleware/webhook/concepthome` — lo llama la Automatización del
  Odoo de CH cuando una tarea cambia. Body: `{"codigo_proyecto": "123456"}`.
  El middleware busca ese proyecto en Atika y gatilla
  `action_actualizar_proyecto` (mismo flujo que el botón, con lo cual también
  puede disparar F1b/F3).
- `POST /middleware/pago-hito/<id_externo>` — lo llama Atika al confirmar el
  wizard de pago de un hito (F4). Escribe en CH
  `x_studio_estado_de_pago='Pagado'` sobre la tarea `id_externo` — es el
  **único write** que hace el middleware sobre CH (todo lo demás es lectura).

## Conexión con CH real

`field_map.py` tiene los nombres reales, confirmados el 2026-07-07 escaneando
en vivo el Odoo de CH vía XML-RPC (ver "Información de CH.txt", Claude
Proyects/Atika):

- `x_studio_id_proyecto_atika` (`project.project` y `crm.lead`) — código Atika,
  clave de correlación.
- `x_studio_tipo_tarea` (`project.task`) — valores `'Hito'` / `'Entrega'` /
  `'Gestión Interna'`.
- `x_studio_monto_hito` (`project.task`, Float) — monto crudo del hito.
- `x_studio_visible` (`project.task`, Boolean) — solo tareas visibles llegan a
  Atika.
- `state` (`project.task`, campo **estándar** de Odoo, no custom) — dispara
  "completada" cuando vale `'1_done'`.
- `x_studio_estado_de_pago` (`project.task`) — confirmado 2026-07-08, valores
  `'Pendiente de Pago'` / `'Pagado'`. Único campo que el middleware escribe.

## Flujo completo — qué conlleva cada paso y qué notificación dispara

**F1 — Enviar proyecto** (botón en Odoo Atika, `action_enviar_proyecto`):
Odoo nativo (`mail.mail`), no pasa por el middleware. Envía "Nuevo proyecto
asignado" a los correos del proveedor. Marca `proyecto_enviado=True`,
`estado_sync='conectado'`.

**F1b — Proyecto vinculado por CH** (detectado, no manual): ocurre dentro de
cualquier `GET /sync/<name>` (botón "Actualizar proyecto" o cron). El
middleware compara `proyecto_creado_proveedor` ANTES (leído de Atika) contra
el hecho de que ahora SÍ encontró el proyecto en CH. Primera vez que pasa de
no-vinculado a vinculado → dispara correo vía Resend HTTP directo
(`notificaciones.py` + `mailer.py`), independiente de Odoo.

**Sync / pull de tareas** (mismo `GET /sync/<name>`): trae todas las tareas
visibles de CH y hace upsert idempotente en `proyecto.tarea.externa`. No
dispara notificación por sí mismo, salvo lo que detecte F1b/F3 en el mismo
llamado.

**F3 — Hito completado por el proveedor** (detectado dentro del mismo sync):
si una tarea tipo `hito` pasa a `state='1_done'` en CH y en Atika seguía
`estado_pago='pendiente'`, el middleware lo detecta comparando antes/después
y dispara correo "Hito completado, pendiente de pago" vía Resend HTTP directo
— igual que F1b, no pasa por Odoo. En Atika queda `estado_pago='notificado'`.

**F4 — Marcar pagado** (wizard `proyecto.pago.hito.wizard` en Atika,
`action_confirmar`): registra `estado_pago='pagado'`, fecha, referencia y
comprobante en Atika. Dispara DOS cosas en el mismo flujo:
1. `_enviar_correo_pago_hito` — correo nativo de Odoo (`mail.mail`) al
   proveedor, "Pago registrado".
2. `_notificar_pago_ch` — POST a `/middleware/pago-hito/<id_externo>`, que
   escribe `x_studio_estado_de_pago='Pagado'` en CH (F4b). Si falla, no
   revierte el pago ya registrado en Atika — solo deja advertencia en el
   chatter.

**Cotización confirmada** (`sale_order.py` en Atika, disparador temporal en
`create()`/`write()` — pendiente moverlo a `action_confirm()`): correo nativo
de Odoo con el detalle de líneas del pedido confirmado, a destinatarios de
prueba hardcodeados (pendiente definir los reales).

⚠️ **Ojo con bases de staging "neutralizadas":** si `database.is_neutralized`
está en `true` (común en bases Odoo Online de desarrollo/duplicadas), los
correos nativos de Odoo (F1, F4, cotización) **no llegan de verdad** aunque
Odoo marque el `mail.mail` como `state='sent'` sin ningún error — es un
comportamiento de la plataforma, no del código. F1b y F3 SÍ funcionan igual
en staging porque van por Resend HTTP directo, no por Odoo.

## Probar

```bash
curl http://localhost:5000/middleware/sync/123456
curl -X POST http://localhost:5000/middleware/webhook/concepthome \
  -H "Content-Type: application/json" \
  -d '{"codigo_proyecto": "123456"}'
curl -X POST http://localhost:5000/middleware/pago-hito/460
```

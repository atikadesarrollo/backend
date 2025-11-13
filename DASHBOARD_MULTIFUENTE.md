# Dashboard Multi-Fuente - Documentación

## Cambios Realizados

### 1. Nuevo Módulo de Facturación

**Archivos creados:**

- `Scripts/pipeline_facturacion.py`: Pipeline ETL para crear tablas resumen de facturación
- `facturacion/__init__.py`: Inicializador del módulo
- `facturacion/periodos.py`: Blueprint Flask con endpoints para facturación
- `facturacion/models.py`: Modelos (pendiente de implementación)
- `API_FACTURACION_FRONTEND.md`: Documentación de API para frontend

**Tablas generadas:**

- `DL_Facturacion_v_Completo`: Copia completa de la vista
- `DL_Facturacion_v_Reciente`: Últimos 30 días
- `DL_Facturacion_v_Media`: Últimos 90 días
- `DL_Facturacion_v_Antiguo`: Últimos 365 días

### 2. Endpoints de Facturación

**Base URL:** `/facturacion`

#### GET /facturacion/periodos

Devuelve lista de periodos disponibles con estadísticas:

```json
{
  "periodos": [
    {
      "periodo": "Completo",
      "tabla": "DL_Facturacion_v_Completo",
      "fecha_min": "2020-01-01",
      "fecha_max": "2025-10-15",
      "total_registros": 150000
    },
    ...
  ]
}
```

#### GET /facturacion/query

Consulta datos con filtros y paginación.

**Parámetros:**

- `periodo`: (opcional) "Completo", "Reciente", "Media", "Antiguo"
- `fecha_inicio`: (opcional) Fecha inicial (YYYY-MM-DD)
- `fecha_fin`: (opcional) Fecha final (YYYY-MM-DD)
- `cliente`: (opcional) Filtro por cliente (LIKE)
- `proyecto`: (opcional) Filtro por proyecto (LIKE)
- `vendedor`: (opcional) Filtro por vendedor (LIKE)
- `sku`: (opcional) Filtro por SKU (LIKE)
- `departamento`: (opcional) Filtro por departamento (LIKE)
- `canal`: (opcional) Filtro por canal (LIKE)
- `monto_min`: (opcional) Monto mínimo
- `monto_max`: (opcional) Monto máximo
- `descripcion`: (opcional) Filtro por descripción (LIKE)
- `rubro`: (opcional) Filtro por rubro (LIKE)
- `familia`: (opcional) Filtro por familia (LIKE)
- `marca`: (opcional) Filtro por marca (LIKE)
- `order_by`: (opcional) Ordenamiento (default: "[Fecha de oferta] DESC")
- `limit`: (opcional) Registros por página (default: 100)
- `offset`: (opcional) Offset para paginación (default: 0)

**Respuesta:**

```json
{
  "tabla": "DL_Facturacion_v_Reciente",
  "total": 1500,
  "data": [
    {
      "Fecha de oferta": "2025-09-15",
      "Cliente": "EmpresaX",
      "Proyecto": "ProyectoY",
      "Monto facturado": 12345.67,
      ...
    }
  ]
}
```

### 3. Cambios en el Dashboard de Administración

**Archivo modificado:** `admin/views.py`

**Cambios principales:**

- Ahora consulta periodos de ambas fuentes (venta y facturación)
- Selección dinámica de API según base de datos elegida
- Variables separadas: `periodos_venta` y `periodos_facturacion`
- Nueva variable de contexto: `base_datos`

**Archivo modificado:** `admin/templates/admin_dashboard.html`

**Cambios principales:**

1. **Selector de Base de Datos:** Nueva sección con dropdown para elegir entre:

   - Análisis de Venta
   - Facturación

2. **Periodos dinámicos:** Se muestran los periodos según la base de datos seleccionada

3. **Filtros condicionales:** Los filtros se muestran solo después de seleccionar la base de datos

4. **JavaScript mejorado:**
   - `mostrarFiltros()`: Muestra/oculta secciones según selección
   - Actualización automática al cambiar base de datos
   - Persistencia de selección en formularios de paginación

### 4. Integración en app.py

**Cambios:**

```python
from facturacion.periodos import bp_facturacion
app.register_blueprint(bp_facturacion, url_prefix='/facturacion')
```

El Blueprint de facturación está registrado y disponible en `/facturacion`.

## Flujo de Uso del Dashboard

1. **Seleccionar Base de Datos:**

   - Usuario elige entre "Análisis de Venta" o "Facturación"
   - Al seleccionar, se recarga la página para obtener periodos disponibles

2. **Ver Periodos Disponibles:**

   - Se muestra tarjeta con periodos, rangos de fechas y total de registros

3. **Aplicar Filtros:**

   - Usuario completa los filtros deseados
   - Click en "Consultar"

4. **Ver Resultados:**
   - Tabla con resultados paginados
   - Controles de paginación
   - Opción "Todos los registros" (con validación de límite)

## Selección Inteligente de Tabla

Ambos endpoints (venta y facturación) usan lógica inteligente:

- Si se proporciona `periodo`: usa la tabla especificada
- Si se proporciona rango de fechas:
  - 0-30 días: usa tabla `Reciente`
  - 31-90 días: usa tabla `Media`
  - 91-365 días: usa tabla `Antiguo`
  - Más de 365 días: usa tabla `Completo`
- Default: usa tabla `Completo`

## Próximos Pasos

1. **Ejecutar pipeline de facturación:**

   ```powershell
   python Scripts/pipeline_facturacion.py
   ```

2. **Probar endpoints:**

   - GET http://localhost:5000/facturacion/periodos
   - GET http://localhost:5000/facturacion/query?periodo=Reciente

3. **Probar dashboard:**

   - http://localhost:5000/admin
   - Seleccionar "Facturación"
   - Aplicar filtros y consultar

4. **Verificar campos:**
   - Confirmar que los campos de filtro coinciden con la estructura de `DL_Facturacion_v`
   - Ajustar nombres de columnas si es necesario

## Notas Técnicas

- Ambos endpoints usan la misma estructura de respuesta
- Paginación implementada con `OFFSET` y `FETCH NEXT`
- Filtros usan `LIKE` para búsquedas flexibles
- Protección contra consultas muy grandes (límite 10,000 en "Todos")
- Timeout de 60 segundos para consultas grandes
- Logging completo en `logs/app.log` y `logs/requests.log`

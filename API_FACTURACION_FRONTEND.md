# API de Facturación - Guía Completa para Frontend

## Endpoints disponibles

### 1. Listar periodos

- **GET** `/facturacion/periodos`
- **Descripción:** Devuelve los periodos disponibles para consulta con estadísticas completas.
- **Ejemplo de respuesta:**

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
    {
      "periodo": "Reciente",
      "tabla": "DL_Facturacion_v_Reciente",
      "fecha_min": "2025-09-15",
      "fecha_max": "2025-10-15",
      "total_registros": 1250
    }
  ]
}
```

### 2. Consultar datos (query)

- **GET** `/facturacion/query`
- **Descripción:** Consulta datos de facturación con filtros, paginación y selección inteligente de tabla.

**Parámetros principales:**

- `periodo`, `fecha_inicio`, `fecha_fin`: Selección de datos
- `limit`, `offset`: Paginación (default: 100, 0)
- `order_by`: Ordenamiento (default: "[Fecha de oferta] DESC")
- Filtros de texto (LIKE): `cliente`, `proyecto`, `vendedor`, `sku`, `departamento`, `canal`, `descripcion`, `rubro`, `familia`, `marca`
- Filtros numéricos: `monto_min`, `monto_max`

**Respuesta:**

```json
{
  "tabla": "DL_Facturacion_v_Reciente",
  "total": 1500,
  "data": [...]
}
```

Ver documentación completa en DASHBOARD_MULTIFUENTE.md

## Endpoints disponibles

### 1. Listar periodos

- **GET** `/facturacion/periodos`
- **Descripción:** Devuelve los periodos disponibles para consulta (Completo, Reciente, Media, Antiguo).
- **Ejemplo de respuesta:**

```json
[
  { "nombre": "Completo", "tabla": "DL_Facturacion_v_Completo" },
  { "nombre": "Reciente", "tabla": "DL_Facturacion_v_Reciente" },
  { "nombre": "Media", "tabla": "DL_Facturacion_v_Media" },
  { "nombre": "Antiguo", "tabla": "DL_Facturacion_v_Antiguo" }
]
```

### 2. Consultar datos (query)

- **GET** `/facturacion/query`
- **Descripción:** Consulta datos de facturación según filtros y periodo seleccionado.
- **Parámetros disponibles:**
  - `periodo`: (opcional) "Completo", "Reciente", "Media", "Antiguo". Default: "Completo".
  - `fecha_inicio`: (opcional) Fecha inicial (YYYY-MM-DD).
  - `fecha_fin`: (opcional) Fecha final (YYYY-MM-DD).
  - `cliente`: (opcional) Nombre del cliente.
  - `proyecto`: (opcional) Nombre del proyecto.
- **Ejemplo de request:**

```
GET /facturacion/query?periodo=Reciente&fecha_inicio=2025-09-01&fecha_fin=2025-09-30&cliente=EmpresaX&proyecto=ProyectoY
```

- **Ejemplo de respuesta:**

```json
[
  {
    "Fecha de oferta": "2025-09-15",
    "Cliente": "EmpresaX",
    "Proyecto": "ProyectoY",
    "Monto": 12345.67,
    ...otros campos...
  },
  ...
]
```

## Notas

- El endpoint `/facturacion/query` devuelve máximo 50 registros por consulta para evitar sobrecarga.
- Si necesitas todos los registros, solicita paginación o consulta por rangos de fecha.
- Los nombres de los campos pueden variar según la estructura de la vista `DL_Facturacion_v`.

## Ejemplo de integración (fetch en JS)

```js
fetch("https://tu-backend/facturacion/query?periodo=Media&cliente=EmpresaX")
  .then((res) => res.json())
  .then((data) => {
    console.log(data);
  });
```

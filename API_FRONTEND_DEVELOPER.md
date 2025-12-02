# Guía para Desarrolladores Frontend - API Analisis Venta

## Introducción

Esta guía explica cómo consumir el backend de Analisis Venta, cómo usar los filtros disponibles y cómo interpretar la paginación y los periodos. Incluye ejemplos prácticos para facilitar la integración desde cualquier frontend (React, Vue, Angular, etc.).

---

## Endpoints principales

### 1. Listar periodos disponibles

**GET** `/analisis_venta/periodos`

**Respuesta:**

```json
{
  "periodos": [
    {
      "periodo": "Reciente",
      "tabla": "DL_Analisis_Venta_v_Reciente",
      "fecha_min": "2025-09-14",
      "fecha_max": "2025-10-14",
      "total_registros": 1234
    },
    {
      "periodo": "Media",
      "tabla": "DL_Analisis_Venta_v_Media",
      ...
    },
    {
      "periodo": "Antiguo",
      "tabla": "DL_Analisis_Venta_v_Antiguo",
      ...
    },
    {
      "periodo": "Completo",
      "tabla": "DL_Analisis_Venta_v_Completo",
      ...
    }
  ]
}
```

---

### 2. Consultar datos con filtros y paginación

**GET** `/analisis_venta/query`

**Parámetros disponibles:**

- `fecha_inicio` (YYYY-MM-DD)
- `fecha_fin` (YYYY-MM-DD)
- `periodo` (Reciente, Media, Antiguo, Completo) [opcional]
- `proyecto`, `cliente`, `vendedor`, `sku`, `departamento`, `canal`, `descripcion`, `rubro`, `familia`, `marca` (texto)
- `monto_min`, `monto_max` (número)
- `order_by` (ejemplo: `[Fecha de oferta] DESC`)
- `limit` (número de registros por página, default: 50)
- `offset` (registro inicial, default: 0)

**Ejemplo de llamada (fetch en JS):**

```js
fetch(
  "http://127.0.0.1:5000/analisis_venta/query?fecha_inicio=2025-10-01&fecha_fin=2025-10-14&proyecto=PROY1&limit=50&offset=0"
)
  .then((res) => res.json())
  .then((data) => console.log(data));
```

**Respuesta:**

```json
{
  "tabla": "DL_Analisis_Venta_v_Reciente",
  "total": 123,
  "data": [
    {
      "Fecha de oferta": "2025-10-01",
      "Proyecto": "PROY1",
      "Cliente": "Cliente A",
      ...
    },
    ...
  ]
}
```

---

## Paginación

- Usa `limit` para definir cuántos registros quieres por página (recomendado: 50)
- Usa `offset` para saltar registros (ejemplo: página 2 → offset=50)
- El backend responde con el total de registros para calcular páginas

**Ejemplo de paginación:**

```js
// Página 1
fetch(".../query?limit=50&offset=0");
// Página 2
fetch(".../query?limit=50&offset=50");
```

---

## Botón "Todos los registros"

- Si necesitas todos los datos, usa `limit=10000` y `offset=0` (máximo permitido por seguridad)
- Si el total supera 10,000, el backend devolverá un error

**Ejemplo:**

```js
fetch(".../query?limit=10000&offset=0");
```

---

## Selección automática de tabla

- Si no envías `periodo`, el backend selecciona la tabla según el rango de fechas:
  - 0-30 días → Reciente
  - 31-90 días → Media
  - 91-365 días → Antiguo
  - > 365 días o sin filtro → Completo
- Puedes forzar el periodo con el parámetro `periodo=Completo`

---

## Filtros disponibles en la API

Puedes combinar todos estos filtros en la consulta. Si no envías alguno, no se aplica ese filtro.

| Parámetro    | Tipo   | Descripción                                                 | Ejemplo valor          |
| ------------ | ------ | ----------------------------------------------------------- | ---------------------- |
| fecha_inicio | fecha  | Fecha inicial del rango (YYYY-MM-DD)                        | 2025-10-01             |
| fecha_fin    | fecha  | Fecha final del rango (YYYY-MM-DD)                          | 2025-10-14             |
| periodo      | texto  | Periodo a consultar (Reciente, Media, Antiguo, Completo)    | Reciente               |
| proyecto     | texto  | Nombre o parte del nombre del proyecto                      | PROY1                  |
| cliente      | texto  | Nombre o parte del nombre del cliente                       | ClienteA               |
| vendedor     | texto  | Nombre o parte del nombre del vendedor                      | VendedorX              |
| sku          | texto  | Código o parte del código SKU                               | SKU123                 |
| departamento | texto  | Nombre o parte del departamento                             | Ventas                 |
| canal        | texto  | Nombre o parte del canal                                    | Online                 |
| monto_min    | número | Monto mínimo facturado                                      | 1000                   |
| monto_max    | número | Monto máximo facturado                                      | 5000                   |
| descripcion  | texto  | Descripción o parte de la descripción                       | Oferta especial        |
| rubro        | texto  | Nombre o parte del rubro                                    | Tecnología             |
| familia      | texto  | Nombre o parte de la familia                                | Computadoras           |
| marca        | texto  | Nombre o parte de la marca                                  | HP                     |
| order_by     | texto  | Orden de los resultados (ejemplo: `[Fecha de oferta] DESC`) | [Fecha de oferta] DESC |
| limit        | número | Número de registros por página (máximo 10,000)              | 50                     |
| offset       | número | Número de registros a saltar (para paginación)              | 0                      |

**Todos los filtros de texto usan búsqueda parcial (`LIKE %valor%`).**

---

## Ejemplo de consulta con todos los filtros

```js
fetch(
  "http://127.0.0.1:5000/analisis_venta/query?fecha_inicio=2025-10-01&fecha_fin=2025-10-14&periodo=Reciente&proyecto=PROY1&cliente=ClienteA&vendedor=VendedorX&sku=SKU123&departamento=Ventas&canal=Online&monto_min=1000&monto_max=5000&descripcion=Oferta especial&rubro=Tecnología&familia=Computadoras&marca=HP&order_by=[Fecha de oferta] DESC&limit=50&offset=0"
)
  .then((res) => res.json())
  .then((data) => console.log(data));
```

---

## Notas para el desarrollador

- Todos los endpoints devuelven JSON
- Si la consulta es muy grande, el backend puede devolver un error por límite de registros
- Usa los periodos para optimizar la consulta y mejorar la velocidad
- Si necesitas más filtros, consulta con el equipo backend para agregar nuevos campos

---

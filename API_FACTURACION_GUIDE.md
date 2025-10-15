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

#### Parámetros disponibles:

**Selección de datos:**

- `periodo`: (opcional) "Completo", "Reciente", "Media", "Antiguo". Si se omite, se selecciona automáticamente según rango de fechas.
- `limit`: (opcional) Registros por página. Default: 100.
- `offset`: (opcional) Offset para paginación. Default: 0.
- `order_by`: (opcional) Campo y orden (ej: "[Fecha documento] DESC"). Default: "[Fecha documento] DESC".

**Filtros de fecha:**

- `fecha_inicio`: (opcional) Fecha inicial (YYYY-MM-DD). Usa comparación >= con CAST a DATE.
- `fecha_fin`: (opcional) Fecha final (YYYY-MM-DD). Usa comparación <= con CAST a DATE.

**Filtros de texto (usan LIKE %valor%):**

- `cliente`: (opcional) Filtro por razón social del cliente (búsqueda parcial).
- `vendedor`: (opcional) Filtro por vendedor factura o vendedor oferta (búsqueda parcial).
- `descripcion`: (opcional) Filtro por descripción del producto (búsqueda parcial).
- `rubro`: (opcional) Filtro por rubro (búsqueda parcial).
- `familia`: (opcional) Filtro por familia de producto (búsqueda parcial).
- `marca`: (opcional) Filtro por marca (búsqueda parcial).
- `tipo_documento`: (opcional) Filtro por tipo de documento (búsqueda parcial).
- `numero_documento`: (opcional) Filtro por número de documento (búsqueda parcial).
- `folio_sii`: (opcional) Filtro por folio SII (búsqueda parcial).
- `codigo`: (opcional) Filtro por código de producto (búsqueda parcial).
- `obra`: (opcional) Filtro por nombre de obra (búsqueda parcial).
- `unidad_negocio`: (opcional) Filtro por unidad de negocios (búsqueda parcial).
- `categoria_cliente`: (opcional) Filtro por categoría de cliente (búsqueda parcial).

**Filtros numéricos:**

- `monto_min`: (opcional) Monto mínimo en campo [Venta neta].
- `monto_max`: (opcional) Monto máximo en campo [Venta neta].

#### Selección Inteligente de Tabla:

Si no se especifica `periodo`, el sistema selecciona automáticamente la tabla más eficiente según el rango de fechas:

- **0-30 días:** usa `DL_Facturacion_v_Reciente`
- **31-90 días:** usa `DL_Facturacion_v_Media`
- **91-365 días:** usa `DL_Facturacion_v_Antiguo`
- **Más de 365 días o sin fechas:** usa `DL_Facturacion_v_Completo`

#### Ejemplo de request:

```
GET /facturacion/query?fecha_inicio=2025-09-01&fecha_fin=2025-09-30&cliente=Empresa&limit=50&offset=0
```

#### Ejemplo de respuesta:

```json
{
  "tabla": "DL_Facturacion_v_Reciente",
  "total": 1500,
  "data": [
    {
      "Tipo documento": "33",
      "Numero de documento": "12345",
      "Fecha documento": "2025-09-15T00:00:00",
      "Razon social": "Empresa X S.A.",
      "Vendedor factura": "Juan Pérez",
      "Descripcion": "PRODUCTO XYZ",
      "Rubro": "Construcción",
      "Familia": "Materiales",
      "Marca": "Marca ABC",
      "Venta neta": 12345.67,
      ...
    }
  ]
}
```

## Campos Principales de la Vista DL_Facturacion_v

La vista contiene 53 columnas, las más relevantes son:

**Documento:**

- Tipo documento
- Numero de documento
- Folio SII
- Fecha documento
- Orden de compra

**Cliente:**

- RUT
- Razon social
- Categoria cliente
- Comuna

**Producto:**

- Codigo
- Descripcion
- Unidad de medida
- Rubro
- Familia
- Marca
- Formato

**Comercial:**

- Vendedor factura
- Email vendedor factura
- Vendedor oferta
- Email vendedor oferta
- Grupo de ventas
- Unidad de negocios
- Area

**Proyecto:**

- Numero oferta
- Nombre obra
- Arquitecto
- Inmobiliaria
- Especificador Arquitectura
- Especificador Inmobiliario

**Valores:**

- Cantidad
- Precio base
- Precio unitario
- Precio unitario descuentos aplicados
- Venta neta
- Moneda
- Tasa de cambio

## Paginación

Para implementar paginación, usa los parámetros `limit` y `offset`:

**Página 1 (primeros 50 registros):**

```
/facturacion/query?fecha_inicio=2025-09-01&limit=50&offset=0
```

**Página 2 (registros 51-100):**

```
/facturacion/query?fecha_inicio=2025-09-01&limit=50&offset=50
```

**Calcular total de páginas:**

```javascript
const totalPaginas = Math.ceil(response.total / limit);
```

## Ejemplos de Integración

### Ejemplo 1: Consulta por Cliente y Fecha

```javascript
const resultado = await fetch(
  "/facturacion/query?" +
    new URLSearchParams({
      fecha_inicio: "2025-09-01",
      fecha_fin: "2025-09-30",
      cliente: "Constructora",
      limit: 50,
      offset: 0,
    })
);
const data = await resultado.json();
console.log(`Total: ${data.total} facturas`);
```

### Ejemplo 2: Consulta por Vendedor

```javascript
const resultado = await fetch(
  "/facturacion/query?" +
    new URLSearchParams({
      vendedor: "Juan",
      periodo: "Reciente",
      limit: 100,
    })
);
```

### Ejemplo 3: Consulta por Tipo de Documento

```javascript
const resultado = await fetch(
  "/facturacion/query?" +
    new URLSearchParams({
      tipo_documento: "33", // Factura electrónica
      fecha_inicio: "2025-10-01",
      limit: 50,
    })
);
```

### Ejemplo 4: Consulta por Obra/Proyecto

```javascript
const resultado = await fetch(
  "/facturacion/query?" +
    new URLSearchParams({
      obra: "Edificio",
      unidad_negocio: "Proyectos",
      limit: 50,
    })
);
```

### Ejemplo 5: Consulta por Rango de Montos

```javascript
const resultado = await fetch(
  "/facturacion/query?" +
    new URLSearchParams({
      monto_min: "1000000",
      monto_max: "50000000",
      fecha_inicio: "2025-01-01",
      limit: 50,
    })
);
```

## Diferencias con API de Ventas

| Aspecto        | Ventas                  | Facturación                                                                  |
| -------------- | ----------------------- | ---------------------------------------------------------------------------- |
| Columna fecha  | `Fecha de oferta`       | `Fecha documento`                                                            |
| Cliente        | `Cliente`               | `Razon social`                                                               |
| Vendedor       | `Vendedor`              | `Vendedor factura` / `Vendedor oferta`                                       |
| Monto          | `Monto facturado`       | `Venta neta`                                                                 |
| Proyecto       | `Proyecto`              | `Nombre obra`                                                                |
| SKU            | `SKU`                   | `Codigo`                                                                     |
| Filtros únicos | `departamento`, `canal` | `tipo_documento`, `folio_sii`, `obra`, `unidad_negocio`, `categoria_cliente` |

## Manejo de Errores

La API devuelve códigos HTTP estándar:

- **200 OK**: Consulta exitosa
- **400 Bad Request**: Parámetros inválidos
- **500 Internal Server Error**: Error en el servidor

Ejemplo de respuesta de error:

```json
{
  "error": "Descripción del error"
}
```

## Notas Importantes

1. **Columna de fecha dinámica:** El sistema detecta automáticamente la columna de fecha al iniciar. Ver logs para confirmar: `[Facturación] Columna de fecha detectada: [Fecha documento]`

2. **Límites de paginación:** Para proteger el servidor, hay un límite máximo de 10,000 registros al solicitar todos los datos.

3. **Búsquedas parciales:** Todos los filtros de texto usan LIKE con comodines, permitiendo búsquedas parciales (ej: `cliente=Const` encuentra "Constructora ABC").

4. **Vendedor dual:** El filtro `vendedor` busca tanto en `[Vendedor factura]` como en `[Vendedor oferta]`.

5. **Performance:** Usa siempre `fecha_inicio` y `fecha_fin` cuando sea posible para aprovechar la selección automática de tabla optimizada.

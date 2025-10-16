# Verificación de Filtros - Análisis de Venta vs Base de Datos

## Estructura Real de DL_Analisis_Venta_v

Total de columnas: **62 columnas**

### Columnas Clave Identificadas:

#### 📅 Fechas

- `[Fecha de oferta]` ✅ - Columna principal de fecha
- `[Fecha creación cliente]` - Fecha secundaria

#### 👤 Cliente

- `[RUT Cliente]`
- `[Cliente]` ✅ - Usado en filtro
- `[Fecha creación cliente]`
- `[Categoria cliente]`

#### 🏗️ Proyecto

- `[Proyecto]` ✅ - Usado en filtro
- `[Nombre Obra]` - Alternativa para proyectos

#### 📦 Producto

- `[CDP Producto]`
- `[SKU]` ✅ - Usado en filtro
- `[Descipción]` ⚠️ - **Nota: Tiene error ortográfico en BD**
- `[Familia]` ✅ - Usado en filtro
- `[Marca]` ✅ - Usado en filtro
- `[Rubro]` ✅ - Usado en filtro
- `[Formato]`
- `[Serie]`
- `[Look]`

#### 🤝 Vendedor

- `[Vendedor]` ✅ - Usado en filtro
- `[Email vendedor]`

#### 🏢 Organización

- `[Departamento]` ✅ - Usado en filtro
- `[Canal]` ✅ - Usado en filtro
- `[Unidad de negocios]`
- `[Area]`
- `[Geografica]`

#### 💰 Montos y Precios

- `[Monto facturado]` ✅ - Usado en filtros monto_min/monto_max
- `[Monto anulado]`
- `[RPT Precio base]`
- `[RPT Precio unitario]`
- `[Total descuento + promoción]`
- `[RPT Substotal]`
- `[Total]`

#### 📊 Cantidades

- `[Cant. producto]`
- `[Cantidad entregada]`
- `[Cantidad facturada]`
- `[Cantidad anulada]`

#### 💱 Moneda

- `[Moneda origen]`
- `[Tasa de cambio]`
- `[Tasa de cambio USD]`

#### 📋 Referencias

- `[Referencia de pedido]`
- `[DocNum oferta]`
- `[DocNum OV]`
- `[Cotización final]`

#### 🚚 Logística

- `[Tipo despacho]`
- `[Comuna]`

## Estado de Filtros en analisis_venta/periodos.py

### ✅ Filtros Correctamente Implementados:

| Filtro Dashboard | Columna BD          | Código Backend                         | Estado                                    |
| ---------------- | ------------------- | -------------------------------------- | ----------------------------------------- |
| `fecha_inicio`   | `[Fecha de oferta]` | `CAST([Fecha de oferta] AS DATE) >= ?` | ✅ Correcto                               |
| `fecha_fin`      | `[Fecha de oferta]` | `CAST([Fecha de oferta] AS DATE) <= ?` | ✅ Correcto                               |
| `proyecto`       | `[Proyecto]`        | `[Proyecto] LIKE ?`                    | ✅ Correcto                               |
| `cliente`        | `[Cliente]`         | `[Cliente] LIKE ?`                     | ✅ Correcto                               |
| `vendedor`       | `[Vendedor]`        | `[Vendedor] LIKE ?`                    | ✅ Correcto                               |
| `sku`            | `[SKU]`             | `[SKU] LIKE ?`                         | ✅ Correcto                               |
| `departamento`   | `[Departamento]`    | `[Departamento] LIKE ?`                | ✅ Correcto                               |
| `canal`          | `[Canal]`           | `[Canal] LIKE ?`                       | ✅ Correcto                               |
| `monto_min`      | `[Monto facturado]` | `[Monto facturado] >= ?`               | ✅ Correcto                               |
| `monto_max`      | `[Monto facturado]` | `[Monto facturado] <= ?`               | ✅ Correcto                               |
| `descripcion`    | `[Descipción]`      | `[Descipción] LIKE ?`                  | ✅ Correcto (con error ortográfico de BD) |
| `rubro`          | `[Rubro]`           | `[Rubro] LIKE ?`                       | ✅ Correcto                               |
| `familia`        | `[Familia]`         | `[Familia] LIKE ?`                     | ✅ Correcto                               |
| `marca`          | `[Marca]`           | `[Marca] LIKE ?`                       | ✅ Correcto                               |

### ⚠️ Nota Importante sobre [Descipción]

La columna en la base de datos tiene un error ortográfico: `[Descipción]` en lugar de `[Descripción]`.

El código backend usa correctamente el nombre erróneo: `[Descipción]`, por lo que **el filtro funciona correctamente**.

### 💡 Filtros Potenciales No Implementados

Estas columnas podrían agregarse como filtros adicionales si fuera necesario:

1. **Ubicación/Geografía:**

   - `[Comuna]`
   - `[Geografica]`

2. **Categorización:**

   - `[Categoria cliente]`
   - `[Area]`
   - `[Unidad de negocios]`
   - `[CDP Producto]`
   - `[CDP Linea]`

3. **Referencias:**

   - `[Referencia de pedido]`
   - `[DocNum oferta]`
   - `[DocNum OV]`

4. **Características del Producto:**

   - `[Formato]`
   - `[Serie]`
   - `[Look]`
   - `[Ancho]`
   - `[Altura]`
   - `[Peso]`

5. **Estado:**

   - `[Estado]`
   - `[EstadoOdoo]`
   - `[Tipo despacho]`

6. **Especificadores:**

   - `[Especificador Arquitectura]`
   - `[Especificador Inmobiliario]`

7. **Obra:**
   - `[Nombre Obra]` (diferente de `[Proyecto]`)

## Comparación: Análisis de Venta vs Facturación

### Campos Similares pero Diferentes Nombres

| Concepto            | Análisis de Venta   | Facturación            |
| ------------------- | ------------------- | ---------------------- |
| **Fecha principal** | `[Fecha de oferta]` | `[Fecha documento]`    |
| **Cliente**         | `[Cliente]`         | `[Razon social]`       |
| **Proyecto**        | `[Proyecto]`        | `[Nombre obra]`        |
| **Código producto** | `[SKU]`             | `[Codigo]`             |
| **Descripción**     | `[Descipción]`      | `[Descripcion]`        |
| **Monto**           | `[Monto facturado]` | `[Venta neta]`         |
| **Organización 1**  | `[Departamento]`    | `[Unidad de negocios]` |
| **Organización 2**  | `[Canal]`           | `[Categoria cliente]`  |

### Campos Únicos de Análisis de Venta

- `[SKU]` - Código SKU interno
- `[Departamento]` - Departamento de venta
- `[Canal]` - Canal de venta
- `[DocNum oferta]` / `[DocNum OV]` - Números de documento SAP
- `[Venta anticipada]` - Flag de venta anticipada
- `[Estado]` / `[EstadoOdoo]` - Estados de proceso
- Campos de especificadores (Arquitectura, Inmobiliario)

### Campos Únicos de Facturación

- `[Tipo documento]` - Tipo de documento tributario
- `[Numero de documento]` - Número de documento
- `[Folio SII]` - Folio del Servicio de Impuestos Internos
- `[Orden de compra]` - OC del cliente
- Dualidad de vendedor: `[Vendedor factura]` y `[Vendedor oferta]`

## Conclusiones

### ✅ Estado Actual: CORRECTO

Todos los filtros implementados en `analisis_venta/periodos.py` corresponden exactamente a las columnas existentes en `DL_Analisis_Venta_v`.

### 🎯 Recomendaciones

1. **No se requieren cambios inmediatos** en los filtros de análisis de venta.

2. **Posibles mejoras futuras:**

   - Agregar filtro por `[Categoria cliente]`
   - Agregar filtro por `[Area]` o `[Unidad de negocios]`
   - Agregar filtro por `[Estado]` / `[EstadoOdoo]`
   - Agregar filtro por `[Comuna]` (ubicación)
   - Agregar filtro por `[Nombre Obra]` (complementario a `[Proyecto]`)

3. **Mantener coherencia:**
   - El dashboard ya muestra los filtros correctos para análisis de venta
   - Los placeholders y labels son apropiados
   - La separación de filtros por base de datos funciona correctamente

### 📊 Uso de Memoria del Dashboard

**Filtros de Análisis de Venta (14 filtros):**

- Proyecto ✅
- Cliente ✅
- Vendedor ✅
- SKU ✅
- Departamento ✅
- Canal ✅
- Monto mínimo/máximo ✅
- Descripción ✅
- Rubro ✅
- Familia ✅
- Marca ✅
- Fecha inicio/fin ✅
- Periodo ✅

**Filtros de Facturación (16 filtros):**

- Cliente (Razón Social) ✅
- Vendedor ✅
- Tipo Documento ✅
- Número Documento ✅
- Folio SII ✅
- Código Producto ✅
- Descripción Producto ✅
- Obra/Proyecto ✅
- Unidad de Negocios ✅
- Categoría Cliente ✅
- Rubro ✅
- Familia ✅
- Marca ✅
- Venta Neta mín/máx ✅
- Fecha inicio/fin ✅
- Periodo ✅

## Verificación de Integridad ✅

- ✅ Filtros de análisis de venta alineados con BD
- ✅ Filtros de facturación alineados con BD
- ✅ Dashboard muestra filtros contextuales correctos
- ✅ Backend procesa parámetros adecuados por fuente
- ✅ Sin conflictos entre ambas fuentes
- ✅ Detección automática de columnas de fecha funcional

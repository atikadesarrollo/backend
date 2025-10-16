# 📊 Endpoints de KPIs - Guía de Uso

## Nuevos Endpoints Implementados

### 1. `/analisis_venta/kpis` - KPIs Principales

Calcula métricas agregadas para el período seleccionado.

#### Parámetros Requeridos:

- `fecha_inicio` (YYYY-MM-DD): Fecha de inicio del período
- `fecha_fin` (YYYY-MM-DD): Fecha de fin del período

#### Parámetros Opcionales (Filtros):

- `canal`: Filtrar por canal
- `departamento`: Filtrar por departamento
- `cliente`: Filtrar por cliente (búsqueda parcial)
- `vendedor`: Filtrar por vendedor (búsqueda parcial)
- `proyecto`: Filtrar por proyecto (búsqueda parcial)

#### Ejemplo de Request:

```http
GET /analisis_venta/kpis?fecha_inicio=2025-09-01&fecha_fin=2025-10-15
```

#### Ejemplo de Response:

```json
{
  "filtros_aplicados": {
    "fecha_inicio": "2025-09-01",
    "fecha_fin": "2025-10-15",
    "canal": null,
    "departamento": null
  },
  "tabla_consultada": "DL_Analisis_Venta_v_Reciente",
  "kpis_principales": {
    "cantidad_clientes": 1250,
    "cantidad_transacciones": 6780,
    "cantidad_clientes_nuevos": 125,
    "porcentaje_clientes_nuevos": 10.0,
    "venta_total": 125000000.5,
    "ticket_promedio": 18436.98,
    "total_vendedores": 45,
    "total_proyectos": 678
  },
  "venta_por_canal": [
    {
      "canal": "Retail",
      "venta_total": 45000000.0,
      "transacciones": 2300,
      "clientes": 450,
      "porcentaje": 36.0
    },
    {
      "canal": "Proyectos",
      "venta_total": 60000000.0,
      "transacciones": 3200,
      "clientes": 600,
      "porcentaje": 48.0
    },
    {
      "canal": "Digital",
      "venta_total": 20000000.0,
      "transacciones": 1280,
      "clientes": 200,
      "porcentaje": 16.0
    }
  ],
  "venta_por_departamento": [
    {
      "departamento": "Ventas Norte",
      "venta_total": 35000000.0,
      "transacciones": 1890,
      "clientes": 380,
      "porcentaje": 28.0
    },
    {
      "departamento": "Ventas Sur",
      "venta_total": 45000000.0,
      "transacciones": 2400,
      "clientes": 480,
      "porcentaje": 36.0
    },
    {
      "departamento": "Ventas Centro",
      "venta_total": 45000000.0,
      "transacciones": 2490,
      "clientes": 390,
      "porcentaje": 36.0
    }
  ]
}
```

---

## KPIs Calculados - Definiciones

### 1. **Cantidad de Clientes** (`cantidad_clientes`)

- **Definición**: Suma de clientes distintos en el período
- **Cálculo**: `COUNT(DISTINCT [Cliente])`
- **Uso**: Medir base de clientes activos

### 2. **Cantidad de Transacciones** (`cantidad_transacciones`)

- **Definición**: Suma de facturas/transacciones en el período
- **Cálculo**: `COUNT(*)`
- **Uso**: Medir volumen de actividad

### 3. **Cantidad de Clientes Nuevos** (`cantidad_clientes_nuevos`)

- **Definición**: Clientes cuya fecha de creación está dentro del período
- **Cálculo**: `COUNT(DISTINCT [Cliente]) WHERE [Fecha creación cliente] BETWEEN fecha_inicio AND fecha_fin`
- **Uso**: Medir adquisición de nuevos clientes

### 4. **Porcentaje de Clientes Nuevos** (`porcentaje_clientes_nuevos`) ⭐

- **Definición**: Proporción de clientes nuevos vs total de clientes
- **Cálculo**: `(cantidad_clientes_nuevos / cantidad_clientes) * 100`
- **Formato**: 2 decimales (ejemplo: 10.00%)
- **Uso**: Evaluar efectividad de captación

### 5. **Venta Total** (`venta_total`)

- **Definición**: Suma de montos facturados en el período
- **Cálculo**: `SUM([Monto facturado])`
- **Formato**: 2 decimales
- **Uso**: Medir revenue total

### 6. **Ticket Promedio** (`ticket_promedio`)

- **Definición**: Valor promedio por transacción
- **Cálculo**: `AVG([Monto facturado])`
- **Formato**: 2 decimales
- **Uso**: Medir valor promedio de compra

---

## 2. `/analisis_venta/top` - Rankings

Obtiene los top N elementos por venta total.

#### Parámetros:

- `fecha_inicio` (requerido): Fecha inicio
- `fecha_fin` (requerido): Fecha fin
- `tipo` (opcional): 'clientes', 'vendedores', 'productos', 'proyectos' (default: clientes)
- `limit` (opcional): Número de registros (default: 10)
- Filtros opcionales: `canal`, `departamento`, etc.

#### Ejemplo de Request:

```http
GET /analisis_venta/top?fecha_inicio=2025-09-01&fecha_fin=2025-10-15&tipo=clientes&limit=5
```

#### Ejemplo de Response:

```json
{
  "tipo": "clientes",
  "periodo": {
    "inicio": "2025-09-01",
    "fin": "2025-10-15"
  },
  "top": [
    {
      "rank": 1,
      "nombre": "Constructora ABC S.A.",
      "venta_total": 15000000.0,
      "transacciones": 234,
      "ticket_promedio": 64102.56
    },
    {
      "rank": 2,
      "nombre": "Inmobiliaria XYZ Ltda.",
      "venta_total": 12000000.0,
      "transacciones": 156,
      "ticket_promedio": 76923.08
    },
    {
      "rank": 3,
      "nombre": "Retail Store S.A.",
      "venta_total": 10500000.0,
      "transacciones": 890,
      "ticket_promedio": 11797.75
    }
  ]
}
```

---

## Ejemplos de Uso

### Caso 1: KPIs del Último Mes

```javascript
const response = await fetch(
  "/analisis_venta/kpis?" +
    new URLSearchParams({
      fecha_inicio: "2025-09-15",
      fecha_fin: "2025-10-15",
    })
);

const data = await response.json();
console.log(`Clientes: ${data.kpis_principales.cantidad_clientes}`);
console.log(
  `Clientes nuevos: ${data.kpis_principales.porcentaje_clientes_nuevos}%`
);
console.log(
  `Venta total: $${data.kpis_principales.venta_total.toLocaleString()}`
);
```

### Caso 2: KPIs Filtrados por Canal

```javascript
const response = await fetch(
  "/analisis_venta/kpis?" +
    new URLSearchParams({
      fecha_inicio: "2025-01-01",
      fecha_fin: "2025-10-15",
      canal: "Retail",
    })
);

const data = await response.json();
// Solo incluirá datos del canal Retail
```

### Caso 3: Top 10 Vendedores

```javascript
const response = await fetch(
  "/analisis_venta/top?" +
    new URLSearchParams({
      fecha_inicio: "2025-09-01",
      fecha_fin: "2025-10-15",
      tipo: "vendedores",
      limit: 10,
    })
);

const data = await response.json();
data.top.forEach((v) => {
  console.log(`#${v.rank} ${v.nombre}: $${v.venta_total}`);
});
```

### Caso 4: Carga Paralela (Dashboard)

```javascript
// Cargar KPIs y datos de detalle en paralelo
const [kpis, datos, topClientes] = await Promise.all([
  fetch(
    "/analisis_venta/kpis?fecha_inicio=2025-09-01&fecha_fin=2025-10-15"
  ).then((r) => r.json()),
  fetch(
    "/analisis_venta/query?fecha_inicio=2025-09-01&fecha_fin=2025-10-15&limit=50"
  ).then((r) => r.json()),
  fetch(
    "/analisis_venta/top?fecha_inicio=2025-09-01&fecha_fin=2025-10-15&tipo=clientes&limit=5"
  ).then((r) => r.json()),
]);

// Renderizar dashboard
renderKPIs(kpis);
renderTabla(datos);
renderChart(topClientes);
```

---

## Performance y Optimizaciones

### Selección Automática de Tabla

El endpoint selecciona automáticamente la tabla más eficiente según el rango de fechas:

- **0-30 días**: `DL_Analisis_Venta_v_Reciente` ⚡ Más rápido
- **31-90 días**: `DL_Analisis_Venta_v_Media`
- **91-365 días**: `DL_Analisis_Venta_v_Antiguo`
- **>365 días**: `DL_Analisis_Venta_v_Completo`

### Tiempos de Respuesta Esperados

| Endpoint | Rango   | Tiempo Estimado |
| -------- | ------- | --------------- |
| `/kpis`  | 30 días | 150-300ms       |
| `/kpis`  | 90 días | 300-500ms       |
| `/kpis`  | 1 año   | 500-1000ms      |
| `/top`   | 30 días | 100-200ms       |

### Queries Optimizados

- ✅ Usa `COUNT(DISTINCT)` para conteos únicos
- ✅ Queries separados por métrica (no un mega-query)
- ✅ Índices en columnas de fecha
- ✅ Agregaciones en SQL Server (no en Python)

---

## Manejo de Errores

### Error 400: Parámetros Faltantes

```json
{
  "error": "Se requieren fecha_inicio y fecha_fin"
}
```

**Solución**: Asegúrate de enviar ambas fechas.

### Error 400: Tipo Inválido (endpoint /top)

```json
{
  "error": "Tipo inválido: productos2. Use: clientes, vendedores, productos, proyectos"
}
```

**Solución**: Usa uno de los tipos válidos.

### Error 500: Error de Base de Datos

```json
{
  "error": "Invalid column name 'Cliente'",
  "traceback": "..."
}
```

**Solución**: Verifica que las columnas existan en la vista DL_Analisis_Venta_v.

---

## Testing

Ejecuta el script de prueba:

```bash
python test_kpis.py
```

El script probará:

1. ✅ Endpoint de KPIs generales
2. ✅ Endpoint de top clientes
3. ✅ KPIs con filtros adicionales

La respuesta completa se guardará en `test_kpis_response.json` para inspección.

---

## Próximos Pasos

### Implementar KPIs de Facturación

Crear `facturacion/kpis.py` con KPIs específicos:

- Cantidad de facturas por tipo documento
- Venta neta por unidad de negocios
- Top obras/proyectos
- % de notas de crédito vs facturas

### Dashboard Frontend

Crear dashboard visual con:

- Cards de KPIs principales
- Gráficos de barras (venta por canal/departamento)
- Gráfico de top clientes
- Serie temporal de evolución

### Caching

Implementar cache de KPIs:

- Redis para cache distribuido
- TTL de 5-10 minutos
- Invalidación al detectar nuevos datos

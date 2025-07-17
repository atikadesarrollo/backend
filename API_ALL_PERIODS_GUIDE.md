# API Completa para Consultar Datos ETL - Todos los Períodos

## 📊 Endpoints Disponibles para Todos los Períodos

### 🔗 **Estructura de URLs**

```
GET /api/analytics/{period}/info
GET /api/analytics/{period}/complete
GET /api/analytics/periods/available
```

**Períodos válidos**: `daily`, `weekly`, `monthly`, `quarterly`, `summary`

---

## 📋 **1. Información General por Período**

### Endpoint: `/api/analytics/{period}/info`

Obtiene estadísticas generales de cada tabla por período.

#### **Ejemplos:**

```bash
# Información de datos diarios
curl "http://localhost:5000/api/analytics/daily/info"

# Información de datos semanales
curl "http://localhost:5000/api/analytics/weekly/info"

# Información de datos mensuales
curl "http://localhost:5000/api/analytics/monthly/info"

# Información de datos trimestrales
curl "http://localhost:5000/api/analytics/quarterly/info"

# Información del resumen por vendedores
curl "http://localhost:5000/api/analytics/summary/info"
```

#### **Respuesta típica:**

```json
{
  "success": true,
  "message": "Daily table information retrieved successfully",
  "data": {
    "general_info": {
      "total_registros": 3010,
      "años_unicos": 1,
      "meses_unicos": 3,
      "fecha_minima": "2025-07-02T10:15:00",
      "fecha_maxima": "2025-07-08T18:04:03",
      "monto_total": 578495637.05,
      "vendedores_unicos": 46,
      "clientes_unicos": 523,
      "familias_productos": 28
    },
    "temporal_distribution": [
      {
        "fecha": "2025-07-08",
        "total_registros": 46,
        "monto_total": 5471173.77,
        "vendedores_unicos": 5,
        "clientes_unicos": 12
      }
    ],
    "table_type": "daily"
  },
  "timestamp": "2025-07-09T12:00:00.000000"
}
```

---

## 📋 **2. Datos Completos con Filtros**

### Endpoint: `/api/analytics/{period}/complete`

Obtiene los datos completos de cada tabla con filtros y paginación.

#### **Parámetros disponibles:**

- `limit`: Número máximo de registros (sin límite por defecto)
- `offset`: Número de registros a saltar (paginación)
- `vendedor`: Filtrar por vendedor (búsqueda parcial)
- `cliente`: Filtrar por cliente (búsqueda parcial)
- `estado`: Filtrar por estado exacto
- `familia`: Filtrar por familia de producto (búsqueda parcial)
- `canal`: Filtrar por canal (búsqueda parcial)
- `departamento`: Filtrar por departamento (búsqueda parcial)
- `categoria`: Filtrar por categoría/rubro exacto
- `fecha_desde`: Filtrar desde fecha (YYYY-MM-DD)
- `fecha_hasta`: Filtrar hasta fecha (YYYY-MM-DD)
- `año`: Filtrar por año
- `trimestre`: Filtrar por trimestre (1, 2, 3, 4) - Para quarterly y monthly
- `mes`: Filtrar por mes (1-12) - Para monthly, weekly y daily

#### **Ejemplos por período:**

##### **📅 DAILY (Datos Diarios)**

```bash
# Últimos 100 registros diarios
curl "http://localhost:5000/api/analytics/daily/complete?limit=100"

# Datos diarios de un vendedor específico
curl "http://localhost:5000/api/analytics/daily/complete?vendedor=Loreto&limit=50"

# Datos diarios del último mes
curl "http://localhost:5000/api/analytics/daily/complete?mes=7&año=2025"
```

##### **📆 WEEKLY (Datos Semanales)**

```bash
# Últimos 50 registros semanales
curl "http://localhost:5000/api/analytics/weekly/complete?limit=50"

# Datos semanales de julio 2025
curl "http://localhost:5000/api/analytics/weekly/complete?mes=7&año=2025"

# Datos semanales por canal
curl "http://localhost:5000/api/analytics/weekly/complete?canal=Showroom&limit=100"
```

##### **🗓️ MONTHLY (Datos Mensuales)**

```bash
# Datos mensuales completos
curl "http://localhost:5000/api/analytics/monthly/complete"

# Datos mensuales del Q2 2025
curl "http://localhost:5000/api/analytics/monthly/complete?trimestre=2&año=2025"

# Datos mensuales por familia de producto
curl "http://localhost:5000/api/analytics/monthly/complete?familia=Porcelanatos&limit=200"
```

##### **📋 QUARTERLY (Datos Trimestrales)**

```bash
# Todos los datos trimestrales
curl "http://localhost:5000/api/analytics/quarterly/complete"

# Datos del Q2 2025
curl "http://localhost:5000/api/analytics/quarterly/complete?trimestre=2&año=2025&limit=1000"

# Datos trimestrales con estado 'sale'
curl "http://localhost:5000/api/analytics/quarterly/complete?estado=sale&limit=500"
```

##### **📊 SUMMARY (Resumen por Vendedores)**

```bash
# Resumen completo por vendedores
curl "http://localhost:5000/api/analytics/summary/complete"

# Top 10 vendedores
curl "http://localhost:5000/api/analytics/summary/complete?limit=10"

# Vendedores específicos
curl "http://localhost:5000/api/analytics/summary/complete?vendedor=Broshkana"
```

---

## 📋 **3. Períodos Disponibles**

### Endpoint: `/api/analytics/periods/available`

Lista todos los períodos disponibles con sus estadísticas.

```bash
curl "http://localhost:5000/api/analytics/periods/available"
```

#### **Respuesta:**

```json
{
  "success": true,
  "message": "Available periods retrieved successfully",
  "data": [
    {
      "period": "daily",
      "table_name": "DL_Analisis_Venta_Daily",
      "display_name": "Daily",
      "record_count": 3010,
      "available": true
    },
    {
      "period": "weekly",
      "table_name": "DL_Analisis_Venta_Weekly",
      "display_name": "Weekly",
      "record_count": 4358,
      "available": true
    },
    {
      "period": "monthly",
      "table_name": "DL_Analisis_Venta_Monthly",
      "display_name": "Monthly",
      "record_count": 0,
      "available": false
    },
    {
      "period": "quarterly",
      "table_name": "DL_Analisis_Venta_Quarterly",
      "display_name": "Quarterly",
      "record_count": 34572,
      "available": true
    },
    {
      "period": "summary",
      "table_name": "DL_Analisis_Venta_Summary",
      "display_name": "Summary",
      "record_count": 46,
      "available": true
    }
  ],
  "timestamp": "2025-07-09T12:00:00.000000"
}
```

---

## 🔧 **4. Ejemplos de Implementación**

### **JavaScript/Frontend**

```javascript
// Obtener períodos disponibles
async function getAvailablePeriods() {
  const response = await fetch(
    "http://localhost:5000/api/analytics/periods/available"
  );
  return await response.json();
}

// Obtener información de un período
async function getPeriodInfo(period) {
  const response = await fetch(
    `http://localhost:5000/api/analytics/${period}/info`
  );
  return await response.json();
}

// Obtener datos con filtros
async function getPeriodData(period, filters = {}) {
  const params = new URLSearchParams(filters);
  const response = await fetch(
    `http://localhost:5000/api/analytics/${period}/complete?${params}`
  );
  return await response.json();
}

// Ejemplo de uso
const periods = await getAvailablePeriods();
const dailyInfo = await getPeriodInfo("daily");
const quarterlyData = await getPeriodData("quarterly", {
  vendedor: "Loreto",
  trimestre: 2,
  año: 2025,
  limit: 100,
});
```

### **Python**

```python
import requests

API_BASE = 'http://localhost:5000/api/analytics'

def get_available_periods():
    return requests.get(f'{API_BASE}/periods/available').json()

def get_period_info(period):
    return requests.get(f'{API_BASE}/{period}/info').json()

def get_period_data(period, **filters):
    response = requests.get(f'{API_BASE}/{period}/complete', params=filters)
    return response.json()

# Ejemplos de uso
periods = get_available_periods()
daily_info = get_period_info('daily')
summary_data = get_period_data('summary', limit=20)
quarterly_data = get_period_data('quarterly',
                                vendedor='Broshkana',
                                estado='sale',
                                limit=500)
```

---

## 📊 **5. Características por Período**

### **📅 DAILY (DL_Analisis_Venta_Daily)**

- **Datos**: Últimos 7 días
- **Actualización**: Diaria (06:00 AM)
- **Filtros específicos**: `mes`, fecha exacta
- **Uso**: Monitoreo diario de ventas

### **📆 WEEKLY (DL_Analisis_Venta_Weekly)**

- **Datos**: Últimas 4 semanas
- **Actualización**: Semanal
- **Filtros específicos**: `mes`, semana del año
- **Uso**: Análisis de tendencias semanales

### **🗓️ MONTHLY (DL_Analisis_Venta_Monthly)**

- **Datos**: Últimos 12 meses
- **Actualización**: Mensual
- **Filtros específicos**: `trimestre`, `mes`
- **Uso**: Reportes mensuales y análisis estacional

### **📋 QUARTERLY (DL_Analisis_Venta_Quarterly)**

- **Datos**: Últimos 4 trimestres
- **Actualización**: Trimestral
- **Filtros específicos**: `trimestre`, año
- **Uso**: Reportes ejecutivos y análisis de largo plazo

### **📊 SUMMARY (DL_Analisis_Venta_Summary)**

- **Datos**: Resumen agregado por vendedores
- **Actualización**: Diaria
- **Campos**: `total_ofertas`, `cantidad_total`, `monto_total`
- **Uso**: Análisis de performance de vendedores

---

## 🌐 **6. Visualizadores**

### **Visualizador Universal**

- **URL**: `file:///c:/Users/Alexis%20Gonzalez/Documents/GitHub/backend/all_periods_viewer.html`
- **Características**:
  - Selector dinámico de períodos
  - Filtros específicos por período
  - Estadísticas en tiempo real
  - Exportación a CSV
  - Interfaz responsive

### **Visualizador Quarterly Específico**

- **URL**: `file:///c:/Users/Alexis%20Gonzalez/Documents/GitHub/backend/quarterly_viewer.html`
- **Características**:
  - Optimizado para datos trimestrales
  - Análisis detallado de distribución temporal
  - Filtros avanzados

---

## ⚠️ **7. Consideraciones Importantes**

### **Rendimiento**

- **Sin límite por defecto**: Los endpoints pueden devolver todos los registros
- **Paginación recomendada**: Usar `limit` y `offset` para grandes volúmenes
- **Filtros eficientes**: Aplicar filtros específicos para reducir transferencia de datos

### **Disponibilidad de Datos**

- Usar `/periods/available` para verificar qué tablas tienen datos
- Algunas tablas pueden no existir si no se ha ejecutado el pipeline ETL correspondiente

### **Actualizaciones**

- Los datos se obtienen en tiempo real de la base de datos
- Las fechas de `processed_at` indican cuándo se procesaron los datos

### **Manejo de Errores**

- Validación de períodos válidos
- Mensajes de error descriptivos
- Manejo de tablas no disponibles

---

## 🚀 **8. Comandos para Generar Datos**

Si algún período no está disponible, ejecutar:

```bash
# Datos diarios
python pipeline.py --mode daily

# Datos semanales
python pipeline.py --mode weekly

# Datos mensuales
python pipeline.py --mode monthly

# Datos trimestrales
python pipeline.py --mode quarterly

# Resumen por vendedores
python pipeline.py --mode summary
```

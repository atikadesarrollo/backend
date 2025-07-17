# 🚀 API FRONTEND INTEGRATION GUIDE

## Endpoints para Consumo de Datos ETL Segmentados

### 📍 **Base URL**

```
http://localhost:5000/api/analytics
```

### 🕒 **Períodos Disponibles**

- `daily` - Datos diarios (últimos 7 días)
- `weekly` - Datos semanales (últimos 30 días)
- `monthly` - Datos mensuales
- `summary` - Resumen por vendedores

---

## 📊 **1. DATOS DE VENTAS PAGINADOS**

### **Endpoint:**

```
GET /api/analytics/sales/{period}
```

### **Parámetros:**

- `period`: daily | weekly | monthly | summary
- `limit`: Número de registros (default: 100)
- `offset`: Posición inicial (default: 0)
- `vendedor`: Filtrar por vendedor
- `cliente`: Filtrar por cliente
- `categoria`: Filtrar por categoría
- `estado`: Filtrar por estado
- `fecha_desde`: Fecha inicio (YYYY-MM-DD)
- `fecha_hasta`: Fecha fin (YYYY-MM-DD)

### **Ejemplos Frontend:**

#### **JavaScript/Fetch:**

```javascript
// Obtener datos diarios paginados
async function getSalesData(
  period = "daily",
  page = 1,
  limit = 50,
  filters = {}
) {
  const offset = (page - 1) * limit;

  const params = new URLSearchParams({
    limit: limit,
    offset: offset,
    ...filters,
  });

  try {
    const response = await fetch(`/api/analytics/sales/${period}?${params}`);
    const data = await response.json();

    if (data.success) {
      return {
        records: data.data,
        totalRecords: data.total_records,
        currentPage: page,
        totalPages: Math.ceil(data.total_records / limit),
        hasNext: offset + limit < data.total_records,
        hasPrev: page > 1,
      };
    } else {
      throw new Error(data.message);
    }
  } catch (error) {
    console.error("Error fetching sales data:", error);
    throw error;
  }
}

// Uso en componente React/Vue
const salesData = await getSalesData("daily", 1, 50, {
  vendedor: "Juan",
  categoria: "Bebidas",
  fecha_desde: "2025-07-01",
});
```

#### **Axios:**

```javascript
import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:5000/api/analytics",
});

// Obtener datos con filtros
async function fetchFilteredSales(period, filters) {
  try {
    const response = await api.get(`/sales/${period}`, {
      params: filters,
    });

    return response.data;
  } catch (error) {
    console.error("API Error:", error.response?.data || error.message);
    throw error;
  }
}

// Ejemplo de uso
const salesData = await fetchFilteredSales("daily", {
  limit: 100,
  vendedor: "Maria",
  estado: "OK",
});
```

---

## 📈 **2. RESÚMENES AGRUPADOS**

### **Endpoint:**

```
GET /api/analytics/summary/{period}
```

### **Parámetros:**

- `period`: daily | weekly | monthly
- `group_by`: date | vendedor | categoria | producto

### **Ejemplos Frontend:**

```javascript
// Resumen por fecha
async function getSummaryByDate(period = "daily") {
  const response = await fetch(
    `/api/analytics/summary/${period}?group_by=date`
  );
  const data = await response.json();

  // Para gráficos de líneas/barras
  return data.data.map((item) => ({
    x: item.fecha,
    y: item.monto_total,
    ofertas: item.total_ofertas,
    cantidad: item.cantidad_total,
  }));
}

// Resumen por vendedores para ranking
async function getTopSalespeople(period = "weekly") {
  const response = await fetch(
    `/api/analytics/summary/${period}?group_by=vendedor`
  );
  const data = await response.json();

  return data.data.map((vendedor, index) => ({
    rank: index + 1,
    name: vendedor.Vendedor,
    sales: vendedor.monto_total,
    offers: vendedor.total_ofertas,
    average: vendedor.promedio_oferta,
  }));
}
```

---

## 🏆 **3. TOP PERFORMERS**

### **Endpoint:**

```
GET /api/analytics/top/{period}
```

### **Parámetros:**

- `period`: daily | weekly | monthly
- `metric`: monto | cantidad | ofertas | promedio
- `limit`: Número de top performers (default: 10)

### **Ejemplo Frontend:**

```javascript
// Top vendedores por monto
async function getTopPerformers(
  period = "daily",
  metric = "monto",
  limit = 10
) {
  const response = await fetch(
    `/api/analytics/top/${period}?metric=${metric}&limit=${limit}`
  );
  const data = await response.json();

  return data.data.map((performer) => ({
    vendedor: performer.Vendedor,
    valor: performer.metric_value,
    ofertas: performer.total_ofertas,
    promedio: performer.promedio_oferta,
  }));
}

// Para componente de leaderboard
const topSellers = await getTopPerformers("weekly", "monto", 5);
```

---

## 📊 **4. KPIs PRINCIPALES**

### **Endpoint:**

```
GET /api/analytics/kpis/{period}
```

### **Ejemplo Frontend:**

```javascript
// Dashboard KPIs
async function getDashboardKPIs(period = "daily") {
  const response = await fetch(`/api/analytics/kpis/${period}`);
  const data = await response.json();

  const kpis = data.data;

  return {
    ventas: {
      total: kpis.monto_total,
      promedio: kpis.promedio_oferta,
      ofertas: kpis.total_ofertas,
    },
    rendimiento: {
      vendedoresActivos: kpis.vendedores_activos,
      clientesActivos: kpis.clientes_activos,
      ofertasPorVendedor: kpis.ofertas_por_vendedor,
    },
    productos: {
      productosVendidos: kpis.productos_vendidos,
      categoriasActivas: kpis.categorias_activas,
    },
    periodo: {
      fechaInicio: kpis.fecha_inicio,
      fechaFin: kpis.fecha_fin,
    },
  };
}
```

---

## 🔄 **5. PERÍODOS DISPONIBLES**

### **Endpoint:**

```
GET /api/analytics/periods
```

### **Ejemplo Frontend:**

```javascript
// Verificar qué períodos están disponibles
async function getAvailablePeriods() {
  const response = await fetch("/api/analytics/periods");
  const data = await response.json();

  return data.data.map((period) => ({
    value: period.period,
    label: period.display_name,
    tableName: period.table_name,
  }));
}

// Para selector de período en UI
const periods = await getAvailablePeriods();
// [{ value: 'daily', label: 'Daily', tableName: 'DL_Analisis_Venta_Daily' }]
```

---

## 🎯 **ESTRATEGIAS DE IMPLEMENTACIÓN FRONTEND**

### **1. Componente de Tabla Paginada (React):**

```jsx
import React, { useState, useEffect } from "react";

function SalesTable({ period = "daily" }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalRecords: 0,
  });

  const [filters, setFilters] = useState({
    vendedor: "",
    categoria: "",
    limite: 50,
  });

  useEffect(() => {
    loadSalesData();
  }, [period, pagination.currentPage, filters]);

  const loadSalesData = async () => {
    setLoading(true);
    try {
      const result = await getSalesData(
        period,
        pagination.currentPage,
        filters.limite,
        filters
      );

      setData(result.records);
      setPagination({
        currentPage: result.currentPage,
        totalPages: result.totalPages,
        totalRecords: result.totalRecords,
      });
    } catch (error) {
      console.error("Error loading sales data:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Filtros */}
      <div className="filters">
        <input
          type="text"
          placeholder="Vendedor"
          value={filters.vendedor}
          onChange={(e) => setFilters({ ...filters, vendedor: e.target.value })}
        />
        {/* Más filtros... */}
      </div>

      {/* Tabla */}
      <table>
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Vendedor</th>
            <th>Cliente</th>
            <th>Monto</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index}>
              <td>{new Date(row["Fecha de oferta"]).toLocaleDateString()}</td>
              <td>{row.Vendedor}</td>
              <td>{row.Cliente}</td>
              <td>${row["Monto orden"].toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Paginación */}
      <div className="pagination">
        <button
          disabled={pagination.currentPage === 1}
          onClick={() =>
            setPagination({
              ...pagination,
              currentPage: pagination.currentPage - 1,
            })
          }
        >
          Anterior
        </button>

        <span>
          Página {pagination.currentPage} de {pagination.totalPages}({
            pagination.totalRecords
          } registros)
        </span>

        <button
          disabled={pagination.currentPage === pagination.totalPages}
          onClick={() =>
            setPagination({
              ...pagination,
              currentPage: pagination.currentPage + 1,
            })
          }
        >
          Siguiente
        </button>
      </div>
    </div>
  );
}
```

### **2. Selector de Período:**

```jsx
function PeriodSelector({ onPeriodChange, currentPeriod }) {
  const [availablePeriods, setAvailablePeriods] = useState([]);

  useEffect(() => {
    getAvailablePeriods().then(setAvailablePeriods);
  }, []);

  return (
    <select
      value={currentPeriod}
      onChange={(e) => onPeriodChange(e.target.value)}
    >
      {availablePeriods.map((period) => (
        <option key={period.value} value={period.value}>
          {period.label}
        </option>
      ))}
    </select>
  );
}
```

### **3. Dashboard KPIs:**

```jsx
function KPIDashboard({ period }) {
  const [kpis, setKpis] = useState({});

  useEffect(() => {
    getDashboardKPIs(period).then(setKpis);
  }, [period]);

  return (
    <div className="kpi-grid">
      <div className="kpi-card">
        <h3>Ventas Totales</h3>
        <span className="kpi-value">
          ${kpis.ventas?.total?.toLocaleString()}
        </span>
      </div>

      <div className="kpi-card">
        <h3>Ofertas</h3>
        <span className="kpi-value">
          {kpis.ventas?.ofertas?.toLocaleString()}
        </span>
      </div>

      <div className="kpi-card">
        <h3>Vendedores Activos</h3>
        <span className="kpi-value">{kpis.rendimiento?.vendedoresActivos}</span>
      </div>

      <div className="kpi-card">
        <h3>Promedio por Oferta</h3>
        <span className="kpi-value">
          ${kpis.ventas?.promedio?.toLocaleString()}
        </span>
      </div>
    </div>
  );
}
```

---

## 🔧 **CONFIGURACIÓN ADICIONAL**

### **1. Interceptor de Errores (Axios):**

```javascript
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 500) {
      console.error("Database connection error");
      // Mostrar mensaje de error al usuario
    }
    return Promise.reject(error);
  }
);
```

### **2. Cache de Datos:**

```javascript
class DataCache {
  constructor(ttl = 300000) {
    // 5 minutos
    this.cache = new Map();
    this.ttl = ttl;
  }

  get(key) {
    const item = this.cache.get(key);
    if (item && Date.now() - item.timestamp < this.ttl) {
      return item.data;
    }
    return null;
  }

  set(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
  }
}

const dataCache = new DataCache();

// Uso con cache
async function getCachedSalesData(period, page, filters) {
  const cacheKey = `sales_${period}_${page}_${JSON.stringify(filters)}`;

  let data = dataCache.get(cacheKey);
  if (!data) {
    data = await getSalesData(period, page, 50, filters);
    dataCache.set(cacheKey, data);
  }

  return data;
}
```

---

## 📱 **RESPUESTA TIPO DE LA API**

```json
{
  "success": true,
  "message": "Sales data retrieved for daily period",
  "data": [
    {
      "Fecha de oferta": "2025-07-08T10:30:00",
      "Vendedor": "Juan Pérez",
      "Cliente": "Empresa ABC",
      "Producto": "Producto XYZ",
      "Categoria": "Bebidas",
      "Cantidad entregada": 100.0,
      "Monto orden": 50000.0,
      "Estado": "OK",
      "processed_at": "2025-07-08T19:15:30"
    }
  ],
  "total_records": 3010,
  "timestamp": "2025-07-08T19:15:30.123456"
}
```

Esta API te permite manejar eficientemente las consultas segmentadas desde el frontend, con paginación, filtros, y diferentes niveles de agregación según tus necesidades de visualización.

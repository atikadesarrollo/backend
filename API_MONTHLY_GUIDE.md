# 📊 API Endpoint para Análisis de Venta Mensual - Guía Completa

## 🎯 **Endpoint Principal: Monthly Complete**

```
GET /api/analytics/monthly/complete
```

Este endpoint te permite consumir **todos los datos** de la tabla `DL_Analisis_Venta_Monthly` con filtros avanzados y paginación.

---

## 📋 **1. Información Básica de la Tabla Monthly**

### **Estadísticas Generales**

```bash
curl "http://localhost:5000/api/analytics/monthly/info"
```

**Respuesta:**

```json
{
  "success": true,
  "message": "Monthly table information retrieved successfully",
  "data": {
    "general_info": {
      "total_registros": 15140,
      "fecha_minima": "2025-06-09 12:40:40.0000000",
      "fecha_maxima": "2025-07-08 23:30:38.0000000",
      "monto_total": 4004716436.86,
      "vendedores_unicos": 48,
      "clientes_unicos": 1847,
      "familias_productos": 2054
    }
  }
}
```

---

## 🔍 **2. Consumir Todos los Datos Mensuales**

### **Obtener Todos los Registros (Sin Paginación)**

```bash
curl "http://localhost:5000/api/analytics/monthly/complete"
```

### **Con Paginación (Recomendado para Apps)**

```bash
# Primeros 100 registros
curl "http://localhost:5000/api/analytics/monthly/complete?limit=100&offset=0"

# Siguientes 100 registros
curl "http://localhost:5000/api/analytics/monthly/complete?limit=100&offset=100"

# Página 3 (registros 201-300)
curl "http://localhost:5000/api/analytics/monthly/complete?limit=100&offset=200"
```

---

## 🎨 **3. Filtros Avanzados**

### **Por Vendedor**

```bash
curl "http://localhost:5000/api/analytics/monthly/complete?vendedor=Juan"
```

### **Por Cliente**

```bash
curl "http://localhost:5000/api/analytics/monthly/complete?cliente=EMPRESA%20XYZ"
```

### **Por Rango de Fechas**

```bash
curl "http://localhost:5000/api/analytics/monthly/complete?fecha_desde=2025-06-15&fecha_hasta=2025-07-01"
```

### **Por Categoría/Rubro**

```bash
curl "http://localhost:5000/api/analytics/monthly/complete?categoria=ALIMENTOS"
```

### **Por Estado**

```bash
curl "http://localhost:5000/api/analytics/monthly/complete?estado=Entregado"
```

### **Por Familia de Productos**

```bash
curl "http://localhost:5000/api/analytics/monthly/complete?familia=BEBIDAS"
```

### **Por Canal**

```bash
curl "http://localhost:5000/api/analytics/monthly/complete?canal=RETAIL"
```

### **Por Departamento**

```bash
curl "http://localhost:5000/api/analytics/monthly/complete?departamento=VENTAS"
```

### **Filtros Combinados**

```bash
curl "http://localhost:5000/api/analytics/monthly/complete?vendedor=Juan&estado=Entregado&limit=50"
```

---

## 📊 **4. Ejemplos de Respuesta**

### **Estructura de Respuesta**

```json
{
  "success": true,
  "message": "Monthly data retrieved successfully. Showing 5 of 15140 records.",
  "data": [
    {
      "Referencia de pedido": "REF001",
      "Fecha de oferta": "2025-07-08 18:04:03.0000000",
      "Vendedor": "JUAN PEREZ",
      "Cliente": "EMPRESA ABC LTDA",
      "RUT Cliente": "12345678-9",
      "SKU": "SKU001",
      "Descipción": "PRODUCTO EJEMPLO",
      "Familia": "ALIMENTOS",
      "Marca": "MARCA XYZ",
      "Cant. producto": 10,
      "RPT Precio unitario": 15000.0,
      "Descuento %": 5.0,
      "Total": 142500.0,
      "Estado": "Entregado",
      "Comuna": "Las Condes",
      "Canal": "RETAIL",
      "Departamento": "VENTAS",
      "Rubro": "ALIMENTARIO",
      "processed_at": "2025-07-09 12:55:18.4790000"
    }
  ],
  "total_records": 15140,
  "timestamp": "2025-07-09T13:15:00.000000"
}
```

---

## 💻 **5. Ejemplos de Código**

### **JavaScript/Fetch**

```javascript
// Obtener todos los datos mensuales
async function getMonthlyData(limit = 100, offset = 0, filters = {}) {
  const params = new URLSearchParams({
    limit: limit,
    offset: offset,
    ...filters,
  });

  const response = await fetch(
    `http://localhost:5000/api/analytics/monthly/complete?${params}`
  );
  const data = await response.json();

  return data;
}

// Ejemplo de uso
getMonthlyData(50, 0, { vendedor: "Juan", estado: "Entregado" }).then(
  (data) => {
    console.log(`Total registros: ${data.total_records}`);
    console.log(`Mostrando: ${data.data.length} registros`);
    data.data.forEach((record) => {
      console.log(`${record.Vendedor} - ${record.Cliente} - $${record.Total}`);
    });
  }
);
```

### **Python/Requests**

```python
import requests
import pandas as pd

def get_monthly_data(limit=None, offset=0, **filters):
    """Obtener datos mensuales de la API"""
    params = {'offset': offset}
    if limit:
        params['limit'] = limit
    params.update(filters)

    response = requests.get(
        'http://localhost:5000/api/analytics/monthly/complete',
        params=params
    )

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code}")

# Ejemplos de uso
# Todos los datos de Juan Pérez
data = get_monthly_data(vendedor='JUAN PEREZ')
df = pd.DataFrame(data['data'])

# Datos de últimos 7 días
from datetime import datetime, timedelta
fecha_desde = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
data = get_monthly_data(fecha_desde=fecha_desde)

# Paginación completa
all_records = []
offset = 0
limit = 1000

while True:
    batch = get_monthly_data(limit=limit, offset=offset)
    all_records.extend(batch['data'])

    if len(batch['data']) < limit:
        break
    offset += limit

print(f"Total registros obtenidos: {len(all_records)}")
```

### **cURL Avanzado**

```bash
# Exportar a archivo JSON
curl "http://localhost:5000/api/analytics/monthly/complete" \
  -H "Accept: application/json" \
  -o monthly_data.json

# Con filtros complejos
curl -G "http://localhost:5000/api/analytics/monthly/complete" \
  --data-urlencode "vendedor=JUAN PEREZ" \
  --data-urlencode "fecha_desde=2025-07-01" \
  --data-urlencode "estado=Entregado" \
  --data-urlencode "limit=500"
```

---

## ⚡ **6. Tips de Rendimiento**

### **Para Aplicaciones Web:**

- Usa paginación: `limit=100&offset=0`
- Implementa filtros del lado cliente para mejor UX
- Cachea los resultados por unos minutos

### **Para Análisis de Datos:**

- Para datasets grandes, usa múltiples requests con paginación
- Procesa los datos en lotes para evitar problemas de memoria
- Considera usar filtros de fecha para reducir el volumen

### **Para Reportes:**

- Usa filtros específicos para obtener solo los datos necesarios
- Combina con otros endpoints para estadísticas agregadas

---

## 🚨 **7. Códigos de Estado**

| Código | Descripción                                |
| ------ | ------------------------------------------ |
| `200`  | ✅ Éxito - Datos obtenidos correctamente   |
| `400`  | ❌ Error en parámetros - Revisar filtros   |
| `404`  | ❌ Período no válido                       |
| `500`  | ❌ Error del servidor - Problema con la BD |

---

## 📈 **8. Casos de Uso Típicos**

### **Dashboard de Ventas Mensuales**

```bash
# KPIs generales
curl "http://localhost:5000/api/analytics/monthly/info"

# Top 10 registros más recientes
curl "http://localhost:5000/api/analytics/monthly/complete?limit=10"

# Ventas de un vendedor específico
curl "http://localhost:5000/api/analytics/monthly/complete?vendedor=JUAN%20PEREZ"
```

### **Análisis de Productos**

```bash
# Productos de una familia específica
curl "http://localhost:5000/api/analytics/monthly/complete?familia=BEBIDAS"

# Productos con descuento
curl "http://localhost:5000/api/analytics/monthly/complete" | jq '.data[] | select(.["Descuento %"] > 0)'
```

### **Reportes por Cliente**

```bash
# Todas las ventas de un cliente
curl "http://localhost:5000/api/analytics/monthly/complete?cliente=EMPRESA%20XYZ"

# Clientes de una comuna específica
curl "http://localhost:5000/api/analytics/monthly/complete?comuna=Las%20Condes"
```

---

## 🔄 **9. Integración con Otras APIs**

Este endpoint se puede combinar con otros endpoints del mismo sistema:

```bash
# Comparar con datos trimestrales
curl "http://localhost:5000/api/analytics/quarterly/complete?limit=10"

# Obtener resumen de vendedores
curl "http://localhost:5000/api/analytics/summary/complete"

# Ver todos los períodos disponibles
curl "http://localhost:5000/api/analytics/periods/available"
```

---

## 📞 **Soporte**

- **Registros totales**: 15,140
- **Rango de fechas**: Jun 9, 2025 - Jul 8, 2025
- **Monto total**: $4,004,716,436.86
- **Vendedores únicos**: 48
- **Última actualización**: Jul 9, 2025

**Nota**: Los datos se actualizan ejecutando el pipeline ETL monthly: `python ETL/pipeline.py --mode monthly`

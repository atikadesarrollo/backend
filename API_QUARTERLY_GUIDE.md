# API para Consultar Tabla Completa DL_Analisis_Venta_Quarterly

## 📊 Nuevos Endpoints Disponibles

### 1. Información General de la Tabla Quarterly

```
GET /api/analytics/quarterly/info
```

**Descripción**: Obtiene estadísticas generales de la tabla quarterly.

**Respuesta**:

```json
{
  "success": true,
  "message": "Quarterly table information retrieved successfully",
  "data": {
    "general_info": {
      "total_registros": 34572,
      "años_unicos": 1,
      "trimestres_unicos": 2,
      "fecha_minima": "2025-04-09T22:24:00",
      "fecha_maxima": "2025-07-08T18:04:03",
      "monto_total": 9839897637.05,
      "vendedores_unicos": 52,
      "clientes_unicos": 3653,
      "familias_productos": 45
    },
    "trimestre_distribution": [
      {
        "año": 2025,
        "trimestre": 3,
        "total_registros": 1147,
        "monto_total": 298001030.24,
        "vendedores_unicos": 30,
        "clientes_unicos": 228
      },
      {
        "año": 2025,
        "trimestre": 2,
        "total_registros": 33425,
        "monto_total": 9541896606.81,
        "vendedores_unicos": 52,
        "clientes_unicos": 3653
      }
    ]
  },
  "timestamp": "2025-07-09T11:31:30.123456"
}
```

### 2. Tabla Completa con Filtros y Paginación

```
GET /api/analytics/quarterly/complete
```

**Parámetros opcionales**:

- `limit`: Número máximo de registros (sin límite por defecto)
- `offset`: Número de registros a saltar (para paginación)
- `vendedor`: Filtrar por vendedor (búsqueda parcial)
- `cliente`: Filtrar por cliente (búsqueda parcial)
- `categoria`: Filtrar por categoría/rubro exacto
- `estado`: Filtrar por estado exacto
- `fecha_desde`: Filtrar desde fecha (YYYY-MM-DD)
- `fecha_hasta`: Filtrar hasta fecha (YYYY-MM-DD)
- `familia`: Filtrar por familia de producto (búsqueda parcial)
- `trimestre`: Filtrar por trimestre (1, 2, 3, 4)
- `año`: Filtrar por año

**Ejemplos de uso**:

#### Obtener todos los registros

```bash
curl "http://localhost:5000/api/analytics/quarterly/complete"
```

#### Paginación - Primeros 100 registros

```bash
curl "http://localhost:5000/api/analytics/quarterly/complete?limit=100&offset=0"
```

#### Filtrar por vendedor específico

```bash
curl "http://localhost:5000/api/analytics/quarterly/complete?vendedor=Loreto%20Guajardo"
```

#### Filtrar por trimestre y año

```bash
curl "http://localhost:5000/api/analytics/quarterly/complete?trimestre=2&año=2025"
```

#### Filtrar por rango de fechas

```bash
curl "http://localhost:5000/api/analytics/quarterly/complete?fecha_desde=2025-07-01&fecha_hasta=2025-07-08"
```

#### Filtrar por familia de producto

```bash
curl "http://localhost:5000/api/analytics/quarterly/complete?familia=Porcelanatos"
```

#### Combinación de filtros con paginación

```bash
curl "http://localhost:5000/api/analytics/quarterly/complete?vendedor=Loreto&estado=sale&limit=50&offset=0"
```

**Respuesta**:

```json
{
  "success": true,
  "message": "Quarterly data retrieved successfully. Showing 100 of 34572 records.",
  "data": [
    {
      "Referencia de pedido": "S089808",
      "Fecha de oferta": "2025-07-08T18:04:03",
      "Vendedor": "Loreto Guajardo",
      "Cliente": "MARIA JOSE CAMPENY",
      "RUT Cliente": "18018192-K",
      "SKU": "514",
      "Descipción": "VIDREPUR, Colors Nieblas, Mos. Vidrio Niebla Gris Claro BR puntos 31,5x31,5",
      "Familia": "Otros Atika",
      "Marca": "Vidrepur",
      "Cant. producto": 83.0,
      "RPT Precio unitario": 2836.11,
      "Descuento %": 17.0,
      "Total": 235397.0,
      "Estado": "sale",
      "Comuna": "COMUNA",
      "Canal": "Showroom",
      "Departamento": "Showroom Santiago",
      "Rubro": "DECORADOS Y MOSAICOS",
      "processed_at": "2025-07-08T22:16:00"
    }
  ],
  "total_records": 34572,
  "timestamp": "2025-07-09T11:31:30.123456"
}
```

## 🔧 Ejemplos de Implementación

### JavaScript/Frontend

```javascript
// Obtener información general
const getQuarterlyInfo = async () => {
  try {
    const response = await fetch(
      "http://localhost:5000/api/analytics/quarterly/info"
    );
    const data = await response.json();
    console.log("Info general:", data);
    return data;
  } catch (error) {
    console.error("Error:", error);
  }
};

// Obtener datos con filtros
const getQuarterlyData = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  try {
    const response = await fetch(
      `http://localhost:5000/api/analytics/quarterly/complete?${params}`
    );
    const data = await response.json();
    console.log("Datos quarterly:", data);
    return data;
  } catch (error) {
    console.error("Error:", error);
  }
};

// Ejemplo de uso
getQuarterlyInfo();
getQuarterlyData({
  vendedor: "Loreto",
  limit: 100,
  trimestre: 2,
  año: 2025,
});
```

### Python

```python
import requests

# Obtener información general
def get_quarterly_info():
    response = requests.get('http://localhost:5000/api/analytics/quarterly/info')
    return response.json()

# Obtener datos con filtros
def get_quarterly_data(filters=None):
    url = 'http://localhost:5000/api/analytics/quarterly/complete'
    response = requests.get(url, params=filters or {})
    return response.json()

# Ejemplos de uso
info = get_quarterly_info()
print(f"Total registros: {info['data']['general_info']['total_registros']}")

data = get_quarterly_data({
    'vendedor': 'Loreto Guajardo',
    'limit': 50,
    'estado': 'sale'
})
print(f"Registros obtenidos: {len(data['data'])}")
```

## 🌐 URLs de Acceso

- **Servidor local**: `http://localhost:5000`
- **Información quarterly**: `http://localhost:5000/api/analytics/quarterly/info`
- **Tabla completa**: `http://localhost:5000/api/analytics/quarterly/complete`

## ⚠️ Consideraciones

1. **Sin límite por defecto**: Si no se especifica `limit`, se devuelven TODOS los registros (34,572)
2. **Paginación recomendada**: Para aplicaciones web, usar `limit` y `offset`
3. **Filtros eficientes**: Usar filtros específicos para reducir la cantidad de datos
4. **Respuesta en tiempo real**: Los datos se obtienen directamente de la base de datos

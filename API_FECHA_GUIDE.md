# 📅 Guía Completa: Consumir API con Intervalos de Fechas

## 🎯 **Filtros de Fecha Disponibles**

La API soporta los siguientes filtros de fecha:

```
fecha_desde: YYYY-MM-DD  (desde esta fecha, inclusive)
fecha_hasta: YYYY-MM-DD  (hasta esta fecha, inclusive)
```

---

## 🔍 **Ejemplos de URLs con Intervalos de Fechas**

### **1. Rango de Fechas Específico**

```bash
# Datos de julio 2025
http://localhost:5000/api/analytics/monthly/complete?fecha_desde=2025-07-01&fecha_hasta=2025-07-31

# Últimos 7 días
http://localhost:5000/api/analytics/daily/complete?fecha_desde=2025-07-03&fecha_hasta=2025-07-10

# Trimestre específico (Q2 2025)
http://localhost:5000/api/analytics/quarterly/complete?fecha_desde=2025-04-01&fecha_hasta=2025-06-30
```

### **2. Solo Fecha de Inicio**

```bash
# Desde una fecha en adelante
http://localhost:5000/api/analytics/monthly/complete?fecha_desde=2025-06-15
```

### **3. Solo Fecha de Fin**

```bash
# Hasta una fecha específica
http://localhost:5000/api/analytics/monthly/complete?fecha_hasta=2025-07-01
```

### **4. Combinado con Otros Filtros**

```bash
# Vendedor específico en rango de fechas
http://localhost:5000/api/analytics/monthly/complete?vendedor=Juan&fecha_desde=2025-07-01&fecha_hasta=2025-07-10

# Estado y fechas
http://localhost:5000/api/analytics/monthly/complete?estado=Entregado&fecha_desde=2025-06-01&fecha_hasta=2025-07-31
```

---

## 💻 **Ejemplos de Código**

### **JavaScript/Fetch**

```javascript
// Función para obtener datos por rango de fechas
async function getDataByDateRange(
  period,
  fechaDesde,
  fechaHasta,
  otrosFiltros = {}
) {
  const params = new URLSearchParams({
    fecha_desde: fechaDesde,
    fecha_hasta: fechaHasta,
    ...otrosFiltros,
  });

  const response = await fetch(
    `http://localhost:5000/api/analytics/${period}/complete?${params}`
  );
  return await response.json();
}

// Ejemplos de uso
// Datos de la última semana
const ultimaSemana = await getDataByDateRange(
  "daily",
  "2025-07-03",
  "2025-07-10"
);

// Datos de un vendedor en junio
const ventasJunio = await getDataByDateRange(
  "monthly",
  "2025-06-01",
  "2025-06-30",
  { vendedor: "Juan Perez" }
);

// Datos con múltiples filtros
const ventasComplejas = await getDataByDateRange(
  "monthly",
  "2025-06-01",
  "2025-07-31",
  {
    vendedor: "Juan",
    estado: "Entregado",
    familia: "BEBIDAS",
    limit: 100,
  }
);

console.log("Registros encontrados:", ventasComplejas.total_records);
console.log("Datos:", ventasComplejas.data);
```

### **Python/Requests**

```python
import requests
from datetime import datetime, timedelta

def get_data_by_date_range(period, fecha_desde, fecha_hasta, **filtros):
    """Obtener datos por rango de fechas"""
    params = {
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        **filtros
    }

    response = requests.get(
        f'http://localhost:5000/api/analytics/{period}/complete',
        params=params
    )

    return response.json()

# Ejemplos de uso
# Datos de los últimos 7 días
fecha_hasta = datetime.now().strftime('%Y-%m-%d')
fecha_desde = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

datos_ultima_semana = get_data_by_date_range(
    'daily',
    fecha_desde,
    fecha_hasta
)

# Datos de un mes específico
datos_junio = get_data_by_date_range(
    'monthly',
    '2025-06-01',
    '2025-06-30',
    vendedor='Juan Perez',
    estado='Entregado'
)

# Datos trimestrales con filtros
datos_q2 = get_data_by_date_range(
    'quarterly',
    '2025-04-01',
    '2025-06-30',
    familia='ALIMENTOS',
    canal='RETAIL',
    limit=200
)

print(f"Registros Q2: {datos_q2['total_records']}")
print(f"Monto total: ${sum(r.get('Total', 0) for r in datos_q2['data']):,.2f}")
```

### **cURL**

```bash
# Datos de julio con paginación
curl -G "http://localhost:5000/api/analytics/monthly/complete" \
  --data-urlencode "fecha_desde=2025-07-01" \
  --data-urlencode "fecha_hasta=2025-07-31" \
  --data-urlencode "limit=100" \
  --data-urlencode "offset=0"

# Vendedor específico en rango de fechas
curl -G "http://localhost:5000/api/analytics/monthly/complete" \
  --data-urlencode "vendedor=Juan Perez" \
  --data-urlencode "fecha_desde=2025-06-15" \
  --data-urlencode "fecha_hasta=2025-07-15" \
  --data-urlencode "estado=Entregado"

# Exportar datos de un período a JSON
curl "http://localhost:5000/api/analytics/monthly/complete?fecha_desde=2025-07-01&fecha_hasta=2025-07-10" \
  -H "Accept: application/json" \
  -o ventas_julio_1-10.json
```

---

## 📊 **Casos de Uso Comunes con Fechas**

### **1. Reporte Diario**

```javascript
// Ventas del día actual
const hoy = new Date().toISOString().split("T")[0];
const ventasHoy = await getDataByDateRange("daily", hoy, hoy);

// Comparar con día anterior
const ayer = new Date(Date.now() - 86400000).toISOString().split("T")[0];
const ventasAyer = await getDataByDateRange("daily", ayer, ayer);
```

### **2. Reporte Semanal**

```javascript
// Última semana completa
const finSemana = new Date().toISOString().split("T")[0];
const inicioSemana = new Date(Date.now() - 7 * 86400000)
  .toISOString()
  .split("T")[0];
const ventasSemana = await getDataByDateRange(
  "weekly",
  inicioSemana,
  finSemana
);
```

### **3. Reporte Mensual**

```javascript
// Mes actual
const hoy = new Date();
const inicioMes = new Date(hoy.getFullYear(), hoy.getMonth(), 1)
  .toISOString()
  .split("T")[0];
const finMes = hoy.toISOString().split("T")[0];
const ventasMes = await getDataByDateRange("monthly", inicioMes, finMes);
```

### **4. Reporte Trimestral**

```javascript
// Q2 2025
const ventasQ2 = await getDataByDateRange(
  "quarterly",
  "2025-04-01",
  "2025-06-30"
);

// Q3 2025
const ventasQ3 = await getDataByDateRange(
  "quarterly",
  "2025-07-01",
  "2025-09-30"
);
```

### **5. Análisis de Tendencias**

```python
import pandas as pd

def analizar_tendencia_mensual(vendedor, meses_atras=6):
    """Analizar tendencia de ventas de un vendedor"""
    datos_completos = []

    for i in range(meses_atras):
        fecha_fin = datetime.now() - timedelta(days=30 * i)
        fecha_inicio = fecha_fin - timedelta(days=30)

        datos_mes = get_data_by_date_range(
            'monthly',
            fecha_inicio.strftime('%Y-%m-%d'),
            fecha_fin.strftime('%Y-%m-%d'),
            vendedor=vendedor
        )

        if datos_mes['success']:
            monto_mes = sum(r.get('Total', 0) for r in datos_mes['data'])
            datos_completos.append({
                'mes': fecha_fin.strftime('%Y-%m'),
                'monto': monto_mes,
                'registros': len(datos_mes['data'])
            })

    return pd.DataFrame(datos_completos)

# Usar la función
tendencia = analizar_tendencia_mensual('Juan Perez', 6)
print(tendencia)
```

---

## ⚡ **Tips de Rendimiento para Consultas por Fecha**

### **1. Usar Rangos Específicos**

```bash
# ✅ Bueno: Rango específico
fecha_desde=2025-07-01&fecha_hasta=2025-07-10

# ❌ Evitar: Rangos muy amplios sin paginación
fecha_desde=2020-01-01&fecha_hasta=2025-12-31
```

### **2. Combinar con Paginación**

```bash
# ✅ Bueno: Rango + paginación
fecha_desde=2025-06-01&fecha_hasta=2025-07-31&limit=100&offset=0

# ✅ Bueno: Filtros adicionales para reducir resultados
fecha_desde=2025-07-01&fecha_hasta=2025-07-31&vendedor=Juan&limit=50
```

### **3. Usar el Período Apropiado**

```bash
# ✅ Para datos recientes: usar daily
/api/analytics/daily/complete?fecha_desde=2025-07-08

# ✅ Para análisis histórico: usar monthly o quarterly
/api/analytics/monthly/complete?fecha_desde=2025-06-01&fecha_hasta=2025-07-31
```

---

## 🧪 **Script de Prueba Completo**

```python
#!/usr/bin/env python3
"""
Script para probar filtros de fecha en la API
"""

import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api/analytics"

def test_date_filters():
    """Probar diferentes filtros de fecha"""

    print("🗓️ PRUEBAS DE FILTROS DE FECHA")
    print("="*50)

    # Test 1: Últimos 7 días
    print("\n1️⃣ ÚLTIMOS 7 DÍAS:")
    fecha_hasta = datetime.now().strftime('%Y-%m-%d')
    fecha_desde = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    response = requests.get(f"{BASE_URL}/daily/complete", params={
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'limit': 10
    })

    if response.status_code == 200:
        data = response.json()
        print(f"   📊 Registros encontrados: {data['total_records']}")
        print(f"   📅 Rango: {fecha_desde} → {fecha_hasta}")

    # Test 2: Mes específico
    print("\n2️⃣ DATOS DE JULIO 2025:")
    response = requests.get(f"{BASE_URL}/monthly/complete", params={
        'fecha_desde': '2025-07-01',
        'fecha_hasta': '2025-07-31',
        'limit': 5
    })

    if response.status_code == 200:
        data = response.json()
        print(f"   📊 Registros en julio: {data['total_records']}")
        if data['data']:
            monto_julio = sum(r.get('Total', 0) for r in data['data'])
            print(f"   💰 Monto en muestra: ${monto_julio:,.2f}")

    # Test 3: Filtro combinado
    print("\n3️⃣ VENDEDOR + FECHAS:")
    response = requests.get(f"{BASE_URL}/monthly/complete", params={
        'vendedor': 'Juan',
        'fecha_desde': '2025-06-01',
        'fecha_hasta': '2025-07-31',
        'limit': 5
    })

    if response.status_code == 200:
        data = response.json()
        print(f"   👤 Vendedor 'Juan' en Jun-Jul: {data['total_records']} registros")

    # Test 4: Solo fecha desde
    print("\n4️⃣ DESDE UNA FECHA:")
    response = requests.get(f"{BASE_URL}/monthly/complete", params={
        'fecha_desde': '2025-07-01',
        'limit': 5
    })

    if response.status_code == 200:
        data = response.json()
        print(f"   📅 Desde 2025-07-01: {data['total_records']} registros")

if __name__ == "__main__":
    try:
        test_date_filters()
        print(f"\n✅ PRUEBAS COMPLETADAS")
        print("📖 Documentación completa en: API_MONTHLY_GUIDE.md")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Servidor no disponible en http://localhost:5000")
```

---

## 📋 **Resumen**

### **Formatos de Fecha Soportados:**

- `YYYY-MM-DD` (recomendado): `2025-07-10`
- La API compara contra el campo `[Fecha de oferta]`

### **Filtros Disponibles:**

- `fecha_desde`: Incluye registros desde esta fecha
- `fecha_hasta`: Incluye registros hasta esta fecha
- Se pueden usar juntos o por separado
- Se pueden combinar con cualquier otro filtro

### **Mejores Prácticas:**

1. ✅ Usar rangos específicos para mejor rendimiento
2. ✅ Combinar con paginación para datasets grandes
3. ✅ Usar el período apropiado (daily, monthly, etc.)
4. ✅ Combinar con otros filtros para resultados precisos
5. ✅ Manejar errores y validar fechas del lado cliente

¡Ya tienes todo lo necesario para consumir la API con intervalos de fechas! 🎉

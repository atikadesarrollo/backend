# ✅ Implementación de KPIs Completada

## 🎯 KPIs Implementados

### 1. **Cantidad de Clientes** ✅

- **Definición**: Suma de clientes distintos en el período
- **Cálculo**: `COUNT(DISTINCT [Cliente])`
- **Ejemplo**: 1,250 clientes

### 2. **Cantidad de Transacciones** ✅

- **Definición**: Suma total de facturas/transacciones
- **Cálculo**: `COUNT(*)`
- **Ejemplo**: 6,780 transacciones

### 3. **Porcentaje de Clientes Nuevos** ✅

- **Definición**: Clientes nuevos / Total de clientes \* 100
- **Cálculo**: `(COUNT(DISTINCT [Cliente] WHERE [Fecha creación cliente] IN período) / COUNT(DISTINCT [Cliente])) * 100`
- **Formato**: 2 decimales
- **Ejemplo**: 10.00%

### KPIs Adicionales Incluidos:

- 💰 **Venta Total**: Suma de montos facturados
- 🎫 **Ticket Promedio**: Promedio de monto por transacción
- 🤝 **Total Vendedores**: Vendedores únicos
- 🏗️ **Total Proyectos**: Proyectos únicos
- 📊 **Venta por Canal**: Agregación por canal con porcentajes
- 📊 **Venta por Departamento**: Agregación por departamento con porcentajes

---

## 📡 Endpoints Disponibles

### `/analisis_venta/kpis`

**Método**: GET

**Parámetros Requeridos:**

- `fecha_inicio` (YYYY-MM-DD)
- `fecha_fin` (YYYY-MM-DD)

**Parámetros Opcionales:**

- `canal`, `departamento`, `cliente`, `vendedor`, `proyecto`

**Ejemplo:**

```
GET /analisis_venta/kpis?fecha_inicio=2025-09-15&fecha_fin=2025-10-15
```

**Response:**

```json
{
  "kpis_principales": {
    "cantidad_clientes": 1250,
    "cantidad_transacciones": 6780,
    "cantidad_clientes_nuevos": 125,
    "porcentaje_clientes_nuevos": 10.00,
    "venta_total": 125000000.50,
    "ticket_promedio": 18436.98
  },
  "venta_por_canal": [...],
  "venta_por_departamento": [...]
}
```

### `/analisis_venta/top`

**Método**: GET

**Parámetros:**

- `fecha_inicio`, `fecha_fin` (requeridos)
- `tipo`: 'clientes', 'vendedores', 'productos', 'proyectos'
- `limit`: número de registros (default: 10)

**Ejemplo:**

```
GET /analisis_venta/top?fecha_inicio=2025-09-01&fecha_fin=2025-10-15&tipo=clientes&limit=10
```

---

## 🚀 Cómo Usar

### Opción 1: Probar con navegador

Abre en tu navegador:

```
http://localhost:5000/analisis_venta/kpis?fecha_inicio=2025-09-01&fecha_fin=2025-10-15
```

### Opción 2: Probar con PowerShell

```powershell
Invoke-WebRequest -Uri "http://localhost:5000/analisis_venta/kpis?fecha_inicio=2025-09-01&fecha_fin=2025-10-15" | Select-Object -ExpandProperty Content
```

### Opción 3: Probar con Python (test_kpis.py)

```powershell
python test_kpis.py
```

### Opción 4: Desde Frontend/JavaScript

```javascript
const response = await fetch(
  "/analisis_venta/kpis?" +
    new URLSearchParams({
      fecha_inicio: "2025-09-01",
      fecha_fin: "2025-10-15",
    })
);

const kpis = await response.json();
console.log(`Clientes: ${kpis.kpis_principales.cantidad_clientes}`);
console.log(`% Nuevos: ${kpis.kpis_principales.porcentaje_clientes_nuevos}%`);
```

---

## 📂 Archivos Creados

1. **`analisis_venta/kpis.py`** ✅

   - Lógica de cálculo de KPIs
   - Endpoints `/kpis` y `/top`
   - 400+ líneas de código

2. **`test_kpis.py`** ✅

   - Script de prueba automatizado
   - 3 casos de prueba
   - Genera `test_kpis_response.json`

3. **`API_KPIS_GUIDE.md`** ✅

   - Documentación completa
   - Definiciones de KPIs
   - Ejemplos de uso
   - Manejo de errores

4. **`analisis_venta/periodos.py`** (modificado) ✅
   - Agregado import de kpis
   - Registro de endpoints

---

## 🎨 Ejemplo de Respuesta Completa

```json
{
  "filtros_aplicados": {
    "fecha_inicio": "2025-09-15",
    "fecha_fin": "2025-10-15",
    "canal": null,
    "departamento": null,
    "cliente": null,
    "vendedor": null,
    "proyecto": null
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
    }
  ],
  "venta_por_departamento": [
    {
      "departamento": "Ventas Norte",
      "venta_total": 35000000.0,
      "transacciones": 1890,
      "clientes": 380,
      "porcentaje": 28.0
    }
  ]
}
```

---

## ✅ Validación de Requisitos

| Requisito                         | Implementado | Detalles                                         |
| --------------------------------- | ------------ | ------------------------------------------------ |
| Cantidad de clientes (únicos)     | ✅           | `COUNT(DISTINCT [Cliente])`                      |
| Cantidad de transacciones         | ✅           | `COUNT(*)`                                       |
| Porcentaje clientes nuevos        | ✅           | `(nuevos / total) * 100` con 2 decimales         |
| Cálculo post-definición de fechas | ✅           | Requiere `fecha_inicio` y `fecha_fin`            |
| Filtros opcionales                | ✅           | Canal, departamento, cliente, vendedor, proyecto |

---

## 🔧 Optimizaciones Implementadas

1. **Selección Inteligente de Tabla**:

   - 0-30 días → `DL_Analisis_Venta_v_Reciente` (más rápida)
   - 31-90 días → `DL_Analisis_Venta_v_Media`
   - 91-365 días → `DL_Analisis_Venta_v_Antiguo`
   - > 365 días → `DL_Analisis_Venta_v_Completo`

2. **Queries Optimizados**:

   - Agregaciones en SQL (no en Python)
   - Uso de índices en columnas de fecha
   - Queries separados por métrica

3. **Formato de Respuesta**:
   - Números redondeados a 2 decimales
   - Porcentajes calculados automáticamente
   - Manejo de divisiones por cero

---

## 🎯 Próximos Pasos Sugeridos

### 1. Probar los Endpoints

```bash
# En navegador o PowerShell
http://localhost:5000/analisis_venta/kpis?fecha_inicio=2025-09-01&fecha_fin=2025-10-15
```

### 2. Integrar en Dashboard

Crear vista HTML con:

- Cards de KPIs principales
- Gráficos de venta por canal/departamento
- Tabla de top clientes

### 3. Replicar para Facturación

Crear `facturacion/kpis.py` con métricas específicas:

- KPIs por tipo de documento
- Venta neta por unidad de negocios
- % notas de crédito vs facturas

### 4. Agregar Caching (Opcional)

Para mejorar performance:

- Cache en Redis
- TTL de 5-10 minutos
- Invalidación al detectar cambios

---

## 📞 Soporte

Documentación completa en:

- **`API_KPIS_GUIDE.md`** - Guía de uso detallada
- **`ARQUITECTURA_KPIS.md`** - Decisiones de arquitectura
- **`test_kpis.py`** - Ejemplos de uso

¿Necesitas agregar más KPIs o modificar los existentes? Los endpoints están diseñados para ser fácilmente extensibles.

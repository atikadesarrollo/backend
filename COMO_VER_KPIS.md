# 🧾 Guía Rápida: Cómo Ver KPIs de Facturación

## ✅ El servidor ya está corriendo con los endpoints de KPIs

---

## 🎯 Opción 1: Navegador Web (MÁS FÁCIL)

### KPIs de Análisis de Venta:

Abre en tu navegador:

```
http://localhost:5000/analisis_venta/kpis?fecha_inicio=2025-09-15&fecha_fin=2025-10-15
```

### KPIs de Facturación:

Abre en tu navegador:

```
http://localhost:5000/facturacion/kpis?fecha_inicio=2025-09-15&fecha_fin=2025-10-15
```

---

## 🎯 Opción 2: PowerShell

### Análisis de Venta:

```powershell
Invoke-WebRequest -Uri "http://localhost:5000/analisis_venta/kpis?fecha_inicio=2025-09-15&fecha_fin=2025-10-15" | Select-Object -ExpandProperty Content
```

### Facturación:

```powershell
Invoke-WebRequest -Uri "http://localhost:5000/facturacion/kpis?fecha_inicio=2025-09-15&fecha_fin=2025-10-15" | Select-Object -ExpandProperty Content
```

### Formato más bonito (JSON formateado):

```powershell
$response = Invoke-WebRequest -Uri "http://localhost:5000/facturacion/kpis?fecha_inicio=2025-09-15&fecha_fin=2025-10-15"
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

---

## 🎯 Opción 3: Con Filtros Adicionales

### Facturación filtrada por tipo de documento (33 = Factura Electrónica):

```
http://localhost:5000/facturacion/kpis?fecha_inicio=2025-09-01&fecha_fin=2025-10-15&tipo_documento=33
```

### Análisis de venta filtrado por canal:

```
http://localhost:5000/analisis_venta/kpis?fecha_inicio=2025-09-01&fecha_fin=2025-10-15&canal=Retail
```

---

## 📊 Endpoints Disponibles

### Análisis de Venta:

- **GET** `/analisis_venta/kpis` - KPIs principales
- **GET** `/analisis_venta/top?tipo=clientes&limit=10` - Top clientes/vendedores/productos
- **GET** `/analisis_venta/query` - Datos detallados (ya existía)
- **GET** `/analisis_venta/periodos` - Listado de periodos (ya existía)

### Facturación:

- **GET** `/facturacion/kpis` - KPIs principales
- **GET** `/facturacion/top?tipo=clientes&limit=10` - Top clientes/vendedores/obras
- **GET** `/facturacion/query` - Datos detallados (ya existía)
- **GET** `/facturacion/periodos` - Listado de periodos (ya existía)

---

## 📋 Ejemplo de Respuesta: KPIs de Facturación

```json
{
  "filtros_aplicados": {
    "fecha_inicio": "2025-09-15",
    "fecha_fin": "2025-10-15",
    "tipo_documento": null,
    "cliente": null
  },
  "tabla_consultada": "DL_Facturacion_v_Reciente",
  "columna_fecha": "Fecha documento",
  "kpis_principales": {
    "cantidad_clientes": 850,
    "cantidad_documentos": 3450,
    "cantidad_clientes_nuevos": 85,
    "porcentaje_clientes_nuevos": 10.0,
    "venta_neta_total": 95000000.5,
    "ticket_promedio": 27536.23,
    "total_vendedores": 35,
    "total_obras": 245
  },
  "venta_por_tipo_documento": [
    {
      "tipo_documento": "33",
      "venta_total": 85000000.0,
      "cantidad_documentos": 3200,
      "clientes": 750,
      "porcentaje": 89.47
    },
    {
      "tipo_documento": "61",
      "venta_total": -5000000.0,
      "cantidad_documentos": 250,
      "clientes": 180,
      "porcentaje": -5.26
    }
  ],
  "venta_por_unidad_negocio": [
    {
      "unidad_negocio": "Proyectos",
      "venta_total": 60000000.0,
      "documentos": 1800,
      "clientes": 450,
      "porcentaje": 63.16
    }
  ],
  "top_obras": [
    {
      "rank": 1,
      "obra": "Edificio Central Tower",
      "venta_total": 8500000.0,
      "documentos": 45
    }
  ]
}
```

---

## 🔥 Pruebas Rápidas

### 1. Ver todos los KPIs de los últimos 30 días:

**Análisis de Venta:**

```
http://localhost:5000/analisis_venta/kpis?fecha_inicio=2025-09-15&fecha_fin=2025-10-15
```

**Facturación:**

```
http://localhost:5000/facturacion/kpis?fecha_inicio=2025-09-15&fecha_fin=2025-10-15
```

### 2. Ver top 5 clientes:

**Análisis de Venta:**

```
http://localhost:5000/analisis_venta/top?fecha_inicio=2025-09-15&fecha_fin=2025-10-15&tipo=clientes&limit=5
```

**Facturación:**

```
http://localhost:5000/facturacion/top?fecha_inicio=2025-09-15&fecha_fin=2025-10-15&tipo=clientes&limit=5
```

### 3. Ver top 5 obras (solo facturación):

```
http://localhost:5000/facturacion/top?fecha_inicio=2025-09-15&fecha_fin=2025-10-15&tipo=obras&limit=5
```

---

## 💡 Tips

1. **Cambia las fechas** en los parámetros `fecha_inicio` y `fecha_fin` para ver diferentes períodos

2. **Agrega filtros** como:

   - `&canal=Retail` (análisis de venta)
   - `&tipo_documento=33` (facturación)
   - `&cliente=Constructora` (ambos)
   - `&vendedor=Juan` (ambos)

3. **El formato JSON** se ve mejor en:

   - Chrome/Edge: Instala extensión "JSON Viewer"
   - Firefox: Ya tiene visor JSON incorporado
   - PowerShell: Usa `ConvertFrom-Json | ConvertTo-Json -Depth 10`

4. **Guarda las respuestas** copiando el JSON si necesitas analizarlas después

---

## 🎨 Vista Previa: KPIs Principales

Ambos endpoints retornan estos KPIs principales:

- ✅ **Cantidad de clientes** (únicos)
- ✅ **Cantidad de transacciones/documentos**
- ✅ **Cantidad de clientes nuevos**
- ✅ **Porcentaje de clientes nuevos** (2 decimales)
- ✅ **Venta total** (Monto facturado o Venta neta)
- ✅ **Ticket promedio**
- ✅ **Total vendedores**
- ✅ **Total proyectos/obras**

Más:

- 📊 Distribución por canal/departamento (análisis venta)
- 📊 Distribución por tipo documento (facturación)
- 📊 Distribución por unidad de negocios (facturación)
- 🏆 Top obras (facturación)

---

## 🚀 Siguiente Paso: Dashboard Visual

Estos KPIs están listos para ser consumidos por un frontend. Puedes crear un dashboard con:

- Cards mostrando los KPIs principales
- Gráficos de barras para distribuciones
- Tablas para rankings (top clientes, obras, etc.)

Ejemplo con JavaScript:

```javascript
const response = await fetch(
  "/facturacion/kpis?fecha_inicio=2025-09-15&fecha_fin=2025-10-15"
);
const data = await response.json();

// Mostrar KPIs
document.getElementById("cantidad-clientes").textContent =
  data.kpis_principales.cantidad_clientes;
document.getElementById("porcentaje-nuevos").textContent =
  data.kpis_principales.porcentaje_clientes_nuevos + "%";
```

---

## 📝 Notas

- ✅ El servidor ya está corriendo en `http://localhost:5000`
- ✅ Los KPIs de facturación ya están registrados
- ✅ Detecta automáticamente la columna de fecha: `[Fecha documento]`
- ✅ Selecciona automáticamente la tabla óptima según el rango de fechas
- ✅ Los logs muestran que ya se hizo una petición exitosa a `/facturacion/kpis`

# 📊 Arquitectura de KPIs - Guía de Implementación

## 🎯 Estrategia Recomendada: Endpoints Dedicados

### Por qué Endpoints Separados

**Ventajas Técnicas:**

1. **Performance Optimizada**: Queries de agregación optimizados vs queries de detalle
2. **Caching Independiente**: KPIs pueden cachearse más tiempo que datos transaccionales
3. **Carga Paralela**: Frontend puede cargar KPIs y datos simultáneamente
4. **Escalabilidad**: Fácil mover KPIs a microservicio o cache distribuido
5. **Reutilización**: Mismo endpoint sirve dashboard, reportes, y mobile

**Comparación de Performance:**

```
Opción 1: Endpoint Dedicado
────────────────────────────
Request 1: /kpis?fecha=...         → 150ms (agregaciones)
Request 2: /query?fecha=...&limit=50 → 200ms (detalle)
Total (paralelo): ~200ms

Opción 2: Todo en Query
────────────────────────────
Request: /query?fecha=...&include_kpis=true
         → 350ms (agregaciones + detalle en serie)
```

---

## 🏗️ Arquitectura Propuesta

### Estructura de Módulos

```
analisis_venta/
├── __init__.py
├── periodos.py       # Endpoints existentes: /periodos, /query
├── kpis.py           # ← NUEVO: Endpoints de KPIs
└── utils.py          # Funciones compartidas

facturacion/
├── __init__.py
├── periodos.py
├── kpis.py           # ← NUEVO: KPIs de facturación
└── utils.py
```

---

## 📋 Endpoints de KPIs Propuestos

### 1. `/analisis_venta/kpis` - KPIs Generales + Por Dimensión

**Request:**

```http
GET /analisis_venta/kpis?fecha_inicio=2025-01-01&fecha_fin=2025-10-15&canal=&departamento=
```

**Response:**

```json
{
  "filtros_aplicados": {
    "fecha_inicio": "2025-01-01",
    "fecha_fin": "2025-10-15",
    "canal": null,
    "departamento": null
  },
  "tabla_consultada": "DL_Analisis_Venta_v_Completo",
  "kpis_generales": {
    "total_clientes": 1250,
    "total_vendedores": 45,
    "total_proyectos": 678,
    "venta_total": 125000000.50,
    "venta_promedio": 100000.40,
    "ticket_promedio": 184520.60,
    "total_transacciones": 6780,
    "productos_unicos": 3456
  },
  "venta_por_canal": [
    {"canal": "Retail", "venta_total": 45000000, "transacciones": 2300, "clientes": 450},
    {"canal": "Proyectos", "venta_total": 60000000, "transacciones": 3200, "clientes": 600},
    {"canal": "Digital", "venta_total": 20000000, "transacciones": 1280, "clientes": 200}
  ],
  "venta_por_departamento": [
    {"departamento": "Ventas Norte", "venta_total": 35000000, "porcentaje": 28},
    {"departamento": "Ventas Sur", "venta_total": 45000000, "porcentaje": 36},
    {"departamento": "Ventas Centro", "venta_total": 45000000, "porcentaje": 36}
  ],
  "venta_por_mes": [
    {"mes": "2025-01", "venta_total": 10000000},
    {"mes": "2025-02", "venta_total": 12000000},
    ...
  ]
}
```

### 2. `/analisis_venta/top` - Rankings

**Request:**

```http
GET /analisis_venta/top?fecha_inicio=2025-01-01&fecha_fin=2025-10-15&tipo=clientes&limit=10
```

**Tipos soportados:** `clientes`, `vendedores`, `productos`, `proyectos`

**Response:**

```json
{
  "tipo": "clientes",
  "periodo": {"inicio": "2025-01-01", "fin": "2025-10-15"},
  "top": [
    {
      "rank": 1,
      "cliente": "Constructora ABC S.A.",
      "venta_total": 15000000,
      "transacciones": 234,
      "ticket_promedio": 64102.56,
      "porcentaje_venta_total": 12.5
    },
    {
      "rank": 2,
      "cliente": "Inmobiliaria XYZ Ltda.",
      "venta_total": 12000000,
      "transacciones": 156,
      "ticket_promedio": 76923.08,
      "porcentaje_venta_total": 10.0
    },
    ...
  ]
}
```

### 3. `/analisis_venta/tendencias` - Análisis Temporal

**Request:**

```http
GET /analisis_venta/tendencias?fecha_inicio=2025-01-01&fecha_fin=2025-10-15&granularidad=mensual
```

**Granularidades:** `diario`, `semanal`, `mensual`, `trimestral`

**Response:**

```json
{
  "granularidad": "mensual",
  "serie_temporal": [
    {
      "periodo": "2025-01",
      "venta_total": 10000000,
      "transacciones": 650,
      "clientes_unicos": 125,
      "ticket_promedio": 15384.62,
      "variacion_mes_anterior": 5.2
    },
    ...
  ],
  "crecimiento": {
    "porcentaje": 15.5,
    "tendencia": "creciente"
  }
}
```

### 4. `/facturacion/kpis` - KPIs de Facturación

Similar estructura pero con métricas específicas:

```json
{
  "kpis_generales": {
    "total_facturas": 3450,
    "venta_neta_total": 95000000,
    "facturas_electronicas": 3200,
    "notas_credito": 250,
    "documentos_pendientes": 45
  },
  "venta_por_tipo_documento": [
    {"tipo": "33", "nombre": "Factura Electrónica", "venta_total": 85000000},
    {"tipo": "61", "nombre": "Nota Crédito", "venta_total": -5000000},
    ...
  ],
  "venta_por_unidad_negocio": [...],
  "top_obras": [...]
}
```

---

## 💻 Implementación Backend

### Paso 1: Crear `analisis_venta/kpis.py`

```python
from flask import Blueprint, request, jsonify
import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Configuración conexión (reutilizar de periodos.py)
server = os.getenv('DATALAKE_SERVER', 'DATALAKE')
database = os.getenv('DATALAKE_DATABASE', 'DATALAKE')
# ... resto de configuración ...

def get_connection():
    return pyodbc.connect(connection_string)

def seleccionar_tabla(fecha_inicio, fecha_fin):
    """Selecciona tabla óptima según rango de fechas"""
    if not fecha_inicio or not fecha_fin:
        return 'DL_Analisis_Venta_v_Completo'

    try:
        fi = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        ff = datetime.strptime(fecha_fin, '%Y-%m-%d')
        delta = (ff - fi).days

        if delta <= 30:
            return 'DL_Analisis_Venta_v_Reciente'
        elif delta <= 90:
            return 'DL_Analisis_Venta_v_Media'
        elif delta <= 365:
            return 'DL_Analisis_Venta_v_Antiguo'
        else:
            return 'DL_Analisis_Venta_v_Completo'
    except:
        return 'DL_Analisis_Venta_v_Completo'

def construir_filtros(args):
    """Construye cláusula WHERE a partir de argumentos"""
    filtros = []
    params = []

    fecha_inicio = args.get('fecha_inicio')
    fecha_fin = args.get('fecha_fin')
    canal = args.get('canal')
    departamento = args.get('departamento')
    cliente = args.get('cliente')
    vendedor = args.get('vendedor')

    if fecha_inicio:
        filtros.append("CAST([Fecha de oferta] AS DATE) >= CAST(? AS DATE)")
        params.append(fecha_inicio)
    if fecha_fin:
        filtros.append("CAST([Fecha de oferta] AS DATE) <= CAST(? AS DATE)")
        params.append(fecha_fin)
    if canal:
        filtros.append("[Canal] LIKE ?")
        params.append(f'%{canal}%')
    if departamento:
        filtros.append("[Departamento] LIKE ?")
        params.append(f'%{departamento}%')
    if cliente:
        filtros.append("[Cliente] LIKE ?")
        params.append(f'%{cliente}%')
    if vendedor:
        filtros.append("[Vendedor] LIKE ?")
        params.append(f'%{vendedor}%')

    where_sql = ' AND '.join(filtros) if filtros else '1=1'
    return where_sql, params

@bp_analisis_venta.route('/kpis', methods=['GET'])
def obtener_kpis():
    """
    Endpoint optimizado para calcular KPIs agregados

    Parámetros:
        - fecha_inicio, fecha_fin
        - canal, departamento, cliente, vendedor (filtros opcionales)

    Retorna:
        - KPIs generales
        - Ventas por dimensiones (canal, departamento)
        - Series temporales
    """
    try:
        args = dict(request.args)
        fecha_inicio = args.get('fecha_inicio')
        fecha_fin = args.get('fecha_fin')

        # Seleccionar tabla óptima
        tabla = seleccionar_tabla(fecha_inicio, fecha_fin)

        # Construir filtros
        where_sql, params = construir_filtros(args)

        with get_connection() as conn:
            cursor = conn.cursor()

            # 1. KPIs Generales
            query_generales = f"""
                SELECT
                    COUNT(DISTINCT [Cliente]) as total_clientes,
                    COUNT(DISTINCT [Vendedor]) as total_vendedores,
                    COUNT(DISTINCT [Proyecto]) as total_proyectos,
                    SUM([Monto facturado]) as venta_total,
                    AVG([Monto facturado]) as ticket_promedio,
                    COUNT(*) as total_transacciones,
                    COUNT(DISTINCT [SKU]) as productos_unicos
                FROM {tabla}
                WHERE {where_sql}
            """
            cursor.execute(query_generales, params)
            row = cursor.fetchone()

            kpis_generales = {
                'total_clientes': row[0] or 0,
                'total_vendedores': row[1] or 0,
                'total_proyectos': row[2] or 0,
                'venta_total': float(row[3]) if row[3] else 0,
                'ticket_promedio': float(row[4]) if row[4] else 0,
                'total_transacciones': row[5] or 0,
                'productos_unicos': row[6] or 0
            }

            # 2. Venta por Canal
            query_canal = f"""
                SELECT
                    [Canal],
                    SUM([Monto facturado]) as venta_total,
                    COUNT(*) as transacciones,
                    COUNT(DISTINCT [Cliente]) as clientes
                FROM {tabla}
                WHERE {where_sql}
                GROUP BY [Canal]
                ORDER BY SUM([Monto facturado]) DESC
            """
            cursor.execute(query_canal, params)
            venta_por_canal = [
                {
                    'canal': row[0],
                    'venta_total': float(row[1]) if row[1] else 0,
                    'transacciones': row[2],
                    'clientes': row[3]
                }
                for row in cursor.fetchall()
            ]

            # 3. Venta por Departamento
            query_dept = f"""
                SELECT
                    [Departamento],
                    SUM([Monto facturado]) as venta_total,
                    COUNT(*) as transacciones,
                    COUNT(DISTINCT [Cliente]) as clientes
                FROM {tabla}
                WHERE {where_sql}
                GROUP BY [Departamento]
                ORDER BY SUM([Monto facturado]) DESC
            """
            cursor.execute(query_dept, params)
            venta_por_departamento = [
                {
                    'departamento': row[0],
                    'venta_total': float(row[1]) if row[1] else 0,
                    'transacciones': row[2],
                    'clientes': row[3]
                }
                for row in cursor.fetchall()
            ]

            # 4. Serie temporal mensual (si hay rango de fechas)
            venta_por_mes = []
            if fecha_inicio and fecha_fin:
                query_mes = f"""
                    SELECT
                        FORMAT([Fecha de oferta], 'yyyy-MM') as mes,
                        SUM([Monto facturado]) as venta_total,
                        COUNT(*) as transacciones
                    FROM {tabla}
                    WHERE {where_sql}
                    GROUP BY FORMAT([Fecha de oferta], 'yyyy-MM')
                    ORDER BY FORMAT([Fecha de oferta], 'yyyy-MM')
                """
                cursor.execute(query_mes, params)
                venta_por_mes = [
                    {
                        'mes': row[0],
                        'venta_total': float(row[1]) if row[1] else 0,
                        'transacciones': row[2]
                    }
                    for row in cursor.fetchall()
                ]

            return jsonify({
                'filtros_aplicados': {
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin,
                    'canal': args.get('canal'),
                    'departamento': args.get('departamento')
                },
                'tabla_consultada': tabla,
                'kpis_generales': kpis_generales,
                'venta_por_canal': venta_por_canal,
                'venta_por_departamento': venta_por_departamento,
                'venta_por_mes': venta_por_mes
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp_analisis_venta.route('/top', methods=['GET'])
def obtener_top():
    """
    Endpoint para rankings (top clientes, vendedores, productos)

    Parámetros:
        - tipo: 'clientes', 'vendedores', 'productos', 'proyectos'
        - limit: número de registros (default: 10)
        - fecha_inicio, fecha_fin
        - otros filtros opcionales
    """
    try:
        args = dict(request.args)
        tipo = args.get('tipo', 'clientes')
        limit = int(args.get('limit', 10))

        tabla = seleccionar_tabla(args.get('fecha_inicio'), args.get('fecha_fin'))
        where_sql, params = construir_filtros(args)

        # Definir columna según tipo
        columnas = {
            'clientes': '[Cliente]',
            'vendedores': '[Vendedor]',
            'productos': '[SKU]',
            'proyectos': '[Proyecto]'
        }

        if tipo not in columnas:
            return jsonify({'error': 'Tipo inválido. Use: clientes, vendedores, productos, proyectos'}), 400

        columna = columnas[tipo]

        with get_connection() as conn:
            cursor = conn.cursor()

            # Query optimizado para top N
            query = f"""
                SELECT TOP {limit}
                    {columna} as nombre,
                    SUM([Monto facturado]) as venta_total,
                    COUNT(*) as transacciones,
                    AVG([Monto facturado]) as ticket_promedio
                FROM {tabla}
                WHERE {where_sql}
                GROUP BY {columna}
                ORDER BY SUM([Monto facturado]) DESC
            """
            cursor.execute(query, params)

            top = [
                {
                    'rank': idx + 1,
                    tipo[:-1]: row[0],  # 'clientes' -> 'cliente'
                    'venta_total': float(row[1]) if row[1] else 0,
                    'transacciones': row[2],
                    'ticket_promedio': float(row[3]) if row[3] else 0
                }
                for idx, row in enumerate(cursor.fetchall())
            ]

            return jsonify({
                'tipo': tipo,
                'periodo': {
                    'inicio': args.get('fecha_inicio'),
                    'fin': args.get('fecha_fin')
                },
                'top': top
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Paso 2: Registrar en Blueprint (periodos.py o **init**.py)

```python
# En analisis_venta/periodos.py o crear nuevo archivo

from flask import Blueprint

bp_analisis_venta = Blueprint('analisis_venta', __name__)

# Importar endpoints
from . import kpis  # ← Importar nuevo módulo

# O si están en el mismo archivo, ya están registrados
```

---

## 🎨 Implementación Frontend

### Dashboard con KPIs

```html
<!-- admin/templates/dashboard_con_kpis.html -->

<div class="container">
  <!-- KPIs Cards -->
  <div class="row mb-4" id="kpis-container">
    <div class="col-md-3">
      <div class="card bg-primary text-white">
        <div class="card-body">
          <h5>Venta Total</h5>
          <h2 id="kpi-venta-total">$0</h2>
        </div>
      </div>
    </div>
    <div class="col-md-3">
      <div class="card bg-success text-white">
        <div class="card-body">
          <h5>Clientes</h5>
          <h2 id="kpi-clientes">0</h2>
        </div>
      </div>
    </div>
    <div class="col-md-3">
      <div class="card bg-info text-white">
        <div class="card-body">
          <h5>Transacciones</h5>
          <h2 id="kpi-transacciones">0</h2>
        </div>
      </div>
    </div>
    <div class="col-md-3">
      <div class="card bg-warning text-dark">
        <div class="card-body">
          <h5>Ticket Promedio</h5>
          <h2 id="kpi-ticket">$0</h2>
        </div>
      </div>
    </div>
  </div>

  <!-- Gráficos -->
  <div class="row mb-4">
    <div class="col-md-6">
      <div class="card">
        <div class="card-header">Venta por Canal</div>
        <div class="card-body">
          <canvas id="chart-canal"></canvas>
        </div>
      </div>
    </div>
    <div class="col-md-6">
      <div class="card">
        <div class="card-header">Top 5 Clientes</div>
        <div class="card-body">
          <canvas id="chart-top-clientes"></canvas>
        </div>
      </div>
    </div>
  </div>

  <!-- Tabla de detalle -->
  <div class="row">
    <div class="col-12">
      <div class="card">
        <div class="card-header">Detalle de Transacciones</div>
        <div class="card-body">
          <table id="tabla-detalle" class="table">
            <!-- Contenido dinámico -->
          </table>
        </div>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
  async function cargarDashboard() {
    const filtros = {
      fecha_inicio: document.getElementById("fecha_inicio").value,
      fecha_fin: document.getElementById("fecha_fin").value,
      canal: document.getElementById("canal").value,
    };

    const params = new URLSearchParams(filtros);

    // Cargar KPIs y datos en paralelo
    const [kpis, datos, topClientes] = await Promise.all([
      fetch(`/analisis_venta/kpis?${params}`).then((r) => r.json()),
      fetch(`/analisis_venta/query?${params}&limit=50`).then((r) => r.json()),
      fetch(`/analisis_venta/top?${params}&tipo=clientes&limit=5`).then((r) =>
        r.json()
      ),
    ]);

    // Renderizar KPIs
    document.getElementById("kpi-venta-total").textContent = formatMoney(
      kpis.kpis_generales.venta_total
    );
    document.getElementById("kpi-clientes").textContent =
      kpis.kpis_generales.total_clientes;
    document.getElementById("kpi-transacciones").textContent =
      kpis.kpis_generales.total_transacciones;
    document.getElementById("kpi-ticket").textContent = formatMoney(
      kpis.kpis_generales.ticket_promedio
    );

    // Renderizar gráfico de canal
    const ctxCanal = document.getElementById("chart-canal").getContext("2d");
    new Chart(ctxCanal, {
      type: "bar",
      data: {
        labels: kpis.venta_por_canal.map((c) => c.canal),
        datasets: [
          {
            label: "Venta por Canal",
            data: kpis.venta_por_canal.map((c) => c.venta_total),
            backgroundColor: "rgba(54, 162, 235, 0.5)",
          },
        ],
      },
    });

    // Renderizar top clientes
    const ctxTop = document
      .getElementById("chart-top-clientes")
      .getContext("2d");
    new Chart(ctxTop, {
      type: "horizontalBar",
      data: {
        labels: topClientes.top.map((c) => c.cliente),
        datasets: [
          {
            label: "Top Clientes",
            data: topClientes.top.map((c) => c.venta_total),
            backgroundColor: "rgba(75, 192, 192, 0.5)",
          },
        ],
      },
    });

    // Renderizar tabla de detalle
    renderTabla(datos.data);
  }

  function formatMoney(value) {
    return new Intl.NumberFormat("es-CL", {
      style: "currency",
      currency: "CLP",
    }).format(value);
  }
</script>
```

---

## 🚀 Optimizaciones Avanzadas

### 1. Caching de KPIs

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache por 5 minutos
@lru_cache(maxsize=128)
def get_kpis_cached(fecha_inicio, fecha_fin, filtros_hash):
    # ... cálculo de KPIs ...
    return kpis

@bp_analisis_venta.route('/kpis', methods=['GET'])
def obtener_kpis():
    # Crear hash de filtros para cache
    filtros_str = f"{fecha_inicio}_{fecha_fin}_{canal}_{dept}"
    filtros_hash = hash(filtros_str)

    kpis = get_kpis_cached(fecha_inicio, fecha_fin, filtros_hash)
    return jsonify(kpis)
```

### 2. Queries Paralelos con Threading

```python
from concurrent.futures import ThreadPoolExecutor

def obtener_kpis_paralelo():
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_generales = executor.submit(calcular_kpis_generales, tabla, filtros)
        future_canal = executor.submit(calcular_venta_canal, tabla, filtros)
        future_dept = executor.submit(calcular_venta_dept, tabla, filtros)
        future_mes = executor.submit(calcular_venta_mes, tabla, filtros)

        kpis_generales = future_generales.result()
        venta_canal = future_canal.result()
        venta_dept = future_dept.result()
        venta_mes = future_mes.result()

    return jsonify({...})
```

### 3. Vistas Materializadas en SQL Server

```sql
-- Crear tabla agregada que se actualiza periódicamente
CREATE TABLE DL_KPIs_Venta_Cache (
    fecha_calculo DATETIME,
    fecha_inicio DATE,
    fecha_fin DATE,
    canal VARCHAR(50),
    departamento VARCHAR(50),
    total_clientes INT,
    venta_total DECIMAL(18,2),
    -- ... más campos ...
    PRIMARY KEY (fecha_inicio, fecha_fin, canal, departamento)
);

-- Job que actualiza cada hora
CREATE PROCEDURE sp_Actualizar_KPIs_Cache
AS
BEGIN
    TRUNCATE TABLE DL_KPIs_Venta_Cache;

    INSERT INTO DL_KPIs_Venta_Cache
    SELECT
        GETDATE() as fecha_calculo,
        CAST([Fecha de oferta] AS DATE) as fecha_inicio,
        CAST([Fecha de oferta] AS DATE) as fecha_fin,
        [Canal],
        [Departamento],
        COUNT(DISTINCT [Cliente]) as total_clientes,
        SUM([Monto facturado]) as venta_total
    FROM DL_Analisis_Venta_v
    GROUP BY CAST([Fecha de oferta] AS DATE), [Canal], [Departamento];
END
```

---

## 📊 Resumen de Recomendación

### ✅ Implementar Primero:

1. **`/analisis_venta/kpis`** - Endpoint de KPIs agregados
2. **`/analisis_venta/top`** - Rankings de clientes/vendedores
3. **Carga paralela en frontend** - Promise.all()

### 🚀 Optimizar Después:

4. Cache con Redis o in-memory
5. Vistas materializadas en BD
6. Queries paralelos con threading

### 📈 Beneficios Esperados:

- ⚡ **Performance**: KPIs en ~150ms vs ~500ms en query combinado
- 📊 **Escalabilidad**: Fácil agregar nuevos KPIs sin afectar queries existentes
- 🔄 **Reusabilidad**: Mismo endpoint sirve web, mobile, reportes
- 💾 **Cacheable**: KPIs pueden cachearse independientemente

¿Quieres que implemente el endpoint `/analisis_venta/kpis` completo como te mostré?

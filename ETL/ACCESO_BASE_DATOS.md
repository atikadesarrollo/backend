"""
🗃️ GUÍA DE ACCESO A LA BASE DE DATOS ETL
===========================================

# UBICACIÓN DE LA BASE DE DATOS RESULTANTE:

La base de datos se encuentra en el mismo servidor SQL Server remoto donde ejecutamos el ETL:

📍 **SERVIDOR:** 45.236.130.211
📍 **BASE DE DATOS:** DATALAKE
📍 **AUTENTICACIÓN:** Windows Authentication (Trusted Connection)
📍 **PUERTO:** 1433 (por defecto)

# TABLAS RESULTANTES CREADAS:

✅ **DL_Analisis_Venta_Daily**

- Datos diarios (últimos 7 días por defecto)
- 3,010 filas actualmente
- 63 columnas de datos completos
- Se actualiza cuando ejecutas: `python pipeline.py --mode daily`

✅ **DL_Analisis_Venta_Summary**

- Resumen por vendedores (últimos 7 días)
- 39 filas actualmente
- 13 columnas de métricas resumidas
- Se actualiza cuando ejecutas: `python pipeline.py --mode summary`

⚠️ **DL_Analisis_Venta_Weekly** (No creada aún)

- Se creará cuando ejecutes: `python pipeline.py --mode weekly`

⚠️ **DL_Analisis_Venta_Processed** (No creada aún)

- Se creará cuando ejecutes: `python pipeline.py --mode custom`

# CÓMO CONSULTAR LA BASE DE DATOS:

### 1️⃣ DESDE PYTHON (Recomendado para desarrollo)

```python
from database_connection import DatabaseConnection

# Conectar a la base de datos
db = DatabaseConnection()

# Consultar tabla diaria
daily_data = db.query_to_dataframe("SELECT TOP 100 * FROM DL_Analisis_Venta_Daily")
print(daily_data.head())

# Consultar resumen por vendedores
summary_data = db.query_to_dataframe("SELECT * FROM DL_Analisis_Venta_Summary ORDER BY monto_total DESC")
print(summary_data.head())
```

### 2️⃣ DESDE SQL SERVER MANAGEMENT STUDIO (SSMS)

1. **Conectar al servidor:** 45.236.130.211
2. **Usar Windows Authentication**
3. **Seleccionar base de datos:** DATALAKE
4. **Ejecutar consultas:**

```sql
-- Ver datos diarios recientes
SELECT TOP 100 * FROM DL_Analisis_Venta_Daily
ORDER BY [Fecha de oferta] DESC

-- Ver resumen por vendedores
SELECT * FROM DL_Analisis_Venta_Summary
ORDER BY monto_total DESC

-- Ver distribución por fechas
SELECT
    CAST([Fecha de oferta] AS DATE) as Fecha,
    COUNT(*) as Total_Ofertas,
    SUM([Cantidad entregada]) as Cantidad_Total,
    SUM([Monto orden]) as Monto_Total
FROM DL_Analisis_Venta_Daily
GROUP BY CAST([Fecha de oferta] AS DATE)
ORDER BY Fecha DESC
```

### 3️⃣ DESDE POWER BI

1. **Origen de datos:** SQL Server
2. **Servidor:** 45.236.130.211
3. **Base de datos:** DATALAKE
4. **Modo de conectividad:** DirectQuery o Import
5. **Autenticación:** Windows
6. **Tablas disponibles:**
   - DL_Analisis_Venta_Daily
   - DL_Analisis_Venta_Summary

### 4️⃣ DESDE EXCEL (Power Query)

1. **Datos → Obtener datos → Desde Azure → Desde SQL Server**
2. **Servidor:** 45.236.130.211
3. **Base de datos:** DATALAKE
4. **Seleccionar tablas:** DL_Analisis_Venta_Daily, DL_Analisis_Venta_Summary

### 5️⃣ DESDE OTRAS HERRAMIENTAS BI

- **Tableau:** Conector SQL Server con credenciales Windows
- **QlikView/QlikSense:** ODBC connection string
- **Looker:** SQL Server connector

# CONNECTION STRING PARA HERRAMIENTAS EXTERNAS:

```
Server=45.236.130.211;Database=DATALAKE;Trusted_Connection=yes;Driver={SQL Server};
```

O para herramientas que requieren ODBC:

```
DRIVER={ODBC Driver 17 for SQL Server};SERVER=45.236.130.211;DATABASE=DATALAKE;Trusted_Connection=yes;
```

# ESTRUCTURA DE DATOS DISPONIBLES:

### 📊 DL_Analisis_Venta_Daily (63 columnas)

Columnas principales:

- Fecha de oferta
- Fecha creación cliente
- Vendedor
- Email vendedor
- Cantidad entregada
- Monto orden
- Estado
- Cliente
- Producto
- Categoria
- Y muchas más...

### 📈 DL_Analisis_Venta_Summary (13 columnas)

Columnas:

- Vendedor
- total_ofertas
- cantidad_total
- monto_total
- promedio_monto
- max_monto
- min_monto
- fecha_primera_venta
- fecha_ultima_venta
- dias_activo
- processed_at
- created_at
- updated_at

# SCRIPTS ÚTILES PARA CONSULTAR:

### Verificar tablas disponibles:

```bash
python verificar_etl.py
```

### Ver datos de cualquier tabla:

```bash
python ver_datos.py
```

### Explorar estructura de tablas:

```bash
python explorar_tablas.py
```

### Ejecutar pipeline para actualizar datos:

```bash
# Datos diarios (últimos 7 días)
python pipeline.py --mode daily

# Datos semanales (últimos 30 días)
python pipeline.py --mode weekly

# Resumen por vendedores
python pipeline.py --mode summary
```

# EJEMPLOS DE CONSULTAS ÚTILES:

### Top vendedores del mes:

```sql
SELECT
    Vendedor,
    COUNT(*) as total_ofertas,
    SUM([Cantidad entregada]) as cantidad_total,
    SUM([Monto orden]) as monto_total,
    AVG([Monto orden]) as promedio_por_oferta
FROM DL_Analisis_Venta_Daily
WHERE [Fecha de oferta] >= DATEADD(MONTH, -1, GETDATE())
GROUP BY Vendedor
ORDER BY monto_total DESC
```

### Ventas por categoría:

```sql
SELECT
    Categoria,
    COUNT(*) as total_ofertas,
    SUM([Monto orden]) as monto_total
FROM DL_Analisis_Venta_Daily
GROUP BY Categoria
ORDER BY monto_total DESC
```

### Evolución diaria de ventas:

```sql
SELECT
    CAST([Fecha de oferta] AS DATE) as Fecha,
    COUNT(*) as Total_Ofertas,
    SUM([Monto orden]) as Monto_Total,
    AVG([Monto orden]) as Promedio_Oferta
FROM DL_Analisis_Venta_Daily
GROUP BY CAST([Fecha de oferta] AS DATE)
ORDER BY Fecha DESC
```

# NOTAS IMPORTANTES:

✅ **Las tablas se actualizan cada vez que ejecutas el pipeline ETL**
✅ **Los datos están limpios y listos para análisis**
✅ **Todas las fechas están en formato estándar**
✅ **Se eliminan duplicados automáticamente**
✅ **Incluye timestamps de procesamiento**

⚠️ **La tabla Weekly aún no se ha creado - ejecuta `python pipeline.py --mode weekly` para crearla**
⚠️ **Asegúrate de tener permisos para conectarte al servidor 45.236.130.211**
⚠️ **Usa Windows Authentication - no se requiere usuario/contraseña**

Para cualquier duda, ejecuta los scripts de diagnóstico incluidos en la carpeta ETL.
"""

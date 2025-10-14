# Pipeline de Análisis de Venta

## Descripción

Este pipeline genera tablas optimizadas a partir de la vista `DL_Analisis_Venta_v` para mejorar el rendimiento de las consultas.

## Tablas Generadas

### 1. DL_Analisis_Venta_v_Completo

- **Descripción**: Copia completa de la vista original
- **Filtro**: Ninguno (todos los registros)
- **Uso**: Para consultas sin filtros de fecha o rangos mayores a 365 días
- **Actualización**: Se recomienda ejecutar semanalmente o mensualmente

### 2. DL_Analisis_Venta_v_Reciente

- **Descripción**: Datos de los últimos 30 días
- **Filtro**: `[Fecha de oferta] >= DATEADD(day, -30, GETDATE())`
- **Uso**: Para consultas de datos recientes (rango <= 30 días)
- **Actualización**: Se recomienda ejecutar diariamente

### 3. DL_Analisis_Venta_v_Media

- **Descripción**: Datos de los últimos 90 días
- **Filtro**: `[Fecha de oferta] >= DATEADD(day, -90, GETDATE())`
- **Uso**: Para consultas de datos del trimestre (rango 31-90 días)
- **Actualización**: Se recomienda ejecutar semanalmente

### 4. DL_Analisis_Venta_v_Antiguo

- **Descripción**: Datos del último año
- **Filtro**: `[Fecha de oferta] >= DATEADD(day, -365, GETDATE())`
- **Uso**: Para consultas anuales (rango 91-365 días)
- **Actualización**: Se recomienda ejecutar mensualmente

## Selección Automática de Tabla

El endpoint `/analisis_venta/query` selecciona automáticamente la tabla según el rango de fechas:

| Rango de fechas         | Tabla utilizada              |
| ----------------------- | ---------------------------- |
| 0-30 días               | DL_Analisis_Venta_v_Reciente |
| 31-90 días              | DL_Analisis_Venta_v_Media    |
| 91-365 días             | DL_Analisis_Venta_v_Antiguo  |
| > 365 días o sin filtro | DL_Analisis_Venta_v_Completo |

## Ejecución del Pipeline

```bash
# Asegúrate de tener las variables de entorno configuradas en .env
# DATALAKE_SERVER, DATALAKE_DATABASE, DATALAKE_USERNAME, DATALAKE_PASSWORD

python pipeline_analisis_venta.py
```

## Tiempo de Ejecución Estimado

- **Completo**: Varía según el tamaño total (puede tomar varios minutos)
- **Reciente**: ~10-30 segundos
- **Media**: ~30-60 segundos
- **Antiguo**: ~1-3 minutos

## Beneficios

- **Rendimiento**: Consultas hasta 10x más rápidas en tablas particionadas
- **Escalabilidad**: Reduce la carga en la vista original
- **Mantenibilidad**: Fácil actualización mediante script automatizado

## Notas Importantes

- Las tablas se crean como tablas físicas, no vistas
- Se utiliza una tabla temporal durante la creación para evitar downtime
- La vista original `DL_Analisis_Venta_v` ya no se usa directamente en consultas del dashboard
- Todas las consultas ahora van a `DL_Analisis_Venta_v_Completo` por defecto

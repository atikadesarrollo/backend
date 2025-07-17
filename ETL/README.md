# Pipeline ETL - Documentación

## Descripción

Este pipeline ETL está diseñado para extraer datos de la base de datos SQL del DATALAKE, transformarlos y cargarlos de vuelta para consumo por aplicaciones frontend.

## Estructura del Proyecto

```
ETL/
├── __init__.py                 # Inicialización del módulo
├── database_connection.py     # Clases para conexión y operaciones de BD
├── pipeline.py                # Pipeline principal y programación
├── config.py                  # Configuración centralizada
├── utils.py                   # Utilidades y funciones auxiliares
├── requirements.txt           # Dependencias Python
└── README.md                  # Esta documentación
```

## Instalación

1. Instalar dependencias:

```bash
pip install -r ETL/requirements.txt
```

2. Configurar variables de entorno en `.env`:

```env
DATALAKE_SERVER=DATALAKE
DATALAKE_DATABASE=DATALAKE
DATALAKE_USERNAME=usuario (opcional si usa autenticación Windows)
DATALAKE_PASSWORD=password (opcional si usa autenticación Windows)
```

## Uso

### Desde línea de comandos

```bash
# Probar conexiones
python ETL/pipeline.py --mode test

# Ejecutar pipeline diario
python ETL/pipeline.py --mode daily

# Ejecutar pipeline semanal
python ETL/pipeline.py --mode weekly

# Pipeline personalizado
python ETL/pipeline.py --mode custom --source "DL_Analisis_Venta_v" --target "Mi_Tabla_Procesada" --days 7

# Programar ejecución automática
python ETL/pipeline.py --mode schedule
```

### Desde código Python

```python
from ETL.pipeline import ETLPipeline
from ETL.database_connection import run_etl_pipeline

# Crear instancia del pipeline
pipeline = ETLPipeline()

# Probar conexiones
if pipeline.test_connections():
    print("Conexiones OK")

# Ejecutar pipeline personalizado
success = pipeline.run_custom_pipeline(
    source_table="DL_Analisis_Venta_v",
    target_table="DL_Analisis_Venta_Processed",
    days_back=30
)

# O usar la función directa
success = run_etl_pipeline("DL_Analisis_Venta_v", "DL_Analisis_Venta_Processed", 30)
```

## Componentes Principales

### DatabaseConnection

- Maneja conexiones a SQL Server
- Ejecuta consultas y retorna DataFrames de pandas
- Inserta datos en tablas

### DataExtractor

- Extrae datos de diferentes fuentes
- Consultas predefinidas para análisis de ventas
- Consultas personalizadas

### DataTransformer

- Limpia datos (duplicados, nulos, etc.)
- Transforma fechas
- Agrega columnas calculadas
- Estandariza formatos

### DataLoader

- Carga datos a tablas de destino
- Crea tablas de staging
- Manejo de errores en carga

### Utilidades

- Validación de calidad de datos
- Perfilado de datasets
- Logging especializado
- Funciones auxiliares

## Configuración

La configuración se maneja en `config.py`:

- **DATABASE_CONFIG**: Configuración de conexión a BD
- **LOGGING_CONFIG**: Configuración de logs
- **DEFAULT_TRANSFORMATIONS**: Transformaciones por defecto
- **PREDEFINED_QUERIES**: Consultas predefinidas
- **TARGET_TABLES**: Mapeo de tablas de destino

## Programación Automática

El pipeline puede programarse para ejecutarse automáticamente:

- **Pipeline diario**: 6:00 AM todos los días
- **Pipeline semanal**: 2:00 AM los lunes

```python
# Iniciar programación
python ETL/pipeline.py --mode schedule
```

## Logging

Los logs se guardan en:

- **Archivo**: `etl_pipeline.log`
- **Consola**: Salida estándar

Niveles de log:

- INFO: Información general del proceso
- ERROR: Errores no críticos
- CRITICAL: Errores que detienen el pipeline

## Validación de Datos

El pipeline incluye validación automática:

- Verificación de columnas requeridas
- Detección de datos faltantes
- Validación de tipos de datos
- Detección de duplicados
- Análisis de rangos de fechas

## Monitoreo

Para monitorear el pipeline:

1. Revisar logs en `etl_pipeline.log`
2. Verificar tablas de destino en la BD
3. Usar reportes de validación

## Ejemplo Completo

```python
#!/usr/bin/env python3

from ETL.pipeline import ETLPipeline
from ETL.utils import DataValidator, DataProfiler

def main():
    # Inicializar pipeline
    pipeline = ETLPipeline()

    # Probar conexiones
    if not pipeline.test_connections():
        print("Error en conexiones")
        return

    # Ejecutar pipeline personalizado
    success = pipeline.run_custom_pipeline(
        source_table="DL_Analisis_Venta_v",
        target_table="DL_Analisis_Venta_Processed",
        days_back=7
    )

    if success:
        print("Pipeline ejecutado exitosamente")
    else:
        print("Error en pipeline")

if __name__ == "__main__":
    main()
```

## Solución de Problemas

### Error de conexión a BD

- Verificar que el servidor DATALAKE esté accesible
- Comprobar credenciales de acceso
- Verificar driver ODBC instalado

### Error en transformaciones

- Revisar calidad de datos fuente
- Verificar tipos de datos
- Comprobar columnas requeridas

### Error en carga de datos

- Verificar permisos de escritura en BD
- Comprobar existencia de tabla destino
- Revisar tipos de datos compatibles

## Próximos Pasos

1. Implementar más transformaciones específicas
2. Agregar soporte para más fuentes de datos
3. Implementar monitoreo avanzado
4. Crear dashboards de monitoreo
5. Implementar notificaciones de errores

# Fix: Error de Columna en Pipeline de Facturación

## Problema

```
Error en el proceso: ('42S22', "[42S22] [Microsoft][ODBC Driver 17 for SQL Server][SQL Server]Invalid column name 'Fecha de oferta'. (207) (SQLExecDirectW)")
```

## Causa

El pipeline asumía que `DL_Facturacion_v` tenía una columna llamada `[Fecha de oferta]`, igual que en `DL_Analisis_Venta_v`. Sin embargo, las vistas tienen estructuras diferentes.

## Solución Implementada

### 1. Detección Automática de Columna de Fecha

El pipeline ahora:

1. Se conecta a la base de datos
2. Lee las columnas de `DL_Facturacion_v`
3. Busca automáticamente cualquier columna que contenga "fecha" en su nombre
4. Usa esa columna para los filtros de periodo
5. Guarda el nombre en `facturacion/fecha_column.txt` para uso del API

**Código agregado en pipeline_facturacion.py:**

```python
# Detectar columna de fecha automáticamente
print("Detectando columna de fecha...")
cursor.execute("SELECT TOP 0 * FROM DL_Facturacion_v")
columnas = [col[0] for col in cursor.description]

# Buscar columna de fecha
fecha_col = None
for col in columnas:
    if 'fecha' in col.lower():
        fecha_col = col
        print(f"Columna de fecha detectada: [{fecha_col}]")
        break

if not fecha_col:
    print("ERROR: No se encontró ninguna columna con 'fecha'")
    print("Columnas disponibles:")
    for col in columnas:
        print(f"  - [{col}]")
    exit(1)

# Guardar para uso del API
config_file = 'facturacion/fecha_column.txt'
with open(config_file, 'w') as f:
    f.write(fecha_col)
```

### 2. Script de Verificación

Creado `Scripts/verificar_columnas_facturacion.py` para inspeccionar la estructura de la vista.

**Uso:**

```powershell
python Scripts\verificar_columnas_facturacion.py
```

**Resultado esperado:**

- Lista todas las columnas de `DL_Facturacion_v`
- Destaca las columnas relacionadas con fecha

### 3. Próximos Pasos para el API

El API de facturación (`facturacion/periodos.py`) también necesita actualizarse para usar la columna de fecha correcta. Opciones:

**Opción A: Leer desde archivo**

```python
# Al inicio del módulo
import os
fecha_col_file = os.path.join(os.path.dirname(__file__), 'fecha_column.txt')
if os.path.exists(fecha_col_file):
    with open(fecha_col_file, 'r') as f:
        FECHA_COLUMN = f.read().strip()
else:
    FECHA_COLUMN = 'Fecha'  # Default
```

**Opción B: Detección dinámica** (más robusta)

```python
def get_fecha_column():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 0 * FROM DL_Facturacion_v_Completo")
        for col in cursor.description:
            if 'fecha' in col[0].lower():
                return col[0]
    return None
```

## Ejecución del Pipeline

Una vez actualizados los archivos:

```powershell
python Scripts\pipeline_facturacion.py
```

**Salida esperada:**

```
Conectado a la base de datos DATALAKE en el servidor DATALAKE
Detectando columna de fecha...
Columna de fecha detectada: [Fecha]  # o el nombre real
Columna de fecha guardada en: facturacion/fecha_column.txt
Creando copia completa de DL_Facturacion_v...
Creando tabla temporal: DL_Facturacion_v_Completo_tmp
Insertando datos en DL_Facturacion_v_Completo_tmp
Tabla DL_Facturacion_v_Completo creada y datos insertados.
...
Proceso finalizado correctamente.
```

## Verificación

1. **Verificar columnas:**

   ```powershell
   python Scripts\verificar_columnas_facturacion.py
   ```

2. **Ejecutar pipeline:**

   ```powershell
   python Scripts\pipeline_facturacion.py
   ```

3. **Verificar tablas creadas:**

   ```powershell
   sqlcmd -S DATALAKE -d DATALAKE -Q "SELECT name FROM sys.tables WHERE name LIKE '%Facturacion%'"
   ```

4. **Verificar archivo de configuración:**
   ```powershell
   cat facturacion\fecha_column.txt
   ```

## Actualización Pendiente

Después de ejecutar el pipeline exitosamente, actualizar `facturacion/periodos.py` para usar el nombre de columna correcto en lugar de `[Fecha de oferta]`.

Buscar y reemplazar todas las instancias de:

- `[Fecha de oferta]` → usar el valor de `fecha_column.txt`

O implementar la detección dinámica en el código del API.

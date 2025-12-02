# Fix Completo: Actualización de Columna de Fecha en API de Facturación

## Cambios Realizados

### 1. Función de Detección Automática

Agregada función `detect_fecha_column()` que:

- Intenta leer las columnas de las tablas de facturación
- Busca la primera columna que contenga "fecha" en su nombre
- Devuelve 'Fecha' como fallback si no encuentra nada

```python
def detect_fecha_column():
    """Detecta automáticamente la columna de fecha en las tablas de facturación"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            for tabla in ['DL_Facturacion_v_Completo', 'DL_Facturacion_v', 'DL_Facturacion_v_Reciente']:
                try:
                    cursor.execute(f"SELECT TOP 0 * FROM {tabla}")
                    for col in cursor.description:
                        if 'fecha' in col[0].lower():
                            return col[0]
                except:
                    continue
    except:
        pass
    return 'Fecha'  # Fallback
```

### 2. Variable Global con Detección

```python
FECHA_COLUMN = detect_fecha_column()
print(f"[Facturación] Columna de fecha detectada: [{FECHA_COLUMN}]")
```

### 3. Actualización del Endpoint `/periodos`

Cambió de:

```python
cursor.execute(f"SELECT MIN([Fecha de oferta]), MAX([Fecha de oferta]), COUNT(*) FROM {tabla}")
```

A:

```python
cursor.execute(f"SELECT MIN([{FECHA_COLUMN}]), MAX([{FECHA_COLUMN}]), COUNT(*) FROM {tabla}")
```

### 4. Actualización del Endpoint `/query`

**Filtros de fecha:**

```python
# Antes:
filtros.append("CAST([Fecha de oferta] AS DATE) >= CAST(? AS DATE)")

# Después:
filtros.append(f"CAST([{FECHA_COLUMN}] AS DATE) >= CAST(? AS DATE)")
```

**Ordenamiento por defecto:**

```python
# Antes:
order_by = '[Fecha de oferta] DESC'

# Después:
order_by = f'[{FECHA_COLUMN}] DESC'
```

## Para Aplicar los Cambios

### 1. Reiniciar el Servidor

```powershell
# Detener el servidor actual (Ctrl+C en la terminal)
# Iniciar nuevamente:
python app.py
```

### 2. Verificar en los Logs

Al iniciar, deberías ver:

```
[Facturación] Columna de fecha detectada: [Fecha]
```

(O el nombre real de la columna)

### 3. Probar el Endpoint

```powershell
curl http://localhost:5000/facturacion/periodos
```

**Resultado esperado:** JSON con periodos, sin errores de columna

## Verificación Completa

### Test 1: Periodos

```powershell
curl http://localhost:5000/facturacion/periodos
```

**Esperado:**

```json
{
  "periodos": [
    {
      "periodo": "Reciente",
      "tabla": "DL_Facturacion_v_Reciente",
      "fecha_min": "2025-09-15",
      "fecha_max": "2025-10-15",
      "total_registros": 1250
    },
    ...
  ]
}
```

### Test 2: Query Simple

```powershell
curl "http://localhost:5000/facturacion/query?periodo=Completo&limit=5"
```

**Esperado:** 5 registros de facturación

### Test 3: Query con Fechas

```powershell
curl "http://localhost:5000/facturacion/query?fecha_inicio=2025-10-01&fecha_fin=2025-10-15&limit=10"
```

**Esperado:** 10 registros dentro del rango de fechas

## Archivos Modificados

✅ `facturacion/periodos.py`

- Agregada función `detect_fecha_column()`
- Variable global `FECHA_COLUMN`
- Actualizado endpoint `/periodos`
- Actualizado endpoint `/query` (filtros y orden)

## Estado

✅ Detección automática de columna implementada
✅ Endpoints actualizados
⏳ Pendiente: Reiniciar servidor para aplicar cambios
⏳ Pendiente: Ejecutar pipeline si aún no se ha hecho

## Próximos Pasos

1. **Reiniciar servidor** para cargar los cambios
2. **Ejecutar pipeline** (si no se ha hecho):
   ```powershell
   python Scripts\pipeline_facturacion.py
   ```
3. **Probar endpoints** como se indica arriba
4. **Probar dashboard** en http://localhost:5000/admin

## Nota Importante

La detección automática se ejecuta **una vez al cargar el módulo**. Si cambias las tablas o la estructura, necesitas reiniciar el servidor para que detecte los cambios.

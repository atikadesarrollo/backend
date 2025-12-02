# Fix: Error en Dashboard Multi-Fuente

## Problema

El dashboard mostraba el error: `{"error":"An unexpected error occurred"}`

## Causa Raíz

Había inconsistencia en los nombres de campos entre el endpoint de facturación y el template HTML:

1. **En views.py:** Se obtenía `resp_facturacion.json()` directamente en lugar de extraer `resp_facturacion.json().get('periodos', [])`

2. **En admin_dashboard.html:** El template usaba `p.nombre` pero el endpoint de facturación devuelve `p.periodo` (igual que el de ventas)

## Solución Aplicada

### 1. Corrección en views.py (línea ~26)

```python
# ANTES:
periodos_facturacion = resp_facturacion.json()

# DESPUÉS:
periodos_facturacion = resp_facturacion.json().get('periodos', [])
```

### 2. Corrección en admin_dashboard.html (línea ~62)

```html
<!-- ANTES: -->
<strong>{{ p.nombre }}</strong> ({{ p.tabla }})

<!-- DESPUÉS: -->
<strong>{{ p.periodo }}</strong> ({{ p.tabla }})<br />
{% if p.fecha_min and p.fecha_max %} Rango: {{ p.fecha_min }} a {{ p.fecha_max
}} | Registros: {{ p.total_registros }} {% endif %}
```

### 3. Corrección en selector de periodo (línea ~101)

```html
<!-- ANTES: -->
<option value="{{ p.nombre }}">{{ p.nombre }}</option>

<!-- DESPUÉS: -->
<option value="{{ p.periodo }}">{{ p.periodo }}</option>
```

## Resultado

Ahora ambos endpoints (venta y facturación) usan la misma estructura de datos:

```json
{
  "periodos": [
    {
      "periodo": "Completo",
      "tabla": "DL_..._v_Completo",
      "fecha_min": "2020-01-01",
      "fecha_max": "2025-10-15",
      "total_registros": 150000
    }
  ]
}
```

## Verificación

✅ Sin errores de sintaxis
✅ Estructura consistente entre venta y facturación
✅ Template HTML correcto
✅ Dashboard debe funcionar correctamente

## Próximo Paso

Reiniciar el servidor y probar:

```powershell
python app.py
```

Luego acceder a http://localhost:5000/admin y seleccionar "Facturación"

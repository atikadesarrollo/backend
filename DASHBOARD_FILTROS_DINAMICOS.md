# Dashboard con Filtros Dinámicos por Base de Datos

## Cambios Implementados

### Problema Identificado

El dashboard mostraba los mismos filtros para ambas bases de datos (Análisis de Venta y Facturación), lo que generaba confusión ya que las estructuras de datos son diferentes.

### Solución Implementada

#### 1. Template HTML Dinámico (`admin_dashboard.html`)

El formulario ahora muestra **filtros diferentes según la base de datos seleccionada** usando condicionales Jinja2:

**Para Análisis de Venta:**

```html
{% if base_datos == 'analisis_venta' %} - Proyecto - Cliente - Vendedor - SKU -
Departamento - Canal - Monto mínimo/máximo - Descripción, Rubro, Familia, Marca
- Ordenar por (default: [Fecha de oferta] DESC) {% endif %}
```

**Para Facturación:**

```html
{% if base_datos == 'facturacion' %} - Cliente (Razón Social) - con placeholder
explicativo - Vendedor - busca en factura y oferta - Tipo Documento (33, 34, 61)
- Número Documento - Folio SII - Código Producto - Descripción Producto -
Obra/Proyecto - Unidad de Negocios - Categoría Cliente - Rubro, Familia, Marca -
Venta Neta - Mínimo/Máximo - Ordenar por (default: [Fecha documento] DESC) {%
endif %}
```

#### 2. Backend Actualizado (`admin/views.py`)

El controlador ahora captura **filtros específicos según la base de datos**:

```python
# Filtros comunes
filtros = {
    'periodo': ...,
    'fecha_inicio': ...,
    'fecha_fin': ...,
    'cliente': ...,
    'vendedor': ...,
    'monto_min': ...,
    'monto_max': ...,
    'descripcion': ...,
    'rubro': ...,
    'familia': ...,
    'marca': ...,
    'order_by': ...,
}

# Filtros específicos
if base_datos == 'analisis_venta':
    filtros['proyecto'] = ...
    filtros['sku'] = ...
    filtros['departamento'] = ...
    filtros['canal'] = ...
elif base_datos == 'facturacion':
    filtros['tipo_documento'] = ...
    filtros['numero_documento'] = ...
    filtros['folio_sii'] = ...
    filtros['codigo'] = ...
    filtros['obra'] = ...
    filtros['unidad_negocio'] = ...
    filtros['categoria_cliente'] = ...
```

## Mejoras de UX

### Placeholders Informativos

Los campos de facturación incluyen placeholders que guían al usuario:

- **Tipo Documento**: "Ej: 33, 34, 61"
- **Vendedor**: "Busca en factura y oferta"
- **Cliente**: "Ej: Constructora"
- **Obra**: "Nombre de la obra"

### Labels Descriptivos

Los labels son más específicos:

- "Cliente (Razón Social)" en lugar de solo "Cliente"
- "Venta Neta - Mínimo/Máximo" en lugar de "Monto mínimo/máximo"
- "Código Producto" y "Descripción Producto" para mayor claridad

## Mapeo de Columnas

### Análisis de Venta (DL_Analisis_Venta_v)

| Campo UI            | Columna BD        | Tipo Filtro  |
| ------------------- | ----------------- | ------------ |
| Cliente             | [Cliente]         | LIKE %valor% |
| Vendedor            | [Vendedor]        | LIKE %valor% |
| Proyecto            | [Proyecto]        | LIKE %valor% |
| SKU                 | [SKU]             | LIKE %valor% |
| Departamento        | [Departamento]    | LIKE %valor% |
| Canal               | [Canal]           | LIKE %valor% |
| Monto mínimo/máximo | [Monto facturado] | >= / <=      |

### Facturación (DL_Facturacion_v)

| Campo UI                   | Columna BD                              | Tipo Filtro  |
| -------------------------- | --------------------------------------- | ------------ |
| Cliente (Razón Social)     | [Razon social]                          | LIKE %valor% |
| Vendedor                   | [Vendedor factura] OR [Vendedor oferta] | LIKE %valor% |
| Tipo Documento             | [Tipo documento]                        | LIKE %valor% |
| Número Documento           | [Numero de documento]                   | LIKE %valor% |
| Folio SII                  | [Folio SII]                             | LIKE %valor% |
| Código Producto            | [Codigo]                                | LIKE %valor% |
| Obra/Proyecto              | [Nombre obra]                           | LIKE %valor% |
| Unidad de Negocios         | [Unidad de negocios]                    | LIKE %valor% |
| Categoría Cliente          | [Categoria cliente]                     | LIKE %valor% |
| Venta Neta - Mínimo/Máximo | [Venta neta]                            | >= / <=      |

## Flujo de Usuario

1. **Seleccionar Base de Datos** → El formulario se adapta automáticamente
2. **Ver Periodos Disponibles** → Se muestran los periodos de la base seleccionada
3. **Aplicar Filtros** → Solo aparecen los campos relevantes para esa base de datos
4. **Consultar** → El backend usa los filtros correctos según la base de datos

## Beneficios

✅ **Claridad**: El usuario ve solo los filtros relevantes para su consulta
✅ **Prevención de errores**: No se pueden aplicar filtros inexistentes
✅ **Mejor UX**: Placeholders y labels guían al usuario
✅ **Mantenibilidad**: Fácil agregar nuevas bases de datos con filtros específicos
✅ **Performance**: Solo se envían parámetros relevantes al backend

## Ejemplo de Uso

### Consulta de Facturación

1. Seleccionar "Facturación" en selector de base de datos
2. Ingresar rango de fechas: 2025-10-01 a 2025-10-15
3. Filtrar por:
   - Tipo Documento: 33 (Factura Electrónica)
   - Cliente: "Constructora"
   - Obra: "Edificio"
4. Ver resultados filtrados por estos criterios específicos de facturación

### Consulta de Análisis de Venta

1. Seleccionar "Análisis de Venta"
2. Ingresar rango de fechas
3. Filtrar por:
   - Proyecto: "Proyecto X"
   - SKU: "ABC123"
   - Departamento: "Ventas"
4. Ver resultados filtrados por estos criterios específicos de ventas

## Notas Técnicas

- Los filtros comunes (cliente, vendedor, descripción, rubro, familia, marca, montos) están disponibles en ambas bases de datos
- La columna de fecha se detecta automáticamente en el backend de facturación
- Los filtros usan búsqueda parcial (LIKE %valor%) para mayor flexibilidad
- El filtro de vendedor en facturación busca en dos columnas: [Vendedor factura] y [Vendedor oferta]

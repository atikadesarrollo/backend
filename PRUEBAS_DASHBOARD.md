# Guía de Pruebas - Dashboard Multi-Fuente

## 1. Ejecutar Pipeline de Facturación

Antes de probar los endpoints, necesitas generar las tablas:

```powershell
cd c:\Users\Alexis.DESKTOP-CHQU3C8\Documents\GitHub\backend
python Scripts\pipeline_facturacion.py
```

**Resultado esperado:**

- Creación de 4 tablas: DL_Facturacion_v_Completo, Reciente, Media, Antiguo
- Reporte de número de registros y espacio usado
- Tiempo total de ejecución

## 2. Iniciar el Servidor

```powershell
python app.py
```

**Verificar:**

- Servidor iniciado en http://0.0.0.0:5000
- Blueprint de facturación registrado en logs
- Sin errores en consola

## 3. Probar Endpoints de Facturación

### 3.1 Listar Periodos

```powershell
curl http://localhost:5000/facturacion/periodos
```

**Esperado:** JSON con 4 periodos, rangos de fechas y totales

### 3.2 Query Simple

```powershell
curl "http://localhost:5000/facturacion/query?periodo=Reciente&limit=10"
```

**Esperado:** JSON con tabla, total y data (10 registros)

### 3.3 Query con Filtros

```powershell
curl "http://localhost:5000/facturacion/query?fecha_inicio=2025-09-01&fecha_fin=2025-09-30&cliente=EmpresaX"
```

**Esperado:** Filtros aplicados, selección automática de tabla según rango

## 4. Probar Dashboard Web

### 4.1 Acceder al Dashboard

```
http://localhost:5000/admin
```

### 4.2 Seleccionar Base de Datos

1. Elegir "Facturación" del dropdown
2. Verificar que se muestran los periodos de facturación
3. Verificar que se despliega el formulario de filtros

### 4.3 Aplicar Filtros

1. Seleccionar fechas (ej: último mes)
2. Opcionalmente: agregar cliente, proyecto, etc.
3. Click en "Consultar"

### 4.4 Verificar Resultados

- Tabla con datos de facturación
- Indicador de tabla utilizada
- Total de registros
- Controles de paginación

### 4.5 Probar Paginación

1. Click en "Siguiente" o números de página
2. Verificar que mantiene filtros y base de datos seleccionada
3. Verificar que los datos cambian

### 4.6 Probar "Todos los Registros"

1. Con filtros que den < 10,000 registros
2. Click en "Todos los registros"
3. Verificar advertencia si > 1,000
4. Verificar error si > 10,000
5. Click en "Volver a paginación"

## 5. Probar Cambio de Base de Datos

### 5.1 De Facturación a Análisis de Venta

1. Cambiar dropdown a "Análisis de Venta"
2. Verificar cambio de periodos
3. Aplicar filtros y consultar
4. Verificar que usa endpoints de venta

### 5.2 De Análisis de Venta a Facturación

1. Cambiar dropdown a "Facturación"
2. Verificar cambio de periodos
3. Aplicar filtros y consultar
4. Verificar que usa endpoints de facturación

## 6. Casos de Prueba Específicos

### 6.1 Selección Inteligente de Tabla

**Test:** Query con rango de 15 días

```
fecha_inicio: 2025-10-01
fecha_fin: 2025-10-15
```

**Esperado:** Usa tabla `DL_Facturacion_v_Reciente`

**Test:** Query con rango de 60 días

```
fecha_inicio: 2025-08-15
fecha_fin: 2025-10-15
```

**Esperado:** Usa tabla `DL_Facturacion_v_Media`

### 6.2 Filtros LIKE

**Test:** Cliente parcial

```
cliente: Empresa
```

**Esperado:** Encuentra "Empresa X", "Empresa Y", etc.

### 6.3 Ordenamiento

**Test:** Order by personalizado

```
order_by: [Monto facturado] DESC
```

**Esperado:** Registros ordenados por monto descendente

### 6.4 Límite de Registros

**Test:** Sin filtros en tabla Completo

- Click en "Todos los registros"
- Si total > 10,000: debe mostrar error
- Si total < 10,000: debe cargar todos

## 7. Verificar Logs

### 7.1 Revisar app.log

```powershell
Get-Content logs\app.log -Tail 50
```

### 7.2 Revisar requests.log

```powershell
Get-Content logs\requests.log -Tail 50
```

**Buscar:**

- Requests a /facturacion/periodos
- Requests a /facturacion/query
- Requests a /admin con POST
- Tiempos de respuesta
- Errores (si los hay)

## 8. Checklist de Validación

- [ ] Pipeline ejecutado sin errores
- [ ] Servidor iniciado correctamente
- [ ] Endpoint /facturacion/periodos responde
- [ ] Endpoint /facturacion/query responde
- [ ] Dashboard carga correctamente
- [ ] Selector de base de datos funciona
- [ ] Periodos se muestran dinámicamente
- [ ] Filtros se despliegan correctamente
- [ ] Consulta de facturación devuelve datos
- [ ] Consulta de venta devuelve datos
- [ ] Paginación funciona
- [ ] "Todos los registros" valida límites
- [ ] Cambio entre bases de datos funciona
- [ ] Selección inteligente de tabla funciona
- [ ] Logs registran actividad
- [ ] Sin errores en consola del navegador

## 9. Solución de Problemas

### Problema: "Table not found"

**Causa:** Pipeline no ejecutado
**Solución:** Ejecutar `python Scripts\pipeline_facturacion.py`

### Problema: "Error al cargar periodos"

**Causa:** Conexión a base de datos fallida
**Solución:** Verificar variables de entorno en `.env`

### Problema: "Selector no muestra facturación"

**Causa:** Blueprint no registrado
**Solución:** Verificar que app.py incluye registro de bp_facturacion

### Problema: Filtros no funcionan

**Causa:** Nombres de columnas incorrectos
**Solución:** Verificar esquema de DL_Facturacion_v y ajustar en periodos.py

### Problema: Paginación pierde selección de BD

**Causa:** Campo hidden no actualizado
**Solución:** Verificar que base_datos_hidden se actualiza en JavaScript

## 10. Próximos Pasos

1. Ajustar nombres de campos si difieren en DL_Facturacion_v
2. Agregar más filtros específicos de facturación si es necesario
3. Considerar crear vistas materializadas para mejor performance
4. Implementar caché para consultas frecuentes
5. Agregar exportación a Excel/CSV
6. Agregar gráficos y visualizaciones

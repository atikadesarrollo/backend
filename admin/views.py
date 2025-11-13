from flask import Blueprint, render_template, request, jsonify
import requests
import os

admin_bp = Blueprint('admin', __name__, template_folder='templates')

@admin_bp.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    filtros = {}
    resultados = None
    error = None
    mensaje = None
    periodos_venta = []
    periodos_facturacion = []
    pagina_actual = 1
    total_registros = 0
    registros_por_pagina = 50
    mostrar_todos = False
    base_datos = 'analisis_venta'  # Default
    
    # Consultar periodos disponibles de ambas fuentes
    try:
        resp_venta = requests.get('http://127.0.0.1:5000/analisis_venta/periodos')
        if resp_venta.status_code == 200:
            periodos_venta = resp_venta.json().get('periodos', [])
    except Exception as e:
        error = f"Error al cargar periodos de venta: {str(e)}"
    
    try:
        resp_facturacion = requests.get('http://127.0.0.1:5000/facturacion/periodos')
        if resp_facturacion.status_code == 200:
            periodos_facturacion = resp_facturacion.json().get('periodos', [])
    except Exception as e:
        if error:
            error += f" | Error al cargar periodos de facturación: {str(e)}"
        else:
            error = f"Error al cargar periodos de facturación: {str(e)}"
    
    if request.method == 'POST':
        # Obtener la base de datos seleccionada
        base_datos = request.form.get('base_datos', 'analisis_venta')
        
        # Determinar API_URL según la base de datos
        if base_datos == 'facturacion':
            API_URL = 'http://127.0.0.1:5000/facturacion/query'
        else:
            API_URL = 'http://127.0.0.1:5000/analisis_venta/query'
        
        # Verificar si se solicitó "Todos los registros"
        mostrar_todos = request.form.get('mostrar_todos') == 'true'
        
        # Obtener página actual
        try:
            pagina_actual = int(request.form.get('pagina', 1))
        except:
            pagina_actual = 1
        
        # Recoger filtros del formulario
        filtros = {
            'periodo': request.form.get('periodo'),
            'fecha_inicio': request.form.get('fecha_inicio'),
            'fecha_fin': request.form.get('fecha_fin'),
            'cliente': request.form.get('cliente'),
            'vendedor': request.form.get('vendedor'),
            'monto_min': request.form.get('monto_min'),
            'monto_max': request.form.get('monto_max'),
            'descripcion': request.form.get('descripcion'),
            'rubro': request.form.get('rubro'),
            'familia': request.form.get('familia'),
            'marca': request.form.get('marca'),
            'order_by': request.form.get('order_by'),
        }
        
        # Filtros específicos según la base de datos
        if base_datos == 'analisis_venta':
            filtros['proyecto'] = request.form.get('proyecto')
            filtros['sku'] = request.form.get('sku')
            filtros['departamento'] = request.form.get('departamento')
            filtros['canal'] = request.form.get('canal')
        elif base_datos == 'facturacion':
            filtros['tipo_documento'] = request.form.get('tipo_documento')
            filtros['numero_documento'] = request.form.get('numero_documento')
            filtros['folio_sii'] = request.form.get('folio_sii')
            filtros['codigo'] = request.form.get('codigo')
            filtros['obra'] = request.form.get('obra')
            filtros['unidad_negocio'] = request.form.get('unidad_negocio')
            filtros['categoria_cliente'] = request.form.get('categoria_cliente')
        
        # Primero, hacer una consulta rápida para saber el total de registros
        filtros_count = filtros.copy()
        filtros_count['limit'] = 1
        filtros_count['offset'] = 0
        
        try:
            response_count = requests.get(API_URL, params=filtros_count, timeout=10)
            if response_count.status_code == 200:
                total_registros = response_count.json().get('total', 0)
            else:
                total_registros = 0
        except:
            total_registros = 0
        
        # Verificar si es seguro cargar todos los registros
        LIMITE_SEGURO = 10000  # Máximo 10,000 registros para "Todos"
        
        # Configurar paginación
        if mostrar_todos:
            if total_registros > LIMITE_SEGURO:
                error = f"No se puede cargar todos los registros. Total: {total_registros:,}. El límite seguro es {LIMITE_SEGURO:,} registros. Por favor, usa filtros para reducir los resultados o navega por páginas."
                mostrar_todos = False
                filtros['limit'] = registros_por_pagina
                filtros['offset'] = 0
                pagina_actual = 1
            else:
                filtros['limit'] = LIMITE_SEGURO
                filtros['offset'] = 0
        else:
            filtros['limit'] = registros_por_pagina
            filtros['offset'] = (pagina_actual - 1) * registros_por_pagina
        
        # Llamar al endpoint de backend solo si no hubo error previo
        if not error:
            try:
                response = requests.get(API_URL, params=filtros, timeout=60)
                if response.status_code == 200:
                    resultados = response.json()
                    mensaje = "Consulta realizada exitosamente."
                else:
                    error = response.text
            except Exception as e:
                error = f"Error al consultar: {str(e)}"
        
        if not error and not resultados:
            mensaje = "Filtro agregado correctamente."
    
    # Calcular número total de páginas
    total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina if total_registros > 0 else 0
    
    return render_template('admin_dashboard.html', 
                         filtros=filtros, 
                         resultados=resultados, 
                         error=error, 
                         mensaje=mensaje, 
                         periodos_venta=periodos_venta,
                         periodos_facturacion=periodos_facturacion,
                         pagina_actual=pagina_actual,
                         total_paginas=total_paginas,
                         registros_por_pagina=registros_por_pagina,
                         mostrar_todos=mostrar_todos,
                         base_datos=base_datos)

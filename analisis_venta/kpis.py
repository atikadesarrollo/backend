"""
Módulo de KPIs para Análisis de Venta
Calcula métricas agregadas optimizadas
"""
from flask import request, jsonify
import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Configuración de conexión
server = os.getenv('DATALAKE_SERVER', 'DATALAKE')
database = os.getenv('DATALAKE_DATABASE', 'DATALAKE')
username = os.getenv('DATALAKE_USERNAME')
password = os.getenv('DATALAKE_PASSWORD')
port = os.getenv('DATALAKE_PORT', '1433')

if username and password:
    connection_string = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server},{port};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
        f'Encrypt=yes;'
        f'TrustServerCertificate=yes;'
        f'Connection Timeout=30;'
    )
else:
    connection_string = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'Trusted_Connection=yes;'
    )

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
    proyecto = args.get('proyecto')
    
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
    if proyecto:
        filtros.append("[Proyecto] LIKE ?")
        params.append(f'%{proyecto}%')
    
    where_sql = ' AND '.join(filtros) if filtros else '1=1'
    return where_sql, params

def registrar_endpoints_kpis(bp):
    """Registra los endpoints de KPIs en el blueprint"""
    
    @bp.route('/kpis', methods=['GET'])
    def obtener_kpis():
        """
        Calcula KPIs agregados para el período seleccionado
        
        KPIs calculados:
        - Cantidad de clientes (únicos)
        - Cantidad de transacciones (facturas)
        - Porcentaje de clientes nuevos
        - Venta total
        - Ticket promedio
        - Ventas por canal/departamento
        
        Parámetros:
            fecha_inicio (str): Fecha inicio YYYY-MM-DD (requerido)
            fecha_fin (str): Fecha fin YYYY-MM-DD (requerido)
            canal (str): Filtro por canal (opcional)
            departamento (str): Filtro por departamento (opcional)
            cliente (str): Filtro por cliente (opcional)
            vendedor (str): Filtro por vendedor (opcional)
            proyecto (str): Filtro por proyecto (opcional)
        
        Returns:
            JSON con KPIs calculados
        """
        try:
            args = dict(request.args)
            fecha_inicio = args.get('fecha_inicio')
            fecha_fin = args.get('fecha_fin')
            
            # Validar fechas requeridas
            if not fecha_inicio or not fecha_fin:
                return jsonify({
                    'error': 'Se requieren fecha_inicio y fecha_fin'
                }), 400
            
            # Seleccionar tabla óptima
            tabla = seleccionar_tabla(fecha_inicio, fecha_fin)
            
            # Construir filtros
            where_sql, params = construir_filtros(args)
            
            with get_connection() as conn:
                cursor = conn.cursor()
                
                # ==========================================
                # 1. CANTIDAD DE CLIENTES (únicos)
                # ==========================================
                query_clientes = f"""
                    SELECT COUNT(DISTINCT [Cliente]) as total_clientes
                    FROM {tabla}
                    WHERE {where_sql}
                """
                cursor.execute(query_clientes, params)
                cantidad_clientes = cursor.fetchone()[0] or 0
                
                # ==========================================
                # 2. CANTIDAD DE TRANSACCIONES (facturas)
                # ==========================================
                query_transacciones = f"""
                    SELECT COUNT(*) as total_transacciones
                    FROM {tabla}
                    WHERE {where_sql}
                """
                cursor.execute(query_transacciones, params)
                cantidad_transacciones = cursor.fetchone()[0] or 0
                
                # ==========================================
                # 3. PORCENTAJE CLIENTES NUEVOS
                # ==========================================
                # Clientes nuevos: aquellos cuya fecha de creación está dentro del período
                query_clientes_nuevos = f"""
                    SELECT 
                        COUNT(DISTINCT [Cliente]) as clientes_nuevos
                    FROM {tabla}
                    WHERE {where_sql}
                    AND CAST([Fecha creación cliente] AS DATE) >= CAST(? AS DATE)
                    AND CAST([Fecha creación cliente] AS DATE) <= CAST(? AS DATE)
                """
                params_nuevos = params + [fecha_inicio, fecha_fin]
                cursor.execute(query_clientes_nuevos, params_nuevos)
                cantidad_clientes_nuevos = cursor.fetchone()[0] or 0
                
                # Calcular porcentaje (evitar división por cero)
                if cantidad_clientes > 0:
                    porcentaje_clientes_nuevos = round((cantidad_clientes_nuevos / cantidad_clientes) * 100, 2)
                else:
                    porcentaje_clientes_nuevos = 0.0
                
                # ==========================================
                # 4. KPIs ADICIONALES
                # ==========================================
                query_adicionales = f"""
                    SELECT 
                        SUM([Monto facturado]) as venta_total,
                        AVG([Monto facturado]) as ticket_promedio,
                        COUNT(DISTINCT [Vendedor]) as total_vendedores,
                        COUNT(DISTINCT [Proyecto]) as total_proyectos
                    FROM {tabla}
                    WHERE {where_sql}
                """
                cursor.execute(query_adicionales, params)
                row = cursor.fetchone()
                
                venta_total = float(row[0]) if row[0] else 0.0
                ticket_promedio = float(row[1]) if row[1] else 0.0
                total_vendedores = row[2] or 0
                total_proyectos = row[3] or 0
                
                # ==========================================
                # 5. VENTA POR CANAL
                # ==========================================
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
                        'canal': row[0] or 'Sin canal',
                        'venta_total': float(row[1]) if row[1] else 0.0,
                        'transacciones': row[2],
                        'clientes': row[3],
                        'porcentaje': round((float(row[1]) / venta_total * 100), 2) if venta_total > 0 else 0.0
                    }
                    for row in cursor.fetchall()
                ]
                
                # ==========================================
                # 6. VENTA POR DEPARTAMENTO
                # ==========================================
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
                        'departamento': row[0] or 'Sin departamento',
                        'venta_total': float(row[1]) if row[1] else 0.0,
                        'transacciones': row[2],
                        'clientes': row[3],
                        'porcentaje': round((float(row[1]) / venta_total * 100), 2) if venta_total > 0 else 0.0
                    }
                    for row in cursor.fetchall()
                ]
                
                # ==========================================
                # RESPUESTA
                # ==========================================
                return jsonify({
                    'filtros_aplicados': {
                        'fecha_inicio': fecha_inicio,
                        'fecha_fin': fecha_fin,
                        'canal': args.get('canal'),
                        'departamento': args.get('departamento'),
                        'cliente': args.get('cliente'),
                        'vendedor': args.get('vendedor'),
                        'proyecto': args.get('proyecto')
                    },
                    'tabla_consultada': tabla,
                    'kpis_principales': {
                        'cantidad_clientes': cantidad_clientes,
                        'cantidad_transacciones': cantidad_transacciones,
                        'cantidad_clientes_nuevos': cantidad_clientes_nuevos,
                        'porcentaje_clientes_nuevos': porcentaje_clientes_nuevos,
                        'venta_total': round(venta_total, 2),
                        'ticket_promedio': round(ticket_promedio, 2),
                        'total_vendedores': total_vendedores,
                        'total_proyectos': total_proyectos
                    },
                    'venta_por_canal': venta_por_canal,
                    'venta_por_departamento': venta_por_departamento
                }), 200
                
        except Exception as e:
            import traceback
            return jsonify({
                'error': str(e),
                'traceback': traceback.format_exc()
            }), 500
    
    @bp.route('/top', methods=['GET'])
    def obtener_top():
        """
        Obtiene rankings (top N) de clientes, vendedores, productos o proyectos
        
        Parámetros:
            tipo (str): 'clientes', 'vendedores', 'productos', 'proyectos' (default: clientes)
            limit (int): Número de registros (default: 10)
            fecha_inicio, fecha_fin: Requeridos
            + filtros opcionales
        
        Returns:
            JSON con ranking ordenado por venta total
        """
        try:
            args = dict(request.args)
            tipo = args.get('tipo', 'clientes')
            limit = int(args.get('limit', 10))
            
            fecha_inicio = args.get('fecha_inicio')
            fecha_fin = args.get('fecha_fin')
            
            if not fecha_inicio or not fecha_fin:
                return jsonify({'error': 'Se requieren fecha_inicio y fecha_fin'}), 400
            
            tabla = seleccionar_tabla(fecha_inicio, fecha_fin)
            where_sql, params = construir_filtros(args)
            
            # Definir columna según tipo
            columnas = {
                'clientes': '[Cliente]',
                'vendedores': '[Vendedor]',
                'productos': '[SKU]',
                'proyectos': '[Proyecto]'
            }
            
            if tipo not in columnas:
                return jsonify({
                    'error': f'Tipo inválido: {tipo}. Use: clientes, vendedores, productos, proyectos'
                }), 400
            
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
                        'nombre': row[0] or f'Sin {tipo[:-1]}',
                        'venta_total': round(float(row[1]), 2) if row[1] else 0.0,
                        'transacciones': row[2],
                        'ticket_promedio': round(float(row[3]), 2) if row[3] else 0.0
                    }
                    for idx, row in enumerate(cursor.fetchall())
                ]
                
                return jsonify({
                    'tipo': tipo,
                    'periodo': {
                        'inicio': fecha_inicio,
                        'fin': fecha_fin
                    },
                    'top': top
                }), 200
                
        except Exception as e:
            import traceback
            return jsonify({
                'error': str(e),
                'traceback': traceback.format_exc()
            }), 500

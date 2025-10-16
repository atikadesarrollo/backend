"""
Módulo de KPIs para Facturación
Calcula métricas agregadas optimizadas para facturas
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
    return 'Fecha documento'

# Detectar columna de fecha
FECHA_COLUMN = detect_fecha_column()

def seleccionar_tabla(fecha_inicio, fecha_fin):
    """Selecciona tabla óptima según rango de fechas"""
    if not fecha_inicio or not fecha_fin:
        return 'DL_Facturacion_v_Completo'
    
    try:
        fi = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        ff = datetime.strptime(fecha_fin, '%Y-%m-%d')
        delta = (ff - fi).days
        
        if delta <= 30:
            return 'DL_Facturacion_v_Reciente'
        elif delta <= 90:
            return 'DL_Facturacion_v_Media'
        elif delta <= 365:
            return 'DL_Facturacion_v_Antiguo'
        else:
            return 'DL_Facturacion_v_Completo'
    except:
        return 'DL_Facturacion_v_Completo'

def construir_filtros(args):
    """Construye cláusula WHERE a partir de argumentos"""
    filtros = []
    params = []
    
    fecha_inicio = args.get('fecha_inicio')
    fecha_fin = args.get('fecha_fin')
    tipo_documento = args.get('tipo_documento')
    cliente = args.get('cliente')
    vendedor = args.get('vendedor')
    obra = args.get('obra')
    unidad_negocio = args.get('unidad_negocio')
    
    if fecha_inicio:
        filtros.append(f"CAST([{FECHA_COLUMN}] AS DATE) >= CAST(? AS DATE)")
        params.append(fecha_inicio)
    if fecha_fin:
        filtros.append(f"CAST([{FECHA_COLUMN}] AS DATE) <= CAST(? AS DATE)")
        params.append(fecha_fin)
    if tipo_documento:
        filtros.append("[Tipo documento] LIKE ?")
        params.append(f'%{tipo_documento}%')
    if cliente:
        filtros.append("[Razon social] LIKE ?")
        params.append(f'%{cliente}%')
    if vendedor:
        filtros.append("([Vendedor factura] LIKE ? OR [Vendedor oferta] LIKE ?)")
        params.append(f'%{vendedor}%')
        params.append(f'%{vendedor}%')
    if obra:
        filtros.append("[Nombre obra] LIKE ?")
        params.append(f'%{obra}%')
    if unidad_negocio:
        filtros.append("[Unidad de negocios] LIKE ?")
        params.append(f'%{unidad_negocio}%')
    
    where_sql = ' AND '.join(filtros) if filtros else '1=1'
    return where_sql, params

def registrar_endpoints_kpis(bp):
    """Registra los endpoints de KPIs en el blueprint"""
    
    @bp.route('/kpis', methods=['GET'])
    def obtener_kpis_facturacion():
        """
        Calcula KPIs agregados de facturación para el período seleccionado
        
        KPIs calculados:
        - Cantidad de clientes (únicos por RUT/Razón Social)
        - Cantidad de facturas/documentos
        - Porcentaje de clientes nuevos
        - Venta neta total
        - Ticket promedio
        - Distribución por tipo documento
        - Ventas por unidad de negocios
        
        Parámetros:
            fecha_inicio (str): Fecha inicio YYYY-MM-DD (requerido)
            fecha_fin (str): Fecha fin YYYY-MM-DD (requerido)
            tipo_documento (str): Filtro por tipo documento (opcional)
            cliente (str): Filtro por razón social (opcional)
            vendedor (str): Filtro por vendedor (opcional)
            obra (str): Filtro por nombre obra (opcional)
            unidad_negocio (str): Filtro por unidad de negocios (opcional)
        
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
                # 1. CANTIDAD DE CLIENTES (únicos por RUT)
                # ==========================================
                query_clientes = f"""
                    SELECT COUNT(DISTINCT [RUT]) as total_clientes
                    FROM {tabla}
                    WHERE {where_sql}
                """
                cursor.execute(query_clientes, params)
                cantidad_clientes = cursor.fetchone()[0] or 0
                
                # ==========================================
                # 2. CANTIDAD DE FACTURAS/DOCUMENTOS
                # ==========================================
                query_documentos = f"""
                    SELECT COUNT(*) as total_documentos
                    FROM {tabla}
                    WHERE {where_sql}
                """
                cursor.execute(query_documentos, params)
                cantidad_documentos = cursor.fetchone()[0] or 0
                
                # ==========================================
                # 3. PORCENTAJE CLIENTES NUEVOS
                # ==========================================
                # Nota: DL_Facturacion_v no tiene fecha de creación de cliente
                # Asumimos clientes nuevos como aquellos cuya primera factura está en el período
                query_clientes_nuevos = f"""
                    SELECT COUNT(DISTINCT c.[RUT]) as clientes_nuevos
                    FROM (
                        SELECT [RUT], MIN([{FECHA_COLUMN}]) as primera_factura
                        FROM {tabla}
                        GROUP BY [RUT]
                    ) c
                    WHERE CAST(c.primera_factura AS DATE) >= CAST(? AS DATE)
                    AND CAST(c.primera_factura AS DATE) <= CAST(? AS DATE)
                """
                params_nuevos = [fecha_inicio, fecha_fin]
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
                        SUM([Venta neta]) as venta_neta_total,
                        AVG([Venta neta]) as ticket_promedio,
                        COUNT(DISTINCT [Vendedor factura]) as total_vendedores,
                        COUNT(DISTINCT [Nombre obra]) as total_obras
                    FROM {tabla}
                    WHERE {where_sql}
                """
                cursor.execute(query_adicionales, params)
                row = cursor.fetchone()
                
                venta_neta_total = float(row[0]) if row[0] else 0.0
                ticket_promedio = float(row[1]) if row[1] else 0.0
                total_vendedores = row[2] or 0
                total_obras = row[3] or 0
                
                # ==========================================
                # 5. DISTRIBUCIÓN POR TIPO DOCUMENTO
                # ==========================================
                query_tipo_doc = f"""
                    SELECT 
                        [Tipo documento],
                        SUM([Venta neta]) as venta_total,
                        COUNT(*) as cantidad_documentos,
                        COUNT(DISTINCT [RUT]) as clientes
                    FROM {tabla}
                    WHERE {where_sql}
                    GROUP BY [Tipo documento]
                    ORDER BY SUM([Venta neta]) DESC
                """
                cursor.execute(query_tipo_doc, params)
                venta_por_tipo_documento = [
                    {
                        'tipo_documento': row[0] or 'Sin tipo',
                        'venta_total': float(row[1]) if row[1] else 0.0,
                        'cantidad_documentos': row[2],
                        'clientes': row[3],
                        'porcentaje': round((float(row[1]) / venta_neta_total * 100), 2) if venta_neta_total > 0 else 0.0
                    }
                    for row in cursor.fetchall()
                ]
                
                # ==========================================
                # 6. VENTA POR UNIDAD DE NEGOCIOS
                # ==========================================
                query_unidad = f"""
                    SELECT 
                        [Unidad de negocios],
                        SUM([Venta neta]) as venta_total,
                        COUNT(*) as documentos,
                        COUNT(DISTINCT [RUT]) as clientes
                    FROM {tabla}
                    WHERE {where_sql}
                    GROUP BY [Unidad de negocios]
                    ORDER BY SUM([Venta neta]) DESC
                """
                cursor.execute(query_unidad, params)
                venta_por_unidad_negocio = [
                    {
                        'unidad_negocio': row[0] or 'Sin unidad',
                        'venta_total': float(row[1]) if row[1] else 0.0,
                        'documentos': row[2],
                        'clientes': row[3],
                        'porcentaje': round((float(row[1]) / venta_neta_total * 100), 2) if venta_neta_total > 0 else 0.0
                    }
                    for row in cursor.fetchall()
                ]
                
                # ==========================================
                # 7. TOP OBRAS
                # ==========================================
                query_obras = f"""
                    SELECT TOP 10
                        [Nombre obra],
                        SUM([Venta neta]) as venta_total,
                        COUNT(*) as documentos
                    FROM {tabla}
                    WHERE {where_sql}
                    GROUP BY [Nombre obra]
                    ORDER BY SUM([Venta neta]) DESC
                """
                cursor.execute(query_obras, params)
                top_obras = [
                    {
                        'rank': idx + 1,
                        'obra': row[0] or 'Sin obra',
                        'venta_total': round(float(row[1]), 2) if row[1] else 0.0,
                        'documentos': row[2]
                    }
                    for idx, row in enumerate(cursor.fetchall())
                ]
                
                # ==========================================
                # RESPUESTA
                # ==========================================
                return jsonify({
                    'filtros_aplicados': {
                        'fecha_inicio': fecha_inicio,
                        'fecha_fin': fecha_fin,
                        'tipo_documento': args.get('tipo_documento'),
                        'cliente': args.get('cliente'),
                        'vendedor': args.get('vendedor'),
                        'obra': args.get('obra'),
                        'unidad_negocio': args.get('unidad_negocio')
                    },
                    'tabla_consultada': tabla,
                    'columna_fecha': FECHA_COLUMN,
                    'kpis_principales': {
                        'cantidad_clientes': cantidad_clientes,
                        'cantidad_documentos': cantidad_documentos,
                        'cantidad_clientes_nuevos': cantidad_clientes_nuevos,
                        'porcentaje_clientes_nuevos': porcentaje_clientes_nuevos,
                        'venta_neta_total': round(venta_neta_total, 2),
                        'ticket_promedio': round(ticket_promedio, 2),
                        'total_vendedores': total_vendedores,
                        'total_obras': total_obras
                    },
                    'venta_por_tipo_documento': venta_por_tipo_documento,
                    'venta_por_unidad_negocio': venta_por_unidad_negocio,
                    'top_obras': top_obras
                }), 200
                
        except Exception as e:
            import traceback
            return jsonify({
                'error': str(e),
                'traceback': traceback.format_exc()
            }), 500
    
    @bp.route('/top', methods=['GET'])
    def obtener_top_facturacion():
        """
        Obtiene rankings (top N) de clientes, vendedores, productos u obras
        
        Parámetros:
            tipo (str): 'clientes', 'vendedores', 'productos', 'obras' (default: clientes)
            limit (int): Número de registros (default: 10)
            fecha_inicio, fecha_fin: Requeridos
            + filtros opcionales
        
        Returns:
            JSON con ranking ordenado por venta neta total
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
                'clientes': '[Razon social]',
                'vendedores': '[Vendedor factura]',
                'productos': '[Codigo]',
                'obras': '[Nombre obra]'
            }
            
            if tipo not in columnas:
                return jsonify({
                    'error': f'Tipo inválido: {tipo}. Use: clientes, vendedores, productos, obras'
                }), 400
            
            columna = columnas[tipo]
            
            with get_connection() as conn:
                cursor = conn.cursor()
                
                # Query optimizado para top N
                query = f"""
                    SELECT TOP {limit}
                        {columna} as nombre,
                        SUM([Venta neta]) as venta_total,
                        COUNT(*) as documentos,
                        AVG([Venta neta]) as ticket_promedio
                    FROM {tabla}
                    WHERE {where_sql}
                    GROUP BY {columna}
                    ORDER BY SUM([Venta neta]) DESC
                """
                cursor.execute(query, params)
                
                top = [
                    {
                        'rank': idx + 1,
                        'nombre': row[0] or f'Sin {tipo[:-1]}',
                        'venta_total': round(float(row[1]), 2) if row[1] else 0.0,
                        'documentos': row[2],
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

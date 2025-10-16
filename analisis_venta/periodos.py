from flask import Blueprint, jsonify, request
import pyodbc
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


analisis_venta_bp = Blueprint('analisis_venta', __name__)

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

PERIODOS = [
    ('DL_Analisis_Venta_v_Reciente', 'Reciente'),
    ('DL_Analisis_Venta_v_Media', 'Media'),
    ('DL_Analisis_Venta_v_Antiguo', 'Antiguo'),
    ('DL_Analisis_Venta_v_Completo', 'Completo')
]

@analisis_venta_bp.route('/periodos', methods=['GET'])
def listar_periodos():
    resultados = []
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            for tabla, nombre in PERIODOS:
                try:
                    cursor.execute(f"SELECT MIN([Fecha de oferta]), MAX([Fecha de oferta]), COUNT(*) FROM {tabla}")
                    row = cursor.fetchone()
                    resultados.append({
                        'periodo': nombre,
                        'tabla': tabla,
                        'fecha_min': str(row[0]) if row[0] else None,
                        'fecha_max': str(row[1]) if row[1] else None,
                        'total_registros': row[2]
                    })
                except Exception as e:
                    resultados.append({
                        'periodo': nombre,
                        'tabla': tabla,
                        'error': str(e)
                    })
        return jsonify({'periodos': resultados}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Endpoint de consulta con filtros tipo ORM
@analisis_venta_bp.route('/query', methods=['GET'])
def query_analisis_venta():
    # Filtros recibidos por parámetros
    args = dict(request.args)
    fecha_inicio = args.get('fecha_inicio')
    fecha_fin = args.get('fecha_fin')
    proyecto = args.get('proyecto')
    cliente = args.get('cliente')
    vendedor = args.get('vendedor')
    sku = args.get('sku')
    departamento = args.get('departamento')
    canal = args.get('canal')
    monto_min = args.get('monto_min')
    monto_max = args.get('monto_max')
    descripcion = args.get('descripcion')
    rubro = args.get('rubro')
    familia = args.get('familia')
    marca = args.get('marca')
    periodo = args.get('periodo')  # Puede ser 'Reciente', 'Media', 'Antiguo', 'Fuente'
    # Validar campo order_by
    order_by = args.get('order_by')
    if not order_by or not isinstance(order_by, str) or order_by.strip() == '':
        order_by = '[Fecha de oferta] DESC'
    else:
        # Si el usuario ingresa solo el nombre, agregar corchetes si hay espacios
        col = order_by.replace(' DESC', '').replace(' ASC', '').strip()
        if ' ' in col and not col.startswith('['):
            # Si tiene espacios y no tiene corchetes, agregar corchetes
            order_by = f'[{col}] DESC' if 'DESC' in order_by else f'[{col}] ASC'
    try:
        limit = int(args.get('limit', 100))
        if limit < 1:
            limit = 1
    except:
        limit = 100
    try:
        offset = int(args.get('offset', 0))
        if offset < 0:
            offset = 0
    except:
        offset = 0

    # Selección de tabla según rango de fechas
    tabla = 'DL_Analisis_Venta_v_Completo'
    if fecha_inicio and fecha_fin:
        from datetime import datetime
        try:
            fi = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            ff = datetime.strptime(fecha_fin, '%Y-%m-%d')
            delta = (ff - fi).days
            if delta <= 30:
                tabla = 'DL_Analisis_Venta_v_Reciente'
            elif delta <= 90:
                tabla = 'DL_Analisis_Venta_v_Media'
            elif delta <= 365:
                tabla = 'DL_Analisis_Venta_v_Antiguo'
            else:
                tabla = 'DL_Analisis_Venta_v_Completo'
        except:
            tabla = 'DL_Analisis_Venta_v_Completo'
    elif periodo:
        if periodo == 'Reciente':
            tabla = 'DL_Analisis_Venta_v_Reciente'
        elif periodo == 'Media':
            tabla = 'DL_Analisis_Venta_v_Media'
        elif periodo == 'Antiguo':
            tabla = 'DL_Analisis_Venta_v_Antiguo'
        elif periodo == 'Completo':
            tabla = 'DL_Analisis_Venta_v_Completo'
        else:
            tabla = 'DL_Analisis_Venta_v_Completo'

    filtros = []
    params = []
    if fecha_inicio:
        filtros.append("CAST([Fecha de oferta] AS DATE) >= CAST(? AS DATE)")
        params.append(fecha_inicio)
    if fecha_fin:
        filtros.append("CAST([Fecha de oferta] AS DATE) <= CAST(? AS DATE)")
        params.append(fecha_fin)
    if proyecto:
        filtros.append("[Proyecto] LIKE ?")
        params.append(f'%{proyecto}%')
    if cliente:
        filtros.append("[Cliente] LIKE ?")
        params.append(f'%{cliente}%')
    if vendedor:
        filtros.append("[Vendedor] LIKE ?")
        params.append(f'%{vendedor}%')
    if sku:
        filtros.append("[SKU] LIKE ?")
        params.append(f'%{sku}%')
    if departamento:
        filtros.append("[Departamento] LIKE ?")
        params.append(f'%{departamento}%')
    if canal:
        filtros.append("[Canal] LIKE ?")
        params.append(f'%{canal}%')
    if monto_min:
        filtros.append("[Monto facturado] >= ?")
        params.append(monto_min)
    if monto_max:
        filtros.append("[Monto facturado] <= ?")
        params.append(monto_max)
    if descripcion:
        filtros.append("[Descipción] LIKE ?")
        params.append(f'%{descripcion}%')
    if rubro:
        filtros.append("[Rubro] LIKE ?")
        params.append(f'%{rubro}%')
    if familia:
        filtros.append("[Familia] LIKE ?")
        params.append(f'%{familia}%')
    if marca:
        filtros.append("[Marca] LIKE ?")
        params.append(f'%{marca}%')

    where_sql = ' AND '.join(filtros) if filtros else '1=1'
    
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            
            # Primero obtener el total de registros que coinciden con los filtros
            count_sql = f"SELECT COUNT(*) FROM {tabla} WHERE {where_sql}"
            cursor.execute(count_sql, params)
            total_registros = cursor.fetchone()[0]
            
            # Luego obtener los datos paginados
            if order_by:
                query_sql = f"SELECT * FROM {tabla} WHERE {where_sql} ORDER BY {order_by} OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"
            else:
                query_sql = f"SELECT TOP {limit} * FROM {tabla} WHERE {where_sql}"
            
            cursor.execute(query_sql, params)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            data = [dict(zip(columns, row)) for row in rows]
            
            return jsonify({'tabla': tabla, 'total': total_registros, 'data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'tabla': tabla}), 500

# Registrar endpoints de KPIs
from .kpis import registrar_endpoints_kpis
registrar_endpoints_kpis(analisis_venta_bp)
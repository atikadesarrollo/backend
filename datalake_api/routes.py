import pyodbc
from flask import Blueprint, Flask, jsonify, request
import os
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
datalake_bp = Blueprint('datalake_api', __name__)

# Configurar logging
logger = logging.getLogger(__name__)

def get_connection_string():
    """Obtener string de conexión según el entorno"""
    server = os.getenv('DATALAKE_SERVER', 'DATALAKE')
    database = os.getenv('DATALAKE_DATABASE', 'DATALAKE')
    username = os.getenv('DATALAKE_USERNAME')
    password = os.getenv('DATALAKE_PASSWORD')
    port = os.getenv('DATALAKE_PORT', '1433')
    
    # Si hay credenciales específicas, usar autenticación SQL
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
        logger.info(f"Usando autenticación SQL para conectar a {server}")
    else:
        # Usar autenticación Windows (solo para conexiones locales)
        connection_string = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'Trusted_Connection=yes;'
        )
        logger.info(f"Usando autenticación Windows para conectar a {server}")
    
    return connection_string

# Obtener string de conexión
connection_string = get_connection_string()

@datalake_bp.route('/connect_db', methods=['GET'])
def connect_db():
    try:
        current_connection_string = get_connection_string()
        logger.info(f"Intentando conectar con: {current_connection_string.replace(os.getenv('DATALAKE_PASSWORD', ''), '***')}")
        
        with pyodbc.connect(current_connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION, @@SERVERNAME, DB_NAME()")
            row = cursor.fetchone()
            
            response = {
                "message": "Conexión exitosa",
                "server_version": row[0],
                "server_name": row[1],
                "database_name": row[2],
                "connection_type": "SQL Authentication" if os.getenv('DATALAKE_USERNAME') else "Windows Authentication"
            }
            
            logger.info(f"Conexión exitosa a {row[1]}")
            return jsonify(response), 200
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error de conexión: {error_msg}")
        
        # Sugerencias basadas en el tipo de error
        suggestions = []
        if "Login failed" in error_msg:
            suggestions.append("Verificar credenciales de usuario y contraseña")
        elif "server was not found" in error_msg:
            suggestions.append("Verificar nombre del servidor y puerto")
        elif "SSL connection is required" in error_msg:
            suggestions.append("Verificar configuración SSL/TLS")
        elif "timeout" in error_msg.lower():
            suggestions.append("Verificar conectividad de red y firewall")
        
        return jsonify({
            "message": "Error al conectar a la base de datos",
            "error": error_msg,
            "suggestions": suggestions,
            "connection_type": "SQL Authentication" if os.getenv('DATALAKE_USERNAME') else "Windows Authentication"
        }), 500

@datalake_bp.route('/test_connection', methods=['GET'])
def test_connection():
    """Endpoint para probar diferentes configuraciones de conexión"""
    results = []
    
    # Configuraciones a probar
    test_configs = [
        {
            "name": "Conexión local (Windows Auth)",
            "connection_string": f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=DATALAKE;DATABASE=DATALAKE;Trusted_Connection=yes;'
        },
        {
            "name": "Conexión remota (SQL Auth)",
            "connection_string": get_connection_string()
        }
    ]
    
    for config in test_configs:
        try:
            with pyodbc.connect(config["connection_string"]) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                results.append({
                    "config": config["name"],
                    "status": "SUCCESS",
                    "message": "Conexión exitosa"
                })
        except Exception as e:
            results.append({
                "config": config["name"],
                "status": "FAILED",
                "error": str(e)
            })
    
    return jsonify({"connection_tests": results}), 200

@datalake_bp.route('/get_models', methods=['GET'])
def get_models():
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_CATALOG = ?", database)
            rows = cursor.fetchall()
            models = [row.TABLE_NAME for row in rows]
            return jsonify({"models": models}), 200
    except Exception as e:
        return jsonify({"message": "Error al obtener los modelos", "error": str(e)}), 500


@datalake_bp.route('/sales_order', methods=['GET'])
def get_analisis_venta():
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            query = """
                SELECT * FROM DL_Analisis_Venta_v 
                WHERE [Fecha de oferta] >= DATEADD(day, -5, GETDATE()) 
                ORDER BY [Fecha de oferta] DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            data = [dict(zip(columns, row)) for row in rows]
            return jsonify({"data": data}), 200
    except Exception as e:
        return jsonify({"message": "Error al obtener los datos de la vista", "error": str(e)}), 500



@datalake_bp.route('/sales_order/<start_date>&<end_date>', methods=['GET'])
def get_analisis_venta_fechas(start_date, end_date):
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                [Referencia de pedido] as 'Referencia_de_pedido'
                ,[Proyecto] 
                ,[Fecha de oferta] as 'Fecha_de_oferta'
                ,[Cotización final] as 'Cotizacion_final'
                ,[Venta anticipada] as 'Venta_anticipada'
                ,[DocNum oferta] as 'DocNum_oferta'
                ,[DocNum OV] as 'DocNum_OV'
                ,[Tipo despacho] as 'Tipo_despacho'
                ,[Comuna]
                ,[RUT Cliente] as 'RUT_Cliente'
                ,[Cliente]
                ,[Fecha creación cliente] as 'Fecha_creacion_cliente' 
                -- ,[Categoria cliente] as ''
                ,[Canal]
                ,[Departamento]
                ,[Vendedor]
                ,[Email vendedor] as 'Correo_vendedor'
                ,[CDP Producto] as 'Cdp_producto'
                ,[Familia]
                ,[SKU]
                ,[Descipción] as 'Descripcion'
                ,[Unidad de medida] as 'Unidad_Medida'
                ,[Inventariable]
                ,[Rubro]
                ,[Formato]
                ,[Marca]
                ,[Serie]
                ,[Look]
                ,[Ancho]
                ,[Altura]
                ,[Peso]
                ,[CDP Linea] as 'Cdp_linea'
                ,[Geografica]
                ,[Unidad de negocios] as 'Unidad_Negocio'
                ,[Area]
                ,[Cant. producto] as 'Cant_producto'
                ,[Cantidad entregada] as 'Cantidad_entregada'
                ,[Cantidad facturada] as 'Cantidad_facturada'
                ,[Monto facturado] as 'Monto_facturado'
                ,[Cantidad anulada] as 'Cantidad_anulada'
                ,[Monto anulado] as 'Monto_anulado'
                ,[Moneda origen] as 'Moneda_origen'
                ,[Tasa de cambio] as 'Tasa_de_cambio'
                ,[RPT Precio base] as 'RPT_Precio_base'
                ,[RPT Precio unitario] as 'RPT_Precio_unitario'
                ,[Descuento original] as 'Descuento_original'
                ,[Descuento %] as 'Descuento_porcentaje'
                ,[Total descuento + promoción] as 'Total_descuento_promocion'
                ,[RPT Descuento] as  'RPT_Descuento'
                ,[RPT Flete unitario] as 'RPT_Flete_unitario' 
                ,[RPT Flete Unitario MO] as 'RPT_Flete_Unitario_MO' 
                ,[RPT Substotal] as 'RPT_Substotal'
                ,[Total]
                ,[U_SEI_CotFin] 
                ,[Estado]
                ,[EstadoOdoo]
                ,[Tasa de cambio USD] as 'Tasa_de_cambio_USD' 
                ,[Nombre Obra] as 'Nombre_obra'
                ,[Especificador Arquitectura] as 'Especificador_arquitectura' 
                ,[Email Esp Arquitectura] as 'Email_esp_Ar'
                ,[Especificador Inmobiliario] as 'Especificador_inmobiliario' 
                ,[Email Esp Inmobiliario] as 'Email_esp_In'
                FROM DL_Analisis_Venta_v 
                WHERE CAST([Fecha de oferta] AS DATE) BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
                ORDER BY [Fecha de oferta] DESC
            """
            cursor.execute(query, start_date, end_date)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            data = [dict(zip(columns, row)) for row in rows]
            return jsonify({"data": data}), 200
    except Exception as e:
        return jsonify({"message": "Error al obtener los datos de la vista", "error": str(e)}), 500
    
@datalake_bp.route('/sales_order/prueba/<start_date>&<end_date>', methods=['GET'])
def get_analisis_venta_fechas(start_date, end_date):
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                [Referencia de pedido] as 'Referencia_de_pedido'
                ,[Proyecto] 
                ,[Fecha de oferta] as 'Fecha_de_oferta'
                ,[Cotización final] as 'Cotizacion_final'
                ,[Venta anticipada] as 'Venta_anticipada'
                ,[DocNum oferta] as 'DocNum_oferta'
                ,[DocNum OV] as 'DocNum_OV'
                ,[Tipo despacho] as 'Tipo_despacho'
                ,[Comuna]
                ,[RUT Cliente] as 'RUT_Cliente'
                ,[Cliente]
                ,[Fecha creación cliente] as 'Fecha_creacion_cliente' 
                -- ,[Categoria cliente] as ''
                ,[Canal]
                ,[Departamento]
                ,[Vendedor]
                ,[Email vendedor] as 'Correo_vendedor'
                ,[CDP Producto] as 'Cdp_producto'
                ,[Familia]
                ,[SKU]
                ,[Descipción] as 'Descripcion'
                ,[Unidad de medida] as 'Unidad_Medida'
                ,[Inventariable]
                ,[Rubro]
                ,[Formato]
                ,[Marca]
                ,[Serie]
                ,[Look]
                ,[Ancho]
                ,[Altura]
                ,[Peso]
                ,[CDP Linea] as 'Cdp_linea'
                ,[Geografica]
                ,[Unidad de negocios] as 'Unidad_Negocio'
                ,[Area]
                ,[Cant. producto] as 'Cant_producto'
                ,[Cantidad entregada] as 'Cantidad_entregada'
                ,[Cantidad facturada] as 'Cantidad_facturada'
                ,[Monto facturado] as 'Monto_facturado'
                ,[Cantidad anulada] as 'Cantidad_anulada'
                ,[Monto anulado] as 'Monto_anulado'
                ,[Moneda origen] as 'Moneda_origen'
                ,[Tasa de cambio] as 'Tasa_de_cambio'
                ,[RPT Precio base] as 'RPT_Precio_base'
                ,[RPT Precio unitario] as 'RPT_Precio_unitario'
                ,[Descuento original] as 'Descuento_original'
                ,[Descuento %] as 'Descuento_porcentaje'
                ,[Total descuento + promoción] as 'Total_descuento_promocion'
                ,[RPT Descuento] as  'RPT_Descuento'
                ,[RPT Flete unitario] as 'RPT_Flete_unitario' 
                ,[RPT Flete Unitario MO] as 'RPT_Flete_Unitario_MO' 
                ,[RPT Substotal] as 'RPT_Substotal'
                ,[Total]
                ,[U_SEI_CotFin] 
                ,[Estado]
                ,[EstadoOdoo]
                ,[Tasa de cambio USD] as 'Tasa_de_cambio_USD' 
                ,[Nombre Obra] as 'Nombre_obra'
                ,[Especificador Arquitectura] as 'Especificador_arquitectura' 
                ,[Email Esp Arquitectura] as 'Email_esp_Ar'
                ,[Especificador Inmobiliario] as 'Especificador_inmobiliario' 
                ,[Email Esp Inmobiliario] as 'Email_esp_In'
                FROM TablaPruebaReporteVentas 
                WHERE CAST([Fecha de oferta] AS DATE) BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
                ORDER BY [Fecha de oferta] DESC
            """
            cursor.execute(query, start_date, end_date)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            data = [dict(zip(columns, row)) for row in rows]
            return jsonify({"data": data}), 200
    except Exception as e:
        return jsonify({"message": "Error al obtener los datos de la vista", "error": str(e)}), 500


@datalake_bp.route('/revision', methods=['GET'])
def get_ultimas_cargas():
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX([Fecha de oferta]) AS FechaUltimaOferta FROM [DATALAKE].[dbo].[DL_Analisis_Venta_v]")
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            data = [dict(zip(columns, row)) for row in rows]
            return jsonify({"data": data}), 200
    except Exception as e:
        return jsonify({"message": "Error al obtener los datos de la tabla", "error": str(e)}), 500

@datalake_bp.route('/date_last_bill', methods=['GET'])
def get_ultima_factura():
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX([Fecha documento]) AS FechaUltimaFactura FROM [DATALAKE].[dbo].[DL_Facturacion_v]")
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            data = [dict(zip(columns, row)) for row in rows]
            return jsonify({"data": data}), 200
    except Exception as e:
        return jsonify({"message": "Error al obtener los datos de la tabla", "error": str(e)}), 500

@datalake_bp.route('/fields', methods=['GET'])
def get_fields():
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'DL_Analisis_Venta_v'")
            rows = cursor.fetchall()
            fields = [row.COLUMN_NAME for row in rows]
            return jsonify({"fields": fields}), 200
    except Exception as e:
        return jsonify({"message": "Error al obtener los campos técnicos", "error": str(e)}), 500


@datalake_bp.route('/facturacion/<start_date>&<end_date>', methods=['GET'])
def get_facturacion_fechas(start_date, end_date):
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    [Tipo documento] as 'Tipo_documento'
                    ,[Numero de documento] as 'Numero_documento'
                    ,[Orden de compra] as 'Orden_compra'
                    ,[Indicador] 
                    ,[Folio SII] as 'Folio_SII'
                    ,[Fecha documento] as 'Fecha_documento'
                    ,[RUT]
                    ,[Razon social] as 'Razon_social'
                    ,[Categoria cliente] as 'Categoria_cliente'
                    ,CASE [Grupo de ventas] 
                        WHEN 'Venta Empresa' THEN 'Venta Empresas'
                        WHEN 'Planta Marmol' THEN 'Planta Mármol'
                        WHEN 'Showroom Pto. Varas' THEN 'Showroom Puerto Varas'
                        WHEN 'Showroom Viña' THEN 'Showroom Viña del Mar'
                        WHEN 'Showroom Concepcion' THEN 'Showroom Concepción'
                        ELSE [Grupo de ventas] 
                        END AS 'Grupo_de_Ventas'
                    ,[Tipo de despacho] as 'Tipo_despacho'
                    ,[Comuna]
                    ,[Codigo]
                    ,[Descripcion]
                    ,[Unidad de medida] as 'Unidad_medida'
                    ,[Inventariable]
                    ,[Rubro]
                    ,[Familia]
                    ,[Formato]
                    ,[Marca]
                    ,[Serie]
                    ,[Look]
                    ,[Moneda]
                    ,[CDP Producto] as 'Cdp_producto'
                    ,[CDP Linea] as 'Cdp_linea'
                    ,[Ancho]
                    ,[Altura]
                    ,[Peso]
                    ,[Moneda]
                    ,[Email vendedor factura] as 'Email_vendedor_factura'
                    ,[Email vendedor oferta] as 'Email_vendedor_oferta'
                    ,CASE 
                        WHEN [Tasa de cambio] IS NULL THEN 0
                        ELSE [Tasa de cambio]
                        END AS 'Tasa_cambio'
                    ,[Cantidad]
                    ,[Precio base] as 'Precio_base'
                    ,[Precio unitario] as 'Precio_unitario'
                    ,[Precio unitario descuentos aplicados] as 'Precio_unitario_descuento'
                    ,[Porcentaje descuentos] as 'Porcentaje_descuento'
                    ,[Porcentaje adicional oferta] as 'Porcentaje_adicional'
                    ,[Flete unitario] as 'Flete_unitario'
                    ,[Venta neta] as 'Venta_neta'
                    ,[Vendedor factura] as 'Vendedor_factura'
                    ,[Numero oferta] as 'Numero_oferta'
                    ,[Vendedor oferta] as 'Vendedor_oferta'
                    ,[Arquitecto] 
                    ,[Inmobiliaria]
                    ,[Arquitecto 2] as 'Arquitecto_2'
                    ,[Geografica]
                    ,[Unidad de negocios] as 'Unidad_negocio'
                    ,[Area]
                    ,[Nombre obra] as 'Nombre_obra'
                    ,[Especificador Arquitectura] as 'Especificador_arquitectura'
                    ,[Email Esp Arquitectura] as 'Email_esp_Ar'
                    ,[Especificador Inmobiliario] as 'Especificador_inmobiliario'
                    ,[Email Esp Inmobiliario] as 'Email_esp_In'
                FROM DL_Facturacion_v 
                WHERE CAST([Fecha documento] AS DATE) BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
                ORDER BY [Fecha documento] DESC;
            """
            cursor.execute(query, start_date, end_date)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            data = [dict(zip(columns, row)) for row in rows]
            return jsonify({"data": data}), 200
    except Exception as e:
        return jsonify({"message": "Error al obtener los datos de la vista", "error": str(e)}), 500
    
@datalake_bp.route('/facturacion/prueba/<start_date>&<end_date>', methods=['GET'])
def get_facturacion_fechas(start_date, end_date):
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    [Tipo documento] as 'Tipo_documento'
                    ,[Numero de documento] as 'Numero_documento'
                    ,[Orden de compra] as 'Orden_compra'
                    ,[Indicador] 
                    ,[Folio SII] as 'Folio_SII'
                    ,[Fecha documento] as 'Fecha_documento'
                    ,[RUT]
                    ,[Razon social] as 'Razon_social'
                    ,[Categoria cliente] as 'Categoria_cliente'
                    ,CASE [Grupo de ventas] 
                        WHEN 'Venta Empresa' THEN 'Venta Empresas'
                        WHEN 'Planta Marmol' THEN 'Planta Mármol'
                        WHEN 'Showroom Pto. Varas' THEN 'Showroom Puerto Varas'
                        WHEN 'Showroom Viña' THEN 'Showroom Viña del Mar'
                        WHEN 'Showroom Concepcion' THEN 'Showroom Concepción'
                        ELSE [Grupo de ventas] 
                        END AS 'Grupo_de_Ventas'
                    ,[Tipo de despacho] as 'Tipo_despacho'
                    ,[Comuna]
                    ,[Codigo]
                    ,[Descripcion]
                    ,[Unidad de medida] as 'Unidad_medida'
                    ,[Inventariable]
                    ,[Rubro]
                    ,[Familia]
                    ,[Formato]
                    ,[Marca]
                    ,[Serie]
                    ,[Look]
                    ,[Moneda]
                    ,[CDP Producto] as 'Cdp_producto'
                    ,[CDP Linea] as 'Cdp_linea'
                    ,[Ancho]
                    ,[Altura]
                    ,[Peso]
                    ,[Moneda]
                    ,[Email vendedor factura] as 'Email_vendedor_factura'
                    ,[Email vendedor oferta] as 'Email_vendedor_oferta'
                    ,CASE 
                        WHEN [Tasa de cambio] IS NULL THEN 0
                        ELSE [Tasa de cambio]
                        END AS 'Tasa_cambio'
                    ,[Cantidad]
                    ,[Precio base] as 'Precio_base'
                    ,[Precio unitario] as 'Precio_unitario'
                    ,[Precio unitario descuentos aplicados] as 'Precio_unitario_descuento'
                    ,[Porcentaje descuentos] as 'Porcentaje_descuento'
                    ,[Porcentaje adicional oferta] as 'Porcentaje_adicional'
                    ,[Flete unitario] as 'Flete_unitario'
                    ,[Venta neta] as 'Venta_neta'
                    ,[Vendedor factura] as 'Vendedor_factura'
                    ,[Numero oferta] as 'Numero_oferta'
                    ,[Vendedor oferta] as 'Vendedor_oferta'
                    ,[Arquitecto] 
                    ,[Inmobiliaria]
                    ,[Arquitecto 2] as 'Arquitecto_2'
                    ,[Geografica]
                    ,[Unidad de negocios] as 'Unidad_negocio'
                    ,[Area]
                    ,[Nombre obra] as 'Nombre_obra'
                    ,[Especificador Arquitectura] as 'Especificador_arquitectura'
                    ,[Email Esp Arquitectura] as 'Email_esp_Ar'
                    ,[Especificador Inmobiliario] as 'Especificador_inmobiliario'
                    ,[Email Esp Inmobiliario] as 'Email_esp_In'
                FROM TablaPruebaReporteFacturacion 
                WHERE CAST([Fecha documento] AS DATE) BETWEEN CAST(? AS DATE) AND CAST(? AS DATE)
                ORDER BY [Fecha documento] DESC;
            """
            cursor.execute(query, start_date, end_date)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            data = [dict(zip(columns, row)) for row in rows]
            return jsonify({"data": data}), 200
    except Exception as e:
        return jsonify({"message": "Error al obtener los datos de la vista", "error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
import pyodbc
from flask import Blueprint, Flask, jsonify, request

app = Flask(__name__)
datalake_bp = Blueprint('datalake_api', __name__)

# Configuración de la conexión a la base de datos datalake bluehosting
server = 'DATALAKE'
database = 'DATALAKE'
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

@datalake_bp.route('/connect_db', methods=['GET'])
def connect_db():
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            row = cursor.fetchone()
            return jsonify({"message": "Conexión exitosa", "version": row[0]}), 200
    except Exception as e:
        return jsonify({"message": "Error al conectar a la base de datos", "error": str(e)}), 500

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


if __name__ == '__main__':
    app.run(debug=True)
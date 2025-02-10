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
            cursor.execute("SELECT * FROM DL_Analisis_Venta_v WHERE YEAR([Fecha de oferta]) = 2025 ORDER BY [Fecha de oferta] DESC")
            # Busca desde el modelo de Analisis de Venta los registros del año 2025 y los ordena en orden descendiente.
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            data = [dict(zip(columns, row)) for row in rows]
            return jsonify({"data": data}), 200
    except Exception as e:
        return jsonify({"message": "Error al obtener los datos de la vista", "error": str(e)}), 500


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


if __name__ == '__main__':
    app.run(debug=True)
import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
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

def get_table_columns(cursor, table_name):
    query = f"""
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
    """
    cursor.execute(query)
    columns = cursor.fetchall()
    col_defs = []
    col_names = []
    for col in columns:
        name, dtype, length = col
        col_names.append(f'[{name}]')
        if dtype in ['varchar', 'nvarchar', 'char', 'nchar'] and length:
            col_defs.append(f'[{name}] {dtype}({length})')
        elif dtype in ['decimal', 'numeric']:
            # Obtener precisión y escala
            cursor.execute(f"SELECT NUMERIC_PRECISION, NUMERIC_SCALE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}' AND COLUMN_NAME = '{name}'")
            prec_scale = cursor.fetchone()
            if prec_scale:
                prec, scale = prec_scale
                col_defs.append(f'[{name}] {dtype}({prec},{scale})')
            else:
                col_defs.append(f'[{name}] {dtype}')
        else:
            col_defs.append(f'[{name}] {dtype}')
    return col_defs, col_names

def create_table_and_insert(cursor, table_name, filter_sql):
    temp_table = f'{table_name}_tmp'
    print(f"Creando tabla temporal: {temp_table}")
    # Obtener columnas y tipos
    col_defs, col_names = get_table_columns(cursor, 'DL_Analisis_Venta_v')
    # Borrar tabla temporal si existe
    cursor.execute(f"IF OBJECT_ID('{temp_table}', 'U') IS NOT NULL DROP TABLE {temp_table}")
    # Crear tabla temporal
    create_sql = f"CREATE TABLE {temp_table} (" + ', '.join(col_defs) + ")"
    cursor.execute(create_sql)
    print(f"Insertando datos en {temp_table}")
    insert_sql = f"INSERT INTO {temp_table} (" + ', '.join(col_names) + ") SELECT " + ', '.join(col_names) + f" FROM DL_Analisis_Venta_v WHERE {filter_sql}"
    cursor.execute(insert_sql)
    # Borrar tabla final si existe
    cursor.execute(f"IF OBJECT_ID('{table_name}', 'U') IS NOT NULL DROP TABLE {table_name}")
    # Renombrar tabla temporal
    cursor.execute(f"EXEC sp_rename '{temp_table}', '{table_name}'")
    print(f"Tabla {table_name} creada y datos insertados.")

if __name__ == "__main__":
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            print(f"Conectado a la base de datos {database} en el servidor {server}")
            # Reciente: últimos 30 días
            create_table_and_insert(cursor, 'DL_Analisis_Venta_v_Reciente', "[Fecha de oferta] >= DATEADD(day, -30, GETDATE())")
            # Media: últimos 90 días
            create_table_and_insert(cursor, 'DL_Analisis_Venta_v_Media', "[Fecha de oferta] >= DATEADD(day, -90, GETDATE())")
            # Antiguo: últimos 365 días
            create_table_and_insert(cursor, 'DL_Analisis_Venta_v_Antiguo', "[Fecha de oferta] >= DATEADD(day, -365, GETDATE())")
            print("Proceso finalizado correctamente.")
    except Exception as e:
        print(f"Error en el proceso: {e}")

import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime
import time

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

def create_table_and_insert(cursor, table_name, filter_sql, fecha_col=None):
    temp_table = f'{table_name}_tmp'
    print(f"Creando tabla temporal: {temp_table}")
    col_defs, col_names = get_table_columns(cursor, 'DL_Facturacion_v')
    cursor.execute(f"IF OBJECT_ID('{temp_table}', 'U') IS NOT NULL DROP TABLE {temp_table}")
    create_sql = f"CREATE TABLE {temp_table} (" + ', '.join(col_defs) + ")"
    cursor.execute(create_sql)
    print(f"Insertando datos en {temp_table}")
    insert_sql = f"INSERT INTO {temp_table} (" + ', '.join(col_names) + ") SELECT " + ', '.join(col_names) + f" FROM DL_Facturacion_v WHERE {filter_sql}"
    cursor.execute(insert_sql)
    cursor.execute(f"IF OBJECT_ID('{table_name}', 'U') IS NOT NULL DROP TABLE {table_name}")
    cursor.execute(f"EXEC sp_rename '{temp_table}', '{table_name}'")
    print(f"Tabla {table_name} creada y datos insertados.")

if __name__ == "__main__":
    start_time = time.time()
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            print(f"Conectado a la base de datos {database} en el servidor {server}")
            
            # Detectar columna de fecha automáticamente
            print("Detectando columna de fecha...")
            cursor.execute("SELECT TOP 0 * FROM DL_Facturacion_v")
            columnas = [col[0] for col in cursor.description]
            
            # Buscar columna de fecha
            fecha_col = None
            for col in columnas:
                if 'fecha' in col.lower():
                    fecha_col = col
                    print(f"Columna de fecha detectada: [{fecha_col}]")
                    break
            
            if not fecha_col:
                print("ERROR: No se encontró ninguna columna con 'fecha' en su nombre.")
                print("Columnas disponibles:")
                for col in columnas:
                    print(f"  - [{col}]")
                exit(1)
            
            # Guardar columna de fecha en archivo para uso del API
            config_file = os.path.join(os.path.dirname(__file__), '..', 'facturacion', 'fecha_column.txt')
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, 'w') as f:
                f.write(fecha_col)
            print(f"Columna de fecha guardada en: {config_file}")
            
            # Completo: copia completa de la vista
            print("Creando copia completa de DL_Facturacion_v...")
            create_table_and_insert(cursor, 'DL_Facturacion_v_Completo', "1=1", fecha_col)
            
            # Reciente: últimos 30 días
            create_table_and_insert(cursor, 'DL_Facturacion_v_Reciente', f"[{fecha_col}] >= DATEADD(day, -30, GETDATE())", fecha_col)
            # Media: últimos 90 días
            create_table_and_insert(cursor, 'DL_Facturacion_v_Media', f"[{fecha_col}] >= DATEADD(day, -90, GETDATE())", fecha_col)
            # Antiguo: últimos 365 días
            create_table_and_insert(cursor, 'DL_Facturacion_v_Antiguo', f"[{fecha_col}] >= DATEADD(day, -365, GETDATE())", fecha_col)

            tablas = [
                'DL_Facturacion_v_Completo',
                'DL_Facturacion_v_Reciente',
                'DL_Facturacion_v_Media',
                'DL_Facturacion_v_Antiguo'
            ]
            print("\nTamaño de las tablas generadas:")
            for tabla in tablas:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                cursor.execute(f"EXEC sp_spaceused '{tabla}'")
                space = cursor.fetchone()
                print(f"{tabla}: {count} filas, {space[1]} KB")

            end_time = time.time()
            elapsed = end_time - start_time
            print(f"\nTiempo total de ejecución: {elapsed:.2f} segundos.")
            print("Proceso finalizado correctamente.")
    except Exception as e:
        print(f"Error en el proceso: {e}")

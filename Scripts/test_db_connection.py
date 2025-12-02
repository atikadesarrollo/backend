import pyodbc
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

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

try:
    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION, @@SERVERNAME, DB_NAME()")
        row = cursor.fetchone()
        print("Conexión exitosa!")
        print(f"Versión del servidor: {row[0]}")
        print(f"Nombre del servidor: {row[1]}")
        print(f"Base de datos: {row[2]}")
except Exception as e:
    print(f"Error al conectar: {e}")

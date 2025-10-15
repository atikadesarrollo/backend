import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

server = os.getenv('DATALAKE_SERVER', 'DATALAKE')
database = os.getenv('DATALAKE_DATABASE', 'DATALAKE')
username = os.getenv('DATALAKE_USERNAME')
password = os.getenv('DATALAKE_PASSWORD')

if username and password:
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=yes;'
else:
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 1 * FROM DL_Facturacion_v")
    
    print("Columnas encontradas en DL_Facturacion_v:")
    print("=" * 60)
    for i, col in enumerate(cursor.description, 1):
        print(f"{i:3d}. [{col[0]}]")
    
    # Buscar columnas relacionadas con fecha
    print("\n" + "=" * 60)
    print("Columnas que contienen 'fecha' o 'date':")
    print("=" * 60)
    fecha_cols = [col[0] for col in cursor.description if 'fecha' in col[0].lower() or 'date' in col[0].lower()]
    if fecha_cols:
        for col in fecha_cols:
            print(f"  - [{col}]")
    else:
        print("  No se encontraron columnas con 'fecha' o 'date'")
    
    conn.close()
    print("\n✓ Consulta exitosa")
except Exception as e:
    print(f"Error: {e}")

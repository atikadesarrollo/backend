"""
Script para verificar la estructura de columnas de DL_Analisis_Venta_v
"""
import pyodbc
import os
from dotenv import load_dotenv

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

print("="*80)
print("VERIFICACIÓN DE ESTRUCTURA - DL_Analisis_Venta_v")
print("="*80)

try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    # Obtener información de columnas
    table_name = 'DL_Analisis_Venta_v'
    
    print(f"\n🔍 Analizando vista: {table_name}\n")
    
    # Método 1: SELECT TOP 0 para obtener estructura
    cursor.execute(f"SELECT TOP 0 * FROM {table_name}")
    columns = [column[0] for column in cursor.description]
    
    print(f"📊 Total de columnas: {len(columns)}\n")
    print("📋 Lista de columnas:\n")
    print("-" * 80)
    
    for idx, col in enumerate(columns, 1):
        print(f"{idx:3d}. [{col}]")
    
    print("-" * 80)
    
    # Identificar columnas de fecha
    print("\n📅 Columnas que contienen 'fecha' o 'date':\n")
    fecha_cols = [col for col in columns if 'fecha' in col.lower() or 'date' in col.lower()]
    for col in fecha_cols:
        print(f"   • [{col}]")
    
    # Identificar columnas relacionadas con montos
    print("\n💰 Columnas que contienen 'monto', 'precio', 'valor':\n")
    monto_cols = [col for col in columns if any(keyword in col.lower() for keyword in ['monto', 'precio', 'valor', 'total', 'costo'])]
    for col in monto_cols:
        print(f"   • [{col}]")
    
    # Identificar columnas de cliente
    print("\n👤 Columnas relacionadas con cliente:\n")
    cliente_cols = [col for col in columns if any(keyword in col.lower() for keyword in ['cliente', 'razon', 'rut', 'empresa'])]
    for col in cliente_cols:
        print(f"   • [{col}]")
    
    # Identificar columnas de producto
    print("\n📦 Columnas relacionadas con producto:\n")
    producto_cols = [col for col in columns if any(keyword in col.lower() for keyword in ['producto', 'sku', 'descripcion', 'item', 'codigo'])]
    for col in producto_cols:
        print(f"   • [{col}]")
    
    # Identificar columnas de vendedor
    print("\n🤝 Columnas relacionadas con vendedor:\n")
    vendedor_cols = [col for col in columns if 'vendedor' in col.lower()]
    for col in vendedor_cols:
        print(f"   • [{col}]")
    
    # Identificar columnas de proyecto
    print("\n🏗️ Columnas relacionadas con proyecto:\n")
    proyecto_cols = [col for col in columns if any(keyword in col.lower() for keyword in ['proyecto', 'obra', 'oferta'])]
    for col in proyecto_cols:
        print(f"   • [{col}]")
    
    # Identificar columnas organizacionales
    print("\n🏢 Columnas organizacionales (departamento, canal, área):\n")
    org_cols = [col for col in columns if any(keyword in col.lower() for keyword in ['departamento', 'canal', 'area', 'unidad', 'division', 'sucursal'])]
    for col in org_cols:
        print(f"   • [{col}]")
    
    # Obtener algunos datos de ejemplo
    print("\n" + "="*80)
    print("📊 MUESTRA DE DATOS (primeros 3 registros)")
    print("="*80 + "\n")
    
    cursor.execute(f"SELECT TOP 3 * FROM {table_name}")
    rows = cursor.fetchall()
    
    if rows:
        print(f"Registro 1:")
        for idx, col in enumerate(columns):
            value = rows[0][idx]
            print(f"  [{col}]: {value}")
        
        print("\n" + "-"*80)
        print(f"\nTotal de registros consultados: {len(rows)}")
    else:
        print("⚠️ No se encontraron datos en la vista")
    
    # Contar total de registros
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total = cursor.fetchone()[0]
    print(f"📈 Total de registros en la vista: {total:,}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*80)
    print("✅ Verificación completada exitosamente")
    print("="*80)
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nDetalles del error:")
    import traceback
    traceback.print_exc()

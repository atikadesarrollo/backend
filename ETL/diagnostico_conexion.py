"""
Script de diagnóstico para verificar la configuración de conexión SQL Server
"""
import pyodbc
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def diagnosticar_drivers():
    """Verificar qué drivers ODBC están disponibles"""
    print("=== DIAGNÓSTICO DE DRIVERS ODBC ===")
    print()
    
    try:
        all_drivers = pyodbc.drivers()
        sql_drivers = [driver for driver in all_drivers if 'SQL Server' in driver]
        
        print(f"Total de drivers ODBC instalados: {len(all_drivers)}")
        print(f"Drivers SQL Server encontrados: {len(sql_drivers)}")
        print()
        
        if sql_drivers:
            print("Drivers SQL Server disponibles:")
            for i, driver in enumerate(sql_drivers, 1):
                print(f"  {i}. {driver}")
        else:
            print("❌ NO SE ENCONTRARON DRIVERS SQL SERVER")
            print("   Necesitas instalar Microsoft ODBC Driver for SQL Server")
            print("   Descarga desde: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
        
        print()
        print("Todos los drivers ODBC disponibles:")
        for driver in sorted(all_drivers):
            print(f"  - {driver}")
            
    except Exception as e:
        print(f"❌ Error al obtener drivers: {e}")

def diagnosticar_configuracion():
    """Verificar la configuración de variables de entorno"""
    print("\n=== DIAGNÓSTICO DE CONFIGURACIÓN ===")
    print()
    
    configs = {
        'DATALAKE_SERVER': os.getenv('DATALAKE_SERVER'),
        'DATALAKE_DATABASE': os.getenv('DATALAKE_DATABASE'),
        'DATALAKE_USERNAME': os.getenv('DATALAKE_USERNAME'),
        'DATALAKE_PASSWORD': '***' if os.getenv('DATALAKE_PASSWORD') else None,
        'DATALAKE_USE_SQL_AUTH': os.getenv('DATALAKE_USE_SQL_AUTH'),
        'DATALAKE_PORT': os.getenv('DATALAKE_PORT'),
        'DATALAKE_DRIVER': os.getenv('DATALAKE_DRIVER'),
        'DATALAKE_TIMEOUT': os.getenv('DATALAKE_TIMEOUT'),
        'DATALAKE_TRUST_CERTIFICATE': os.getenv('DATALAKE_TRUST_CERTIFICATE')
    }
    
    print("Variables de entorno configuradas:")
    for key, value in configs.items():
        status = "✅" if value else "❌"
        print(f"  {status} {key}: {value}")
    
    # Verificar si existe archivo .env
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        print(f"\n✅ Archivo .env encontrado: {env_file}")
    else:
        print(f"\n❌ Archivo .env NO encontrado: {env_file}")

def probar_conexion_basica():
    """Probar conexión básica usando la configuración actual"""
    print("\n=== PRUEBA DE CONEXIÓN ===")
    print()
    
    try:
        from database_connection import DatabaseConnection
        
        db = DatabaseConnection()
        print("Información de conexión:")
        conn_info = db.get_connection_info()
        for key, value in conn_info.items():
            print(f"  {key}: {value}")
        
        print("\nProbando conexión...")
        if db.test_connection():
            print("✅ CONEXIÓN EXITOSA")
        else:
            print("❌ FALLO EN LA CONEXIÓN")
            
    except Exception as e:
        print(f"❌ Error al probar conexión: {e}")

def sugerir_solucion():
    """Sugerir soluciones basadas en el diagnóstico"""
    print("\n=== SUGERENCIAS DE SOLUCIÓN ===")
    print()
    
    # Verificar drivers
    try:
        sql_drivers = [driver for driver in pyodbc.drivers() if 'SQL Server' in driver]
        if not sql_drivers:
            print("1. INSTALAR DRIVER ODBC:")
            print("   - Descarga Microsoft ODBC Driver 17 o 18 for SQL Server")
            print("   - URL: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
            print("   - Reinicia el sistema después de la instalación")
            print()
    except:
        pass
    
    # Verificar configuración
    if not os.getenv('DATALAKE_SERVER'):
        print("2. CONFIGURAR VARIABLES DE ENTORNO:")
        print("   - Crea o edita el archivo .env")
        print("   - Asegúrate de que DATALAKE_SERVER esté configurado")
        print()
    
    print("3. ALTERNATIVAS DE DRIVER:")
    print("   - Intenta cambiar DATALAKE_DRIVER en .env a:")
    print("     * ODBC Driver 18 for SQL Server")
    print("     * ODBC Driver 17 for SQL Server")
    print("     * SQL Server Native Client 11.0")
    print("     * SQL Server")
    print()
    
    print("4. CONFIGURACIÓN DE RED:")
    print("   - Verifica que el puerto 1433 esté abierto")
    print("   - Confirma que SQL Server permita conexiones remotas")
    print("   - Verifica que el firewall no bloquee la conexión")

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DE CONEXIÓN SQL SERVER")
    print("=" * 50)
    
    diagnosticar_drivers()
    diagnosticar_configuracion()
    probar_conexion_basica()
    sugerir_solucion()
    
    print("\n" + "=" * 50)
    print("Diagnóstico completado.")

"""
Script para explorar y visualizar tablas de la base de datos
"""
import pandas as pd
from database_connection import DatabaseConnection
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def listar_tablas():
    """Listar todas las tablas disponibles en la base de datos"""
    print("=== LISTADO DE TABLAS ===")
    print()
    
    try:
        db = DatabaseConnection()
        
        # Consulta para obtener todas las tablas
        query = """
        SELECT 
            TABLE_SCHEMA as Esquema,
            TABLE_NAME as Tabla,
            TABLE_TYPE as Tipo
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
        """
        
        tablas_df = db.execute_query(query)
        
        if len(tablas_df) > 0:
            print(f"Se encontraron {len(tablas_df)} tablas:")
            print()
            
            # Agrupar por esquema
            esquemas = tablas_df['Esquema'].unique()
            for esquema in esquemas:
                tablas_esquema = tablas_df[tablas_df['Esquema'] == esquema]
                print(f"📁 Esquema: {esquema}")
                for idx, row in tablas_esquema.iterrows():
                    print(f"  📊 {row['Tabla']}")
                print()
            
            return tablas_df
        else:
            print("❌ No se encontraron tablas")
            return None
            
    except Exception as e:
        print(f"❌ Error al listar tablas: {e}")
        return None

def mostrar_estructura_tabla(nombre_tabla, esquema='dbo'):
    """Mostrar la estructura de una tabla específica"""
    print(f"=== ESTRUCTURA DE LA TABLA {esquema}.{nombre_tabla} ===")
    print()
    
    try:
        db = DatabaseConnection()
        
        # Consulta para obtener la estructura de la tabla
        query = """
        SELECT 
            COLUMN_NAME as Columna,
            DATA_TYPE as Tipo,
            CHARACTER_MAXIMUM_LENGTH as Longitud,
            IS_NULLABLE as Permite_NULL,
            COLUMN_DEFAULT as Valor_Por_Defecto
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
        """
        
        estructura_df = db.execute_query(query, [esquema, nombre_tabla])
        
        if len(estructura_df) > 0:
            print("Columnas:")
            for idx, row in estructura_df.iterrows():
                tipo_completo = row['Tipo']
                if pd.notna(row['Longitud']):
                    tipo_completo += f"({int(row['Longitud'])})"
                
                null_info = "NULL" if row['Permite_NULL'] == 'YES' else "NOT NULL"
                default_info = f" DEFAULT: {row['Valor_Por_Defecto']}" if pd.notna(row['Valor_Por_Defecto']) else ""
                
                print(f"  📝 {row['Columna']} - {tipo_completo} {null_info}{default_info}")
            
            return estructura_df
        else:
            print(f"❌ No se encontró la tabla {esquema}.{nombre_tabla}")
            return None
            
    except Exception as e:
        print(f"❌ Error al obtener estructura: {e}")
        return None

def mostrar_datos_tabla(nombre_tabla, esquema='dbo', limite=10):
    """Mostrar una muestra de datos de una tabla"""
    print(f"=== DATOS DE LA TABLA {esquema}.{nombre_tabla} (primeras {limite} filas) ===")
    print()
    
    try:
        db = DatabaseConnection()
        
        # Consulta para obtener datos de muestra
        query = f"SELECT TOP {limite} * FROM [{esquema}].[{nombre_tabla}]"
        
        datos_df = db.execute_query(query)
        
        if len(datos_df) > 0:
            print(f"Total de columnas: {len(datos_df.columns)}")
            print(f"Filas mostradas: {len(datos_df)}")
            print()
            
            # Mostrar los datos
            print(datos_df.to_string(index=False, max_cols=10, max_colwidth=30))
            
            if len(datos_df.columns) > 10:
                print(f"\n... y {len(datos_df.columns) - 10} columnas más")
            
            return datos_df
        else:
            print(f"❌ La tabla {esquema}.{nombre_tabla} está vacía")
            return None
            
    except Exception as e:
        print(f"❌ Error al obtener datos: {e}")
        return None

def buscar_tablas_por_patron(patron):
    """Buscar tablas que coincidan con un patrón"""
    print(f"=== BUSCANDO TABLAS CON PATRÓN: '{patron}' ===")
    print()
    
    try:
        db = DatabaseConnection()
        
        query = """
        SELECT 
            TABLE_SCHEMA as Esquema,
            TABLE_NAME as Tabla,
            TABLE_TYPE as Tipo
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        AND (TABLE_NAME LIKE ? OR TABLE_SCHEMA LIKE ?)
        ORDER BY TABLE_SCHEMA, TABLE_NAME
        """
        
        patron_sql = f"%{patron}%"
        tablas_df = db.execute_query(query, [patron_sql, patron_sql])
        
        if len(tablas_df) > 0:
            print(f"Se encontraron {len(tablas_df)} tablas que coinciden:")
            print()
            
            for idx, row in tablas_df.iterrows():
                print(f"  📊 {row['Esquema']}.{row['Tabla']}")
            
            return tablas_df
        else:
            print(f"❌ No se encontraron tablas con el patrón '{patron}'")
            return None
            
    except Exception as e:
        print(f"❌ Error al buscar tablas: {e}")
        return None

def obtener_conteo_filas(nombre_tabla, esquema='dbo'):
    """Obtener el conteo total de filas de una tabla"""
    try:
        db = DatabaseConnection()
        query = f"SELECT COUNT(*) as total_filas FROM [{esquema}].[{nombre_tabla}]"
        resultado = db.execute_query(query)
        return resultado.iloc[0]['total_filas']
    except Exception as e:
        print(f"Error al contar filas: {e}")
        return 0

def menu_interactivo():
    """Menú interactivo para explorar la base de datos"""
    print("🔍 EXPLORADOR DE BASE DE DATOS")
    print("=" * 40)
    
    while True:
        print("\nOpciones disponibles:")
        print("1. Listar todas las tablas")
        print("2. Mostrar estructura de una tabla")
        print("3. Mostrar datos de una tabla")
        print("4. Buscar tablas por nombre")
        print("5. Explorar tabla específica (estructura + datos)")
        print("6. Salir")
        
        opcion = input("\nSelecciona una opción (1-6): ").strip()
        
        if opcion == '1':
            print()
            tablas = listar_tablas()
            
        elif opcion == '2':
            esquema = input("Esquema (presiona Enter para 'dbo'): ").strip() or 'dbo'
            tabla = input("Nombre de la tabla: ").strip()
            if tabla:
                print()
                mostrar_estructura_tabla(tabla, esquema)
                
        elif opcion == '3':
            esquema = input("Esquema (presiona Enter para 'dbo'): ").strip() or 'dbo'
            tabla = input("Nombre de la tabla: ").strip()
            limite = input("Número de filas a mostrar (presiona Enter para 10): ").strip()
            limite = int(limite) if limite.isdigit() else 10
            
            if tabla:
                print()
                mostrar_datos_tabla(tabla, esquema, limite)
                
        elif opcion == '4':
            patron = input("Patrón de búsqueda: ").strip()
            if patron:
                print()
                buscar_tablas_por_patron(patron)
                
        elif opcion == '5':
            esquema = input("Esquema (presiona Enter para 'dbo'): ").strip() or 'dbo'
            tabla = input("Nombre de la tabla: ").strip()
            
            if tabla:
                print()
                # Mostrar estructura
                mostrar_estructura_tabla(tabla, esquema)
                print()
                
                # Mostrar conteo total
                total_filas = obtener_conteo_filas(tabla, esquema)
                print(f"Total de filas en la tabla: {total_filas:,}")
                print()
                
                # Mostrar datos de muestra
                mostrar_datos_tabla(tabla, esquema, 5)
                
        elif opcion == '6':
            print("¡Hasta luego!")
            break
            
        else:
            print("❌ Opción inválida. Por favor, selecciona un número del 1 al 6.")

def explorar_tablas_ejemplo():
    """Función para explorar tablas comunes que podrían existir"""
    print("=== EXPLORANDO TABLAS DE EJEMPLO ===")
    print()
    
    # Tablas comunes que podrían existir
    tablas_comunes = [
        'DL_Analisis_Venta_v',
        'Ventas',
        'Productos',
        'Clientes',
        'Pedidos',
        'Facturas'
    ]
    
    db = DatabaseConnection()
    
    for tabla in tablas_comunes:
        try:
            # Intentar obtener información básica de la tabla
            query = f"SELECT TOP 1 * FROM {tabla}"
            resultado = db.execute_query(query)
            
            print(f"✅ Tabla encontrada: {tabla}")
            print(f"   Columnas: {len(resultado.columns)}")
            
            # Contar filas totales
            query_count = f"SELECT COUNT(*) as total FROM {tabla}"
            conteo = db.execute_query(query_count)
            print(f"   Filas: {conteo.iloc[0]['total']:,}")
            print()
            
        except Exception:
            print(f"❌ Tabla no encontrada o sin acceso: {tabla}")

if __name__ == "__main__":
    try:
        # Primero verificar la conexión
        db = DatabaseConnection()
        if not db.test_connection():
            print("❌ No se pudo conectar a la base de datos")
            print("Ejecuta 'python diagnostico_conexion.py' para más información")
            exit(1)
        
        print("✅ Conexión exitosa a la base de datos")
        print()
        
        # Explorar tablas comunes primero
        explorar_tablas_ejemplo()
        print()
        
        # Luego mostrar el menú interactivo
        menu_interactivo()
        
    except Exception as e:
        print(f"❌ Error general: {e}")

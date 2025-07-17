"""
Script simple para ejecutar el pipeline ETL de ejemplo y ver las tablas
"""
from database_connection import DatabaseConnection, run_etl_pipeline
import pandas as pd

def mostrar_tablas_disponibles():
    """Mostrar las tablas más comunes del DataLake"""
    print("=== VERIFICANDO TABLAS DEL DATALAKE ===")
    print()
    
    db = DatabaseConnection()
    
    # Lista de tablas que podrían existir en el DataLake
    tablas_posibles = [
        'DL_Analisis_Venta_v',
        'DL_Ventas',
        'DL_Productos', 
        'DL_Clientes',
        'DL_Pedidos',
        'DL_Facturas',
        'DL_Analisis_Venta_Processed'
    ]
    
    tablas_encontradas = []
    
    for tabla in tablas_posibles:
        try:
            # Intentar hacer una consulta simple
            query = f"SELECT TOP 5 * FROM {tabla}"
            df = db.execute_query(query)
            
            print(f"✅ {tabla}")
            print(f"   - Columnas: {len(df.columns)}")
            print(f"   - Columnas disponibles: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
            
            # Contar filas totales
            count_query = f"SELECT COUNT(*) as total FROM {tabla}"
            count_df = db.execute_query(count_query)
            total_filas = count_df.iloc[0]['total']
            print(f"   - Total de filas: {total_filas:,}")
            print()
            
            tablas_encontradas.append(tabla)
            
        except Exception as e:
            print(f"❌ {tabla} - No disponible")
    
    return tablas_encontradas

def ejecutar_ejemplo_etl():
    """Ejecutar el ejemplo de ETL si las tablas están disponibles"""
    print("=== EJECUTANDO EJEMPLO DE ETL ===")
    print()
    
    try:
        # Verificar si existe la tabla fuente
        db = DatabaseConnection()
        
        # Intentar con la tabla principal del ejemplo
        try:
            test_query = "SELECT TOP 1 * FROM DL_Analisis_Venta_v"
            df_test = db.execute_query(test_query)
            
            print("✅ Tabla fuente DL_Analisis_Venta_v encontrada")
            print(f"Columnas disponibles: {', '.join(df_test.columns)}")
            print()
            
            # Ejecutar el pipeline ETL
            print("Ejecutando pipeline ETL...")
            success = run_etl_pipeline(
                source_table="DL_Analisis_Venta_v", 
                target_table="DL_Analisis_Venta_Processed", 
                days_back=30
            )
            
            if success:
                print("✅ Pipeline ETL ejecutado exitosamente")
                
                # Mostrar los resultados
                result_query = "SELECT TOP 10 * FROM DL_Analisis_Venta_Processed ORDER BY processed_at DESC"
                result_df = db.execute_query(result_query)
                
                print(f"\nResultados procesados (últimas 10 filas):")
                print(f"Total de columnas: {len(result_df.columns)}")
                print("\nPrimeras columnas:")
                print(result_df.iloc[:, :5].to_string(index=False))
                
            else:
                print("❌ Error en el pipeline ETL")
                
        except Exception as e:
            print(f"❌ La tabla DL_Analisis_Venta_v no está disponible: {e}")
            print("Intentando con otras tablas...")
            
            # Intentar con tablas alternativas
            tablas_alternativas = ['DL_Ventas', 'Ventas', 'Sales']
            
            for tabla_alt in tablas_alternativas:
                try:
                    test_query = f"SELECT TOP 1 * FROM {tabla_alt}"
                    df_test = db.execute_query(test_query)
                    
                    print(f"✅ Tabla alternativa encontrada: {tabla_alt}")
                    print(f"Columnas: {', '.join(df_test.columns[:10])}")
                    
                    # Mostrar muestra de datos
                    sample_query = f"SELECT TOP 5 * FROM {tabla_alt}"
                    sample_df = db.execute_query(sample_query)
                    print("\nMuestra de datos:")
                    print(sample_df.to_string(index=False, max_cols=5))
                    break
                    
                except:
                    continue
            else:
                print("❌ No se encontraron tablas de datos conocidas")
                
    except Exception as e:
        print(f"❌ Error al ejecutar ejemplo: {e}")

def mostrar_esquema_completo():
    """Mostrar el esquema completo de la base de datos"""
    print("=== ESQUEMA COMPLETO DE LA BASE DE DATOS ===")
    print()
    
    try:
        db = DatabaseConnection()
        
        # Obtener todas las tablas
        query = """
        SELECT 
            s.name AS esquema,
            t.name AS tabla,
            COUNT(c.column_id) AS num_columnas
        FROM sys.tables t
        INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
        LEFT JOIN sys.columns c ON t.object_id = c.object_id
        GROUP BY s.name, t.name
        ORDER BY s.name, t.name
        """
        
        schema_df = db.execute_query(query)
        
        if len(schema_df) > 0:
            print(f"Total de tablas: {len(schema_df)}")
            print()
            
            esquemas = schema_df['esquema'].unique()
            for esquema in esquemas:
                tablas_esquema = schema_df[schema_df['esquema'] == esquema]
                print(f"📁 Esquema: {esquema} ({len(tablas_esquema)} tablas)")
                
                for _, row in tablas_esquema.iterrows():
                    print(f"  📊 {row['tabla']} ({row['num_columnas']} columnas)")
                print()
        else:
            print("❌ No se pudieron obtener las tablas")
            
    except Exception as e:
        print(f"❌ Error al obtener esquema: {e}")

if __name__ == "__main__":
    print("🚀 EXPLORADOR RÁPIDO DE TABLAS Y ETL")
    print("=" * 50)
    
    try:
        # Verificar conexión
        db = DatabaseConnection()
        if not db.test_connection():
            print("❌ No se pudo conectar a la base de datos")
            exit(1)
        
        print("✅ Conexión exitosa")
        print()
        
        # Mostrar esquema completo
        mostrar_esquema_completo()
        
        # Mostrar tablas disponibles
        tablas_encontradas = mostrar_tablas_disponibles()
        
        if tablas_encontradas:
            print(f"Se encontraron {len(tablas_encontradas)} tablas del DataLake")
            
            # Preguntar si ejecutar ETL
            respuesta = input("\n¿Quieres ejecutar el ejemplo de ETL? (s/n): ").strip().lower()
            if respuesta in ['s', 'si', 'yes', 'y']:
                print()
                ejecutar_ejemplo_etl()
        else:
            print("No se encontraron tablas conocidas del DataLake")
            print("Usa 'python explorar_tablas.py' para explorar manualmente")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        print("\nPara más información sobre el error, ejecuta:")
        print("python diagnostico_conexion.py")

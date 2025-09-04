"""
Script para listar todas las tablas ETL disponibles en el servidor
"""
from database_connection import DatabaseConnection

def listar_tablas_etl():
    """Listar todas las tablas relacionadas con el ETL"""
    print("🗄️  TABLAS ETL DISPONIBLES EN EL SERVIDOR")
    print("=" * 60)
    print(f"📍 Servidor: 45.236.130.211:1433")
    print(f"📊 Base de datos: DATALAKE")
    print(f"🔐 Esquema: dbo")
    print()
    
    try:
        db = DatabaseConnection()
        
        # Consultar todas las tablas que empiecen con DL_Analisis_Venta
        query = """
        SELECT 
            TABLE_NAME as tabla,
            TABLE_TYPE as tipo,
            (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
             WHERE TABLE_NAME = t.TABLE_NAME) as columnas
        FROM INFORMATION_SCHEMA.TABLES t
        WHERE TABLE_NAME LIKE 'DL_Analisis_Venta%'
        ORDER BY TABLE_NAME
        """
        
        tablas_df = db.execute_query(query)
        
        if len(tablas_df) > 0:
            print("📋 TABLAS ENCONTRADAS:")
            print()
            
            for idx, row in tablas_df.iterrows():
                tabla = row['tabla']
                columnas = row['columnas']
                
                # Obtener conteo de filas
                try:
                    count_query = f"SELECT COUNT(*) as filas FROM [{tabla}]"
                    count_result = db.execute_query(count_query)
                    filas = count_result.iloc[0]['filas']
                    
                    print(f"✅ {tabla}")
                    print(f"   📊 Filas: {filas:,}")
                    print(f"   🔢 Columnas: {columnas}")
                    
                    # Información adicional según el tipo de tabla
                    if "Daily" in tabla:
                        print("   📅 Tipo: Datos diarios (últimos 7 días)")
                    elif "Weekly" in tabla:
                        print("   📅 Tipo: Datos semanales (últimos 30 días)")
                    elif "Summary" in tabla:
                        print("   📈 Tipo: Resumen por vendedores")
                    elif "Processed" in tabla:
                        print("   ⚙️  Tipo: Datos procesados generales")
                    else:
                        print("   📄 Tipo: Vista fuente original")
                    
                    print(f"   🔗 Consulta SQL: SELECT * FROM [DATALAKE].[dbo].[{tabla}]")
                    print()
                    
                except Exception as e:
                    print(f"❌ {tabla} - Error al contar filas: {e}")
                    print()
        else:
            print("❌ No se encontraron tablas ETL")
        
        # Mostrar información de conexión
        print("🔧 INFORMACIÓN DE CONEXIÓN:")
        print(f"   Server: 45.236.130.211,1433")
        print(f"   Database: DATALAKE")
        print(f"   User: sa")
        print(f"   Driver: SQL Server")
        print()
        
        print("💡 EJEMPLOS DE CONSULTA:")
        print("   -- Datos diarios recientes")
        print("   SELECT TOP 100 * FROM DL_Analisis_Venta_Daily ORDER BY processed_at DESC")
        print()
        print("   -- Resumen de vendedores")
        print("   SELECT * FROM DL_Analisis_Venta_Summary ORDER BY monto_total DESC")
        print()
        print("   -- Unir con tabla original")
        print("   SELECT d.*, v.Cliente FROM DL_Analisis_Venta_Daily d")
        print("   INNER JOIN DL_Analisis_Venta_v v ON d.[Referencia de pedido] = v.[Referencia de pedido]")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    listar_tablas_etl()

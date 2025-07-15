"""
Script simple para ver datos de la tabla principal DL_Analisis_Venta_v
"""
from database_connection import DatabaseConnection
import pandas as pd

def mostrar_tabla_principal():
    """Mostrar información de la tabla principal de análisis de ventas"""
    print("🔍 EXPLORANDO TABLA PRINCIPAL: DL_Analisis_Venta_v")
    print("=" * 60)
    
    try:
        db = DatabaseConnection()
        
        # 1. Información básica de la tabla
        print("\n1. INFORMACIÓN BÁSICA:")
        count_query = "SELECT COUNT(*) as total_filas FROM DL_Analisis_Venta_v"
        count_df = db.execute_query(count_query)
        total_filas = count_df.iloc[0]['total_filas']
        print(f"   Total de filas: {total_filas:,}")
        
        # 2. Mostrar estructura de columnas (optimizada)
        print("\n2. ESTRUCTURA DE COLUMNAS:")
        # Usar una consulta más rápida para obtener solo la estructura
        struct_query = """
        SELECT TOP 1 * FROM DL_Analisis_Venta_v 
        WHERE [Fecha de oferta] IS NOT NULL
        """
        struct_df = db.execute_query(struct_query)
        
        print(f"   Columnas totales: {len(struct_df.columns)}")
        
        # Mostrar todas las columnas en grupos de 10
        print("\n   Lista completa de columnas:")
        for i in range(0, len(struct_df.columns), 10):
            grupo = struct_df.columns[i:i+10]
            print(f"   Columnas {i+1}-{min(i+10, len(struct_df.columns))}:")
            for j, col in enumerate(grupo, i+1):
                print(f"      {j:2d}. {col}")
            print()
        
        # Muestra simple de datos (solo las primeras 5 columnas)
        print("\n   MUESTRA DE DATOS (primeras 5 columnas):")
        columnas_muestra = struct_df.columns[:5]
        muestra_simple = struct_df[columnas_muestra]
        
        pd.set_option('display.max_columns', 5)
        pd.set_option('display.width', 100)
        pd.set_option('display.max_colwidth', 20)
        print(muestra_simple.to_string(index=False))
        
        # 3. Análisis por fechas
        print("\n\n3. ANÁLISIS POR FECHAS:")
        fecha_query = """
        SELECT 
            MIN([Fecha de oferta]) as fecha_minima,
            MAX([Fecha de oferta]) as fecha_maxima,
            COUNT(*) as total_registros
        FROM DL_Analisis_Venta_v
        WHERE [Fecha de oferta] IS NOT NULL
        """
        fecha_df = db.execute_query(fecha_query)
        
        print(f"   Fecha más antigua: {fecha_df.iloc[0]['fecha_minima']}")
        print(f"   Fecha más reciente: {fecha_df.iloc[0]['fecha_maxima']}")
        print(f"   Registros con fecha: {fecha_df.iloc[0]['total_registros']:,}")
        
        # 4. Top vendedores
        print("\n4. TOP 10 VENDEDORES:")
        vendedores_query = """
        SELECT TOP 10
            Vendedor,
            COUNT(*) as num_ofertas,
            SUM([Cant. producto]) as cantidad_total
        FROM DL_Analisis_Venta_v
        WHERE Vendedor IS NOT NULL
        GROUP BY Vendedor
        ORDER BY COUNT(*) DESC
        """
        vendedores_df = db.execute_query(vendedores_query)
        
        print(vendedores_df.to_string(index=False))
        
        # 5. Top productos
        print("\n5. TOP 10 PRODUCTOS MÁS VENDIDOS:")
        productos_query = """
        SELECT TOP 10
            [Descipción] as Descripcion,
            COUNT(*) as num_ofertas,
            SUM([Cant. producto]) as cantidad_total
        FROM DL_Analisis_Venta_v
        WHERE [Descipción] IS NOT NULL
        GROUP BY [Descipción]
        ORDER BY SUM([Cant. producto]) DESC
        """
        productos_df = db.execute_query(productos_query)
        
        pd.set_option('display.max_colwidth', 30)
        print(productos_df.to_string(index=False))
        
        # 6. Resumen de estados
        print("\n6. RESUMEN POR ESTADO:")
        estados_query = """
        SELECT 
            Estado,
            COUNT(*) as cantidad,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM DL_Analisis_Venta_v), 2) as porcentaje
        FROM DL_Analisis_Venta_v
        WHERE Estado IS NOT NULL
        GROUP BY Estado
        ORDER BY COUNT(*) DESC
        """
        estados_df = db.execute_query(estados_query)
        
        print(estados_df.to_string(index=False))
        
        print("\n" + "=" * 60)
        print("✅ Exploración completada")
        print("\nPara ver más detalles, puedes usar:")
        print("- python explorar_tablas.py (explorador interactivo)")
        print("- python ejemplo_rapido.py (ETL completo)")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    mostrar_tabla_principal()

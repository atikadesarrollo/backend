"""
Script para consultar las tablas ETL desde Python
Ejemplo práctico de cómo acceder a los datos procesados
"""

from database_connection import DatabaseConnection
import pandas as pd
from datetime import datetime, timedelta

def consultar_datos_diarios(limite=50):
    """Consultar datos de la tabla diaria"""
    print("🔍 CONSULTANDO DATOS DIARIOS")
    print("="*50)
    
    db = DatabaseConnection()
    
    # Consulta básica
    query = f"""
    SELECT TOP {limite}
        [Fecha de oferta],
        Vendedor,
        Cliente,
        [Cantidad entregada],
        [Monto orden],
        Estado,
        Categoria
    FROM DL_Analisis_Venta_Daily
    ORDER BY [Fecha de oferta] DESC
    """
    
    df = db.execute_query(query)
    print(f"✅ Datos obtenidos: {len(df)} filas")
    print("\n📊 PRIMEROS 10 REGISTROS:")
    print(df.head(10).to_string(index=False))
    
    return df

def consultar_resumen_vendedores():
    """Consultar resumen por vendedores"""
    print("\n🔍 CONSULTANDO RESUMEN POR VENDEDORES")
    print("="*50)
    
    db = DatabaseConnection()
    
    query = """
    SELECT 
        Vendedor,
        total_ofertas,
        cantidad_total,
        monto_total,
        promedio_monto,
        fecha_primera_venta,
        fecha_ultima_venta
    FROM DL_Analisis_Venta_Summary
    ORDER BY monto_total DESC
    """
    
    df = db.execute_query(query)
    print(f"✅ Vendedores encontrados: {len(df)}")
    print("\n📈 TOP 10 VENDEDORES:")
    print(df.head(10).to_string(index=False))
    
    return df

def analisis_por_fecha():
    """Análisis de ventas por fecha"""
    print("\n🔍 ANÁLISIS POR FECHA")
    print("="*50)
    
    db = DatabaseConnection()
    
    query = """
    SELECT 
        CAST([Fecha de oferta] AS DATE) as Fecha,
        COUNT(*) as Total_Ofertas,
        SUM([Cantidad entregada]) as Cantidad_Total,
        SUM([Monto orden]) as Monto_Total,
        AVG([Monto orden]) as Promedio_Oferta
    FROM DL_Analisis_Venta_Daily
    GROUP BY CAST([Fecha de oferta] AS DATE)
    ORDER BY Fecha DESC
    """
    
    df = db.execute_query(query)
    print(f"✅ Fechas analizadas: {len(df)}")
    print("\n📅 RESUMEN POR FECHA:")
    
    # Formatear números para mejor lectura
    df['Monto_Total'] = df['Monto_Total'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
    df['Promedio_Oferta'] = df['Promedio_Oferta'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
    df['Cantidad_Total'] = df['Cantidad_Total'].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A")
    
    print(df.to_string(index=False))
    
    return df

def top_productos():
    """Top productos más vendidos"""
    print("\n🔍 TOP PRODUCTOS MÁS VENDIDOS")
    print("="*50)
    
    db = DatabaseConnection()
    
    query = """
    SELECT TOP 15
        Producto,
        COUNT(*) as total_ofertas,
        SUM([Cantidad entregada]) as cantidad_total,
        SUM([Monto orden]) as monto_total,
        AVG([Monto orden]) as promedio_por_oferta
    FROM DL_Analisis_Venta_Daily
    GROUP BY Producto
    ORDER BY monto_total DESC
    """
    
    df = db.execute_query(query)
    print(f"✅ Productos analizados: {len(df)}")
    print("\n🛍️ TOP 15 PRODUCTOS:")
    
    # Formatear para mejor lectura
    df['monto_total'] = df['monto_total'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
    df['promedio_por_oferta'] = df['promedio_por_oferta'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
    
    print(df.to_string(index=False))
    
    return df

def ventas_por_categoria():
    """Ventas por categoría"""
    print("\n🔍 VENTAS POR CATEGORÍA")
    print("="*50)
    
    db = DatabaseConnection()
    
    query = """
    SELECT 
        Categoria,
        COUNT(*) as total_ofertas,
        SUM([Cantidad entregada]) as cantidad_total,
        SUM([Monto orden]) as monto_total,
        AVG([Monto orden]) as promedio_por_oferta
    FROM DL_Analisis_Venta_Daily
    WHERE Categoria IS NOT NULL AND Categoria != ''
    GROUP BY Categoria
    ORDER BY monto_total DESC
    """
    
    df = db.execute_query(query)
    print(f"✅ Categorías encontradas: {len(df)}")
    print("\n📂 VENTAS POR CATEGORÍA:")
    
    # Formatear números
    df['monto_total'] = df['monto_total'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
    df['promedio_por_oferta'] = df['promedio_por_oferta'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
    
    print(df.to_string(index=False))
    
    return df

def buscar_vendedor(nombre_vendedor):
    """Buscar información específica de un vendedor"""
    print(f"\n🔍 INFORMACIÓN DEL VENDEDOR: {nombre_vendedor}")
    print("="*60)
    
    db = DatabaseConnection()
    
    # Buscar en datos diarios
    query_daily = f"""
    SELECT 
        [Fecha de oferta],
        Cliente,
        Producto,
        [Cantidad entregada],
        [Monto orden],
        Estado
    FROM DL_Analisis_Venta_Daily
    WHERE Vendedor LIKE '%{nombre_vendedor}%'
    ORDER BY [Fecha de oferta] DESC
    """
    
    df_daily = db.execute_query(query_daily)
    
    # Buscar en resumen
    query_summary = f"""
    SELECT * FROM DL_Analisis_Venta_Summary
    WHERE Vendedor LIKE '%{nombre_vendedor}%'
    """
    
    df_summary = db.execute_query(query_summary)
    
    if len(df_summary) > 0:
        print("📊 RESUMEN DEL VENDEDOR:")
        for col in df_summary.columns:
            valor = df_summary.iloc[0][col]
            if 'monto' in col.lower() and pd.notna(valor):
                print(f"   {col}: ${valor:,.2f}")
            else:
                print(f"   {col}: {valor}")
    
    if len(df_daily) > 0:
        print(f"\n📋 ÚLTIMAS 10 VENTAS:")
        print(df_daily.head(10).to_string(index=False))
    else:
        print("❌ No se encontraron datos para este vendedor")
    
    return df_daily, df_summary

def menu_principal():
    """Menú principal de consultas"""
    print("\n" + "="*60)
    print("🗃️  CONSULTA DE DATOS ETL - DATALAKE")
    print("="*60)
    print("1. Ver datos diarios recientes")
    print("2. Ver resumen por vendedores")
    print("3. Análisis por fecha")
    print("4. Top productos más vendidos")
    print("5. Ventas por categoría")
    print("6. Buscar vendedor específico")
    print("7. Salir")
    print("="*60)
    
    while True:
        try:
            opcion = input("\n👉 Selecciona una opción (1-7): ").strip()
            
            if opcion == '1':
                consultar_datos_diarios()
            elif opcion == '2':
                consultar_resumen_vendedores()
            elif opcion == '3':
                analisis_por_fecha()
            elif opcion == '4':
                top_productos()
            elif opcion == '5':
                ventas_por_categoria()
            elif opcion == '6':
                nombre = input("👤 Ingresa el nombre del vendedor: ").strip()
                if nombre:
                    buscar_vendedor(nombre)
                else:
                    print("❌ Debes ingresar un nombre")
            elif opcion == '7':
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción no válida. Selecciona del 1 al 7.")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        menu_principal()
    except Exception as e:
        print(f"❌ Error al ejecutar el script: {e}")
        print("💡 Asegúrate de que:")
        print("   - La base de datos esté disponible")
        print("   - Las tablas ETL hayan sido creadas")
        print("   - Tienes permisos de conexión")

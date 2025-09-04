"""
Script para consultar la tabla completa DL_Analisis_Venta_Quarterly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_connection import DatabaseConnection
from config import ETLConfig
import pandas as pd

def consultar_tabla_quarterly():
    """Consultar toda la tabla DL_Analisis_Venta_Quarterly"""
    
    # Nombre de la tabla
    tabla_quarterly = ETLConfig.TARGET_TABLES['analisis_venta_quarterly']
    
    print(f"🔍 Consultando tabla: {tabla_quarterly}")
    print("=" * 50)
    
    try:
        # Crear conexión
        db = DatabaseConnection()
        
        # Consulta para obtener información básica de la tabla
        query_info = f"""
        SELECT 
            COUNT(*) as total_registros,
            COUNT(DISTINCT YEAR([Fecha de oferta])) as años_unicos,
            COUNT(DISTINCT DATEPART(quarter, [Fecha de oferta])) as trimestres_unicos,
            MIN([Fecha de oferta]) as fecha_minima,
            MAX([Fecha de oferta]) as fecha_maxima,
            SUM(Total) as monto_total
        FROM {tabla_quarterly}
        """
        
        print("📊 Información general de la tabla:")
        df_info = db.execute_query(query_info)
        if not df_info.empty:
            for col in df_info.columns:
                print(f"   {col}: {df_info[col].iloc[0]}")
        
        print("\n" + "=" * 50)
        
        # Consulta para ver distribución por trimestre
        query_trimestres = f"""
        SELECT 
            YEAR([Fecha de oferta]) as año,
            DATEPART(quarter, [Fecha de oferta]) as trimestre,
            COUNT(*) as total_registros,
            SUM(Total) as monto_total,
            COUNT(DISTINCT Vendedor) as vendedores_unicos,
            COUNT(DISTINCT Cliente) as clientes_unicos
        FROM {tabla_quarterly}
        GROUP BY YEAR([Fecha de oferta]), DATEPART(quarter, [Fecha de oferta])
        ORDER BY año DESC, trimestre DESC
        """
        
        print("📈 Distribución por trimestre:")
        df_trimestres = db.execute_query(query_trimestres)
        if not df_trimestres.empty:
            print(df_trimestres.to_string(index=False))
        
        print("\n" + "=" * 50)
        
        # Consulta para ver los últimos registros
        query_ultimos = f"""
        SELECT TOP 10 
            [Fecha de oferta],
            Vendedor,
            Cliente,
            [Referencia de pedido],
            SKU,
            [Cant. producto],
            Total,
            Estado
        FROM {tabla_quarterly}
        ORDER BY [Fecha de oferta] DESC
        """
        
        print("📋 Últimos 10 registros:")
        df_ultimos = db.execute_query(query_ultimos)
        if not df_ultimos.empty:
            print(df_ultimos.to_string(index=False))
        
        print("\n" + "=" * 50)
        
        # Consulta para obtener TODA la tabla (usar con precaución)
        respuesta = input("¿Deseas obtener TODOS los registros de la tabla? (s/n): ").lower()
        
        if respuesta == 's':
            print("⚠️  Obteniendo todos los registros... Esto puede tomar tiempo.")
            
            query_completa = f"SELECT * FROM {tabla_quarterly} ORDER BY [Fecha de oferta] DESC"
            df_completa = db.execute_query(query_completa)
            
            if not df_completa.empty:
                print(f"\n✅ Tabla completa obtenida: {len(df_completa)} registros")
                print(f"📊 Columnas: {len(df_completa.columns)}")
                print(f"🏷️  Nombres de columnas:")
                for i, col in enumerate(df_completa.columns, 1):
                    print(f"   {i:2d}. {col}")
                
                # Opción para guardar en CSV
                guardar = input("\n¿Deseas guardar los datos en un archivo CSV? (s/n): ").lower()
                if guardar == 's':
                    archivo_csv = f"DL_Analisis_Venta_Quarterly_completo.csv"
                    df_completa.to_csv(archivo_csv, index=False, encoding='utf-8-sig')
                    print(f"💾 Datos guardados en: {archivo_csv}")
                
                # Mostrar una muestra de los datos
                print("\n📋 Muestra de los primeros 5 registros:")
                print(df_completa.head().to_string(index=False))
                
                return df_completa
            else:
                print("❌ No se encontraron datos en la tabla")
                return None
        else:
            print("ℹ️  Consulta completada sin obtener todos los registros")
            return None
            
    except Exception as e:
        print(f"❌ Error al consultar la tabla: {str(e)}")
        return None
    
    finally:
        try:
            db.close()
        except:
            pass

if __name__ == "__main__":
    consultar_tabla_quarterly()

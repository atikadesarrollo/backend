"""
Script para verificar las tablas procesadas por el ETL
"""
from database_connection import DatabaseConnection
import pandas as pd

def verificar_tablas_etl():
    """Verificar las tablas creadas por el pipeline ETL"""
    print("🔍 VERIFICANDO TABLAS PROCESADAS POR ETL")
    print("=" * 60)
    
    try:
        db = DatabaseConnection()
        
        # Tablas a verificar
        tablas_etl = {
            'DL_Analisis_Venta_Daily': 'Datos diarios (últimos 7 días)',
            'DL_Analisis_Venta_Summary': 'Resumen por vendedores (últimos 7 días)',
            'DL_Analisis_Venta_Weekly': 'Datos semanales (últimos 30 días)',
            'DL_Analisis_Venta_Monthly': 'Datos mensuales (últimos 90 días)',
            'DL_Analisis_Venta_Quarterly': 'Datos trimestrales (últimos 365 días)',
            'DL_Analisis_Venta_Processed': 'Datos procesados generales (si existe)'
        }
        
        tablas_encontradas = []
        
        for tabla, descripcion in tablas_etl.items():
            try:
                # Verificar si la tabla existe y obtener información básica
                count_query = f"SELECT COUNT(*) as total_filas FROM [{tabla}]"
                count_df = db.execute_query(count_query)
                total_filas = count_df.iloc[0]['total_filas']
                
                print(f"\n✅ {tabla}")
                print(f"   📝 {descripcion}")
                print(f"   📊 Total de filas: {total_filas:,}")
                
                # Obtener información de columnas
                sample_query = f"SELECT TOP 1 * FROM [{tabla}]"
                sample_df = db.execute_query(sample_query)
                
                print(f"   🔢 Total de columnas: {len(sample_df.columns)}")
                
                # Mostrar algunas columnas clave
                columnas_importantes = []
                for col in sample_df.columns:
                    if any(keyword in col.lower() for keyword in ['vendedor', 'fecha', 'total', 'cantidad', 'processed']):
                        columnas_importantes.append(col)
                
                if columnas_importantes:
                    print(f"   🎯 Columnas clave: {', '.join(columnas_importantes[:5])}")
                
                # Para tabla de resumen, mostrar datos de muestra
                if 'Summary' in tabla and total_filas > 0:
                    print(f"\n   📈 TOP 5 VENDEDORES (últimos 7 días):")
                    top_query = f"""
                    SELECT TOP 5 Vendedor, total_ofertas, cantidad_total, monto_total
                    FROM [{tabla}]
                    ORDER BY monto_total DESC
                    """
                    top_df = db.execute_query(top_query)
                    
                    pd.set_option('display.max_columns', 4)
                    pd.set_option('display.width', 80)
                    pd.set_option('display.max_colwidth', 20)
                    print(top_df.to_string(index=False, float_format='%.2f'))
                
                # Para tabla diaria, mostrar distribución por fecha
                elif 'Daily' in tabla and total_filas > 0:
                    print(f"\n   📅 DISTRIBUCIÓN POR FECHA:")
                    date_query = f"""
                    SELECT TOP 5
                        CAST([Fecha de oferta] as DATE) as Fecha,
                        COUNT(*) as Ofertas,
                        SUM([Cant. producto]) as Cantidad_Total,
                        SUM([Total]) as Monto_Total
                    FROM [{tabla}]
                    WHERE [Fecha de oferta] IS NOT NULL
                    GROUP BY CAST([Fecha de oferta] as DATE)
                    ORDER BY CAST([Fecha de oferta] as DATE) DESC
                    """
                    date_df = db.execute_query(date_query)
                    
                    if len(date_df) > 0:
                        print(date_df.to_string(index=False, float_format='%.2f'))
                
                tablas_encontradas.append(tabla)
                
            except Exception as e:
                if "Invalid object name" in str(e):
                    print(f"\n❌ {tabla}")
                    print(f"   📝 {descripcion}")
                    print(f"   ⚠️  Tabla no encontrada (no se ha ejecutado este pipeline)")
                else:
                    print(f"\n❌ {tabla}")
                    print(f"   📝 {descripcion}")
                    print(f"   ⚠️  Error: {str(e)}")
        
        # Resumen final
        print(f"\n" + "=" * 60)
        print(f"📊 RESUMEN:")
        print(f"   ✅ Tablas encontradas: {len(tablas_encontradas)}")
        print(f"   📋 Tablas disponibles: {', '.join(tablas_encontradas)}")
        
        if len(tablas_encontradas) > 0:
            print(f"\n🎯 COMANDOS DISPONIBLES:")
            print(f"   • python pipeline.py --mode daily       (Procesar últimos 7 días)")
            print(f"   • python pipeline.py --mode weekly      (Procesar últimos 30 días)")
            print(f"   • python pipeline.py --mode monthly     (Procesar últimos 30 días)")
            print(f"   • python pipeline.py --mode quarterly   (Procesar últimos 90 días)")
            print(f"   • python pipeline.py --mode summary     (Crear resumen por vendedores)")
            print(f"   • python pipeline.py --mode test        (Probar conexiones)")
        else:
            print(f"\n💡 PARA CREAR TABLAS ETL:")
            print(f"   • python pipeline.py --mode daily       (Crear tabla diaria)")
            print(f"   • python pipeline.py --mode monthly     (Crear tabla mensual)")
            print(f"   • python pipeline.py --mode quarterly   (Crear tabla trimestral)")
            print(f"   • python pipeline.py --mode summary     (Crear tabla resumen)")
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    verificar_tablas_etl()

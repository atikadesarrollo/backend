"""
Ejemplos de consultas para la tabla DL_Analisis_Venta_Quarterly
"""

# Ejemplos de consultas SQL para diferentes análisis

CONSULTAS_QUARTERLY = {
    
    # Consulta básica - todos los registros
    'todos_los_registros': """
        SELECT * FROM DL_Analisis_Venta_Quarterly
        ORDER BY [Fecha de oferta] DESC
    """,
    
    # Top vendedores por trimestre
    'top_vendedores_trimestre': """
        SELECT 
            YEAR([Fecha de oferta]) as año,
            DATEPART(quarter, [Fecha de oferta]) as trimestre,
            Vendedor,
            COUNT(*) as total_ventas,
            SUM(Total) as monto_total,
            AVG(Total) as promedio_venta
        FROM DL_Analisis_Venta_Quarterly
        GROUP BY YEAR([Fecha de oferta]), DATEPART(quarter, [Fecha de oferta]), Vendedor
        ORDER BY año DESC, trimestre DESC, monto_total DESC
    """,
    
    # Análisis por familia de productos
    'analisis_por_familia': """
        SELECT 
            Familia,
            COUNT(*) as cantidad_ventas,
            SUM([Cant. producto]) as cantidad_productos,
            SUM(Total) as monto_total,
            AVG(Total) as promedio_venta
        FROM DL_Analisis_Venta_Quarterly
        WHERE Familia IS NOT NULL
        GROUP BY Familia
        ORDER BY monto_total DESC
    """,
    
    # Ventas por cliente
    'top_clientes': """
        SELECT 
            Cliente,
            COUNT(*) as total_compras,
            SUM(Total) as monto_total,
            AVG(Total) as promedio_compra,
            MIN([Fecha de oferta]) as primera_compra,
            MAX([Fecha de oferta]) as ultima_compra
        FROM DL_Analisis_Venta_Quarterly
        GROUP BY Cliente
        ORDER BY monto_total DESC
    """,
    
    # Evolución mensual
    'evolucion_mensual': """
        SELECT 
            YEAR([Fecha de oferta]) as año,
            MONTH([Fecha de oferta]) as mes,
            COUNT(*) as total_ventas,
            SUM(Total) as monto_total,
            COUNT(DISTINCT Cliente) as clientes_unicos,
            COUNT(DISTINCT Vendedor) as vendedores_activos
        FROM DL_Analisis_Venta_Quarterly
        GROUP BY YEAR([Fecha de oferta]), MONTH([Fecha de oferta])
        ORDER BY año DESC, mes DESC
    """,
    
    # Análisis de estados
    'analisis_estados': """
        SELECT 
            Estado,
            COUNT(*) as cantidad,
            SUM(Total) as monto_total,
            AVG(Total) as promedio,
            (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM DL_Analisis_Venta_Quarterly)) as porcentaje
        FROM DL_Analisis_Venta_Quarterly
        GROUP BY Estado
        ORDER BY monto_total DESC
    """,
    
    # Productos más vendidos
    'productos_mas_vendidos': """
        SELECT 
            SKU,
            Descipción,
            Familia,
            SUM([Cant. producto]) as cantidad_vendida,
            COUNT(*) as numero_ventas,
            SUM(Total) as monto_total,
            AVG([RPT Precio unitario]) as precio_promedio
        FROM DL_Analisis_Venta_Quarterly
        WHERE SKU IS NOT NULL AND SKU != 'DESPACHO ATIKA'
        GROUP BY SKU, Descipción, Familia
        ORDER BY cantidad_vendida DESC
    """,
    
    # Análisis de descuentos
    'analisis_descuentos': """
        SELECT 
            CASE 
                WHEN [Descuento %] = 0 THEN 'Sin descuento'
                WHEN [Descuento %] <= 10 THEN '1-10%'
                WHEN [Descuento %] <= 20 THEN '11-20%'
                WHEN [Descuento %] <= 30 THEN '21-30%'
                ELSE 'Más de 30%'
            END as rango_descuento,
            COUNT(*) as cantidad_ventas,
            SUM(Total) as monto_total,
            AVG([Descuento %]) as descuento_promedio
        FROM DL_Analisis_Venta_Quarterly
        GROUP BY 
            CASE 
                WHEN [Descuento %] = 0 THEN 'Sin descuento'
                WHEN [Descuento %] <= 10 THEN '1-10%'
                WHEN [Descuento %] <= 20 THEN '11-20%'
                WHEN [Descuento %] <= 30 THEN '21-30%'
                ELSE 'Más de 30%'
            END
        ORDER BY monto_total DESC
    """
}

# Función para ejecutar cualquiera de estas consultas
def ejecutar_consulta_quarterly(tipo_consulta: str):
    """
    Ejecutar una consulta específica de la tabla quarterly
    
    Args:
        tipo_consulta: Clave del diccionario CONSULTAS_QUARTERLY
    """
    from database_connection import DatabaseConnection
    
    if tipo_consulta not in CONSULTAS_QUARTERLY:
        print(f"❌ Tipo de consulta '{tipo_consulta}' no válido")
        print("Consultas disponibles:")
        for key in CONSULTAS_QUARTERLY.keys():
            print(f"   - {key}")
        return None
    
    try:
        db = DatabaseConnection()
        query = CONSULTAS_QUARTERLY[tipo_consulta]
        
        print(f"🔍 Ejecutando consulta: {tipo_consulta}")
        print("=" * 50)
        
        df = db.execute_query(query)
        
        if not df.empty:
            print(f"✅ Consulta exitosa: {len(df)} registros")
            print(df.to_string(index=False))
            return df
        else:
            print("❌ No se encontraron datos")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None
    finally:
        try:
            db.close()
        except:
            pass

if __name__ == "__main__":
    # Ejemplo de uso
    print("Consultas disponibles para DL_Analisis_Venta_Quarterly:")
    for i, key in enumerate(CONSULTAS_QUARTERLY.keys(), 1):
        print(f"{i:2d}. {key}")
    
    print("\nEjemplo de uso:")
    print("ejecutar_consulta_quarterly('top_vendedores_trimestre')")

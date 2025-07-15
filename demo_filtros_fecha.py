#!/usr/bin/env python3
"""
Script de ejemplo para consumir la API con intervalos de fechas
"""

import requests
from datetime import datetime, timedelta
import pandas as pd

BASE_URL = "http://localhost:5000/api/analytics"

def get_data_by_date_range(period, fecha_desde, fecha_hasta, **filtros):
    """Obtener datos por rango de fechas"""
    params = {
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        **filtros
    }
    
    # Remover parámetros vacíos
    params = {k: v for k, v in params.items() if v}
    
    response = requests.get(f'{BASE_URL}/{period}/complete', params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

def demo_intervalos_fecha():
    """Demostrar diferentes usos de intervalos de fecha"""
    
    print("📅 DEMO: CONSUMIR API CON INTERVALOS DE FECHAS")
    print("="*60)
    
    # 1. Últimos 7 días
    print("\n1️⃣ ÚLTIMOS 7 DÍAS (DAILY):")
    try:
        fecha_hasta = datetime.now().strftime('%Y-%m-%d')
        fecha_desde = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        datos = get_data_by_date_range('daily', fecha_desde, fecha_hasta, limit=10)
        
        print(f"   📊 Total registros: {datos['total_records']:,}")
        print(f"   📅 Rango: {fecha_desde} → {fecha_hasta}")
        print(f"   📄 Mostrando: {len(datos['data'])} registros")
        
        if datos['data']:
            monto_total = sum(r.get('Total', 0) for r in datos['data'])
            print(f"   💰 Monto en muestra: ${monto_total:,.2f}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Mes específico (Julio 2025)
    print("\n2️⃣ MES ESPECÍFICO - JULIO 2025 (MONTHLY):")
    try:
        datos = get_data_by_date_range(
            'monthly', 
            '2025-07-01', 
            '2025-07-31',
            limit=15
        )
        
        print(f"   📊 Registros en julio: {datos['total_records']:,}")
        print(f"   📄 Mostrando: {len(datos['data'])} registros")
        
        if datos['data']:
            # Análisis de los datos
            vendedores = set(r.get('Vendedor', '') for r in datos['data'] if r.get('Vendedor'))
            clientes = set(r.get('Cliente', '') for r in datos['data'] if r.get('Cliente'))
            monto_total = sum(r.get('Total', 0) for r in datos['data'])
            
            print(f"   👥 Vendedores únicos en muestra: {len(vendedores)}")
            print(f"   🏢 Clientes únicos en muestra: {len(clientes)}")
            print(f"   💰 Monto total en muestra: ${monto_total:,.2f}")
            
            # Top 3 vendedores por monto
            vendedores_monto = {}
            for record in datos['data']:
                vendedor = record.get('Vendedor', 'Sin vendedor')
                monto = record.get('Total', 0)
                vendedores_monto[vendedor] = vendedores_monto.get(vendedor, 0) + monto
            
            top_vendedores = sorted(vendedores_monto.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"   🏆 Top 3 vendedores en muestra:")
            for i, (vendedor, monto) in enumerate(top_vendedores, 1):
                print(f"      {i}. {vendedor}: ${monto:,.2f}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Filtros combinados: Vendedor + Fechas
    print("\n3️⃣ FILTROS COMBINADOS - VENDEDOR + FECHAS:")
    try:
        # Buscar un vendedor que tenga datos
        datos_sample = get_data_by_date_range('monthly', '2025-06-01', '2025-07-31', limit=50)
        
        if datos_sample['data']:
            vendedor_ejemplo = None
            for record in datos_sample['data']:
                if record.get('Vendedor') and record.get('Vendedor').strip():
                    vendedor_ejemplo = record['Vendedor']
                    break
            
            if vendedor_ejemplo:
                datos_vendedor = get_data_by_date_range(
                    'monthly',
                    '2025-06-01',
                    '2025-07-31',
                    vendedor=vendedor_ejemplo,
                    limit=20
                )
                
                print(f"   👤 Vendedor: {vendedor_ejemplo}")
                print(f"   📊 Registros Jun-Jul: {datos_vendedor['total_records']:,}")
                print(f"   📄 Mostrando: {len(datos_vendedor['data'])} registros")
                
                if datos_vendedor['data']:
                    monto_vendedor = sum(r.get('Total', 0) for r in datos_vendedor['data'])
                    print(f"   💰 Monto en muestra: ${monto_vendedor:,.2f}")
                    
                    # Productos más vendidos por este vendedor
                    productos = {}
                    for record in datos_vendedor['data']:
                        producto = record.get('Descipción', 'Sin descripción')[:50]
                        monto = record.get('Total', 0)
                        productos[producto] = productos.get(producto, 0) + monto
                    
                    top_productos = sorted(productos.items(), key=lambda x: x[1], reverse=True)[:3]
                    print(f"   📦 Top 3 productos del vendedor:")
                    for i, (producto, monto) in enumerate(top_productos, 1):
                        print(f"      {i}. {producto}...: ${monto:,.2f}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Comparación entre períodos
    print("\n4️⃣ COMPARACIÓN ENTRE PERÍODOS:")
    try:
        # Semana actual vs semana anterior
        hoy = datetime.now()
        
        # Semana actual (últimos 7 días)
        fin_semana_actual = hoy.strftime('%Y-%m-%d')
        inicio_semana_actual = (hoy - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Semana anterior (días 8-14 atrás)
        fin_semana_anterior = (hoy - timedelta(days=7)).strftime('%Y-%m-%d')
        inicio_semana_anterior = (hoy - timedelta(days=14)).strftime('%Y-%m-%d')
        
        # Obtener datos de ambas semanas
        datos_actual = get_data_by_date_range('daily', inicio_semana_actual, fin_semana_actual)
        datos_anterior = get_data_by_date_range('daily', inicio_semana_anterior, fin_semana_anterior)
        
        registros_actual = datos_actual['total_records']
        registros_anterior = datos_anterior['total_records']
        
        print(f"   📊 Semana actual ({inicio_semana_actual} → {fin_semana_actual}): {registros_actual:,} registros")
        print(f"   📊 Semana anterior ({inicio_semana_anterior} → {fin_semana_anterior}): {registros_anterior:,} registros")
        
        if registros_anterior > 0:
            cambio_porcentual = ((registros_actual - registros_anterior) / registros_anterior) * 100
            emoji = "📈" if cambio_porcentual > 0 else "📉" if cambio_porcentual < 0 else "➡️"
            print(f"   {emoji} Cambio: {cambio_porcentual:+.1f}%")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 5. Análisis de tendencia mensual
    print("\n5️⃣ ANÁLISIS DE TENDENCIA (ÚLTIMOS 3 MESES):")
    try:
        tendencia_datos = []
        
        for i in range(3):
            # Calcular mes
            fecha_fin = datetime.now() - timedelta(days=30 * i)
            fecha_inicio = fecha_fin - timedelta(days=30)
            
            datos_mes = get_data_by_date_range(
                'monthly',
                fecha_inicio.strftime('%Y-%m-%d'),
                fecha_fin.strftime('%Y-%m-%d')
            )
            
            mes_nombre = fecha_fin.strftime('%B %Y')
            registros = datos_mes['total_records']
            
            tendencia_datos.append({
                'mes': mes_nombre,
                'registros': registros,
                'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
                'fecha_fin': fecha_fin.strftime('%Y-%m-%d')
            })
            
            print(f"   📅 {mes_nombre}: {registros:,} registros")
        
        # Mostrar tendencia
        if len(tendencia_datos) >= 2:
            ultimo_mes = tendencia_datos[0]['registros']
            mes_anterior = tendencia_datos[1]['registros']
            
            if mes_anterior > 0:
                tendencia = ((ultimo_mes - mes_anterior) / mes_anterior) * 100
                emoji_tendencia = "📈" if tendencia > 0 else "📉" if tendencia < 0 else "➡️"
                print(f"   {emoji_tendencia} Tendencia último mes: {tendencia:+.1f}%")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def exportar_datos_fecha():
    """Ejemplo de exportación con filtros de fecha"""
    print("\n6️⃣ EXPORTACIÓN CON FILTROS DE FECHA:")
    try:
        # Exportar datos de julio a CSV
        datos = get_data_by_date_range(
            'monthly',
            '2025-07-01',
            '2025-07-31',
            limit=1000  # Obtener más datos para exportación
        )
        
        if datos['data']:
            df = pd.DataFrame(datos['data'])
            filename = f"ventas_julio_2025_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            print(f"   ✅ Exportado: {filename}")
            print(f"   📊 Registros exportados: {len(datos['data']):,}")
            print(f"   📅 Período: 2025-07-01 → 2025-07-31")
            print(f"   📋 Columnas: {', '.join(df.columns.tolist()[:5])}...")
        else:
            print(f"   ⚠️ No hay datos para exportar en el período seleccionado")
        
    except Exception as e:
        print(f"   ❌ Error en exportación: {e}")

if __name__ == "__main__":
    try:
        demo_intervalos_fecha()
        exportar_datos_fecha()
        
        print(f"\n✅ DEMO COMPLETADO")
        print("="*60)
        print("📚 Documentación completa:")
        print("   • API_FECHA_GUIDE.md - Guía de filtros de fecha")
        print("   • API_MONTHLY_GUIDE.md - Guía específica monthly")
        print("   • all_periods_viewer.html - Visualizador web")
        print("\n🔗 URLs de ejemplo:")
        print("   • Últimos 7 días: http://localhost:5000/api/analytics/daily/complete?fecha_desde=2025-07-03&fecha_hasta=2025-07-10")
        print("   • Julio 2025: http://localhost:5000/api/analytics/monthly/complete?fecha_desde=2025-07-01&fecha_hasta=2025-07-31")
        print("   • Con vendedor: http://localhost:5000/api/analytics/monthly/complete?vendedor=Juan&fecha_desde=2025-07-01")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor.")
        print("   Asegúrate de que esté ejecutándose en http://localhost:5000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

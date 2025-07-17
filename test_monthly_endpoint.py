#!/usr/bin/env python3
"""
Ejemplos prácticos para consumir el endpoint de análisis mensual
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000/api/analytics/monthly"

def test_monthly_endpoint():
    """Probar diferentes usos del endpoint monthly"""
    
    print("🔍 EJEMPLOS DE USO - ENDPOINT MONTHLY")
    print("="*50)
    
    # 1. Información general
    print("\n1️⃣ INFORMACIÓN GENERAL DE LA TABLA MONTHLY:")
    try:
        response = requests.get(f"{BASE_URL}/info")
        if response.status_code == 200:
            info = response.json()['data']['general_info']
            print(f"   📊 Total registros: {info['total_registros']:,}")
            print(f"   📅 Rango fechas: {info['fecha_minima']} → {info['fecha_maxima']}")
            print(f"   💰 Monto total: ${info['monto_total']:,.2f}")
            print(f"   👥 Vendedores únicos: {info['vendedores_unicos']}")
            print(f"   🏢 Clientes únicos: {info['clientes_unicos']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Primeros 5 registros
    print("\n2️⃣ PRIMEROS 5 REGISTROS:")
    try:
        response = requests.get(f"{BASE_URL}/complete?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"   📄 Mostrando {len(data['data'])} de {data['total_records']:,} registros")
            for i, record in enumerate(data['data'], 1):
                fecha = record.get('Fecha de oferta', 'N/A')[:10] if record.get('Fecha de oferta') else 'N/A'
                vendedor = record.get('Vendedor', 'N/A')
                cliente = record.get('Cliente', 'N/A')[:30] + '...' if len(record.get('Cliente', '')) > 30 else record.get('Cliente', 'N/A')
                total = record.get('Total', 0)
                print(f"   {i}. {fecha} | {vendedor} | {cliente} | ${total:,.2f}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Filtros por vendedor
    print("\n3️⃣ FILTRO POR VENDEDOR (Primeros 3 vendedores):")
    try:
        # Primero obtener lista de vendedores únicos
        response = requests.get(f"{BASE_URL}/complete?limit=50")
        if response.status_code == 200:
            data = response.json()
            vendedores = list(set([r.get('Vendedor', '') for r in data['data'] if r.get('Vendedor')]))[:3]
            
            for vendedor in vendedores:
                if vendedor:
                    vendor_response = requests.get(f"{BASE_URL}/complete", params={'vendedor': vendedor, 'limit': 3})
                    if vendor_response.status_code == 200:
                        vendor_data = vendor_response.json()
                        print(f"   👤 {vendedor}: {vendor_data['total_records']} registros")
                        if vendor_data['data']:
                            total_ventas = sum(r.get('Total', 0) for r in vendor_data['data'])
                            print(f"      💰 Muestra de ventas: ${total_ventas:,.2f}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Filtros por fecha
    print("\n4️⃣ FILTRO POR FECHA (Últimos 7 días):")
    try:
        fecha_desde = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        response = requests.get(f"{BASE_URL}/complete", params={
            'fecha_desde': fecha_desde,
            'limit': 5
        })
        if response.status_code == 200:
            data = response.json()
            print(f"   📅 Desde {fecha_desde}: {data['total_records']} registros")
            if data['data']:
                monto_reciente = sum(r.get('Total', 0) for r in data['data'])
                print(f"   💰 Monto en muestra: ${monto_reciente:,.2f}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 5. Paginación
    print("\n5️⃣ EJEMPLO DE PAGINACIÓN:")
    try:
        total_pages = 3
        limit = 10
        
        for page in range(total_pages):
            offset = page * limit
            response = requests.get(f"{BASE_URL}/complete", params={
                'limit': limit,
                'offset': offset
            })
            if response.status_code == 200:
                data = response.json()
                print(f"   📄 Página {page + 1}: registros {offset + 1}-{offset + len(data['data'])} de {data['total_records']:,}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 6. Análisis de estados
    print("\n6️⃣ ANÁLISIS POR ESTADO:")
    try:
        response = requests.get(f"{BASE_URL}/complete?limit=100")
        if response.status_code == 200:
            data = response.json()
            estados = {}
            for record in data['data']:
                estado = record.get('Estado', 'Sin Estado')
                if estado not in estados:
                    estados[estado] = {'count': 0, 'monto': 0}
                estados[estado]['count'] += 1
                estados[estado]['monto'] += record.get('Total', 0)
            
            print("   📊 Estados en muestra de 100 registros:")
            for estado, stats in estados.items():
                print(f"      {estado}: {stats['count']} registros, ${stats['monto']:,.2f}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def export_monthly_to_csv():
    """Exportar datos mensuales a CSV"""
    print("\n7️⃣ EXPORTACIÓN A CSV:")
    try:
        # Obtener datos con paginación
        all_data = []
        offset = 0
        limit = 1000
        
        while True:
            response = requests.get(f"{BASE_URL}/complete", params={
                'limit': limit,
                'offset': offset
            })
            
            if response.status_code == 200:
                batch = response.json()
                all_data.extend(batch['data'])
                
                print(f"   📥 Descargados {len(all_data)} registros...")
                
                if len(batch['data']) < limit:
                    break
                offset += limit
                
                # Limitar para ejemplo (no descargar todo)
                if len(all_data) >= 2000:
                    print("   ⚠️ Limitando descarga a 2000 registros para ejemplo")
                    break
            else:
                break
        
        if all_data:
            # Crear DataFrame y exportar
            df = pd.DataFrame(all_data)
            filename = f"monthly_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"   ✅ Exportado: {filename} ({len(all_data)} registros)")
            print(f"   📊 Columnas: {', '.join(df.columns.tolist()[:5])}...")
        
    except Exception as e:
        print(f"   ❌ Error en exportación: {e}")

def test_advanced_filters():
    """Probar filtros avanzados"""
    print("\n8️⃣ FILTROS AVANZADOS:")
    
    filters_to_test = [
        {'categoria': 'ALIMENTOS', 'name': 'Categoría: ALIMENTOS'},
        {'estado': 'Entregado', 'name': 'Estado: Entregado'},
        {'familia': 'BEBIDAS', 'name': 'Familia: BEBIDAS'},
        {'canal': 'RETAIL', 'name': 'Canal: RETAIL'}
    ]
    
    for filter_test in filters_to_test:
        try:
            name = filter_test.pop('name')
            response = requests.get(f"{BASE_URL}/complete", params={**filter_test, 'limit': 5})
            
            if response.status_code == 200:
                data = response.json()
                print(f"   🔍 {name}: {data['total_records']} registros")
                if data['data']:
                    sample_total = sum(r.get('Total', 0) for r in data['data'])
                    print(f"      💰 Muestra: ${sample_total:,.2f}")
        except Exception as e:
            print(f"   ❌ Error con filtro {name}: {e}")

if __name__ == "__main__":
    try:
        test_monthly_endpoint()
        export_monthly_to_csv()
        test_advanced_filters()
        
        print(f"\n✅ PRUEBAS COMPLETADAS")
        print("="*50)
        print("📚 Documentación completa en: API_MONTHLY_GUIDE.md")
        print("🌐 Visualizador web: all_periods_viewer.html")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor.")
        print("   Asegúrate de que esté ejecutándose en http://localhost:5000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

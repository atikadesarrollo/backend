"""
Script de prueba para endpoints de KPIs
"""
import requests
import json
from datetime import datetime, timedelta

# URL base del API
BASE_URL = 'http://localhost:5000'

def test_kpis_analisis_venta():
    """Prueba el endpoint de KPIs de análisis de venta"""
    
    print("="*80)
    print("TEST: Endpoint /analisis_venta/kpis")
    print("="*80)
    
    # Definir período de prueba (últimos 30 días)
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=30)
    
    params = {
        'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
        'fecha_fin': fecha_fin.strftime('%Y-%m-%d')
    }
    
    print(f"\n📅 Período: {params['fecha_inicio']} a {params['fecha_fin']}")
    print(f"🔗 URL: {BASE_URL}/analisis_venta/kpis")
    print(f"📋 Parámetros: {params}")
    
    try:
        response = requests.get(f'{BASE_URL}/analisis_venta/kpis', params=params, timeout=30)
        
        print(f"\n✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n" + "="*80)
            print("📊 KPIs PRINCIPALES")
            print("="*80)
            
            kpis = data.get('kpis_principales', {})
            print(f"\n👥 Cantidad de clientes: {kpis.get('cantidad_clientes', 0):,}")
            print(f"📄 Cantidad de transacciones: {kpis.get('cantidad_transacciones', 0):,}")
            print(f"🆕 Clientes nuevos: {kpis.get('cantidad_clientes_nuevos', 0):,}")
            print(f"📈 Porcentaje clientes nuevos: {kpis.get('porcentaje_clientes_nuevos', 0)}%")
            print(f"💰 Venta total: ${kpis.get('venta_total', 0):,.2f}")
            print(f"🎫 Ticket promedio: ${kpis.get('ticket_promedio', 0):,.2f}")
            print(f"🤝 Total vendedores: {kpis.get('total_vendedores', 0):,}")
            print(f"🏗️ Total proyectos: {kpis.get('total_proyectos', 0):,}")
            
            print("\n" + "="*80)
            print("📊 VENTA POR CANAL")
            print("="*80)
            
            for canal in data.get('venta_por_canal', []):
                print(f"\n🔹 {canal['canal']}")
                print(f"   Venta: ${canal['venta_total']:,.2f} ({canal['porcentaje']}%)")
                print(f"   Transacciones: {canal['transacciones']:,}")
                print(f"   Clientes: {canal['clientes']:,}")
            
            print("\n" + "="*80)
            print("📊 VENTA POR DEPARTAMENTO")
            print("="*80)
            
            for dept in data.get('venta_por_departamento', []):
                print(f"\n🔹 {dept['departamento']}")
                print(f"   Venta: ${dept['venta_total']:,.2f} ({dept['porcentaje']}%)")
                print(f"   Transacciones: {dept['transacciones']:,}")
                print(f"   Clientes: {dept['clientes']:,}")
            
            print("\n" + "="*80)
            print("✅ TEST EXITOSO")
            print("="*80)
            
            # Guardar respuesta completa en archivo
            with open('test_kpis_response.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("\n💾 Respuesta completa guardada en: test_kpis_response.json")
            
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar al servidor")
        print("   Asegúrate de que el servidor esté corriendo en http://localhost:5000")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def test_top_clientes():
    """Prueba el endpoint de top clientes"""
    
    print("\n\n" + "="*80)
    print("TEST: Endpoint /analisis_venta/top (clientes)")
    print("="*80)
    
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=30)
    
    params = {
        'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
        'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
        'tipo': 'clientes',
        'limit': 10
    }
    
    print(f"\n📅 Período: {params['fecha_inicio']} a {params['fecha_fin']}")
    print(f"🔗 URL: {BASE_URL}/analisis_venta/top")
    print(f"📋 Parámetros: {params}")
    
    try:
        response = requests.get(f'{BASE_URL}/analisis_venta/top', params=params, timeout=30)
        
        print(f"\n✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n" + "="*80)
            print("🏆 TOP 10 CLIENTES")
            print("="*80)
            
            for cliente in data.get('top', []):
                print(f"\n#{cliente['rank']} - {cliente['nombre']}")
                print(f"   💰 Venta: ${cliente['venta_total']:,.2f}")
                print(f"   📄 Transacciones: {cliente['transacciones']:,}")
                print(f"   🎫 Ticket promedio: ${cliente['ticket_promedio']:,.2f}")
            
            print("\n" + "="*80)
            print("✅ TEST EXITOSO")
            print("="*80)
            
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def test_kpis_con_filtros():
    """Prueba KPIs con filtros adicionales"""
    
    print("\n\n" + "="*80)
    print("TEST: KPIs con Filtros (Canal: Retail)")
    print("="*80)
    
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=90)
    
    params = {
        'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
        'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
        'canal': 'Retail'
    }
    
    print(f"\n📅 Período: {params['fecha_inicio']} a {params['fecha_fin']}")
    print(f"🏪 Filtro Canal: {params['canal']}")
    
    try:
        response = requests.get(f'{BASE_URL}/analisis_venta/kpis', params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            kpis = data.get('kpis_principales', {})
            
            print(f"\n👥 Clientes: {kpis.get('cantidad_clientes', 0):,}")
            print(f"📄 Transacciones: {kpis.get('cantidad_transacciones', 0):,}")
            print(f"📈 % Clientes nuevos: {kpis.get('porcentaje_clientes_nuevos', 0)}%")
            print(f"💰 Venta total: ${kpis.get('venta_total', 0):,.2f}")
            
            print("\n✅ TEST EXITOSO")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║                   TEST DE ENDPOINTS DE KPIs                               ║
    ║                     Análisis de Venta                                     ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Ejecutar tests
    test_kpis_analisis_venta()
    test_top_clientes()
    test_kpis_con_filtros()
    
    print("\n\n" + "="*80)
    print("🎉 TESTS COMPLETADOS")
    print("="*80)

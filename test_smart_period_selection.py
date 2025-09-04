#!/usr/bin/env python3
"""
Script de demostración para la selección automática de períodos
basada en rangos de fechas
"""

from datetime import datetime, timedelta
import requests

def test_date_range_optimization():
    """Probar diferentes rangos de fechas y ver qué período se recomienda"""
    
    print("🧪 PRUEBA DE OPTIMIZACIÓN POR RANGO DE FECHAS")
    print("="*60)
    
    # Casos de prueba con diferentes rangos
    test_cases = [
        {
            'name': 'Rango de 3 días (Corto)',
            'days': 3,
            'expected': 'daily'
        },
        {
            'name': 'Rango de 1 semana (Semanal)',
            'days': 7,
            'expected': 'daily'
        },
        {
            'name': 'Rango de 2 semanas (Bi-semanal)',
            'days': 14,
            'expected': 'weekly'
        },
        {
            'name': 'Rango de 1 mes (Mensual)',
            'days': 30,
            'expected': 'weekly'
        },
        {
            'name': 'Rango de 2 meses (Bi-mensual)',
            'days': 60,
            'expected': 'monthly'
        },
        {
            'name': 'Rango de 3 meses (Trimestral)',
            'days': 90,
            'expected': 'monthly'
        },
        {
            'name': 'Rango de 6 meses (Semestral)',
            'days': 180,
            'expected': 'quarterly'
        },
        {
            'name': 'Rango de 1 año (Anual)',
            'days': 365,
            'expected': 'quarterly'
        },
        {
            'name': 'Rango de 2 años (Bi-anual)',
            'days': 730,
            'expected': 'quarterly'
        }
    ]
    
    # Obtener fecha base (hoy)
    end_date = datetime.now()
    
    print(f"📅 Fecha base: {end_date.strftime('%Y-%m-%d')}")
    print()
    
    for i, case in enumerate(test_cases, 1):
        start_date = end_date - timedelta(days=case['days'])
        fecha_desde = start_date.strftime('%Y-%m-%d')
        fecha_hasta = end_date.strftime('%Y-%m-%d')
        
        print(f"{i}. {case['name']}")
        print(f"   📅 Rango: {fecha_desde} → {fecha_hasta}")
        print(f"   📊 Días: {case['days']}")
        print(f"   🎯 Período esperado: {case['expected'].upper()}")
        
        # Lógica de selección (replicada del frontend)
        if case['days'] <= 7:
            suggested = 'daily'
            reason = f"Rango corto ({case['days']} días)"
        elif case['days'] <= 30:
            suggested = 'weekly'
            reason = f"Rango medio ({case['days']} días)"
        elif case['days'] <= 90:
            suggested = 'monthly'
            reason = f"Rango extendido ({case['days']} días)"
        else:
            suggested = 'quarterly'
            reason = f"Rango largo ({case['days']} días)"
        
        match = "✅" if suggested == case['expected'] else "❌"
        print(f"   🤖 Período sugerido: {suggested.upper()} - {reason}")
        print(f"   {match} Coincide con expectativa")
        print()

def test_api_with_different_periods():
    """Probar la API con diferentes períodos para comparar rendimiento"""
    
    print("🚀 PRUEBA DE RENDIMIENTO POR PERÍODO")
    print("="*60)
    
    # Rango de prueba: últimos 30 días
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    fecha_desde = start_date.strftime('%Y-%m-%d')
    fecha_hasta = end_date.strftime('%Y-%m-%d')
    
    print(f"📅 Rango de prueba: {fecha_desde} → {fecha_hasta} (30 días)")
    print()
    
    periods_to_test = ['daily', 'weekly', 'monthly', 'quarterly']
    results = []
    
    for period in periods_to_test:
        print(f"🔍 Probando período: {period.upper()}")
        
        try:
            # Probar endpoint de información
            start_time = datetime.now()
            
            info_response = requests.get(f'http://localhost:5000/api/analytics/{period}/info')
            
            if info_response.status_code == 200:
                info_data = info_response.json()
                info_time = (datetime.now() - start_time).total_seconds()
                
                # Probar endpoint de datos
                data_start = datetime.now()
                
                data_response = requests.get(
                    f'http://localhost:5000/api/analytics/{period}/complete',
                    params={
                        'fecha_desde': fecha_desde,
                        'fecha_hasta': fecha_hasta,
                        'limit': 100
                    }
                )
                
                if data_response.status_code == 200:
                    data_result = data_response.json()
                    data_time = (datetime.now() - data_start).total_seconds()
                    
                    result = {
                        'period': period,
                        'total_records': info_data['data']['general_info'].get('total_registros', 0),
                        'filtered_records': data_result['total_records'],
                        'returned_records': len(data_result['data']),
                        'info_time': info_time,
                        'data_time': data_time,
                        'total_time': info_time + data_time
                    }
                    
                    results.append(result)
                    
                    print(f"   📊 Registros totales: {result['total_records']:,}")
                    print(f"   🎯 Registros filtrados: {result['filtered_records']:,}")
                    print(f"   📄 Registros devueltos: {result['returned_records']}")
                    print(f"   ⏱️ Tiempo info: {result['info_time']:.3f}s")
                    print(f"   ⏱️ Tiempo datos: {result['data_time']:.3f}s")
                    print(f"   ⏱️ Tiempo total: {result['total_time']:.3f}s")
                    print()
                else:
                    print(f"   ❌ Error en datos: {data_response.status_code}")
                    print()
            else:
                print(f"   ❌ Error en info: {info_response.status_code}")
                print()
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print()
    
    # Mostrar recomendación
    if results:
        print("📋 RESUMEN Y RECOMENDACIÓN")
        print("-" * 40)
        
        # Período más rápido
        fastest = min(results, key=lambda x: x['total_time'])
        print(f"⚡ Más rápido: {fastest['period'].upper()} ({fastest['total_time']:.3f}s)")
        
        # Período con más datos relevantes
        most_relevant = max(results, key=lambda x: x['filtered_records'])
        print(f"📊 Más datos: {most_relevant['period'].upper()} ({most_relevant['filtered_records']:,} registros)")
        
        # Recomendación para 30 días
        recommended = next((r for r in results if r['period'] == 'weekly'), results[0])
        print(f"🎯 Recomendado para 30 días: {recommended['period'].upper()}")
        print(f"   Razón: Balance entre velocidad y cantidad de datos")

def test_smart_selection_examples():
    """Ejemplos de casos de uso para selección inteligente"""
    
    print("💡 EJEMPLOS DE CASOS DE USO")
    print("="*60)
    
    examples = [
        {
            'scenario': 'Dashboard diario de ventas',
            'range': 'Últimos 7 días',
            'optimal': 'DAILY',
            'reason': 'Granularidad máxima para análisis reciente'
        },
        {
            'scenario': 'Reporte semanal para gerencia',
            'range': 'Últimas 4 semanas',
            'optimal': 'WEEKLY',
            'reason': 'Balance entre detalle y rendimiento'
        },
        {
            'scenario': 'Análisis mensual de tendencias',
            'range': 'Últimos 3 meses',
            'optimal': 'MONTHLY',
            'reason': 'Datos agregados ideales para tendencias'
        },
        {
            'scenario': 'Reporte trimestral ejecutivo',
            'range': 'Último año',
            'optimal': 'QUARTERLY',
            'reason': 'Vista de alto nivel para decisiones estratégicas'
        },
        {
            'scenario': 'Análisis de performance de vendedor',
            'range': 'Últimas 2 semanas',
            'optimal': 'WEEKLY',
            'reason': 'Suficiente detalle sin sobrecarga de datos'
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['scenario']}")
        print(f"   📅 Rango típico: {example['range']}")
        print(f"   🎯 Período óptimo: {example['optimal']}")
        print(f"   💡 Razón: {example['reason']}")
        print()

if __name__ == "__main__":
    try:
        test_date_range_optimization()
        print()
        test_api_with_different_periods()
        print()
        test_smart_selection_examples()
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor API.")
        print("   Asegúrate de que esté ejecutándose en http://localhost:5000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

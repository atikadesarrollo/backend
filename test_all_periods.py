#!/usr/bin/env python3
"""
Test script para verificar todos los períodos ETL
"""

import requests
import json
from datetime import datetime

def test_all_periods():
    """Probar todos los períodos disponibles"""
    base_url = "http://localhost:5000/api/analytics"
    
    print("🧪 PROBANDO API DE ANALYTICS - TODOS LOS PERÍODOS")
    print("="*60)
    
    # 1. Verificar períodos disponibles
    print("\n1️⃣  PERÍODOS DISPONIBLES:")
    response = requests.get(f"{base_url}/periods/available")
    if response.status_code == 200:
        periods_data = response.json()['data']
        for period in periods_data:
            status = "✅" if period['available'] else "❌"
            print(f"   {status} {period['display_name']}: {period['record_count']:,} registros")
    else:
        print("   ❌ Error obteniendo períodos disponibles")
        return
    
    # 2. Probar cada período disponible
    available_periods = [p['period'] for p in periods_data if p['available']]
    
    for period in available_periods:
        print(f"\n2️⃣  PROBANDO PERÍODO: {period.upper()}")
        print("-" * 40)
        
        # Info del período
        info_response = requests.get(f"{base_url}/{period}/info")
        if info_response.status_code == 200:
            info_data = info_response.json()['data']
            general = info_data['general_info']
            print(f"   📊 Total registros: {general.get('total_registros', 'N/A'):,}")
            print(f"   📅 Rango fechas: {general.get('fecha_minima', 'N/A')} → {general.get('fecha_maxima', 'N/A')}")
            print(f"   💰 Monto total: ${general.get('monto_total', 0):,.2f}")
            print(f"   👥 Vendedores únicos: {general.get('vendedores_unicos', 'N/A')}")
        
        # Datos de muestra
        data_response = requests.get(f"{base_url}/{period}/complete?limit=3")
        if data_response.status_code == 200:
            sample_data = data_response.json()
            print(f"   📄 Muestra de datos: {len(sample_data['data'])} registros de {sample_data['total_records']:,}")
        else:
            print(f"   ❌ Error obteniendo datos de muestra: {data_response.status_code}")
    
    # 3. Resumen final
    print(f"\n3️⃣  RESUMEN FINAL:")
    print("-" * 40)
    total_records = sum(p['record_count'] for p in periods_data if p['available'])
    available_count = len([p for p in periods_data if p['available']])
    
    print(f"   📈 Períodos disponibles: {available_count}/5")
    print(f"   📊 Total registros: {total_records:,}")
    print(f"   ✅ Estado general: {'Todos los períodos funcionando' if available_count == 5 else 'Algunos períodos no disponibles'}")
    
    return True

if __name__ == "__main__":
    try:
        test_all_periods()
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor. Asegúrate de que esté ejecutándose en http://localhost:5000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

"""
Script de prueba para validar endpoints de Analytics API
Permite probar los endpoints desde línea de comandos
"""

import requests
import json
import sys
from datetime import datetime

class AnalyticsAPITester:
    """Tester para la API de Analytics"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
    
    def test_health(self):
        """Probar endpoint de health"""
        print("🔍 TESTING HEALTH ENDPOINT")
        print("="*50)
        
        try:
            response = self.session.get(f"{self.base_url}/api/analytics/health")
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_available_periods(self):
        """Probar endpoint de períodos disponibles"""
        print("\n🔍 TESTING AVAILABLE PERIODS")
        print("="*50)
        
        try:
            response = self.session.get(f"{self.base_url}/api/analytics/periods")
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print(f"Available Periods: {len(data.get('data', []))}")
            
            for period in data.get('data', []):
                print(f"  - {period['display_name']} ({period['period']}) -> {period['table_name']}")
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_sales_data(self, period="daily", limit=10):
        """Probar endpoint de datos de ventas"""
        print(f"\n🔍 TESTING SALES DATA - {period.upper()}")
        print("="*50)
        
        try:
            params = {
                'limit': limit,
                'offset': 0
            }
            
            response = self.session.get(
                f"{self.base_url}/api/analytics/sales/{period}",
                params=params
            )
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            
            if data.get('success'):
                print(f"Total Records: {data.get('total_records', 0)}")
                print(f"Records Retrieved: {len(data.get('data', []))}")
                
                # Mostrar primera fila como ejemplo
                if data.get('data'):
                    first_record = data['data'][0]
                    print("\n📊 SAMPLE RECORD:")
                    for key, value in first_record.items():
                        if isinstance(value, (int, float)) and key in ['Monto orden', 'Cantidad entregada']:
                            print(f"  {key}: {value:,.2f}")
                        else:
                            print(f"  {key}: {value}")
            else:
                print(f"❌ Error: {data.get('message')}")
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_sales_with_filters(self, period="daily"):
        """Probar endpoint con filtros"""
        print(f"\n🔍 TESTING SALES DATA WITH FILTERS - {period.upper()}")
        print("="*50)
        
        try:
            params = {
                'limit': 5,
                'offset': 0,
                'vendedor': 'Angel'  # Buscar vendedores que contengan "Angel"
            }
            
            response = self.session.get(
                f"{self.base_url}/api/analytics/sales/{period}",
                params=params
            )
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            
            if data.get('success'):
                print(f"Filtered Records: {len(data.get('data', []))}")
                print(f"Filter: vendedor contains 'Angel'")
                
                # Mostrar vendedores encontrados
                vendedores = set()
                for record in data.get('data', []):
                    vendedores.add(record.get('Vendedor', 'N/A'))
                
                print(f"Vendedores encontrados: {list(vendedores)}")
            else:
                print(f"❌ Error: {data.get('message')}")
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_summary_data(self, period="daily", group_by="vendedor"):
        """Probar endpoint de resumen"""
        print(f"\n🔍 TESTING SUMMARY DATA - {period.upper()} BY {group_by.upper()}")
        print("="*50)
        
        try:
            params = {
                'group_by': group_by
            }
            
            response = self.session.get(
                f"{self.base_url}/api/analytics/summary/{period}",
                params=params
            )
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            
            if data.get('success'):
                records = data.get('data', [])
                print(f"Summary Records: {len(records)}")
                
                # Mostrar top 5 registros
                print(f"\n📈 TOP 5 {group_by.upper()}S:")
                for i, record in enumerate(records[:5]):
                    if group_by == 'vendedor':
                        print(f"  {i+1}. {record.get('Vendedor', 'N/A')} - ${record.get('monto_total', 0):,.2f}")
                    elif group_by == 'date':
                        print(f"  {i+1}. {record.get('fecha', 'N/A')} - ${record.get('monto_total', 0):,.2f}")
                    elif group_by == 'categoria':
                        print(f"  {i+1}. {record.get('Categoria', 'N/A')} - ${record.get('monto_total', 0):,.2f}")
            else:
                print(f"❌ Error: {data.get('message')}")
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_top_performers(self, period="daily", metric="monto", limit=5):
        """Probar endpoint de top performers"""
        print(f"\n🔍 TESTING TOP PERFORMERS - {period.upper()} BY {metric.upper()}")
        print("="*50)
        
        try:
            params = {
                'metric': metric,
                'limit': limit
            }
            
            response = self.session.get(
                f"{self.base_url}/api/analytics/top/{period}",
                params=params
            )
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            
            if data.get('success'):
                records = data.get('data', [])
                print(f"Top Performers: {len(records)}")
                
                print(f"\n🏆 TOP {limit} BY {metric.upper()}:")
                for i, record in enumerate(records):
                    vendedor = record.get('Vendedor', 'N/A')
                    metric_value = record.get('metric_value', 0)
                    ofertas = record.get('total_ofertas', 0)
                    
                    if metric == 'monto':
                        print(f"  {i+1}. {vendedor} - ${metric_value:,.2f} ({ofertas} ofertas)")
                    else:
                        print(f"  {i+1}. {vendedor} - {metric_value:,.2f} ({ofertas} ofertas)")
            else:
                print(f"❌ Error: {data.get('message')}")
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_kpis(self, period="daily"):
        """Probar endpoint de KPIs"""
        print(f"\n🔍 TESTING KPIs - {period.upper()}")
        print("="*50)
        
        try:
            response = self.session.get(f"{self.base_url}/api/analytics/kpis/{period}")
            
            print(f"Status Code: {response.status_code}")
            data = response.json()
            
            if data.get('success'):
                kpis = data.get('data', {})
                
                print("\n📊 KEY PERFORMANCE INDICATORS:")
                print(f"  💰 Monto Total: ${kpis.get('monto_total', 0):,.2f}")
                print(f"  📋 Total Ofertas: {kpis.get('total_ofertas', 0):,}")
                print(f"  📈 Promedio por Oferta: ${kpis.get('promedio_oferta', 0):,.2f}")
                print(f"  👥 Vendedores Activos: {kpis.get('vendedores_activos', 0)}")
                print(f"  🏢 Clientes Activos: {kpis.get('clientes_activos', 0)}")
                print(f"  📦 Productos Vendidos: {kpis.get('productos_vendidos', 0)}")
                print(f"  📂 Categorías Activas: {kpis.get('categorias_activas', 0)}")
                
                if kpis.get('fecha_inicio') and kpis.get('fecha_fin'):
                    print(f"  📅 Período: {kpis['fecha_inicio']} a {kpis['fecha_fin']}")
            else:
                print(f"❌ Error: {data.get('message')}")
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 INICIANDO PRUEBAS DE ANALYTICS API")
        print("="*60)
        print(f"Base URL: {self.base_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("="*60)
        
        tests = [
            ("Health Check", lambda: self.test_health()),
            ("Available Periods", lambda: self.test_available_periods()),
            ("Sales Data - Daily", lambda: self.test_sales_data("daily", 5)),
            ("Sales Data with Filters", lambda: self.test_sales_with_filters("daily")),
            ("Summary by Vendedor", lambda: self.test_summary_data("daily", "vendedor")),
            ("Summary by Date", lambda: self.test_summary_data("daily", "date")),
            ("Top Performers by Monto", lambda: self.test_top_performers("daily", "monto", 5)),
            ("Top Performers by Ofertas", lambda: self.test_top_performers("daily", "ofertas", 5)),
            ("KPIs Daily", lambda: self.test_kpis("daily")),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                print(f"\n{'✅' if result else '❌'} {test_name}: {'PASSED' if result else 'FAILED'}")
            except Exception as e:
                results.append((test_name, False))
                print(f"\n❌ {test_name}: FAILED - {e}")
        
        # Resumen final
        print("\n" + "="*60)
        print("📊 RESUMEN DE PRUEBAS")
        print("="*60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"Total: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\n📋 DETALLE:")
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {status} - {test_name}")
        
        return passed == total

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Analytics API endpoints")
    parser.add_argument("--url", default="http://localhost:5000", help="Base URL del servidor")
    parser.add_argument("--test", choices=[
        "health", "periods", "sales", "sales-filter", "summary", "top", "kpis", "all"
    ], default="all", help="Tipo de prueba a ejecutar")
    parser.add_argument("--period", default="daily", choices=["daily", "weekly", "monthly", "quarterly"], 
                       help="Período para las pruebas")
    
    args = parser.parse_args()
    
    tester = AnalyticsAPITester(args.url)
    
    if args.test == "all":
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    elif args.test == "health":
        success = tester.test_health()
    elif args.test == "periods":
        success = tester.test_available_periods()
    elif args.test == "sales":
        success = tester.test_sales_data(args.period)
    elif args.test == "sales-filter":
        success = tester.test_sales_with_filters(args.period)
    elif args.test == "summary":
        success = tester.test_summary_data(args.period, "vendedor")
    elif args.test == "top":
        success = tester.test_top_performers(args.period, "monto")
    elif args.test == "kpis":
        success = tester.test_kpis(args.period)
    else:
        print("❌ Tipo de prueba no válido")
        sys.exit(1)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

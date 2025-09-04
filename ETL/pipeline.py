"""
Pipeline ETL principal para ejecutar procesos de Extract, Transform, Load
"""

import sys
import os
import argparse
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import schedule
import time

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ETL.database_connection import DatabaseConnection, DataExtractor, DataTransformer, DataLoader, run_etl_pipeline
from ETL.config import ETLConfig, get_table_mapping, get_analisis_venta_query, validate_analisis_venta_data

class ETLPipeline:
    """Clase principal para manejar pipelines ETL"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.db_connection = DatabaseConnection()
        self.extractor = DataExtractor(self.db_connection)
        self.transformer = DataTransformer()
        self.loader = DataLoader(self.db_connection)
        
    def _setup_logging(self) -> logging.Logger:
        """Configurar logging para el pipeline"""
        logging.basicConfig(
            level=getattr(logging, ETLConfig.LOGGING_CONFIG['level']),
            format=ETLConfig.LOGGING_CONFIG['format'],
            handlers=[
                logging.FileHandler(ETLConfig.LOGGING_CONFIG['log_file']),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def run_daily_pipeline(self):
        """Ejecutar pipeline diario de análisis de ventas"""
        self.logger.info("Iniciando pipeline diario de análisis de ventas")
        
        try:
            # Usar la configuración específica para análisis de ventas
            source_table = ETLConfig.ANALISIS_VENTA_CONFIG['source_table']
            target_table = ETLConfig.TARGET_TABLES['analisis_venta_daily']
            days_back = 7  # Datos de los últimos 7 días para pipeline diario
            
            self.logger.info(f"Procesando: {source_table} -> {target_table} (últimos {days_back} días)")
            
            # Extraer datos de los últimos 7 días
            success = run_etl_pipeline(
                source_table=source_table,
                target_table=target_table,
                days_back=days_back
            )
            
            if success:
                self.logger.info("Pipeline diario completado exitosamente")
            else:
                self.logger.error("Error en pipeline diario")
                
        except Exception as e:
            self.logger.error(f"Error crítico en pipeline diario: {str(e)}")
    
    def run_weekly_pipeline(self):
        """Ejecutar pipeline semanal completo"""
        self.logger.info("Iniciando pipeline semanal completo")
        
        try:
            # Usar la configuración específica para análisis de ventas
            source_table = ETLConfig.ANALISIS_VENTA_CONFIG['source_table']
            target_table = ETLConfig.TARGET_TABLES['analisis_venta_weekly']
            days_back = 30  # Datos de los últimos 30 días para pipeline semanal
            
            self.logger.info(f"Procesando: {source_table} -> {target_table} (últimos {days_back} días)")
            
            # Procesar datos de los últimos 30 días
            success = run_etl_pipeline(
                source_table=source_table,
                target_table=target_table,
                days_back=days_back
            )
            
            if success:
                self.logger.info("Pipeline semanal completado exitosamente")
            else:
                self.logger.error("Error en pipeline semanal")
                
        except Exception as e:
            self.logger.error(f"Error crítico en pipeline semanal: {str(e)}")
    
    def run_custom_pipeline(self, source_table: str, target_table: str, days_back: int = 30):
        """Ejecutar pipeline personalizado"""
        self.logger.info(f"Iniciando pipeline personalizado: {source_table} -> {target_table}")
        
        try:
            success = run_etl_pipeline(
                source_table=source_table,
                target_table=target_table,
                days_back=days_back
            )
            
            if success:
                self.logger.info("Pipeline personalizado completado exitosamente")
                return True
            else:
                self.logger.error("Error en pipeline personalizado")
                return False
                
        except Exception as e:
            self.logger.error(f"Error crítico en pipeline personalizado: {str(e)}")
            return False
    
    def run_summary_pipeline(self, days_back: int = 30):
        """Ejecutar pipeline de resumen de análisis de ventas"""
        self.logger.info(f"Iniciando pipeline de resumen (últimos {days_back} días)")
        
        try:
            # Usar consulta de resumen predefinida
            query = get_analisis_venta_query('analisis_venta_summary', days_back)
            params = {'days_back': -days_back}
            
            # Extraer datos de resumen
            summary_data = self.db_connection.execute_query(query, params)
            
            if len(summary_data) > 0:
                # Validar datos
                if validate_analisis_venta_data(summary_data):
                    # Transformar y cargar
                    transformed_data = self.transformer.clean_data(summary_data)
                    transformed_data = self.transformer.add_calculated_columns(transformed_data)
                    
                    target_table = ETLConfig.TARGET_TABLES['analisis_venta_summary']
                    success = self.loader.load_to_table_safe(transformed_data, target_table, 'replace')
                    
                    if success:
                        self.logger.info(f"Pipeline de resumen completado exitosamente. Registros procesados: {len(summary_data)}")
                        return True
                    else:
                        self.logger.error("Error al cargar datos de resumen")
                        return False
                else:
                    self.logger.error("Error en validación de datos")
                    return False
            else:
                self.logger.warning("No se encontraron datos para el resumen")
                return False
                
        except Exception as e:
            self.logger.error(f"Error crítico en pipeline de resumen: {str(e)}")
            return False

    def run_quarterly_pipeline(self):
        """Ejecutar pipeline trimestral (últimos 90 días)"""
        self.logger.info("Iniciando pipeline trimestral completo")
        
        try:
            # Usar la configuración específica para análisis de ventas
            source_table = ETLConfig.ANALISIS_VENTA_CONFIG['source_table']
            target_table = ETLConfig.TARGET_TABLES['analisis_venta_quarterly']
            days_back = 90  # Datos de los últimos 90 días (aproximadamente 1 trimestre)
            
            self.logger.info(f"Procesando: {source_table} -> {target_table} (últimos {days_back} días)")
            
            # Procesar datos de los últimos 90 días
            success = run_etl_pipeline(
                source_table=source_table,
                target_table=target_table,
                days_back=days_back
            )
            
            if success:
                self.logger.info("Pipeline trimestral completado exitosamente")
                return True
            else:
                self.logger.error("Error en pipeline trimestral")
                return False
                
        except Exception as e:
            self.logger.error(f"Error crítico en pipeline trimestral: {str(e)}")
            return False
    
    def run_monthly_pipeline(self):
        """Ejecutar pipeline mensual (últimos 30 días)"""
        self.logger.info("Iniciando pipeline mensual completo")
        
        try:
            # Usar la configuración específica para análisis de ventas
            source_table = ETLConfig.ANALISIS_VENTA_CONFIG['source_table']
            target_table = ETLConfig.TARGET_TABLES['analisis_venta_monthly']
            days_back = 30  # Datos de los últimos 30 días
            
            self.logger.info(f"Procesando: {source_table} -> {target_table} (últimos {days_back} días)")
            
            # Procesar datos de los últimos 30 días
            success = run_etl_pipeline(
                source_table=source_table,
                target_table=target_table,
                days_back=days_back
            )
            
            if success:
                self.logger.info("Pipeline mensual completado exitosamente")
                return True
            else:
                self.logger.error("Error en pipeline mensual")
                return False
                
        except Exception as e:
            self.logger.error(f"Error crítico en pipeline mensual: {str(e)}")
            return False

    def test_connections(self):
        """Probar todas las conexiones necesarias"""
        self.logger.info("Probando conexiones...")
        
        # Probar conexión a base de datos
        db_status = self.db_connection.test_connection()
        
        if db_status:
            self.logger.info("✓ Conexión a base de datos exitosa")
        else:
            self.logger.error("✗ Error en conexión a base de datos")
        
        return db_status
    
    def schedule_pipelines(self):
        """Programar ejecución automática de pipelines"""
        self.logger.info("Configurando programación de pipelines...")
        
        # Pipeline diario a las 6:00 AM
        schedule.every().day.at("06:00").do(self.run_daily_pipeline)
        
        # Pipeline semanal los lunes a las 2:00 AM
        schedule.every().monday.at("02:00").do(self.run_weekly_pipeline)
        
        self.logger.info("Pipelines programados exitosamente")
        self.logger.info("- Pipeline diario: todos los días a las 6:00 AM")
        self.logger.info("- Pipeline semanal: lunes a las 2:00 AM")
        
        # Mantener el programa corriendo
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto

def main():
    """Función principal para ejecutar desde línea de comandos"""
    parser = argparse.ArgumentParser(description='Pipeline ETL para procesamiento de datos de análisis de ventas')
    parser.add_argument('--mode', choices=['daily', 'weekly', 'monthly', 'quarterly', 'summary', 'custom', 'test', 'schedule'], 
                       default='test', help='Modo de ejecución del pipeline')
    parser.add_argument('--source', type=str, default='DL_Analisis_Venta_v', help='Tabla fuente para modo custom')
    parser.add_argument('--target', type=str, help='Tabla destino para modo custom')
    parser.add_argument('--days', type=int, default=30, help='Días hacia atrás para extraer datos')
    
    args = parser.parse_args()
    
    # Inicializar pipeline
    pipeline = ETLPipeline()
    
    # Mostrar información de configuración
    print(f"📊 Pipeline ETL - Análisis de Ventas")
    print(f"🗄️  Tabla fuente: {ETLConfig.ANALISIS_VENTA_CONFIG['source_table']}")
    print(f"🎯 Modo: {args.mode}")
    print("=" * 50)
    
    # Ejecutar según el modo seleccionado
    if args.mode == 'test':
        print("Probando conexiones...")
        if pipeline.test_connections():
            print("✓ Todas las conexiones funcionan correctamente")
            print(f"✓ Tabla fuente disponible: {ETLConfig.ANALISIS_VENTA_CONFIG['source_table']}")
        else:
            print("✗ Error en las conexiones")
            sys.exit(1)
    
    elif args.mode == 'daily':
        print("Ejecutando pipeline diario...")
        pipeline.run_daily_pipeline()
    
    elif args.mode == 'weekly':
        print("Ejecutando pipeline semanal...")
        pipeline.run_weekly_pipeline()
    
    elif args.mode == 'summary':
        print(f"Ejecutando pipeline de resumen (últimos {args.days} días)...")
        success = pipeline.run_summary_pipeline(args.days)
        if not success:
            sys.exit(1)
    
    elif args.mode == 'custom':
        if not args.target:
            print("Error: Para modo custom se requiere --target")
            print(f"Usando tabla fuente por defecto: {args.source}")
            sys.exit(1)
        
        print(f"Ejecutando pipeline personalizado: {args.source} -> {args.target}")
        success = pipeline.run_custom_pipeline(args.source, args.target, args.days)
        
        if not success:
            sys.exit(1)
    
    elif args.mode == 'monthly':
        print("Ejecutando pipeline mensual...")
        success = pipeline.run_monthly_pipeline()
        if not success:
            sys.exit(1)
    
    elif args.mode == 'quarterly':
        print("Ejecutando pipeline trimestral...")
        success = pipeline.run_quarterly_pipeline()
        if not success:
            sys.exit(1)
    
    elif args.mode == 'schedule':
        print("Iniciando programación automática de pipelines...")
        pipeline.schedule_pipelines()

if __name__ == "__main__":
    main()

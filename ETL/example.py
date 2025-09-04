#!/usr/bin/env python3
"""
Script de ejemplo para demostrar el uso del pipeline ETL
"""

import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ETL.pipeline import ETLPipeline
from ETL.database_connection import run_etl_pipeline
from ETL.utils import DataValidator, DataProfiler, ETLLogger

def ejemplo_basico():
    """Ejemplo básico de uso del pipeline"""
    print("=== EJEMPLO BÁSICO DE PIPELINE ETL ===")
    
    # Crear instancia del pipeline
    pipeline = ETLPipeline()
    
    # Probar conexiones
    print("1. Probando conexiones...")
    if pipeline.test_connections():
        print("✓ Conexiones exitosas")
    else:
        print("✗ Error en conexiones")
        return
    
    # Ejecutar pipeline básico
    print("2. Ejecutando pipeline básico...")
    success = pipeline.run_custom_pipeline(
        source_table="DL_Analisis_Venta_v",
        target_table="DL_Analisis_Venta_Example",
        days_back=7
    )
    
    if success:
        print("✓ Pipeline ejecutado exitosamente")
    else:
        print("✗ Error en pipeline")

def ejemplo_con_validacion():
    """Ejemplo con validación de datos"""
    print("\n=== EJEMPLO CON VALIDACIÓN DE DATOS ===")
    
    from ETL.database_connection import DatabaseConnection, DataExtractor
    
    # Inicializar componentes
    db = DatabaseConnection()
    extractor = DataExtractor(db)
    validator = DataValidator()
    profiler = DataProfiler()
    
    try:
        # Extraer datos
        print("1. Extrayendo datos...")
        df = extractor.extract_analisis_venta(days_back=7)
        print(f"   Datos extraídos: {len(df)} filas, {len(df.columns)} columnas")
        
        # Validar datos
        print("2. Validando calidad de datos...")
        validation_report = validator.validate_dataframe(df)
        
        print(f"   Total filas: {validation_report['total_rows']}")
        print(f"   Total columnas: {validation_report['total_columns']}")
        print(f"   Duplicados: {validation_report['duplicates']}")
        print(f"   Validación pasada: {validation_report['validation_passed']}")
        
        if validation_report['issues']:
            print("   Problemas encontrados:")
            for issue in validation_report['issues']:
                print(f"     - {issue}")
        
        # Generar perfil de datos
        print("3. Generando perfil de datos...")
        profile = profiler.generate_profile(df)
        
        print(f"   Memoria utilizada: {profile['dataset_info']['memory_usage_mb']} MB")
        print("   Perfiles de columnas principales:")
        
        # Mostrar perfil de algunas columnas
        for col, col_profile in list(profile['column_profiles'].items())[:3]:
            print(f"     {col}:")
            print(f"       - Tipo: {col_profile['data_type']}")
            print(f"       - Valores únicos: {col_profile['unique_count']}")
            print(f"       - Nulos: {col_profile['null_percentage']}%")
        
    except Exception as e:
        print(f"Error en ejemplo con validación: {str(e)}")

def ejemplo_con_logging():
    """Ejemplo con logging detallado"""
    print("\n=== EJEMPLO CON LOGGING DETALLADO ===")
    
    from ETL.database_connection import DatabaseConnection, DataExtractor, DataTransformer
    
    # Inicializar logger
    etl_logger = ETLLogger("EJEMPLO_ETL")
    
    try:
        # Iniciar pipeline
        etl_logger.start_pipeline("Pipeline de Ejemplo")
        
        # Inicializar componentes
        db = DatabaseConnection()
        extractor = DataExtractor(db)
        transformer = DataTransformer()
        
        # Extraer datos
        etl_logger.log_stage("EXTRACT", "Iniciando extracción de datos")
        df = extractor.extract_analisis_venta(days_back=5)
        etl_logger.log_stage("EXTRACT", f"Datos extraídos: {len(df)} filas")
        
        # Transformar datos
        etl_logger.log_stage("TRANSFORM", "Iniciando transformación de datos")
        df_clean = transformer.clean_data(df)
        etl_logger.log_stage("TRANSFORM", f"Datos limpiados: {len(df_clean)} filas")
        
        df_final = transformer.add_calculated_columns(df_clean)
        etl_logger.log_stage("TRANSFORM", f"Columnas calculadas agregadas: {len(df_final.columns)} columnas")
        
        # Simular carga (no cargaremos realmente)
        etl_logger.log_stage("LOAD", "Simulando carga de datos")
        etl_logger.log_stage("LOAD", f"Datos listos para cargar: {len(df_final)} filas")
        
        # Finalizar pipeline
        etl_logger.end_pipeline(success=True)
        
    except Exception as e:
        etl_logger.end_pipeline(success=False)
        print(f"Error en ejemplo con logging: {str(e)}")

def ejemplo_programacion():
    """Ejemplo de programación de pipelines"""
    print("\n=== EJEMPLO DE PROGRAMACIÓN ===")
    print("Para programar pipelines automáticamente, ejecuta:")
    print("python ETL/pipeline.py --mode schedule")
    print()
    print("Esto programará:")
    print("- Pipeline diario: 6:00 AM todos los días")
    print("- Pipeline semanal: 2:00 AM los lunes")
    print()
    print("El programa quedará corriendo en segundo plano.")

def main():
    """Función principal que ejecuta todos los ejemplos"""
    print("EJEMPLOS DE USO DEL PIPELINE ETL")
    print("=" * 50)
    
    try:
        # Ejecutar ejemplos
        ejemplo_basico()
        ejemplo_con_validacion()
        ejemplo_con_logging()
        ejemplo_programacion()
        
        print("\n" + "=" * 50)
        print("EJEMPLOS COMPLETADOS")
        print("\nPara más información, consulta el README.md")
        
    except KeyboardInterrupt:
        print("\nEjemplos interrumpidos por el usuario")
    except Exception as e:
        print(f"\nError general en ejemplos: {str(e)}")

if __name__ == "__main__":
    main()

"""
Configuración y utilidades para el pipeline ETL
"""

import os
from typing import Dict, Any

class ETLConfig:
    """Configuración centralizada para el pipeline ETL"""
    
    # Configuración de base de datos
    DATABASE_CONFIG = {
        'server': os.getenv('DATALAKE_SERVER', 'DATALAKE'),
        'database': os.getenv('DATALAKE_DATABASE', 'DATALAKE'),
        'driver': 'ODBC Driver 17 for SQL Server',
        'trusted_connection': True
    }
    
    # Configuración de logging
    LOGGING_CONFIG = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'log_file': 'etl_pipeline.log'
    }
    
    # Configuración de transformaciones por defecto
    DEFAULT_TRANSFORMATIONS = {
        'clean_duplicates': True,
        'fill_nulls': True,
        'add_timestamps': True,
        'standardize_dates': True
    }
    
    # Tablas y consultas predefinidas
    PREDEFINED_QUERIES = {
        'analisis_venta': """
            SELECT * FROM DL_Analisis_Venta_v 
            WHERE [Fecha de oferta] >= DATEADD(day, :days_back, GETDATE()) 
            ORDER BY [Fecha de oferta] DESC
        """,
        'analisis_venta_recent': """
            SELECT * FROM DL_Analisis_Venta_v 
            WHERE [Fecha de oferta] >= DATEADD(day, :days_back, GETDATE())
            AND Estado IN ('sale', 'OK', 'sent')
            ORDER BY [Fecha de oferta] DESC
        """,
        'analisis_venta_summary': """
            SELECT 
                Vendedor,
                COUNT(*) as total_ofertas,
                SUM([Cant. producto]) as cantidad_total,
                SUM(Total) as monto_total,
                MIN([Fecha de oferta]) as primera_oferta,
                MAX([Fecha de oferta]) as ultima_oferta
            FROM DL_Analisis_Venta_v 
            WHERE [Fecha de oferta] >= DATEADD(day, :days_back, GETDATE())
            AND Vendedor IS NOT NULL
            GROUP BY Vendedor
            ORDER BY SUM(Total) DESC
        """,
        'last_records': """
            SELECT TOP 1000 * FROM {table_name} 
            ORDER BY {order_column} DESC
        """
    }
    
    # Configuración de tablas de destino
    TARGET_TABLES = {
        'analisis_venta_processed': 'DL_Analisis_Venta_Processed',
        'analisis_venta_daily': 'DL_Analisis_Venta_Daily',
        'analisis_venta_weekly': 'DL_Analisis_Venta_Weekly',
        'analisis_venta_monthly': 'DL_Analisis_Venta_Monthly',
        'analisis_venta_quarterly': 'DL_Analisis_Venta_Quarterly',
        'analisis_venta_summary': 'DL_Analisis_Venta_Summary',
        'staging_prefix': 'STG_',
        'backup_prefix': 'BCK_'
    }
    
    # Configuración específica para DL_Analisis_Venta_v
    ANALISIS_VENTA_CONFIG = {
        'source_table': 'DL_Analisis_Venta_v',
        'date_column': 'Fecha de oferta',
        'key_columns': ['Referencia de pedido', 'DocNum oferta', 'SKU'],
        'numeric_columns': ['Cant. producto', 'Total', 'Monto facturado', 'RPT Precio unitario'],
        'categorical_columns': ['Estado', 'Vendedor', 'Cliente', 'Familia', 'Canal'],
        'default_days_back': 30,
        'batch_size': 10000
    }

def get_connection_string() -> str:
    """Obtener string de conexión a la base de datos"""
    config = ETLConfig.DATABASE_CONFIG
    
    # Obtener credenciales del entorno
    username = os.getenv('DATALAKE_USERNAME')
    password = os.getenv('DATALAKE_PASSWORD')
    port = os.getenv('DATALAKE_PORT', '1433')
    
    # Si hay credenciales específicas, usar autenticación SQL
    if username and password:
        return (f"DRIVER={{{config['driver']}}};"
               f"SERVER={config['server']},{port};"
               f"DATABASE={config['database']};"
               f"UID={username};"
               f"PWD={password};"
               f"Encrypt=yes;"
               f"TrustServerCertificate=yes;"
               f"Connection Timeout=30;")
    else:
        # Usar autenticación Windows (solo para conexiones locales)
        return (f"DRIVER={{{config['driver']}}};"
               f"SERVER={config['server']};"
               f"DATABASE={config['database']};"
               f"Trusted_Connection=yes;")

def get_table_mapping() -> Dict[str, str]:
    """Obtener mapeo de tablas fuente a destino"""
    return {
        'DL_Analisis_Venta_v': ETLConfig.TARGET_TABLES['analisis_venta_processed'],
        # Mapeos adicionales para diferentes tipos de procesamiento
        'DL_Analisis_Venta_v_daily': ETLConfig.TARGET_TABLES['analisis_venta_daily'],
        'DL_Analisis_Venta_v_weekly': ETLConfig.TARGET_TABLES['analisis_venta_weekly'],
        'DL_Analisis_Venta_v_summary': ETLConfig.TARGET_TABLES['analisis_venta_summary'],
    }

def get_analisis_venta_query(query_type: str = 'analisis_venta', days_back: int = 30) -> str:
    """Obtener consulta predefinida para análisis de ventas"""
    queries = ETLConfig.PREDEFINED_QUERIES
    if query_type in queries:
        return queries[query_type]
    else:
        return queries['analisis_venta']

def validate_analisis_venta_data(df) -> bool:
    """Validar que los datos de análisis de ventas tengan las columnas esperadas"""
    # Para datos de resumen, validar columnas diferentes
    if 'Vendedor' in df.columns and 'total_ofertas' in df.columns:
        # Es un resumen por vendedor
        required_columns = ['Vendedor', 'total_ofertas']
    else:
        # Es data completa
        required_columns = ETLConfig.ANALISIS_VENTA_CONFIG['key_columns']
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ Faltan columnas requeridas: {missing_columns}")
        return False
    
    return True

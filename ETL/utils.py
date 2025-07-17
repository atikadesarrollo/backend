"""
Utilidades y funciones auxiliares para el pipeline ETL
"""

import pandas as pd
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

class DataValidator:
    """Clase para validar calidad de datos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_dataframe(self, df: pd.DataFrame, required_columns: List[str] = None) -> Dict[str, Any]:
        """Validar un DataFrame y retornar reporte de calidad"""
        validation_report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'duplicates': df.duplicated().sum(),
            'missing_data': {},
            'data_types': {},
            'validation_passed': True,
            'issues': []
        }
        
        # Verificar columnas requeridas
        if required_columns:
            missing_columns = set(required_columns) - set(df.columns)
            if missing_columns:
                validation_report['validation_passed'] = False
                validation_report['issues'].append(f"Columnas faltantes: {missing_columns}")
        
        # Analizar datos faltantes
        for column in df.columns:
            null_count = df[column].isnull().sum()
            null_percentage = (null_count / len(df)) * 100
            validation_report['missing_data'][column] = {
                'count': null_count,
                'percentage': round(null_percentage, 2)
            }
            
            # Marcar como problema si más del 50% de datos están faltantes
            if null_percentage > 50:
                validation_report['validation_passed'] = False
                validation_report['issues'].append(f"Columna {column} tiene {null_percentage:.1f}% de datos faltantes")
        
        # Analizar tipos de datos
        for column in df.columns:
            validation_report['data_types'][column] = str(df[column].dtype)
        
        return validation_report
    
    def validate_date_columns(self, df: pd.DataFrame, date_columns: List[str]) -> Dict[str, Any]:
        """Validar columnas de fecha específicamente"""
        date_validation = {
            'valid_dates': {},
            'invalid_dates': {},
            'date_ranges': {}
        }
        
        for column in date_columns:
            if column in df.columns:
                # Convertir a datetime y contar valores válidos/inválidos
                date_series = pd.to_datetime(df[column], errors='coerce')
                valid_count = date_series.notna().sum()
                invalid_count = date_series.isna().sum()
                
                date_validation['valid_dates'][column] = valid_count
                date_validation['invalid_dates'][column] = invalid_count
                
                # Obtener rango de fechas
                if valid_count > 0:
                    min_date = date_series.min()
                    max_date = date_series.max()
                    date_validation['date_ranges'][column] = {
                        'min_date': min_date.strftime('%Y-%m-%d') if pd.notna(min_date) else None,
                        'max_date': max_date.strftime('%Y-%m-%d') if pd.notna(max_date) else None
                    }
        
        return date_validation

class DataProfiler:
    """Clase para generar perfiles de datos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generar perfil completo de un DataFrame"""
        profile = {
            'dataset_info': {
                'shape': df.shape,
                'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
                'created_at': datetime.now().isoformat()
            },
            'column_profiles': {}
        }
        
        for column in df.columns:
            column_profile = self._profile_column(df[column])
            profile['column_profiles'][column] = column_profile
        
        return profile
    
    def _profile_column(self, series: pd.Series) -> Dict[str, Any]:
        """Generar perfil de una columna específica"""
        profile = {
            'data_type': str(series.dtype),
            'count': len(series),
            'null_count': series.isnull().sum(),
            'null_percentage': round((series.isnull().sum() / len(series)) * 100, 2),
            'unique_count': series.nunique(),
            'unique_percentage': round((series.nunique() / len(series)) * 100, 2)
        }
        
        # Estadísticas específicas por tipo de dato
        if series.dtype in ['int64', 'float64']:
            profile['statistics'] = {
                'min': series.min(),
                'max': series.max(),
                'mean': round(series.mean(), 2),
                'median': series.median(),
                'std': round(series.std(), 2)
            }
        elif series.dtype == 'object':
            # Para texto, obtener las 5 valores más comunes
            value_counts = series.value_counts().head(5)
            profile['top_values'] = value_counts.to_dict()
            
            # Estadísticas de longitud de texto
            text_lengths = series.astype(str).str.len()
            profile['text_stats'] = {
                'avg_length': round(text_lengths.mean(), 2),
                'min_length': text_lengths.min(),
                'max_length': text_lengths.max()
            }
        
        return profile

class ETLLogger:
    """Clase para logging especializado del pipeline ETL"""
    
    def __init__(self, name: str = 'ETL'):
        self.logger = logging.getLogger(name)
        self.start_time = None
        self.stage_times = {}
    
    def start_pipeline(self, pipeline_name: str):
        """Iniciar logging de pipeline"""
        self.start_time = datetime.now()
        self.logger.info(f"=== INICIANDO PIPELINE: {pipeline_name} ===")
        self.logger.info(f"Tiempo de inicio: {self.start_time}")
    
    def log_stage(self, stage_name: str, message: str = ""):
        """Log de una etapa específica"""
        stage_time = datetime.now()
        if self.start_time:
            elapsed = (stage_time - self.start_time).total_seconds()
            self.logger.info(f"[{stage_name}] {message} (Tiempo transcurrido: {elapsed:.2f}s)")
        else:
            self.logger.info(f"[{stage_name}] {message}")
        
        self.stage_times[stage_name] = stage_time
    
    def end_pipeline(self, success: bool = True):
        """Finalizar logging de pipeline"""
        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds() if self.start_time else 0
        
        status = "EXITOSO" if success else "FALLIDO"
        self.logger.info(f"=== PIPELINE {status} ===")
        self.logger.info(f"Tiempo total: {total_time:.2f} segundos")
        
        # Log de tiempos por etapa
        if len(self.stage_times) > 1:
            self.logger.info("Tiempos por etapa:")
            prev_time = self.start_time
            for stage, stage_time in self.stage_times.items():
                stage_duration = (stage_time - prev_time).total_seconds()
                self.logger.info(f"  {stage}: {stage_duration:.2f}s")
                prev_time = stage_time

def format_bytes(bytes_size: int) -> str:
    """Formatear tamaño en bytes a formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def sanitize_table_name(name: str) -> str:
    """Limpiar nombre de tabla para que sea válido en SQL Server"""
    # Remover caracteres especiales y reemplazar con underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    
    # Asegurar que comience con letra o underscore
    if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
        sanitized = f"_{sanitized}"
    
    # Limitar longitud a 128 caracteres (límite de SQL Server)
    if len(sanitized) > 128:
        sanitized = sanitized[:128]
    
    return sanitized

def create_backup_table_name(original_name: str) -> str:
    """Crear nombre de tabla de backup con timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"BCK_{original_name}_{timestamp}"

def get_data_type_mapping() -> Dict[str, str]:
    """Obtener mapeo de tipos de datos de pandas a SQL Server"""
    return {
        'int64': 'BIGINT',
        'float64': 'FLOAT',
        'object': 'NVARCHAR(MAX)',
        'bool': 'BIT',
        'datetime64[ns]': 'DATETIME2',
        'category': 'NVARCHAR(255)'
    }

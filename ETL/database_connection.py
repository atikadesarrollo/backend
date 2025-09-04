import pyodbc
import pandas as pd
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# Cargar variables de entorno
load_dotenv()

class DatabaseConnection:
    """Clase para manejar la conexión a la base de datos"""
    
    def __init__(self):
        # Configuración de la conexión usando las mismas credenciales de datalake_api
        self.server = os.getenv('DATALAKE_SERVER', 'DATALAKE')
        self.database = os.getenv('DATALAKE_DATABASE', 'DATALAKE')
        self.username = os.getenv('DATALAKE_USERNAME', 'sa')
        self.password = os.getenv('DATALAKE_PASSWORD', 'jsexkodV2W4XJpI')
        self.port = os.getenv('DATALAKE_PORT', '1433')
        self.driver = os.getenv('DATALAKE_DRIVER', 'ODBC Driver 17 for SQL Server')
        self.timeout = os.getenv('DATALAKE_TIMEOUT', '30')
        self.trust_cert = os.getenv('DATALAKE_TRUST_CERTIFICATE', 'yes')
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Intentar encontrar el mejor driver disponible desde el inicio
        try:
            best_driver = self.get_best_driver()
            if best_driver != self.driver:
                self.logger.info(f"Cambiando driver de '{self.driver}' a '{best_driver}'")
                self.driver = best_driver
        except Exception as e:
            self.logger.warning(f"No se pudo determinar el mejor driver: {e}")
        
        # Determinar tipo de autenticación y construir cadena de conexión
        use_sql_auth = os.getenv('DATALAKE_USE_SQL_AUTH', 'true').lower() == 'true'
        
        # Construir el servidor con puerto si es necesario
        server_with_port = f"{self.server},{self.port}" if self.port and self.port != '1433' else self.server
        
        if use_sql_auth and self.username and self.password:
            # Autenticación SQL Server
            self.connection_string = (
                f'DRIVER={{{self.driver}}};'
                f'SERVER={server_with_port};'
                f'DATABASE={self.database};'
                f'UID={self.username};'
                f'PWD={self.password};'
                f'Connection Timeout={self.timeout};'
                f'TrustServerCertificate={self.trust_cert};'
            )
        else:
            # Autenticación de Windows (fallback)
            self.connection_string = (
                f'DRIVER={{{self.driver}}};'
                f'SERVER={server_with_port};'
                f'DATABASE={self.database};'
                f'Trusted_Connection=yes;'
                f'Connection Timeout={self.timeout};'
                f'TrustServerCertificate={self.trust_cert};'
            )
        
        # Crear engine de SQLAlchemy para operaciones con pandas
        self._create_sqlalchemy_engine()
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        try:
            # Log de información de conexión (sin mostrar contraseña)
            auth_type = "SQL Server" if self.username else "Windows"
            self.logger.info(f"Intentando conectar a {self.server}/{self.database} usando autenticación {auth_type}")
            
            connection = pyodbc.connect(self.connection_string)
            self.logger.info("Conexión a base de datos establecida exitosamente")
            return connection
        except pyodbc.Error as e:
            # Si hay error con el driver, intentar con el mejor driver disponible
            if "No se encuentra el nombre del origen de datos" in str(e) or "No data source name found" in str(e):
                self.logger.warning(f"Error con driver configurado: {str(e)}")
                self.logger.info("Intentando reconstruir conexión con el mejor driver disponible...")
                
                try:
                    self.rebuild_connection_string()
                    connection = pyodbc.connect(self.connection_string)
                    self.logger.info("Conexión exitosa con driver alternativo")
                    return connection
                except Exception as retry_error:
                    self.logger.error(f"Error incluso con driver alternativo: {str(retry_error)}")
                    raise retry_error
            else:
                self.logger.error(f"Error de SQL al conectar a la base de datos: {str(e)}")
                raise
        except Exception as e:
            self.logger.error(f"Error general al conectar a la base de datos: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """Probar la conexión a la base de datos"""
        try:
            # Validar configuración primero
            if not self.validate_connection_config():
                return False
            
            # Mostrar información de conexión
            conn_info = self.get_connection_info()
            self.logger.info(f"Probando conexión: {conn_info['auth_type']} auth a {conn_info['server']}/{conn_info['database']}")
            
            # Probar conexión pyodbc
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result[0] != 1:
                    return False
            
            # Probar engine SQLAlchemy si está disponible
            if self.engine is not None:
                with self.engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    row = result.fetchone()
                    if row[0] != 1:
                        return False
                self.logger.info("Prueba de conexión exitosa (pyodbc + SQLAlchemy)")
            else:
                self.logger.info("Prueba de conexión exitosa (solo pyodbc)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error en prueba de conexión: {str(e)}")
            return False
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> pd.DataFrame:
        """Ejecutar una consulta y retornar DataFrame de pandas"""
        try:
            # Usar SQLAlchemy engine para consultas con pandas
            if self.engine is not None:
                if params:
                    # Usar text() para consultas parametrizadas
                    df = pd.read_sql(text(query), self.engine, params=params)
                else:
                    df = pd.read_sql(text(query), self.engine)
            else:
                # Fallback a pyodbc si SQLAlchemy no está disponible
                with self.get_connection() as conn:
                    if params:
                        # Convertir diccionario a lista para pyodbc
                        param_list = list(params.values()) if isinstance(params, dict) else params
                        df = pd.read_sql(query, conn, params=param_list)
                    else:
                        df = pd.read_sql(query, conn)
            
            self.logger.info(f"Consulta ejecutada exitosamente. Filas obtenidas: {len(df)}")
            return df
        except Exception as e:
            self.logger.error(f"Error al ejecutar consulta: {str(e)}")
            raise
    
    def execute_insert(self, table_name: str, data: pd.DataFrame, if_exists: str = 'append') -> bool:
        """Insertar datos en una tabla"""
        try:
            # Usar SQLAlchemy engine para operaciones con pandas
            if self.engine is not None:
                data.to_sql(table_name, self.engine, if_exists=if_exists, index=False, method='multi')
            else:
                # Fallback a pyodbc si SQLAlchemy no está disponible
                with self.get_connection() as conn:
                    data.to_sql(table_name, conn, if_exists=if_exists, index=False)
            
            self.logger.info(f"Datos insertados exitosamente en tabla {table_name}. Filas: {len(data)}")
            return True
        except Exception as e:
            self.logger.error(f"Error al insertar datos en {table_name}: {str(e)}")
            return False
        
    def get_connection_info(self) -> Dict[str, Any]:
        """Obtener información de configuración de conexión (sin credenciales sensibles)"""
        return {
            'server': self.server,
            'database': self.database,
            'username': self.username,
            'auth_type': 'SQL Server' if self.username else 'Windows',
            'sqlalchemy_available': self.engine is not None,
            'connection_string_template': self.connection_string.replace(self.password, '***') if hasattr(self, 'password') else self.connection_string
        }
    
    def validate_connection_config(self) -> bool:
        """Validar que la configuración de conexión sea correcta"""
        try:
            if not self.server:
                self.logger.error("DATALAKE_SERVER no está configurado")
                return False
            
            if not self.database:
                self.logger.error("DATALAKE_DATABASE no está configurado")
                return False
            
            # Si se usa autenticación SQL, validar credenciales
            use_sql_auth = os.getenv('DATALAKE_USE_SQL_AUTH', 'true').lower() == 'true'
            if use_sql_auth:
                if not self.username:
                    self.logger.error("DATALAKE_USERNAME no está configurado para autenticación SQL")
                    return False
                
                if not self.password:
                    self.logger.error("DATALAKE_PASSWORD no está configurado para autenticación SQL")
                    return False
            
            self.logger.info("Configuración de conexión validada exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al validar configuración: {str(e)}")
            return False

    def get_available_drivers(self) -> List[str]:
        """Obtener lista de drivers ODBC disponibles"""
        try:
            drivers = [driver for driver in pyodbc.drivers() if 'SQL Server' in driver]
            self.logger.info(f"Drivers SQL Server disponibles: {drivers}")
            return drivers
        except Exception as e:
            self.logger.error(f"Error al obtener drivers: {str(e)}")
            return []
    
    def get_best_driver(self) -> str:
        """Obtener el mejor driver disponible"""
        # Orden de preferencia de drivers
        preferred_drivers = [
            'ODBC Driver 18 for SQL Server',
            'ODBC Driver 17 for SQL Server',
            'ODBC Driver 13 for SQL Server',
            'ODBC Driver 11 for SQL Server',
            'SQL Server Native Client 11.0',
            'SQL Server Native Client 10.0',
            'SQL Server'
        ]
        
        available_drivers = self.get_available_drivers()
        
        for driver in preferred_drivers:
            if driver in available_drivers:
                self.logger.info(f"Usando driver: {driver}")
                return driver
        
        # Si no se encuentra ningún driver preferido, usar el primero disponible
        if available_drivers:
            driver = available_drivers[0]
            self.logger.warning(f"Usando driver no preferido: {driver}")
            return driver
        
        # Si no hay drivers disponibles, intentar con el driver por defecto
        self.logger.error("No se encontraron drivers SQL Server. Intentando con driver por defecto.")
        return 'SQL Server'

    def rebuild_connection_string(self):
        """Reconstruir la cadena de conexión con el mejor driver disponible"""
        best_driver = self.get_best_driver()
        use_sql_auth = os.getenv('DATALAKE_USE_SQL_AUTH', 'true').lower() == 'true'
        
        # Actualizar driver
        self.driver = best_driver
        
        # Construir el servidor con puerto si es necesario
        server_with_port = f"{self.server},{self.port}" if self.port and self.port != '1433' else self.server
        
        if use_sql_auth and self.username and self.password:
            # Autenticación SQL Server
            self.connection_string = (
                f'DRIVER={{{best_driver}}};'
                f'SERVER={server_with_port};'
                f'DATABASE={self.database};'
                f'UID={self.username};'
                f'PWD={self.password};'
                f'Connection Timeout={self.timeout};'
                f'TrustServerCertificate={self.trust_cert};'
            )
        else:
            # Autenticación de Windows (fallback)
            self.connection_string = (
                f'DRIVER={{{best_driver}}};'
                f'SERVER={server_with_port};'
                f'DATABASE={self.database};'
                f'Trusted_Connection=yes;'
                f'Connection Timeout={self.timeout};'
                f'TrustServerCertificate={self.trust_cert};'
            )
        
        # Reconstruir engine de SQLAlchemy
        self._create_sqlalchemy_engine()
        
        self.logger.info(f"Cadena de conexión reconstruida con driver: {best_driver}")

    def _create_sqlalchemy_engine(self):
        """Crear engine de SQLAlchemy para operaciones con pandas"""
        try:
            # Determinar tipo de autenticación
            use_sql_auth = os.getenv('DATALAKE_USE_SQL_AUTH', 'true').lower() == 'true'
            
            # Usar el driver actual (que puede haber sido corregido por get_best_driver)
            driver_to_use = self.driver
            
            # Construir URL de conexión para SQLAlchemy
            if use_sql_auth and self.username and self.password:
                # Codificar password para URL
                password_encoded = quote_plus(self.password)
                username_encoded = quote_plus(self.username)
                
                # Crear URL de conexión con autenticación SQL
                connection_url = (
                    f"mssql+pyodbc://{username_encoded}:{password_encoded}@"
                    f"{self.server}:{self.port}/{self.database}?"
                    f"driver={quote_plus(driver_to_use)}&"
                    f"TrustServerCertificate={self.trust_cert}&"
                    f"Connection+Timeout={self.timeout}"
                )
            else:
                # Crear URL de conexión con autenticación Windows
                connection_url = (
                    f"mssql+pyodbc://@{self.server}:{self.port}/{self.database}?"
                    f"driver={quote_plus(driver_to_use)}&"
                    f"trusted_connection=yes&"
                    f"TrustServerCertificate={self.trust_cert}&"
                    f"Connection+Timeout={self.timeout}"
                )
            
            # Crear engine
            self.engine = create_engine(
                connection_url,
                echo=False,  # Cambiar a True para debug SQL
                pool_pre_ping=True,  # Verificar conexiones antes de usar
                pool_recycle=3600,   # Reciclar conexiones cada hora
                connect_args={
                    "timeout": int(self.timeout)
                }
            )
            
            self.logger.info(f"Engine de SQLAlchemy creado exitosamente con driver: {driver_to_use}")
            
        except Exception as e:
            self.logger.error(f"Error al crear engine de SQLAlchemy: {str(e)}")
            # En caso de error, intentar usar el mejor driver disponible
            try:
                best_driver = self.get_best_driver()
                self.driver = best_driver
                self.logger.info(f"Reintentando con driver: {best_driver}")
                
                # Reconstruir URL con el mejor driver
                if use_sql_auth and self.username and self.password:
                    password_encoded = quote_plus(self.password)
                    username_encoded = quote_plus(self.username)
                    
                    connection_url = (
                        f"mssql+pyodbc://{username_encoded}:{password_encoded}@"
                        f"{self.server}:{self.port}/{self.database}?"
                        f"driver={quote_plus(best_driver)}&"
                        f"TrustServerCertificate={self.trust_cert}&"
                        f"Connection+Timeout={self.timeout}"
                    )
                else:
                    connection_url = (
                        f"mssql+pyodbc://@{self.server}:{self.port}/{self.database}?"
                        f"driver={quote_plus(best_driver)}&"
                        f"trusted_connection=yes&"
                        f"TrustServerCertificate={self.trust_cert}&"
                        f"Connection+Timeout={self.timeout}"
                    )
                
                self.engine = create_engine(
                    connection_url,
                    echo=False,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    connect_args={
                        "timeout": int(self.timeout)
                    }
                )
                
                self.logger.info(f"Engine de SQLAlchemy creado exitosamente con driver alternativo: {best_driver}")
                
            except Exception as retry_error:
                self.logger.error(f"Error al crear engine incluso con driver alternativo: {str(retry_error)}")
                self.engine = None

class DataExtractor:
    """Clase para extraer datos de diferentes fuentes"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
    
    def extract_analisis_venta(self, days_back: int = 30) -> pd.DataFrame:
        """Extraer datos de análisis de ventas"""
        query = """
            SELECT * FROM DL_Analisis_Venta_v 
            WHERE [Fecha de oferta] >= DATEADD(day, ?, GETDATE()) 
            ORDER BY [Fecha de oferta] DESC
        """
        # Convertir parámetro simple a diccionario para SQLAlchemy
        params = {"days_back": -days_back}
        query_with_params = """
            SELECT * FROM DL_Analisis_Venta_v 
            WHERE [Fecha de oferta] >= DATEADD(day, :days_back, GETDATE()) 
            ORDER BY [Fecha de oferta] DESC
        """
        return self.db.execute_query(query_with_params, params)
    
    def extract_table(self, table_name: str, where_clause: str = "", limit: Optional[int] = None) -> pd.DataFrame:
        """Extraer datos de una tabla específica"""
        query = f"SELECT * FROM {table_name}"
        
        if where_clause:
            query += f" WHERE {where_clause}"
        
        if limit:
            query = f"SELECT TOP {limit} * FROM ({query}) AS limited_query"
        
        return self.db.execute_query(query)
    
    def extract_custom_query(self, query: str, params: Optional[List] = None) -> pd.DataFrame:
        """Extraer datos usando una consulta personalizada"""
        return self.db.execute_query(query, params)

class DataTransformer:
    """Clase para transformar datos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpiar datos básicos"""
        try:
            # Eliminar duplicados
            df_cleaned = df.drop_duplicates()
            
            # Eliminar filas completamente vacías
            df_cleaned = df_cleaned.dropna(how='all')
            
            # Limpiar valores infinitos en columnas numéricas
            numeric_columns = df_cleaned.select_dtypes(include=['int64', 'float64']).columns
            for col in numeric_columns:
                # Reemplazar inf y -inf con NaN
                df_cleaned[col] = df_cleaned[col].replace([float('inf'), float('-inf')], pd.NaT)
                # Rellenar NaN con 0 para columnas numéricas
                df_cleaned[col] = df_cleaned[col].fillna(0)
            
            # Rellenar valores nulos con valores por defecto según el tipo de columna
            for column in df_cleaned.columns:
                if df_cleaned[column].dtype == 'object':
                    df_cleaned[column] = df_cleaned[column].fillna('')
                elif column not in numeric_columns:  # Ya procesamos las numéricas
                    df_cleaned[column] = df_cleaned[column].fillna(0)
            
            self.logger.info(f"Datos limpiados. Filas originales: {len(df)}, Filas después de limpiar: {len(df_cleaned)}")
            return df_cleaned
            
        except Exception as e:
            self.logger.error(f"Error al limpiar datos: {str(e)}")
            return df
    
    def transform_dates(self, df: pd.DataFrame, date_columns: List[str]) -> pd.DataFrame:
        """Transformar columnas de fecha"""
        try:
            df_transformed = df.copy()
            
            for column in date_columns:
                if column in df_transformed.columns:
                    # Convertir a datetime con manejo de errores
                    df_transformed[column] = pd.to_datetime(df_transformed[column], errors='coerce')
                    
                    # Filtrar fechas fuera de rango válido para SQL Server (1753-9999)
                    min_date = pd.Timestamp('1753-01-01')
                    max_date = pd.Timestamp('9999-12-31')
                    
                    # Reemplazar fechas fuera de rango con NULL
                    mask = (df_transformed[column] < min_date) | (df_transformed[column] > max_date)
                    df_transformed.loc[mask, column] = pd.NaT
                    
                    self.logger.info(f"Columna de fecha transformada: {column} ({mask.sum()} valores fuera de rango limpiados)")
                    
            self.logger.info(f"Columnas de fecha transformadas: {date_columns}")
            return df_transformed
            
        except Exception as e:
            self.logger.error(f"Error al transformar fechas: {str(e)}")
            return df
    
    def add_calculated_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agregar columnas calculadas"""
        try:
            df_transformed = df.copy()
            
            # Agregar timestamp de procesamiento
            df_transformed['processed_at'] = datetime.now()
            
            # Agregar año y mes si hay columnas de fecha
            date_columns = df_transformed.select_dtypes(include=['datetime64']).columns
            for date_col in date_columns:
                if not date_col.endswith('_year') and not date_col.endswith('_month'):
                    df_transformed[f'{date_col}_year'] = df_transformed[date_col].dt.year
                    df_transformed[f'{date_col}_month'] = df_transformed[date_col].dt.month
            
            self.logger.info("Columnas calculadas agregadas exitosamente")
            return df_transformed
            
        except Exception as e:
            self.logger.error(f"Error al agregar columnas calculadas: {str(e)}")
            return df

class DataLoader:
    """Clase para cargar datos transformados"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
    
    def load_to_table(self, df: pd.DataFrame, table_name: str, if_exists: str = 'append') -> bool:
        """Cargar datos a una tabla usando el método seguro"""
        return self.load_to_table_safe(df, table_name, if_exists)
    
    def create_staging_table(self, df: pd.DataFrame, table_name: str) -> bool:
        """Crear tabla de staging temporal"""
        try:
            staging_table = f"{table_name}_staging"
            success = self.db.execute_insert(staging_table, df, if_exists='replace')
            if success:
                self.logger.info(f"Tabla de staging {staging_table} creada exitosamente")
            return success
        except Exception as e:
            self.logger.error(f"Error al crear tabla de staging: {str(e)}")
            return False
        
    def create_table_if_not_exists(self, table_name: str, df: pd.DataFrame) -> bool:
        """Crear tabla si no existe, basándose en la estructura del DataFrame"""
        try:
            # Verificar si la tabla ya existe usando una consulta simple
            check_query = f"""
            SELECT COUNT(*) as table_exists 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = 'dbo'
            """
            
            result = self.db.execute_query(check_query)
            table_exists = result.iloc[0]['table_exists'] > 0
            
            if not table_exists:
                self.logger.info(f"Creando tabla {table_name}...")
                
                # Construir comando CREATE TABLE basado en los tipos de datos del DataFrame
                columns_def = []
                for col in df.columns:
                    dtype = df[col].dtype
                    
                    if dtype == 'object':
                        col_def = f"[{col}] NVARCHAR(255)"
                    elif dtype == 'int64':
                        col_def = f"[{col}] BIGINT"
                    elif dtype == 'float64':
                        col_def = f"[{col}] FLOAT"
                    elif dtype == 'datetime64[ns]':
                        col_def = f"[{col}] DATETIME2"
                    else:
                        col_def = f"[{col}] NVARCHAR(255)"
                    
                    columns_def.append(col_def)
                
                create_query = f"""
                CREATE TABLE [{table_name}] (
                    {', '.join(columns_def)}
                )
                """
                
                # Ejecutar usando pyodbc directamente
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(create_query)
                    conn.commit()
                
                self.logger.info(f"Tabla {table_name} creada exitosamente")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error al crear tabla {table_name}: {str(e)}")
            return False

    def load_to_table_safe(self, df: pd.DataFrame, table_name: str, if_exists: str = 'append') -> bool:
        """Método seguro para cargar datos que maneja la creación de tablas"""
        try:
            # Primero intentar crear la tabla si no existe
            if if_exists == 'replace':
                # Para replace, eliminar la tabla si existe
                try:
                    drop_query = f"DROP TABLE IF EXISTS [{table_name}]"
                    with self.db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute(drop_query)
                        conn.commit()
                    self.logger.info(f"Tabla {table_name} eliminada para reemplazo")
                except:
                    pass  # Ignorar si la tabla no existe
            
            # Crear tabla si no existe
            if not self.create_table_if_not_exists(table_name, df):
                return False
            
            # Usar insert directo con pyodbc
            if if_exists == 'replace' or if_exists == 'append':
                # Construir query de insert
                columns = ', '.join([f'[{col}]' for col in df.columns])
                placeholders = ', '.join(['?' for _ in df.columns])
                insert_query = f"INSERT INTO [{table_name}] ({columns}) VALUES ({placeholders})"
                
                # Preparar datos
                data_tuples = [tuple(row) for row in df.values]
                
                # Ejecutar insert por lotes
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.executemany(insert_query, data_tuples)
                    conn.commit()
                
                self.logger.info(f"Datos insertados exitosamente en tabla {table_name}. Filas: {len(df)}")
                return True
            else:
                # Usar el método original para otros modos
                return self.execute_insert(table_name, df, if_exists)
            
        except Exception as e:
            self.logger.error(f"Error al cargar datos en {table_name}: {str(e)}")
            return False

# Función principal para ejecutar el pipeline completo
def run_etl_pipeline(source_table: str, target_table: str, days_back: int = 30) -> bool:
    """Ejecutar pipeline ETL completo"""
    logger = logging.getLogger(__name__)
    
    try:
        # Inicializar componentes
        db_connection = DatabaseConnection()
        extractor = DataExtractor(db_connection)
        transformer = DataTransformer()
        loader = DataLoader(db_connection)
        
        # Probar conexión
        if not db_connection.test_connection():
            raise Exception("No se pudo establecer conexión con la base de datos")
        
        # Extract
        logger.info("Iniciando extracción de datos...")
        if source_table == "DL_Analisis_Venta_v":
            raw_data = extractor.extract_analisis_venta(days_back)
        else:
            raw_data = extractor.extract_table(source_table)
        
        # Transform
        logger.info("Iniciando transformación de datos...")
        cleaned_data = transformer.clean_data(raw_data)
        
        # Identificar columnas de fecha automáticamente
        date_columns = []
        for col in cleaned_data.columns:
            if 'fecha' in col.lower() or 'date' in col.lower():
                date_columns.append(col)
        
        if date_columns:
            cleaned_data = transformer.transform_dates(cleaned_data, date_columns)
        
        final_data = transformer.add_calculated_columns(cleaned_data)
        
        # Load
        logger.info("Iniciando carga de datos...")
        success = loader.load_to_table(final_data, target_table)
        
        if success:
            logger.info("Pipeline ETL ejecutado exitosamente")
            return True
        else:
            logger.error("Error en la carga de datos")
            return False
            
    except Exception as e:
        logger.error(f"Error en pipeline ETL: {str(e)}")
        return False

if __name__ == "__main__":
    # Ejemplo de uso
    success = run_etl_pipeline("DL_Analisis_Venta_v", "DL_Analisis_Venta_Processed", 30)
    if success:
        print("Pipeline ETL completado exitosamente")
    else:
        print("Error en pipeline ETL")

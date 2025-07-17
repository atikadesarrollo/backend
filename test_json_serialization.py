"""
Script de prueba para depurar el problema de serialización JSON
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ETL'))

from ETL.database_connection import DatabaseConnection
import pandas as pd
import numpy as np
import json

def test_json_serialization():
    """Probar serialización JSON con datos de la tabla quarterly"""
    print("🔍 Probando serialización JSON de DL_Analisis_Venta_Quarterly")
    
    try:
        db = DatabaseConnection()
        
        # Query simple para obtener 2 registros
        query = """
        SELECT TOP 2
            [Referencia de pedido],
            [Fecha de oferta],
            Vendedor,
            Cliente,
            [Cant. producto],
            Total
        FROM DL_Analisis_Venta_Quarterly
        WHERE Vendedor LIKE '%Loreto%'
        ORDER BY [Fecha de oferta] DESC
        """
        
        df = db.execute_query(query)
        print(f"✅ Datos obtenidos: {len(df)} registros")
        print(f"📊 Columnas: {list(df.columns)}")
        print(f"🔧 Tipos de datos:")
        for col in df.columns:
            print(f"   {col}: {df[col].dtype}")
        
        # Método 1: to_dict('records') directo
        print("\n🧪 Método 1: to_dict('records') directo")
        try:
            records = df.to_dict('records')
            json_str = json.dumps(records)
            print("✅ Serialización exitosa con to_dict")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Método 2: Conversión manual
        print("\n🧪 Método 2: Conversión manual")
        try:
            manual_records = []
            for _, row in df.iterrows():
                record = {}
                for col in df.columns:
                    value = row[col]
                    if pd.isna(value):
                        record[col] = None
                    elif isinstance(value, (pd.Timestamp,)):
                        record[col] = value.isoformat()
                    elif isinstance(value, (np.integer, np.int64, np.int32)):
                        record[col] = int(value)
                    elif isinstance(value, (np.floating, np.float64, np.float32)):
                        record[col] = float(value)
                    else:
                        record[col] = str(value)
                manual_records.append(record)
            
            json_str = json.dumps(manual_records)
            print("✅ Serialización exitosa con conversión manual")
            print(f"📄 JSON resultado: {json_str[:200]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Método 3: Usando astype para convertir tipos
        print("\n🧪 Método 3: Conversión de tipos con astype")
        try:
            df_converted = df.copy()
            for col in df_converted.columns:
                if df_converted[col].dtype == 'int64':
                    df_converted[col] = df_converted[col].astype('int32')
                elif df_converted[col].dtype == 'float64':
                    df_converted[col] = df_converted[col].astype('float32')
            
            records = df_converted.to_dict('records')
            json_str = json.dumps(records, default=str)
            print("✅ Serialización exitosa con conversión de tipos")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_json_serialization()

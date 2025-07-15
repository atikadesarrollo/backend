#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión a la base de datos
"""

import os
import sys
from database_connection import DatabaseConnection

def main():
    print("=== Prueba de Conexión a Base de Datos ===\n")
    
    # Crear instancia de conexión
    db = DatabaseConnection()
    
    # Mostrar información de configuración
    print("1. Información de configuración:")
    conn_info = db.get_connection_info()
    for key, value in conn_info.items():
        print(f"   {key}: {value}")
    print()
    
    # Validar configuración
    print("2. Validando configuración...")
    if db.validate_connection_config():
        print("   ✓ Configuración válida")
    else:
        print("   ✗ Error en configuración")
        return False
    print()
    
    # Probar conexión
    print("3. Probando conexión...")
    if db.test_connection():
        print("   ✓ Conexión exitosa")
        
        # Probar consulta simple
        print("\n4. Ejecutando consulta de prueba...")
        try:
            result = db.execute_query("SELECT GETDATE() as fecha_actual, @@VERSION as version")
            print("   ✓ Consulta ejecutada exitosamente")
            print(f"   Fecha actual: {result.iloc[0]['fecha_actual']}")
            print(f"   Versión SQL Server: {result.iloc[0]['version'][:100]}...")
            return True
        except Exception as e:
            print(f"   ✗ Error en consulta: {str(e)}")
            return False
    else:
        print("   ✗ Error en conexión")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

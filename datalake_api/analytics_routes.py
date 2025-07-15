"""
API Routes para consultas analíticas de datos ETL
Endpoints especializados para consultar datos del ETL desde frontend
"""

from flask import Blueprint, request, jsonify, Response
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import sys
import os

# Agregar el directorio ETL al path para importar las clases
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ETL'))
from database_connection import DatabaseConnection

# Crear blueprint para rutas analíticas
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

class AnalyticsService:
    """Servicio para consultas analíticas"""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def get_table_name_by_period(self, period: str) -> str:
        """Obtener nombre de tabla según el período"""
        table_mapping = {
            'daily': 'DL_Analisis_Venta_Daily',
            'weekly': 'DL_Analisis_Venta_Weekly',
            'monthly': 'DL_Analisis_Venta_Monthly',
            'quarterly': 'DL_Analisis_Venta_Quarterly',
            'summary': 'DL_Analisis_Venta_Summary'
        }
        return table_mapping.get(period.lower(), 'DL_Analisis_Venta_Daily')
    
    def format_response(self, data: pd.DataFrame, message: str = "Success", total_records: int = None) -> dict:
        """Formatear respuesta estándar para la API"""
        if data.empty:
            return {
                "success": True,
                "message": "No data found",
                "data": [],
                "total_records": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        # Convertir DataFrame a lista de diccionarios
        data_list = data.to_dict('records')
        
        return {
            "success": True,
            "message": message,
            "data": data_list,
            "total_records": total_records or len(data_list),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_sales_data(self, period: str = 'daily', limit: int = 100, offset: int = 0, filters: dict = None) -> dict:
        """Obtener datos de ventas con filtros"""
        try:
            table_name = self.get_table_name_by_period(period)
            
            # Construir query base
            base_query = f"""
            SELECT 
                [Fecha de oferta],
                Vendedor,
                Cliente,
                [Descipción] as Producto,
                Rubro as Categoria,
                [Cantidad entregada],
                Total as [Monto orden],
                Estado,
                processed_at
            FROM [{table_name}]
            """
            
            # Aplicar filtros
            where_conditions = []
            if filters:
                if filters.get('vendedor'):
                    where_conditions.append(f"Vendedor LIKE '%{filters['vendedor']}%'")
                if filters.get('cliente'):
                    where_conditions.append(f"Cliente LIKE '%{filters['cliente']}%'")
                if filters.get('categoria'):
                    where_conditions.append(f"Categoria = '{filters['categoria']}'")
                if filters.get('estado'):
                    where_conditions.append(f"Estado = '{filters['estado']}'")
                if filters.get('fecha_desde'):
                    where_conditions.append(f"[Fecha de oferta] >= '{filters['fecha_desde']}'")
                if filters.get('fecha_hasta'):
                    where_conditions.append(f"[Fecha de oferta] <= '{filters['fecha_hasta']}'")
            
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            # Contar total de registros para paginación
            count_query = f"""
            SELECT COUNT(*) as total 
            FROM ({base_query}) as filtered_data
            """
            total_result = self.db.execute_query(count_query)
            total_records = total_result.iloc[0]['total'] if not total_result.empty else 0
            
            # Aplicar paginación y ordenamiento
            final_query = f"""
            {base_query}
            ORDER BY [Fecha de oferta] DESC
            OFFSET {offset} ROWS
            FETCH NEXT {limit} ROWS ONLY
            """
            
            data = self.db.execute_query(final_query)
            
            # Convertir tipos de datos problemáticos antes de serializar
            if not data.empty:
                # Convertir todas las columnas numéricas a tipos Python nativos
                for col in data.columns:
                    if data[col].dtype in ['int64', 'float64']:
                        data[col] = data[col].astype('object')
                    elif pd.api.types.is_datetime64_any_dtype(data[col]):
                        data[col] = data[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            return self.format_response(
                data, 
                f"Sales data retrieved for {period} period", 
                total_records
            )
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving sales data: {str(e)}",
                "data": [],
                "total_records": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_summary_by_period(self, period: str = 'daily', group_by: str = 'date') -> dict:
        """Obtener resumen agrupado por período"""
        try:
            table_name = self.get_table_name_by_period(period)
            
            if group_by == 'date':
                query = f"""
                SELECT 
                    CAST([Fecha de oferta] AS DATE) as fecha,
                    COUNT(*) as total_ofertas,
                    SUM([Cantidad entregada]) as cantidad_total,
                    SUM(Total) as monto_total,
                    AVG(Total) as promedio_oferta,
                    COUNT(DISTINCT Vendedor) as vendedores_activos,
                    COUNT(DISTINCT Cliente) as clientes_activos
                FROM [{table_name}]
                GROUP BY CAST([Fecha de oferta] AS DATE)
                ORDER BY fecha DESC
                """
            elif group_by == 'vendedor':
                query = f"""
                SELECT 
                    Vendedor,
                    COUNT(*) as total_ofertas,
                    SUM([Cantidad entregada]) as cantidad_total,
                    SUM(Total) as monto_total,
                    AVG(Total) as promedio_oferta,
                    MIN([Fecha de oferta]) as primera_venta,
                    MAX([Fecha de oferta]) as ultima_venta
                FROM [{table_name}]
                GROUP BY Vendedor
                ORDER BY monto_total DESC
                """
            elif group_by == 'categoria':
                query = f"""
                SELECT 
                    Rubro as Categoria,
                    COUNT(*) as total_ofertas,
                    SUM([Cantidad entregada]) as cantidad_total,
                    SUM(Total) as monto_total,
                    AVG(Total) as promedio_oferta
                FROM [{table_name}]
                WHERE Rubro IS NOT NULL AND Rubro != ''
                GROUP BY Rubro
                ORDER BY monto_total DESC
                """
            elif group_by == 'producto':
                query = f"""
                SELECT 
                    [Descipción] as Producto,
                    COUNT(*) as total_ofertas,
                    SUM([Cantidad entregada]) as cantidad_total,
                    SUM(Total) as monto_total,
                    AVG(Total) as promedio_oferta
                FROM [{table_name}]
                WHERE [Descipción] IS NOT NULL AND [Descipción] != ''
                GROUP BY [Descipción]
                ORDER BY monto_total DESC
                """
            else:
                return {
                    "success": False,
                    "message": "Invalid group_by parameter. Use: date, vendedor, categoria, producto",
                    "data": [],
                    "total_records": 0,
                    "timestamp": datetime.now().isoformat()
                }
            
            data = self.db.execute_query(query)
            
            return self.format_response(
                data, 
                f"Summary data grouped by {group_by} for {period} period"
            )
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving summary data: {str(e)}",
                "data": [],
                "total_records": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_top_performers(self, period: str = 'daily', metric: str = 'monto', limit: int = 10) -> dict:
        """Obtener top performers según métrica"""
        try:
            table_name = self.get_table_name_by_period(period)
            
            metric_mapping = {
                'monto': 'SUM(Total)',
                'cantidad': 'SUM([Cantidad entregada])',
                'ofertas': 'COUNT(*)',
                'promedio': 'AVG(Total)'
            }
            
            if metric not in metric_mapping:
                return {
                    "success": False,
                    "message": "Invalid metric. Use: monto, cantidad, ofertas, promedio",
                    "data": [],
                    "total_records": 0,
                    "timestamp": datetime.now().isoformat()
                }
            
            query = f"""
            SELECT TOP {limit}
                Vendedor,
                COUNT(*) as total_ofertas,
                SUM([Cantidad entregada]) as cantidad_total,
                SUM(Total) as monto_total,
                AVG(Total) as promedio_oferta,
                {metric_mapping[metric]} as metric_value
            FROM [{table_name}]
            GROUP BY Vendedor
            ORDER BY metric_value DESC
            """
            
            data = self.db.execute_query(query)
            
            return self.format_response(
                data, 
                f"Top {limit} performers by {metric} for {period} period"
            )
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving top performers: {str(e)}",
                "data": [],
                "total_records": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_kpis(self, period: str = 'daily') -> dict:
        """Obtener KPIs principales"""
        try:
            table_name = self.get_table_name_by_period(period)
            
            query = f"""
            SELECT 
                COUNT(*) as total_ofertas,
                SUM([Cantidad entregada]) as cantidad_total,
                SUM(Total) as monto_total,
                AVG(Total) as promedio_oferta,
                COUNT(DISTINCT Vendedor) as vendedores_activos,
                COUNT(DISTINCT Cliente) as clientes_activos,
                COUNT(DISTINCT [Descipción]) as productos_vendidos,
                COUNT(DISTINCT Rubro) as categorias_activas,
                MIN([Fecha de oferta]) as fecha_inicio,
                MAX([Fecha de oferta]) as fecha_fin
            FROM [{table_name}]
            """
            
            data = self.db.execute_query(query)
            
            if not data.empty:
                kpis = data.iloc[0].to_dict()
                
                # Calcular KPIs adicionales
                if kpis['vendedores_activos'] > 0:
                    kpis['ofertas_por_vendedor'] = round(kpis['total_ofertas'] / kpis['vendedores_activos'], 2)
                    kpis['monto_por_vendedor'] = round(kpis['monto_total'] / kpis['vendedores_activos'], 2)
                
                if kpis['clientes_activos'] > 0:
                    kpis['ofertas_por_cliente'] = round(kpis['total_ofertas'] / kpis['clientes_activos'], 2)
                    kpis['monto_por_cliente'] = round(kpis['monto_total'] / kpis['clientes_activos'], 2)
                
                return {
                    "success": True,
                    "message": f"KPIs retrieved for {period} period",
                    "data": kpis,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": True,
                    "message": "No data available for KPIs",
                    "data": {},
                    "timestamp": datetime.now().isoformat()
                }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving KPIs: {str(e)}",
                "data": {},
                "timestamp": datetime.now().isoformat()
            }
    
    def get_complete_quarterly_table(self, limit: int = None, offset: int = 0, filters: dict = None) -> dict:
        """Obtener tabla completa DL_Analisis_Venta_Quarterly con paginación"""
        try:
            table_name = 'DL_Analisis_Venta_Quarterly'
            
            # Construir condiciones WHERE
            where_conditions = []
            if filters:
                if filters.get('vendedor'):
                    where_conditions.append(f"Vendedor LIKE '%{filters['vendedor']}%'")
                if filters.get('cliente'):
                    where_conditions.append(f"Cliente LIKE '%{filters['cliente']}%'")
                if filters.get('categoria'):
                    where_conditions.append(f"Rubro = '{filters['categoria']}'")
                if filters.get('estado'):
                    where_conditions.append(f"Estado = '{filters['estado']}'")
                if filters.get('fecha_desde'):
                    where_conditions.append(f"[Fecha de oferta] >= '{filters['fecha_desde']}'")
                if filters.get('fecha_hasta'):
                    where_conditions.append(f"[Fecha de oferta] <= '{filters['fecha_hasta']}'")
                if filters.get('familia'):
                    where_conditions.append(f"Familia LIKE '%{filters['familia']}%'")
                if filters.get('trimestre'):
                    where_conditions.append(f"DATEPART(quarter, [Fecha de oferta]) = {filters['trimestre']}")
                if filters.get('año'):
                    where_conditions.append(f"YEAR([Fecha de oferta]) = {filters['año']}")
            
            where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Query para contar total de registros
            count_query = f"SELECT COUNT(*) as total FROM {table_name}{where_clause}"
            count_result = self.db.execute_query(count_query)
            total_records = count_result.iloc[0]['total'] if not count_result.empty else 0
            
            # Query para obtener los datos
            limit_clause = ""
            if limit:
                limit_clause = f" ORDER BY [Fecha de oferta] DESC OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"
            else:
                limit_clause = " ORDER BY [Fecha de oferta] DESC"
            
            data_query = f"""
            SELECT 
                [Referencia de pedido],
                [Fecha de oferta],
                Vendedor,
                Cliente,
                [RUT Cliente],
                SKU,
                [Descipción],
                Familia,
                Marca,
                [Cant. producto],
                [RPT Precio unitario],
                [Descuento %],
                Total,
                Estado,
                Comuna,
                Canal,
                Departamento,
                Rubro,
                processed_at
            FROM {table_name}{where_clause}{limit_clause}
            """
            
            df = self.db.execute_query(data_query)
            
            return self.format_response(
                df, 
                f"Quarterly data retrieved successfully. Showing {len(df)} of {total_records} records.",
                total_records
            )
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving quarterly data: {str(e)}",
                "data": [],
                "total_records": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_quarterly_table_info(self) -> dict:
        """Obtener información general de la tabla quarterly"""
        try:
            table_name = 'DL_Analisis_Venta_Quarterly'
            
            info_query = f"""
            SELECT 
                COUNT(*) as total_registros,
                COUNT(DISTINCT YEAR([Fecha de oferta])) as años_unicos,
                COUNT(DISTINCT DATEPART(quarter, [Fecha de oferta])) as trimestres_unicos,
                MIN([Fecha de oferta]) as fecha_minima,
                MAX([Fecha de oferta]) as fecha_maxima,
                SUM(Total) as monto_total,
                COUNT(DISTINCT Vendedor) as vendedores_unicos,
                COUNT(DISTINCT Cliente) as clientes_unicos,
                COUNT(DISTINCT Familia) as familias_productos
            FROM {table_name}
            """
            
            df_info = self.db.execute_query(info_query)
            
            # Query para distribución por trimestre
            trimestre_query = f"""
            SELECT 
                YEAR([Fecha de oferta]) as año,
                DATEPART(quarter, [Fecha de oferta]) as trimestre,
                COUNT(*) as total_registros,
                SUM(Total) as monto_total,
                COUNT(DISTINCT Vendedor) as vendedores_unicos,
                COUNT(DISTINCT Cliente) as clientes_unicos
            FROM {table_name}
            GROUP BY YEAR([Fecha de oferta]), DATEPART(quarter, [Fecha de oferta])
            ORDER BY año DESC, trimestre DESC
            """
            
            df_trimestres = self.db.execute_query(trimestre_query)
            
            return {
                "success": True,
                "message": "Quarterly table information retrieved successfully",
                "data": {
                    "general_info": df_info.to_dict('records')[0] if not df_info.empty else {},
                    "trimestre_distribution": df_trimestres.to_dict('records') if not df_trimestres.empty else []
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving quarterly table info: {str(e)}",
                "data": {},
                "timestamp": datetime.now().isoformat()
            }
    
    def get_complete_period_table(self, period: str, limit: int = None, offset: int = 0, filters: dict = None) -> dict:
        """Obtener tabla completa por período con paginación"""
        try:
            table_name = self.get_table_name_by_period(period)
            
            # Construir condiciones WHERE
            where_conditions = []
            if filters:
                if filters.get('vendedor'):
                    where_conditions.append(f"Vendedor LIKE '%{filters['vendedor']}%'")
                if filters.get('cliente'):
                    where_conditions.append(f"Cliente LIKE '%{filters['cliente']}%'")
                if filters.get('categoria'):
                    where_conditions.append(f"Rubro = '{filters['categoria']}'")
                if filters.get('estado'):
                    where_conditions.append(f"Estado = '{filters['estado']}'")
                if filters.get('fecha_desde'):
                    where_conditions.append(f"[Fecha de oferta] >= '{filters['fecha_desde']}'")
                if filters.get('fecha_hasta'):
                    where_conditions.append(f"[Fecha de oferta] <= '{filters['fecha_hasta']}'")
                if filters.get('familia'):
                    where_conditions.append(f"Familia LIKE '%{filters['familia']}%'")
                if filters.get('canal'):
                    where_conditions.append(f"Canal LIKE '%{filters['canal']}%'")
                if filters.get('departamento'):
                    where_conditions.append(f"Departamento LIKE '%{filters['departamento']}%'")
                
                # Filtros específicos por período
                if period in ['quarterly', 'monthly', 'weekly']:
                    if filters.get('trimestre'):
                        where_conditions.append(f"DATEPART(quarter, [Fecha de oferta]) = {filters['trimestre']}")
                    if filters.get('mes'):
                        where_conditions.append(f"MONTH([Fecha de oferta]) = {filters['mes']}")
                    if filters.get('año'):
                        where_conditions.append(f"YEAR([Fecha de oferta]) = {filters['año']}")
            
            where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Query para contar total de registros
            count_query = f"SELECT COUNT(*) as total FROM {table_name}{where_clause}"
            count_result = self.db.execute_query(count_query)
            total_records = count_result.iloc[0]['total'] if not count_result.empty else 0
            
            # Query para obtener los datos
            limit_clause = ""
            if limit:
                limit_clause = f" ORDER BY [Fecha de oferta] DESC OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"
            else:
                limit_clause = " ORDER BY [Fecha de oferta] DESC"
            
            # Columnas específicas según el período
            if period == 'summary':
                columns = """
                    Vendedor,
                    total_ofertas,
                    cantidad_total,
                    monto_total,
                    primera_oferta,
                    ultima_oferta,
                    processed_at
                """
            else:
                columns = """
                    [Referencia de pedido],
                    [Fecha de oferta],
                    Vendedor,
                    Cliente,
                    [RUT Cliente],
                    SKU,
                    [Descipción],
                    Familia,
                    Marca,
                    [Cant. producto],
                    [RPT Precio unitario],
                    [Descuento %],
                    Total,
                    Estado,
                    Comuna,
                    Canal,
                    Departamento,
                    Rubro,
                    processed_at
                """
            
            data_query = f"""
            SELECT {columns}
            FROM {table_name}{where_clause}{limit_clause}
            """
            
            df = self.db.execute_query(data_query)
            
            return self.format_response(
                df, 
                f"{period.title()} data retrieved successfully. Showing {len(df)} of {total_records} records.",
                total_records
            )
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving {period} data: {str(e)}",
                "data": [],
                "total_records": 0,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_period_table_info(self, period: str) -> dict:
        """Obtener información general de una tabla por período"""
        try:
            table_name = self.get_table_name_by_period(period)
            
            if period == 'summary':
                info_query = f"""
                SELECT 
                    COUNT(*) as total_registros,
                    SUM(total_ofertas) as total_ofertas_sum,
                    SUM(cantidad_total) as cantidad_total_sum,
                    SUM(monto_total) as monto_total_sum,
                    MIN(primera_oferta) as fecha_minima,
                    MAX(ultima_oferta) as fecha_maxima,
                    COUNT(DISTINCT Vendedor) as vendedores_unicos
                FROM {table_name}
                """
                
                df_info = self.db.execute_query(info_query)
                
                return {
                    "success": True,
                    "message": f"{period.title()} table information retrieved successfully",
                    "data": {
                        "general_info": df_info.to_dict('records')[0] if not df_info.empty else {},
                        "table_type": "summary"
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                info_query = f"""
                SELECT 
                    COUNT(*) as total_registros,
                    COUNT(DISTINCT YEAR([Fecha de oferta])) as años_unicos,
                    COUNT(DISTINCT MONTH([Fecha de oferta])) as meses_unicos,
                    MIN([Fecha de oferta]) as fecha_minima,
                    MAX([Fecha de oferta]) as fecha_maxima,
                    SUM(Total) as monto_total,
                    COUNT(DISTINCT Vendedor) as vendedores_unicos,
                    COUNT(DISTINCT Cliente) as clientes_unicos,
                    COUNT(DISTINCT Familia) as familias_productos
                FROM {table_name}
                """
                
                df_info = self.db.execute_query(info_query)
                
                # Query para distribución temporal según el período
                if period == 'daily':
                    temporal_query = f"""
                    SELECT 
                        CAST([Fecha de oferta] as DATE) as fecha,
                        COUNT(*) as total_registros,
                        SUM(Total) as monto_total,
                        COUNT(DISTINCT Vendedor) as vendedores_unicos,
                        COUNT(DISTINCT Cliente) as clientes_unicos
                    FROM {table_name}
                    GROUP BY CAST([Fecha de oferta] as DATE)
                    ORDER BY CAST([Fecha de oferta] as DATE) DESC
                    """
                elif period == 'weekly':
                    temporal_query = f"""
                    SELECT 
                        YEAR([Fecha de oferta]) as año,
                        DATEPART(week, [Fecha de oferta]) as semana,
                        COUNT(*) as total_registros,
                        SUM(Total) as monto_total,
                        COUNT(DISTINCT Vendedor) as vendedores_unicos,
                        COUNT(DISTINCT Cliente) as clientes_unicos
                    FROM {table_name}
                    GROUP BY YEAR([Fecha de oferta]), DATEPART(week, [Fecha de oferta])
                    ORDER BY año DESC, semana DESC
                    """
                elif period == 'monthly':
                    temporal_query = f"""
                    SELECT 
                        YEAR([Fecha de oferta]) as año,
                        MONTH([Fecha de oferta]) as mes,
                        COUNT(*) as total_registros,
                        SUM(Total) as monto_total,
                        COUNT(DISTINCT Vendedor) as vendedores_unicos,
                        COUNT(DISTINCT Cliente) as clientes_unicos
                    FROM {table_name}
                    GROUP BY YEAR([Fecha de oferta]), MONTH([Fecha de oferta])
                    ORDER BY año DESC, mes DESC
                    """
                else:
                    temporal_query = info_query  # Fallback
                
                df_temporal = self.db.execute_query(temporal_query)
                
                return {
                    "success": True,
                    "message": f"{period.title()} table information retrieved successfully",
                    "data": {
                        "general_info": df_info.to_dict('records')[0] if not df_info.empty else {},
                        "temporal_distribution": df_temporal.to_dict('records') if not df_temporal.empty else [],
                        "table_type": period
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving {period} table info: {str(e)}",
                "data": {},
                "timestamp": datetime.now().isoformat()
            }

# Instanciar servicio
analytics_service = AnalyticsService()

# Endpoints de la API

@analytics_bp.route('/sales/<period>', methods=['GET'])
def get_sales_data(period):
    """
    Obtener datos de ventas por período
    GET /api/analytics/sales/daily?limit=100&offset=0&vendedor=Juan&categoria=Bebidas
    """
    try:
        # Parámetros de consulta
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Filtros opcionales
        filters = {}
        if request.args.get('vendedor'):
            filters['vendedor'] = request.args.get('vendedor')
        if request.args.get('cliente'):
            filters['cliente'] = request.args.get('cliente')
        if request.args.get('categoria'):
            filters['categoria'] = request.args.get('categoria')
        if request.args.get('estado'):
            filters['estado'] = request.args.get('estado')
        if request.args.get('fecha_desde'):
            filters['fecha_desde'] = request.args.get('fecha_desde')
        if request.args.get('fecha_hasta'):
            filters['fecha_hasta'] = request.args.get('fecha_hasta')
        
        result = analytics_service.get_sales_data(period, limit, offset, filters)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error in sales endpoint: {str(e)}",
            "data": [],
            "timestamp": datetime.now().isoformat()
        }), 500

@analytics_bp.route('/summary/<period>', methods=['GET'])
def get_summary(period):
    """
    Obtener resumen agrupado
    GET /api/analytics/summary/daily?group_by=vendedor
    """
    try:
        group_by = request.args.get('group_by', 'date')
        
        result = analytics_service.get_summary_by_period(period, group_by)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error in summary endpoint: {str(e)}",
            "data": [],
            "timestamp": datetime.now().isoformat()
        }), 500

@analytics_bp.route('/top/<period>', methods=['GET'])
def get_top_performers(period):
    """
    Obtener top performers
    GET /api/analytics/top/daily?metric=monto&limit=10
    """
    try:
        metric = request.args.get('metric', 'monto')
        limit = request.args.get('limit', 10, type=int)
        
        result = analytics_service.get_top_performers(period, metric, limit)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error in top performers endpoint: {str(e)}",
            "data": [],
            "timestamp": datetime.now().isoformat()
        }), 500

@analytics_bp.route('/kpis/<period>', methods=['GET'])
def get_kpis(period):
    """
    Obtener KPIs principales
    GET /api/analytics/kpis/daily
    """
    try:
        result = analytics_service.get_kpis(period)
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error in KPIs endpoint: {str(e)}",
            "data": {},
            "timestamp": datetime.now().isoformat()
        }), 500

@analytics_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db = DatabaseConnection()
        connection_ok = db.test_connection()
        
        return jsonify({
            "success": True,
            "message": "Analytics API is healthy",
            "database_connection": connection_ok,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Health check failed: {str(e)}",
            "database_connection": False,
            "timestamp": datetime.now().isoformat()
        }), 500

# Endpoints genéricos agregados - Los específicos de quarterly se han reemplazado por los genéricos

@analytics_bp.route('/<period>/complete', methods=['GET'])
def get_complete_period_data(period):
    """
    Obtener tabla completa por período
    GET /api/analytics/{period}/complete?limit=1000&offset=0&vendedor=Juan
    Períodos válidos: daily, weekly, monthly, quarterly, summary
    """
    try:
        # Validar período
        valid_periods = ['daily', 'weekly', 'monthly', 'quarterly', 'summary']
        if period not in valid_periods:
            return Response(
                json.dumps({
                    "success": False,
                    "message": f"Invalid period. Valid periods: {', '.join(valid_periods)}",
                    "data": [],
                    "timestamp": datetime.now().isoformat()
                }), 
                mimetype='application/json'
            ), 400
        
        # Parámetros de paginación
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Filtros opcionales
        filters = {}
        if request.args.get('vendedor'):
            filters['vendedor'] = request.args.get('vendedor')
        if request.args.get('cliente'):
            filters['cliente'] = request.args.get('cliente')
        if request.args.get('categoria'):
            filters['categoria'] = request.args.get('categoria')
        if request.args.get('estado'):
            filters['estado'] = request.args.get('estado')
        if request.args.get('fecha_desde'):
            filters['fecha_desde'] = request.args.get('fecha_desde')
        if request.args.get('fecha_hasta'):
            filters['fecha_hasta'] = request.args.get('fecha_hasta')
        if request.args.get('familia'):
            filters['familia'] = request.args.get('familia')
        if request.args.get('canal'):
            filters['canal'] = request.args.get('canal')
        if request.args.get('departamento'):
            filters['departamento'] = request.args.get('departamento')
        if request.args.get('trimestre'):
            filters['trimestre'] = request.args.get('trimestre')
        if request.args.get('mes'):
            filters['mes'] = request.args.get('mes')
        if request.args.get('año'):
            filters['año'] = request.args.get('año')
        
        # Usar el método específico para quarterly o genérico para otros
        if period == 'quarterly':
            result = analytics_service.get_complete_quarterly_table(limit, offset, filters)
        else:
            result = analytics_service.get_complete_period_table(period, limit, offset, filters)
        
        # Serialización JSON personalizada
        def custom_serializer(obj):
            if pd.isna(obj):
                return None
            elif isinstance(obj, (pd.Timestamp, datetime)):
                return obj.isoformat() if obj else None
            elif isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif hasattr(obj, 'item'):
                try:
                    return obj.item()
                except:
                    return str(obj)
            return str(obj)
        
        json_str = json.dumps(result, default=custom_serializer)
        return Response(json_str, mimetype='application/json'), 200 if result['success'] else 400
        
    except Exception as e:
        error_response = {
            "success": False,
            "message": f"Error in {period} complete endpoint: {str(e)}",
            "data": [],
            "timestamp": datetime.now().isoformat()
        }
        return Response(json.dumps(error_response), mimetype='application/json'), 500

@analytics_bp.route('/<period>/info', methods=['GET'])
def get_period_info(period):
    """
    Obtener información general de una tabla por período
    GET /api/analytics/{period}/info
    Períodos válidos: daily, weekly, monthly, quarterly, summary
    """
    try:
        # Validar período
        valid_periods = ['daily', 'weekly', 'monthly', 'quarterly', 'summary']
        if period not in valid_periods:
            return Response(
                json.dumps({
                    "success": False,
                    "message": f"Invalid period. Valid periods: {', '.join(valid_periods)}",
                    "data": {},
                    "timestamp": datetime.now().isoformat()
                }), 
                mimetype='application/json'
            ), 400
        
        # Usar el método específico para quarterly o genérico para otros
        if period == 'quarterly':
            result = analytics_service.get_quarterly_table_info()
        else:
            result = analytics_service.get_period_table_info(period)
        
        # Serialización JSON personalizada
        def custom_serializer(obj):
            if pd.isna(obj):
                return None
            elif isinstance(obj, (pd.Timestamp, datetime)):
                return obj.isoformat() if obj else None
            elif isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif hasattr(obj, 'item'):
                try:
                    return obj.item()
                except:
                    return str(obj)
            return str(obj)
        
        json_str = json.dumps(result, default=custom_serializer)
        return Response(json_str, mimetype='application/json'), 200 if result['success'] else 400
        
    except Exception as e:
        error_response = {
            "success": False,
            "message": f"Error in {period} info endpoint: {str(e)}",
            "data": {},
            "timestamp": datetime.now().isoformat()
        }
        return Response(json.dumps(error_response), mimetype='application/json'), 500

@analytics_bp.route('/periods/available', methods=['GET'])
def get_available_periods():
    """
    Obtener lista de períodos disponibles con sus estadísticas
    GET /api/analytics/periods/available
    """
    try:
        periods = ['daily', 'weekly', 'monthly', 'quarterly', 'summary']
        available_periods = []
        
        for period in periods:
            try:
                table_name = analytics_service.get_table_name_by_period(period)
                
                # Verificar si la tabla existe
                check_query = f"SELECT COUNT(*) as count FROM {table_name}"
                result = analytics_service.db.execute_query(check_query)
                
                if not result.empty and result.iloc[0]['count'] > 0:
                    count = result.iloc[0]['count']
                    available_periods.append({
                        'period': period,
                        'table_name': table_name,
                        'display_name': period.title(),
                        'record_count': int(count),
                        'available': True
                    })
                else:
                    available_periods.append({
                        'period': period,
                        'table_name': table_name,
                        'display_name': period.title(),
                        'record_count': 0,
                        'available': False
                    })
                    
            except Exception as e:
                available_periods.append({
                    'period': period,
                    'table_name': analytics_service.get_table_name_by_period(period),
                    'display_name': period.title(),
                    'record_count': 0,
                    'available': False,
                    'error': str(e)
                })
        
        return Response(
            json.dumps({
                "success": True,
                "message": "Available periods retrieved successfully",
                "data": available_periods,
                "timestamp": datetime.now().isoformat()
            }), 
            mimetype='application/json'
        ), 200
        
    except Exception as e:
        error_response = {
            "success": False,
            "message": f"Error retrieving available periods: {str(e)}",
            "data": [],
            "timestamp": datetime.now().isoformat()
        }
        return Response(json.dumps(error_response), mimetype='application/json'), 500

import xmlrpc.client
from flask import Blueprint, jsonify, request
from dotenv import load_dotenv
import os

# Crea el Blueprint
odoo_bp = Blueprint('odoo_api', __name__)

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Obtene las variables de entorno
url = os.getenv('ODOO_URL')
db = os.getenv('ODOO_DB')
username = os.getenv('ODOO_USERNAME')
password = os.getenv('ODOO_PASSWORD')

@odoo_bp.route('/sale_orders/date/<string:date_range>', methods=['GET'])
@odoo_bp.route('/sale_orders/<string:order_names>', methods=['GET'])
def get_sale_orders(date_range=None, order_names=None):
    try:
        domain = []
        if date_range:
            params = date_range.split('&')
            if len(params) != 2 or not all(len(p) == 10 and p.count('-') == 2 for p in params):
                return jsonify({"error": "Para búsqueda por fechas usa: YYYY-MM-DD&YYYY-MM-DD"}), 400
            domain = [
                ['date_order', '>=', params[0]],
                ['date_order', '<=', params[1]]
            ]
        elif order_names:
            params = order_names.split('&')
            domain = [['name', 'in', params]]
        else:
            return jsonify({"error": "Parámetros de búsqueda no proporcionados"}), 400

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        sale_order_ids = models.execute_kw(db, uid, password,
            'sale.order', 'search',
            [domain])
#Información de cabecera
        if sale_order_ids:
            header_fields = [
                'name', 'state', 'project_id', 'construction_company', 'decorator', 
                'architect', 'partner_id', 'partner_invoice_id', 
                'partner_shipping_id', 'client_order_ref', 'payment_term_id','date_order', 
                'validity_date', 'note','np_sei_cotfin', 'np_sei_vreserva', 'np_sei_vcalzada', 
                'np_sei_factanticpag', 'np_sei_esp', 'np_sei_arq2', 'np_sei_tdes',
                'np_sei_einm', 'np_sei_obc', 'np_sei_pesodoc', 'np_sei_nob', 'np_oport', 
                'np_sei_autoriztc', 'np_origen_documento', 'order_line', 'intermediary', 'nxt_id_erp',
                'user_id','ov_nxt_sync', 'ov_nxt_id_erp', 'ov_docnum_ref'
            ]

            sale_orders = models.execute_kw(db, uid, password,
                'sale.order', 'read',
                [sale_order_ids],
                {'fields': header_fields})

            # Obtiene información de empleados
            for order in sale_orders:
                if order.get('user_id'):
                    employee_ids = models.execute_kw(db, uid, password,
                        'hr.employee', 'search',
                        [[('user_id', '=', order['user_id'][0])]])
                    
                    if employee_ids:
                        employee_data = models.execute_kw(db, uid, password,
                            'hr.employee', 'read',
                            [employee_ids[0]],
                            {'fields': ['np_sei_geo', 'np_sei_une', 'np_sei_area']})
                        
                        if employee_data:
                            order['np_sei_geo'] = employee_data[0].get('np_sei_geo', False)
                            order['np_sei_une'] = employee_data[0].get('np_sei_une', False)
                            order['np_sei_area'] = employee_data[0].get('np_sei_area', False)

            # Obtiene los códigos de nxt_id_erp
            partner_ids = [order['partner_id'][0] for order in sale_orders if order['partner_id']]
            partners = models.execute_kw(db, uid, password,
                'res.partner', 'read',
                [partner_ids],
                {'fields': ['nxt_id_erp']})

            partner_dict = {partner['id']: partner['nxt_id_erp'] for partner in partners}

            for order in sale_orders:
                partner_id = order.get('partner_id')
                if partner_id:
                    order['nxt_id_erp'] = partner_dict.get(partner_id[0], '')

            line_fields = [
                'product_id', 'product_uom_qty', 'np_rpt_base_price', 'order_id',
                'np_fecha_de_entrega', 'np_rpt_base_price', 'np_mo_price_unit', 'source_currency_id',
                'np_rate_currency', 'discount', 'tax_id', 'price_subtotal', 
                'discount', 'np_original_discount',
                'np_rpt_flete_unitario', 'np_product_sku', 'source_currency_id', 'np_sei_cdp'
            ]

            order_line_ids = [line_id for order in sale_orders for line_id in order['order_line']]
            sale_order_lines = models.execute_kw(db, uid, password,
                'sale.order.line', 'read',
                [order_line_ids],
                {'fields': line_fields})

            sale_order_lines_grouped = {}
            for line in sale_order_lines:
                order_id = line['order_id'][0]
                if order_id not in sale_order_lines_grouped:
                    sale_order_lines_grouped[order_id] = []
                sale_order_lines_grouped[order_id].append(line)

            for order in sale_orders:
                order['sale_order_line_data'] = sale_order_lines_grouped.get(order['id'], [])

            result = [{"sale_order_data": order} for order in sale_orders]

            return jsonify(result)
        else:
            return jsonify({"error": "No se encontraron órdenes de venta"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@odoo_bp.route('/update_fields/<order_names>', methods=['GET'])
@odoo_bp.route('/update_fields/date/<date_range>', methods=['GET'])
def update_fields(order_names=None, date_range=None):
    try:
        domain = []

        if date_range:
            date_start, date_end = date_range.split('&')
            domain.append(['date_order', '>=', date_start])
            domain.append(['date_order', '<=', date_end])
        elif order_names:
            order_names_list = order_names.split('&')
            domain.append(['name', 'in', order_names_list])
        else:
            return jsonify({"error": "No se proporcionaron parámetros de búsqueda"}), 400

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})

        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        # Buscar las Órdenes de Venta
        sale_order_ids = models.execute_kw(db, uid, password,
            'sale.order', 'search',
            [domain])

        if sale_order_ids:
            # Campos específicos para la cabecera y del modelo sale.order y sale.order.line
            header_fields = [
                'name', 'project_id', 'state', 'construction_company', 'decorator', 
                'architect', 'construction_company', 'order_line', 'intermediary'
            ]

            line_fields = [
                'order_id', 'discount', 'np_original_discount', 'np_rpt_flete_unitario'
            ]

            # Leer los campos de las Órdenes de Venta
            sale_orders = models.execute_kw(db, uid, password,
                'sale.order', 'read',
                [sale_order_ids],
                {'fields': header_fields})

            # Obtener las líneas de las Órdenes de Venta
            order_line_ids = [line_id for order in sale_orders for line_id in order['order_line']]
            sale_order_lines = models.execute_kw(db, uid, password,
                'sale.order.line', 'read',
                [order_line_ids],
                {'fields': line_fields})

            # Ordenar y agrupar las órdenes de venta por el código de la orden
            sale_orders_sorted = sorted(sale_orders, key=lambda x: x['name'])
            sale_order_lines_grouped = {}
            for line in sale_order_lines:
                order_id = line['order_id'][0]
                if order_id not in sale_order_lines_grouped:
                    sale_order_lines_grouped[order_id] = []
                sale_order_lines_grouped[order_id].append(line)

            response = {
                "sale_order_data": sale_orders_sorted,
                "sale_order_line_data": sale_order_lines
            }

            return jsonify(response)
        else:
            return jsonify({"error": "No se encontraron órdenes de venta"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@odoo_bp.route('/sale_orders_status/<string:search_params>', methods=['GET'])
def get_sales_order_status(search_params):
    
    try:
        domain = []
        params = search_params.split('&')
        
        # Detectar si son fechas (si el primer parámetro tiene formato YYYY-MM-DD)
        if len(params[0]) == 10 and params[0].count('-') == 2:
            if len(params) != 2:
                return jsonify({"error": "Para búsqueda por fechas use: YYYY-MM-DD&YYYY-MM-DD"}), 400
            domain = [
                ('date_order', '>=', params[0]),
                ('date_order', '<=', params[1])
            ]
        # Si no son fechas, buscar por códigos
        else:
            domain = [('name', 'in', params)]

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        sale_order_ids = models.execute_kw(db, uid, password,
            'sale.order', 'search',
            [domain])

        if sale_order_ids:
            sale_orders = models.execute_kw(db, uid, password,
                'sale.order', 'read',
                [sale_order_ids],
                {'fields': ['name', 'state']})

            return jsonify({"orders_status": sale_orders})
        else:
            return jsonify({"error": "No sale orders found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
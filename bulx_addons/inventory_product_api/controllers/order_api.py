import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class Bulx(http.Controller):

    def bulx_create_address(self, rec):
        if "address_type" in rec and rec['address_type']:
            if rec['address_type'] not in ['Home', 'Business']:
                return {'status': 500, 'message': "address_type must be 'Home','Business'"}
        if "building_type" in rec and rec['building_type']:
            if rec['building_type'] not in ['Apartment', 'Villa_House']:
                return {'status': 500, 'message': "building_type must be 'Apartment','Villa_House'"}
        if not 'region_id' in rec and rec['region_id']:
            return {'status': 500, 'message': "region_id field is required and blank is not acceptable"}
        else:
            region_id = request.env['bulx.region'].sudo().search([('bulx_id', '=', rec['region_id'])])
        vals = {
            "address_type": rec['address_type'] if "address_type" in rec else False,
            'building_type': rec['building_type'] if "building_type" in rec else False,
            'street': rec['street'] if "street" in rec else False,
            'land_mark': rec['land_mark'] if "land_mark" in rec else False,
            'latitude': rec['latitude'] if "latitude" in rec else False,
            'Longitude': rec['Longitude'] if "Longitude" in rec else False,
            'building_number': rec['building_number'] if "building_number" in rec else False,
            'villa_number': rec['villa_number'] if "villa_number" in rec else False,
            'floor_number': rec['floor_number'] if "floor_number" in rec else False,
            'apartment_number': rec['apartment_number'] if "apartment_number" in rec else False,
            'region_id': region_id.id if "region_id" in rec else False,
            'is_api': True,
        }
        return vals

    @http.route('/bulx/create-order', type='json', auth='public')
    def bulx_create_order(self, **rec):
        logging.warn(rec)
        if not 'bulx_id' in rec:
            return {'status': 500, 'message': "bulx_id field is required"}
        if not "customer_code" in rec:
            return {'status': 500, 'message': "customer_code field is required and blank is not acceptable"}
        if not "order_date" in rec:
            return {'status': 500, 'message': "product_id field is required and blank is not acceptable"}
        if not 'order_list' in rec:
            return {'status': 500, 'message': "order_list field is required and blank is not acceptable"}
        if not 'address_details' in rec:
            return {'status': 500, 'message': "address_details field is required "}
        if not 'shipping_fees' in rec:
            return {'status': 500, 'message': "shipping_fees is required"}
        for line in rec['order_list']:
            if not "product_code" in line:
                return {'status': 500, 'message': "product_code field is required and blank is not acceptable"}
            print(line)
            if not "qty" in line:
                return {'status': 500, 'message': "qty field is required and blank is not acceptable"}
            if not "price" in line:
                return {'status': 500, 'message': "price field is required and blank is not acceptable"}
            if not "description" in line:
                return {'status': 500, 'message': "description field is required and blank is not acceptable"}
            if not "delivery_days" in line:
                return {'status': 500, 'message': "delivery_days field is required and blank is not acceptable"}

        customer_id = request.env['res.partner'].sudo().search([('bulx_code', '=', rec['customer_code'])])
        if not customer_id:
            return {'status': 500, 'message': "Customer not found"}
        address = self.bulx_create_address(rec['address_details'])
        print(address, "address")
        vals = {
            'partner_id': customer_id.id,
            'date_order': rec['order_date'],
            'bulx_id': rec['bulx_id'],
            'bulx_code': rec['bulx_code'],
            'payment_method':rec['payment_method'],
            'shipping_fees': rec['shipping_fees']
        }
        vals.update(address)
        order_obj = request.env['sale.order'].sudo().create(vals)
        for order in rec['order_list']:
            print(order)
            logging.warn(order)
            product_id = request.env['product.product'].sudo().search([('bulx_id', '=', order['product_code'])])
            if not product_id:
                order_obj.unlink()
                return {'status': 500, 'message': "Product not found"}
            request.env['sale.order.line'].sudo().create({
                "product_id": product_id.id,
                "name": order['description'] if order['description'] else product_id.name,
                'product_uom': product_id.uom_id.id,
                'product_uom_qty': order["qty"],
                'price_unit': order['price'],
                'customer_lead': 1,
                'order_id': order_obj.id,
            })
        product_id = request.env['product.product'].sudo().search([('name', '=', 'shipment')])
        if product_id:
            request.env['sale.order.line'].sudo().create({
                "product_id": product_id.id,
                "name": "shipment",
                'product_uom': product_id.uom_id.id,
                'product_uom_qty': 1,
                'price_unit': rec['shipping_fees'],
                'customer_lead': 1,
                'order_id': order_obj.id,
            })
        else:
            return {'status': 500, 'messagate': "shipment not found" + order_obj.name}

        return {"status": 200, "message": "order created successfully"}

    @http.route('/bulx/update-order-status', type='json', auth='public')
    def bulx_update_order_state(self, **rec):
        print(rec)
        logging.warn(rec)
        if not 'bulx_id' in rec:
            return {'status': 500, 'message': "bulx_id field is required"}
        if not "status" in rec:
            return {'status': 500, 'message': "status field is required and blank is not acceptable"}
        if rec['status'] not in ['new', 'preparing', 'shipped', 'delivered', 'cancelled']:
            return {'status': 500, 'message': "status must be one of  ['new','preparing','shipped','delivered','cancelled']"}
        vals = {
            'order_status_in': rec['status'],
            'is_api': True,
        }
        sale_order = request.env['sale.order'].sudo().search([('bulx_id', '=', rec['bulx_id'])], limit=1)
        print(sale_order)
        logging.warn(sale_order)
        if not sale_order:
            return {'status': 500, 'message': "order not found]"}
        order_s = ''
        if rec['status'] == 'new':
            order_s = 'new'
        elif rec['status'] == 'preparing':
            order_s = 'prepare'
        elif rec['status'] == 'shipped':
            order_s = 'ship'
        elif rec['status'] == 'delivered':
            order_s = 'deliver'
        elif rec['status'] == 'cancelled':
            order_s = 'cancel'
        logging.warn(order_s)
        sale_order_state = sale_order.write({"order_status_in": order_s, "is_api": True})
        logging.warn(sale_order_state)
        # order_obj = request.env['sale.order'].sudo().write(vals)
        # print(order_obj)
        if sale_order_state:
            if order_s == 'cancel':
                sale_order.action_cancel()
            return {"status": 200, "message": "order status updated successfully"}
        else:
            return {"status": 500, "message": "order status update failed"}

    @http.route('/bulx/update-order-address', type='json', auth='public')
    def bulx_update_order(self, **rec):
        print(rec)
        if not 'bulx_id' in rec:
            return {'status': 500, 'message': "bulx_id field is required"}
        if not "address_details" in rec:
            return {'status': 500, 'message': "address_details field is required and blank is not acceptable"}
        address = self.bulx_create_address(rec['address_details'])
        print(address, "address")
        vals = {'is_api'}
        vals.update(address)
        print(vals)
        order_obj = request.env['sale.order'].sudo().search([('bulx_id', '=', rec['bulx_id'])])
        if not order_obj:
            return {'status': 500, 'message': "Order not found"}
        stat = order_obj.write(vals)
        if stat:
            return {"status": 200, "message": "order update successfully"}
        else:
            return {"status": 400, "message": "order update failed"}

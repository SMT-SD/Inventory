from odoo import http
from odoo.http import request


class Bulx(http.Controller):
    @http.route('/bulx/create-customer', type='json', auth='public')
    def bulx_create_customer(self, **rec):
        if not 'code' in rec and rec['code']:
            return {'status': 500, 'message': "code field is required and blank is not acceptable"}
        if not 'id' in rec and rec['id']:
            return {'status': 500, 'message': "id field is required and blank is not acceptable"}
        if not 'phone' in rec and rec['phone']:
            return {'status': 500, 'message': "phone field is required and blank is not acceptable"}
        if 'name' in rec and rec['name']:
            category = request.env['res.partner'].sudo().create(
                {
                    'is_api': True,
                    'name': rec['name'],
                    'customer': 1,
                    'bulx_code': rec['id'],
                    'ref': rec['code'],
                    'phone': rec['phone'] if 'phone' in rec else False,
                    'email': rec['email'] if 'email' in rec else False,
                })
        else:
            return {'status': 500, 'message': "name field is required and blank is not acceptabel"}
        return {'status': 200, 'message': category.name + "- success"}

    @http.route('/bulx/update-customer', type='json', auth='public')
    def bulx_update_customer(self, **rec):
        if not 'id' in rec :
            return {'status': 500, 'message': "code field is required and blank is not acceptable"}
        customer = request.env['res.partner'].sudo().search([('bulx_code', '=', rec['id'])])
        customer_valsue = {'is_api': True}
        if 'name' in rec and rec['name']:
            customer_valsue['name'] = rec['name']
        if 'phone' in rec and rec['phone']:
            customer_valsue['phone'] = rec['phone']
        if 'email' in rec and rec['email']:
            customer_valsue['email'] = rec['email']
        customer.sudo().write(customer_valsue)
        return {'status': 200, 'message': " update success"}

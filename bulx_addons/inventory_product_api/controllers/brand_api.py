from odoo import http
from odoo.http import request


class Bulx(http.Controller):

    @http.route('/bulx/create-brand', type='json', auth='public')
    def bulx_create_brand(self, **rec):
        if not 'name' in rec and rec['name']:
            return {'status': 500, 'message': "name field is required and blank is not acceptable"}
        if not 'arabic_name' in rec and rec['arabic_name']:
            return {'status': 500, 'message': "arabic_name field is required and blank is not acceptable"}
        if not 'id' in rec and rec['id']:
            return {'status': 500, 'message': "id field is required and blank is not acceptable"}
        brand = request.env['product.brand'].sudo().create(
            {'name': rec['name'], 'arabic_name': rec['arabic_name'], 'code': rec['id'], 'is_api': True})
        return {'status': 200, 'message': brand.name + "- success"}

    @http.route('/bulx/update-brand', type='json', auth='public')
    def bulx_update_brand(self, **rec):
        brandv = {'is_api': True}
        if not 'id' in rec and rec['id']:
            return {'status': 500, 'message': "id field is required and blank is not acceptable"}
        if 'name' in rec and rec['name']:
            brandv['name'] = rec['name']
        if 'arabic_name' in rec and rec['arabic_name']:
            brandv['arabic_name'] = rec['arabic_name']
        brand_id = request.env['product.brand'].sudo().search([('code', '=', rec['id'])])
        if not brand_id:
            return {'status': 500, 'message': "brand record not found in DB"}
        brand = brand_id.sudo().write(brandv)
        return {'status': 200, 'message': "updated- success"}

    @http.route('/bulx/delete-brand', type='json', auth='public')
    def bulx_delete_brand(self, **rec):
        if not 'id' in rec and rec['id']:
            return {'status': 500, 'message': "code field is required and blank is not acceptable"}
        try:
            brand_id = request.env['product.brand'].sudo().search([('code', '=', rec['id'])])
            if not brand_id:
                return {'status': 500, 'message': "brand code not found in DB"}
            brand_id.unlink()
        except:
            return {'status': 500, 'message': "cannot delete brand as it related to other record"}
        return {'status': 200, 'message': "Deleted Success"}

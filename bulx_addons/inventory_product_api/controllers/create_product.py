import base64

import requests

from odoo import http
from odoo.http import request


class Bulx(http.Controller):

    @http.route('/bulx/create-product', type='json', auth='public')
    def bulx_create_product(self, **rec):
        if 'brand' in rec:
            brand_id = request.env['product.brand'].sudo().search([('code', '=', rec['brand'])])
            if not brand_id:
                return {'status': 500,
                        'message': "brand {}is not found please check again from your side".format(rec['brand'])}
        else:
            return {'status': 500, 'message': "brand field is required"}
        if 'category' in rec:
            category_id = request.env['product.category'].sudo().search([('category_code', '=', rec['category'])])
            if not category_id:
                return {'status': 500,
                        'message': "Category {}is not found please check again from your side".format(rec['category'])}
        else:
            return {'status': 500, 'message': "Category field is required"}
        if not 'sku' in rec:
            return {'status': 500, 'message': "Sku field is required"}
        if not 'name' in rec:
            return {'status': 500, 'message': "Name field is required"}
        if not 'arabic_name' in rec:
            return {'status': 500, 'message': "Arabic Name field is required"}
        if not 'price' in rec:
            return {'status': 500, 'message': "Price  field is required"}
        if not 'retail_price' in rec:
            return {'status': 500, 'message': "retail_price  field is required"}
        if rec['sku']:
            product_sku = request.env['product.product'].sudo().search([('barcode', '=', rec['sku'])])
            if product_sku:
                return {'status': 500, 'message': "sku  is uniqe"}
        if not 'bulx_image' in rec:
            return {'status': 500, 'message': "Bulx_Image  field is required"}
        else:
            path = "img/product_" + str(rec['sku']) + "_categ.png"
            img_url = "https://bulxstaging.azureedge.net/products/" + rec["bulx_image"]
            img_data = requests.get(img_url).content
            with open(path, 'wb') as handler:
                handler.write(img_data)
            with open(path, 'rb') as handler:
                imgdata = base64.b64encode(handler.read())
        if rec['price'] > rec['retail_price']:
            return {'status': 500, 'message': "Price must be Less Than Retail Price "}
        values = {'name': rec['name'], 'arabic_name': rec['arabic_name'],
                  'image_medium': imgdata,
                  'image_medium_two': imgdata,
                  'type': 'product', 'product_brand_id': brand_id.id,
                  'description_sale': rec['english_description'] if 'english_description' in rec else False,
                  'arabic_description': rec['arabic_description'] if 'arabic_description' in rec else False,
                  'barcode': rec['sku'],
                  'active': True if rec['status'] == 'Visible' else False,
                  'lst_price': rec['price'], 'retail_price': rec['retail_price'], 'uom_id': 1, 'uom_po_id': 1,
                  'is_api': True,
                  'bulx_id': rec['bulx_id'],
                  'categ_id': category_id.id}
        print(values,"valuse")
        product = request.env['product.product'].sudo().create(values)
        return {'status': 200,
                'message': product.name + "-" + product.name + "-" + product.product_brand_id.name + "-" + "success"}

    @http.route('/bulx/update-product', type='json', auth='public')
    def bulx_update_product(self, **rec):
        valuse = {'is_api': True}
        if 'brand' in rec:
            brand_id = request.env['product.brand'].sudo().search([('code', '=', rec['brand'])])
            print(brand_id.name, "brandName")
            if not brand_id:
                return {'status': 500,
                        'message': "brand {}is not found please check again from your side".format(rec['brand'])}
            valuse.update({'product_brand_id': brand_id.id})
        else:
            return {'status': 500, 'message': "brand field is required"}
        if not 'bulx_id' in rec:
            return {'status': 500, 'message': "bulx_id Is Required"}
        if 'name' in rec and rec['name']:
            valuse.update({'name': rec['name']})
        if 'status' in rec:
            valuse.update({'active': True if rec['status'] == "Visible" else False})
        if 'arabic_name' in rec and rec['name']:
            valuse.update({'arabic_name': rec['arabic_name']})
        if 'sku' in rec and rec['sku']:
            valuse.update({'barcode': rec['sku']})
        if 'price' in rec and rec['price']:
            valuse.update({'list_price': rec['price']})
        if 'retail_price' in rec and rec['retail_price']:
            valuse.update({'retail_price': rec['retail_price']})
        if 'category' in rec:
            category_id = request.env['product.category'].sudo().search([('bulx_code', '=', rec['category'])])
            if not category_id:
                return {'status': 500,
                        'message': "Category {}is not found please check again from your side".format(rec['category'])}
            valuse.update({'categ_id': category_id.id})
        if 'bulx_image' in rec:
            path = "img/product_" + str(rec['sku']) + "_categ.png"
            img_url = "https://bulxstaging.azureedge.net/products/" + rec["bulx_image"]
            img_data = requests.get(img_url).content
            with open(path, 'wb') as handler:
                handler.write(img_data)
            with open(path, 'rb') as handler:
                imgdata = base64.b64encode(handler.read())
            valuse.update({'image_medium': imgdata, 'image_medium_two': imgdata, })
        product = request.env['product.product'].sudo().search(['|','&',('active','=',False),('active','=',True),('bulx_id', '=', rec['bulx_id'])])
        if not product:
            return {'status': 500, 'message': "Product not found"}
        product_id = product.sudo().write(valuse)
        return {'status': 200, 'message': "Update success"}

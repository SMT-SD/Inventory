import base64

import requests

from odoo import http
from odoo.http import request


class Bulx(http.Controller):
    @http.route('/bulx/create-category', type='json', auth='public')
    def bulx_create_category(self, **rec):
        imgdata = ""
        if 'bulx_image' in rec:
            path = "img/product_category" + str(rec['code']) + "_categ.png"
            img_url = "https://bulxstaging.azureedge.net/categories/" + rec["bulx_image"]
            img_data = requests.get(img_url).content
            with open(path, 'wb') as handler:
                handler.write(img_data)
            with open(path, 'rb') as handler:
                imgdata = base64.b64encode(handler.read())
                print(imgdata)
        if not 'status' in rec:
            return {'status': 500, 'message': "Status fields are required "}
        if 'name' in rec and rec['name'] and 'code' in rec and rec['code']:
            category = request.env['product.category'].sudo().create(
                {'name': rec['name'], 'bulx_code': rec['code'], "category_code": rec['code'], 'image': imgdata,
                 'active':True if rec['status'] == "Visible" else False,
                 'parent_id': 1, 'is_api': True, "arabic_name": rec['arabic_name']})
        else:
            return {'status': 500, 'message': "name and code fields are required and blank is not acceptable"}
        return {'status': 200, 'message': category.name + "- success"}

    @http.route('/bulx/update-category', type='json', auth='public')
    def bulx_update_category(self, **rec):
        valuse = {'is_api': True}
        if not 'code' in rec:
            return {'status': 500, 'message': "Code Is Required"}
        if 'name' in rec and rec['name']:
            valuse.update({'name': rec['name']})
        if 'arabic_name' in rec and rec['name']:
            valuse.update({'arabic_name': rec['arabic_name']})
        if 'status' in rec:
            valuse.update({'active': True if rec['status'] == "Visible" else False})
        if 'bulx_image' in rec:
            path = "img/product_category" + str(rec['code']) + "_categ.png"
            img_url = "https://bulxstaging.azureedge.net/categories/" + rec["bulx_image"]
            img_data = requests.get(img_url).content
            with open(path, 'wb') as handler:
                handler.write(img_data)
            with open(path, 'rb') as handler:
                imgdata = base64.b64encode(handler.read())
                print(imgdata)
            valuse.update({'image': imgdata})
        category = request.env['product.category'].sudo().search(['|','&',('active','=',False),('active','=',True),('bulx_code', '=', rec['code'])])
        print(category,"categoru")
        if not category:
            return {'status': 500, 'message': "Category not found"}
        category_id = category.sudo().write(valuse)
        return {'status': 200, 'message': "Update success"}

    @http.route('/bulx/delete-category', type='json', auth='public')
    def bulx_delete_category(self, **rec):
        if 'id' in rec and rec['id']:
            category = request.env['product.category'].sudo().search(['|','&',('active','=',False),('active','=',True),('bulx_code', '=', rec['id'])])
            print(category)
            if not category:
                return {'status': 500, 'message': "Category not found in DB"}
            try:
                category_id = category.sudo().unlink()
                if category_id:
                    return {'status': 200, 'message': "delete success"}
            except:
                return {'status': 500, 'message': "Cannot Delete Category as it is related to anther tables in db"}
        else:
            return {'status': 500, 'message': "id field is required and blank is not acceptable"}

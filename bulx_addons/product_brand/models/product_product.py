import base64
import json
import logging
import PIL
from odoo.exceptions import ValidationError
from odoo import models, api, fields,_
from ..bulx_tools import check_type
_logger = logging.getLogger(__name__)
import requests


class StockQuant(models.Model):
    _inherit = "stock.quant"

    # @api.model
    # def create(self, vals):
    #     stock_quant = super(StockQuant, self).create(vals)
    #     if stock_quant and stock_quant.location_id and stock_quant.location_id.usage == 'internal':
    #         self.product_id.write({'qty_available':self.product_id._compute_product_quantities()})
    #     return stock_quant

    # @api.model
    # def write(self, vals):
    #     print("========================================")
    #     print(vals)
    #     stock_quant = super(StockQuant, self).write(vals)
    #     if 'package_id' in vals:
    #         return stock_quant
    #     if  self.location_id and self.location_id.usage == 'internal':
    #         print(self.product_id)
    #         qty_real= self.product_id._compute_product_quantities()
    #         self.product_id.write({'qty_available':int(qty_real)})
    #     return stock_quant


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def create_product_image(self):
        print("iam in create image")
        for rec in self:
            print(rec, "rec rec rec")
            path = '/product_brand/static/src/img/' + str(rec.id) + 'categ.png'
            print(path)
            with open('img/product_brand', 'wb') as image_file:
                if not rec.image:
                    raise ValidationError(_('you shoud add an image to product with dimension 768*768'))
                image_file.write(rec.image)
                imgdata = base64.b64decode(rec.image)
                # print(imgdata)
                path = "img/product_brand" + str(rec.id) + "_product.jpeg"
                with open(path, 'wb') as f:
                    f.write(imgdata)
                up = {'Image': (path, open(path, 'rb'), "multipart/form-data"),
                      'Banner': (path, open(path, 'rb'), "multipart/form-data")}
                print(up, "Up Category")
                image = PIL.Image.open(path)
                width, height = image.size
                print(width, height)
                return up

    def _compute_product_quantities(self):
        res = self._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))
        qty_available = 0
        outgoing_qty = 0
        qty_real = 0
        real_real = 0
        for product in self:
            qty_available = res[product.id]['qty_available']
            outgoing_qty = res[product.id]['outgoing_qty']
            real_real = res[product.id]['virtual_available'] - res[product.id]['incoming_qty']
            logging.warn("qty_available",qty_available)
            logging.warn("outgoing_qty",outgoing_qty)
            logging.warn("real_real",real_real)
            qty_real = qty_available - outgoing_qty
            logging.warn("qty_done:",qty_real)
        return real_real

    def create_bulx_product(self,res_create):
        access_token = check_type.get_bulx_authintecation()
        print(access_token)
        print(res_create.barcode)
        data = {
            "EnglishName": res_create.name,
            "SKU": res_create.barcode,
            "ArabicName": res_create.arabic_name,
            "EnglishDescription": res_create.description_sale,
            "ArabicDescription": res_create.arabic_description,
            "State": "Visible" if res_create.active else "Invisible",
            "Type": "Simple",
            "Price": res_create.lst_price,
            "RetailPrice": res_create.retail_price,
            "CategoryId": res_create.categ_id.bulx_code,
            "BrandId": res_create.product_brand_id.code,
            "Quantity": 0,
            "InStock": True,
        }
        up = res_create.create_product_image()
        print(data)
        try:
            request = requests.post('https://bulxperformancetest.azurewebsites.net/api/v1/Catalog/Products',
                                    files=up, data=data, headers={'Authorization': 'Bearer %s' % access_token})
            print(request.text)
            text_val = request.text
            res = json.loads(text_val)
            print(res)
            if request.status_code == 400:
                print("CreateCreateCreate")
                raise ValidationError(request.text)
            bulx_code = res['id']
            print('brand_code',bulx_code)
            res_create.write({'bulx_id': bulx_code,'is_api':True})
            request.raise_for_status()
            # return request.json()
        except requests.HTTPError as e:
            _logger.debug("request failed with code: %r, msg: %r, content: %r",
                          e.response.status_code, e.response.reason, e.response.content)
    @api.model
    def create(self, values):
        print(values,"VALUES")
        if 'is_api' in values or values['type'] != 'product':
            res_create = super(ProductProduct, self).create(values)
            print(res_create)
            # raise Warning(res_create)
            return res_create
        res_create = super(ProductProduct, self).create(values)
        res_create.create_bulx_product(res_create)
        return res_create

    @api.multi
    def write(self, vals):
        print('write vals',vals)
        if 'is_api' in vals or 'list_price' in vals or 'image_variant' in vals :
            res_write = super(ProductProduct, self).write(vals)
            return res_write
        res_write = super(ProductProduct, self).write(vals)
        print(res_write)
        print("updateupdateupdateupdate")
        for product in self:
            if 'bulx_id' in vals:
                return res_write
            access_token = check_type.get_bulx_authintecation()

            qty_available = vals['qty_available'] if 'qty_available' in vals else product._compute_product_quantities()
            data = {
                "id":product.bulx_id,
                "SKU": product.barcode,
                "EnglishName": product.name,
                "ArabicName": product.arabic_name,
                "EnglishDescription": product.product_tmpl_id.description_sale,
                "ArabicDescription": product.product_tmpl_id.arabic_description,
                "State": "Visible" if product.active else "Invisible",
                "Type": "Simple",
                "Price": product.lst_price,
                "RetailPrice": product.retail_price,
                "CategoryId": product.categ_id.bulx_code,
                "BrandId": product.product_brand_id.code,
                "Quantity": int(qty_available),
                "InStock": True,
            }
            logging.warn(data)
            print(data)
            if product.image and 'image' in vals:
                up = product.create_product_image()
            try:
                request = requests.put('https://bulxperformancetest.azurewebsites.net/api/v1/Catalog/Products',
                                       files=up, data=data,
                                       headers={'Authorization': 'Bearer %s' % access_token}) if product.image and 'image' in vals else requests.put('https://bulxperformancetest.azurewebsites.net/api/v1/Catalog/Products',
                                        data=data,
                                       headers={'Authorization': 'Bearer %s' % access_token})
                print(request.content)
                print(request.status_code)
                if request.status_code == 404 :
                    text_val = request.text
                    res = json.loads(text_val)
                    print(res)
                    print(res["Errors"][0]["ErrorCode"])
                    error = res["Errors"][0]["ErrorCode"]
                    if error == 'product_not_found':
                        product.create_bulx_product(product)
                        return res_write
                    # raise ValidationError(res["Errors"][0]["ErrorCode"])
                if request.status_code != 200:
                    raise ValidationError(request.text)
                request.raise_for_status()
            except requests.HTTPError as e:
                _logger.debug(" request failed with code: %r, msg: %r, content: %r",
                              e.response.status_code, e.response.reason, e.response.content)
        return res_write
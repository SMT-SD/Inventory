import logging

# from requests_toolbelt.multipart.encoder import MultipartEncoder
import json
from odoo import models, fields, api
from ..bulx_tools import check_type

_logger = logging.getLogger(__name__)
import requests

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client


class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = "Product Brand"
    _order = 'name'

    brand_code = fields.Char(string='Brand Code',default='0', store=True, copy=True, track_visibility='onchange')
    name = fields.Char('Brand Name', required=True)
    code = fields.Char()
    brand_code = fields.Char(string='Brand Code', default='0', store=True, copy=True, track_visibility='onchange')
    arabic_name = fields.Char('arabic name',required=True)
    description = fields.Text(translate=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        help='Select a partner for this brand if any.',
        ondelete='restrict'
    )
    logo = fields.Binary('Logo File', attachment=True)
    product_ids = fields.One2many(
        'product.template',
        'product_brand_id',
        string='Brand Products',
    )
    products_count = fields.Integer(
        string='Number of products',
        compute='_compute_products_count',
    )

    @api.multi
    @api.depends('product_ids')
    def _compute_products_count(self):
        for brand in self:
            brand.products_count = len(brand.product_ids)

    @api.model
    def create(self, values):
        if 'is_api' in values :
            res_create = super(ProductBrand, self).create(values)
            return res_create
        res_create = super(ProductBrand, self).create(values)
        access_token = check_type.get_bulx_authintecation()
        data = {
            'EnglishName': res_create.name,
            'ArabicName': res_create.arabic_name,
        }
        print(data)
        try:
            request = requests.post('https://bulxperformancetest.azurewebsites.net/api/v1/Catalog/Brands',
                                    json=data, headers={'Authorization': 'Bearer %s' % access_token,
                                                        'Content-Type': 'application/json'}, )
            print(request.text)
            text_val = request.text
            res = json.loads(text_val)
            print(res)
            brand_code = res['id']
            res_create.write({'code':brand_code,'is_api':True})
            request.raise_for_status()
            # return request.json()
        except requests.HTTPError as e:
            _logger.debug("API request failed with code: %r, msg: %r, content: %r",
                          e.response.status_code, e.response.reason, e.response.content)
        return res_create

    @api.multi
    def write(self, vals):
        print(vals)
        if 'is_api' in vals :
            res_write = super(ProductBrand, self).write(vals)
            return res_write
        res_write = super(ProductBrand, self).write(vals)
        if 'code' in vals :
            return res_write
        access_token = check_type.get_bulx_authintecation()
        data = {"englishName": self.name, 'arabicName': self.arabic_name, 'Id': self.code}
        print(data)
        try:
            request = requests.put('https://bulxperformancetest.azurewebsites.net/api/v1/Catalog/Brands',
                                   json=data,
                                   headers={'Authorization': 'Bearer %s' % access_token,})
            print(request.content)
            print(request.status_code)
            request.raise_for_status()

        except requests.HTTPError as e:
            _logger.debug("Twitter API request failed with code: %r, msg: %r, content: %r",
                          e.response.status_code, e.response.reason, e.response.content)
        return res_write

    @api.multi
    def unlink(self):
        # code_id = self.category_code

        access_token = check_type.get_bulx_authintecation()
        data = {
            "id": self.code,
        }
        try:
            request = requests.delete('https://bulxperformancetest.azurewebsites.net/api/v1/Catalog/Brands',
                                      json=data,
                                      headers={'Authorization': 'Bearer %s' % access_token}, )
            print(request.content)
            print(request.status_code)

        except requests.HTTPError as e:
            _logger.debug("Twitter API request failed with code: %r, msg: %r, content: %r",
                          e.response.status_code, e.response.reason, e.response.content)
        rest_unlink = super(ProductBrand, self).unlink()
        return rest_unlink


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    arabic_description = fields.Text()
    arabic_name = fields.Char()
    product_brand_id = fields.Many2one(
        'product.brand',
        string='Brand',
        index=True,
        help='Select a brand for this product'
    )

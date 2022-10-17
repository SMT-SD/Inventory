import logging
import json
from odoo.osv import expression
from ..bulx_tools import check_type
import os
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
from odoo import api, fields, models
import requests
import base64
import urllib.request

class ProductCategoryCode(models.Model):
    _inherit = 'product.category'

    # _sql_constraints = [('category_code_unique', 'unique (category_code)', 'The code must be unique')]

    active = fields.Boolean(default=True)
    image = fields.Binary()
    bulx_image = fields.Char()

    category_code = fields.Char(string='Code', copy=False)
    bulx_code = fields.Char(string='Code', copy=False)
    arabic_name = fields.Char(string="Arabic Name", )
    colored_icon = fields.Char()

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            # Be sure name_search is symetric to name_get
            category_names = name.split(' / ')
            parents = list(category_names)
            child = parents.pop()
            domain = ['|', ('name', operator, child), ('category_code', operator, child)]
            if parents:
                names_ids = self.name_search(' / '.join(parents), args=args, operator='ilike', limit=limit)
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([('id', 'not in', category_ids)])
                    domain = expression.OR([[('parent_id', 'in', categories.ids)], domain])
                else:
                    domain = expression.AND([[('parent_id', 'in', category_ids)], domain])
                for i in range(1, len(category_names)):
                    domain = [[('name', operator, ' / '.join(category_names[-1 - i:]))], domain]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            categories = self.search(expression.AND([domain, args]), limit=limit)
        else:
            categories = self.search(args, limit=limit)
        return categories.name_get()

    def create_category_image(self):
        print("iam in create image")
        for rec in self:
            path = '../product_category_codes/static/src/img/' + str(rec.id) + 'categ.png'

            cwd = os.getcwd()
            print(cwd)
            # raise ValidationError(cwd)
            with open('img/product_category_codes', 'wb') as image_file:
                image_file.write(rec.image)
                imgdata = base64.b64decode(rec.image)
                path = "img/product_category_codes" + str(rec.id) + "_categ.jpeg"
                with open(path, 'wb') as f:
                    f.write(imgdata)
                up = {'SolidIcon': (path, open(path, 'rb'), "multipart/form-data"),
                      'ColoredIcon': (path, open(path, 'rb'), "multipart/form-data")}
                print(up, "Up Category")
                return up

    @api.model
    def create(self, values):
        print(values)
        if 'is_api' in values :
            res_create = super(ProductCategoryCode, self).create(values)
            return res_create
            # urllib.request.urlretrieve("https://bulxstaging.azureedge.net/products/875f4e69-4d88-4889-9995-1e3e2872a873.png", "00000001.jpg",verify=False)

        res_create = super(ProductCategoryCode, self).create(values)
        access_token = check_type.get_bulx_authintecation()
        print(access_token)
        print(values)
        data = {
            'EnglishName': res_create.name,
            'arabicName': res_create.arabic_name,
            'State': "Invisible" if not res_create.active else "Visible" ,
        }
        up = res_create.create_category_image()
        print("UP",up,"")
        try:
            request = requests.post('https://bulxperformancetest.azurewebsites.net/api/v1/Catalog/Categories',
                                    files=up, data=data, headers={'Authorization': 'Bearer %s' % access_token}, )
            print(request.text)
            text_val = request.text
            res = json.loads(text_val)
            print(res)
            brand_code = res['id']
            res_create.write({'bulx_code': brand_code})
            request.raise_for_status()
        except requests.HTTPError as e:
            _logger.debug(" API request failed with code: %r, msg: %r, content: %r",
                          e.response.status_code, e.response.reason, e.response.content)
        return res_create

    @api.multi
    def write(self, vals):
        if 'is_api' in vals:
            res_write = super(ProductCategoryCode, self).write(vals)
            return res_write
        res_write = super(ProductCategoryCode, self).write(vals)
        access_token = check_type.get_bulx_authintecation()
        up = self.create_category_image()
        data = {'Id': self.bulx_code,
                "EnglishName": self.name,
                "ArabicName": self.arabic_name,
                'State': "Invisible" if not self.active else "Visible" ,
                }
        try:
            request = requests.put('https://bulxperformancetest.azurewebsites.net/api/v1/Catalog/Categories', data=data,files=up,
                                   headers={'Authorization': 'Bearer %s' % access_token, }, )
            print(request.content)
            print(request.status_code)
            request.raise_for_status()
        except requests.HTTPError as e:
            _logger.debug("Twitter API request failed with code: %r, msg: %r, content: %r",
                          e.response.status_code, e.response.reason, e.response.content)
        return res_write

    @api.multi
    def unlink(self):
        code_id = self.bulx_code

        access_token = check_type.get_bulx_authintecation()
        print(access_token)
        data = {
            "id": self.bulx_code
        }
        try:
            request = requests.delete('https://bulxperformancetest.azurewebsites.net/api/v1/Catalog/Categories',
                                      json=data,
                                      headers={'Authorization': 'Bearer %s' % access_token, }, )
            print(request.content)
            print(request.status_code)
        except requests.HTTPError as e:
            _logger.debug("Twitter API request failed with code: %r, msg: %r, content: %r",
                          e.response.status_code, e.response.reason, e.response.content)
        rest_unlink = super(ProductCategoryCode, self).unlink()
        return rest_unlink

import logging
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from ..bulx_tools import check_type
import requests
import json
_logger = logging.getLogger(__name__)


class SyncAllData(models.TransientModel):
    _name = 'sync.all.data'

    response_data = fields.Char(default="Are you sure to sync all Product Quantities !!!")
    qty_updated = fields.Boolean()
    update_products = fields.Boolean()

    def update_bulx_stock(self, updated_list):
        access_token = check_type.get_bulx_authintecation()
        data = {
            "productStocks": updated_list
        }
        logging.warn(data)
        try:
            request = requests.post(
                'https://bulxperformancetest.azurewebsites.net/api/v1/Catalog/Products/update-stock',
                json=data,
                headers={'Authorization': 'Bearer %s' % access_token, 'Content-Type': 'application/json'})
            text_val = request.text
            res = json.loads(text_val)
            logging.warn(res)
            self.response_data = str(request.status_code)
            logging.warn(request.status_code)
            if request.status_code != 200:
                raise ValidationError(request.text)
            request.raise_for_status()
        except requests.HTTPError as e:
            _logger.debug("request failed with code: %r, msg: %r, content: %r",
                          e.response.status_code, e.response.reason, e.response.content)

    def get_products_list(self):
        products_list = []
        products = self.env['product.product'].search([('bulx_id', '!=', False), ('type','=','product')])
        for line in products:
            product_guid = line.bulx_id
            product_qty = line._compute_product_quantities()
            item = {'productId': product_guid, 'stock': int(product_qty)}
            products_list.append(item)
        logging.warn(products_list)
        self.update_bulx_stock(products_list)
        self.qty_updated = True

    # @api.onchange('update_products')
    # def update_all_products(self):
    #     if self.qty_updated == False and self.update_products:
    #         self.get_products_list()
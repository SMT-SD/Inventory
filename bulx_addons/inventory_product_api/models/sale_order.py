import logging

import requests
from odoo.exceptions import ValidationError, UserError
from odoo import fields, models, api
from ..bulx_tools import check_type

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    address_type = fields.Selection([
        ('Home', 'Home'),
        ("Business", "Business"), ])

    building_type = fields.Selection([
        ('Apartment', 'Apartment'),
        ('Villa_House', 'Villa_House')])

    street = fields.Char()
    land_mark = fields.Char()
    latitude  = fields.Float()
    Longitude  = fields.Float()
    building_number = fields.Char()
    villa_number = fields.Char()
    floor_number  = fields.Integer()
    apartment_number = fields.Integer()
    shipping_fees  = fields.Float()
    payment_method = fields.Selection([('Cash','Cash'),('POS','POS')],default="Cash")
    bulx_order_Id  = fields.Char()
    region_id = fields.Many2one('bulx.region')
    # shipment_fees = fields.Float()

    order_status_in = fields.Selection([
        ('new', 'new'),
        ('prepare', "Preparing"),
        ('ship', "On the way"),
        ('deliver', "Delivered"),
        ('cancel', "Cancelled"),
    ], default='new', track_visibility='onchange', string='Order Status')

    @api.multi
    def action_confirm(self):
        order = super(SaleOrder, self).action_confirm()

    order_state = fields.Selection([
        ('new','new'),
        ('prepare', "Preparing"),
        ('ship', "On the way"),
        ('deliver', "Delivered"),
        ('cancel', "Cancelled"),
    ], default='new', track_visibility='onchange', string='Order Status')

    bulx_id = fields.Char()
    bulx_code = fields.Char()

    @api.multi
    def write(self, vals):
        if 'is_api' in vals or not self.bulx_id:
            res_write = super(SaleOrder, self).write(vals)
            return res_write
        res_write = super(SaleOrder, self).write(vals)
        if not res_write:
            return {'status':500,'message':res_write}
        if "order_status_in" in vals:
            url = ""
            print(url)
            if self.order_status_in == 'prepare':
                url = "https://bulxperformancetest.azurewebsites.net/api/v1/Ordering/Orders/{}/prepare".format(self.bulx_id)
            elif self.order_status_in == 'ship':
                url = "https://bulxperformancetest.azurewebsites.net/api/v1/Ordering/Orders/{}/ship".format(self.bulx_id)
            elif self.order_status_in == 'deliver':
                url = "https://bulxperformancetest.azurewebsites.net/api/v1/Ordering/Orders/{}/deliver".format(self.bulx_id)
            elif self.order_status_in == 'cancel':
                url = "https://bulxperformancetest.azurewebsites.net/api/v1/Ordering/Orders/{}/admin-cancel".format(self.bulx_id)
            access_token = check_type.get_bulx_authintecation()
            try:
                if url :
                    request = requests.post(url, headers={'Authorization': 'Bearer %s' % access_token, })
                    if request.status_code == 405:
                        raise ValidationError("405 Error")
                    elif request.status_code == 400:
                        raise ValidationError(request.content)
                    request.raise_for_status()
                if self.order_status_in == 'cancel':
                    cancel_res = self.action_cancel()
                    print(cancel_res)
                    return cancel_res
            except requests.HTTPError as e:
                _logger.debug(" API request failed with code: %r, msg: %r, content: %r",
                              e.response.status_code, e.response.reason, e.response.content)
        return res_write

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    bulx_code = fields.Char()
    bulx_address = fields.One2many('bulx.address','customer_id')

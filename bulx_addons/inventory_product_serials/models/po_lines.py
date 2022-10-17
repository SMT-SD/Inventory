from odoo import api, fields, models
from odoo.tools import float_round


class InheritPoLinesBrand(models.Model):
    _inherit = 'purchase.order.line'

    brand_pp =fields.Many2one('product.brand',related='product_id.product_brand_id')


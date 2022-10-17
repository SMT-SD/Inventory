from odoo import models, fields, api, tools, exceptions, _

class HubHubAppbulx(models.Model):
    _name = "hub.hub"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', copy=True, store=True, track_visibility='onchange')
    short_name = fields.Char('Short Name/Code', copy=True, store=True, track_visibility='onchange')
    warehouse = fields.Many2one('stock.warehouse',string='Warehouse')

    lines_hub =fields.One2many('hub.bridge','hub_inverse')


class HubBridgebulx(models.Model):
    _name = "hub.bridge"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    product_id= fields.Many2one('product.product',string='Product')
    initial_demand= fields.Float(string='Initial Demand')
    quantity_done= fields.Float(string='Quantity Done')
    unit_of_measure = fields.Many2one('uom.uom',string='Unit Of Measure',related='product_id.uom_id')

    hub_inverse =fields.Many2one('hub.hub')




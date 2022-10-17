from odoo import models, fields, api, tools, exceptions, _
from odoo.exceptions import ValidationError


class StockLocationBulxOffline(models.Model):
    _inherit = "stock.location"

    is_offline_stock = fields.Boolean(string='Is offline Location?', store=True, copy=True, track_visibility='onchange')


class StockQuantBulxOffline(models.Model):
    _inherit = "stock.quant"

    is_offline_stock = fields.Boolean(string='Is offline Location?', store=True, copy=True,related='location_id.is_offline_stock',track_visibility='onchange')
    usage = fields.Selection([
        ('supplier', 'Vendor Location'),
        ('view', 'View'),
        ('internal', 'Internal Location'),
        ('customer', 'Customer Location'),
        ('inventory', 'Inventory Loss'),
        ('procurement', 'Procurement'),
        ('production', 'Production'),
        ('transit', 'Transit Location')], string='Location Type',
        default='internal', index=True, required=True,related='location_id.usage')


class ProductProductOfflineInheritClass(models.Model):
    _inherit = "product.product"

    offline_count = fields.Float(string='Offline Quantity', store=True, copy=True, track_visibility='onchange',compute='compute_offline_locations')
    online_count = fields.Float(string='Online Quantity', store=True, copy=True, track_visibility='onchange',compute='compute_offline_locations')

    @api.multi
    @api.depends('name','active','qty_available')
    def compute_offline_locations(self):
        for rec in self:
            if rec.name and rec.active==True:
                off=[]
                on=[]
                offline = self.env['stock.quant'].search(
                    [('product_id', '=', rec.id),('is_offline_stock', '=',True),('usage','=','internal')])
                online = self.env['stock.quant'].search(
                    [('product_id', '=', rec.id), ('is_offline_stock', '=', False),('usage','=','internal')])
                print(offline,"====")
                print(online)
                for record in offline:
                      off.append(record.quantity)
                print(off)
                for line in online:
                       on.append(line.quantity)
                print(on)
                rec.offline_count = sum(off)
                rec.online_count =sum(on)
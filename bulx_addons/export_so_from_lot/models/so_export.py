from odoo import models, fields, api, tools, exceptions, _
from odoo.exceptions import ValidationError


class StockProductionLotInheritExport(models.Model):
    _inherit = "stock.production.lot"

    last_sale_order = fields.Many2one('sale.order',string='Last SO',compute='cal_last_so')

    @api.multi
    @api.depends('sale_order_ids')
    def cal_last_so(self):
        for rec in self:
            list=[]
            if rec.sale_order_ids:
                for line in rec.sale_order_ids:
                    list.append(line.id)
                print(list,"====")
                print(max(list))
                max_so = max(list)
                so = self.env['sale.order'].search([('id', '=', max_so)])
                if so:
                  rec.last_sale_order = so.id


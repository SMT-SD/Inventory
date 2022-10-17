from odoo import models, fields, api, tools, exceptions, _
import datetime

class MovesProductAnalysisbulx(models.Model):
    _name = "moves.analysis"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', copy=True, store=True, track_visibility='onchange')
    no_of_days = fields.Integer(string='Number of days', copy=True, store=True, track_visibility='onchange')
    required_date = fields.Datetime('Desired Date', store=True, copy=True)
    state = fields.Selection([
        ('draft', "Draft"),
        ('finish', "Finished"),
    ], default='draft', track_visibility='onchange')

    @api.multi
    @api.onchange('no_of_days', 'required_date')
    def compute_date(self):
        for rec in self:
            approve_date = fields.datetime.now()
            # planned = (datetime.datetime.strptime(str(approve_date), '%Y-%m-%d') - datetime.timedelta(
            #     rec.no_of_days)).strftime('%Y-%m-%d')
            planned = approve_date - datetime.timedelta(rec.no_of_days)
            rec.required_date = planned

    @api.multi
    def action_start(self):
        for rec in self:
            rec.product_moves_res.unlink()
            list = []
            moves = rec.env['stock.move'].search([
                ('date', '>=', rec.required_date), ('state', '=', 'done')])
            if moves:
               for line in moves:
                    if 'OUT' not in str(line.picking_id.picking_type_id.sequence_id.prefix):
                        list.append(line.product_id)
               list2 = set(list)
               asd = []
               for m in list2:
                    asd.append({'product_id': m.id

                                }
                               )
               rec.product_moves_res = asd
               self.state = 'finish'

    product_moves_res = fields.One2many('moves.analysis_bridge', 'res_analysis_inv', copy=True, store=True,
                                        track_visibility='onchange')


class MovesProductAnalysisbulxBridge(models.Model):
    _name = "moves.analysis_bridge"

    product_id = fields.Many2one('product.product', string='Product')
    product_brand = fields.Many2one('product.brand', string='Product Brand', related='product_id.product_brand_id')
    product_category = fields.Many2one('product.category', string='Product Category', related='product_id.categ_id')

    res_analysis_inv = fields.Many2one('moves.analysis')

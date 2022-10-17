from odoo import models, fields, api,tools, exceptions, _
from odoo.tools import dateutil
import datetime


class StockProductionLotInherit(models.Model):
    _inherit="stock.production.lot"

    lot_location = fields.Many2one('stock.location',string='Location')
    exp_date = fields.Datetime(string='Expiration Date',compute='cal_exp_date_from_life')
    production_date = fields.Datetime(string='Production Date',compute='cal_exp_date_from_life')

    @api.multi
    @api.depends('life_date','product_id')
    def cal_exp_date_from_life(self):
        for line in self:
            if line.life_date:
              line.exp_date = line.life_date
              planned = line.exp_date - datetime.timedelta(line.product_id.life_time)
              line.production_date = planned


    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Serial must be unique!'),
    ]
    # name = fields.Char(
    #     'Unique Lot/Serial Number', compute='cal_lot_serial_collection',
    #     required=True, help="Unique Lot/Serial Number")
    # alternative_serial = fields.Integer(
    #     'Lot/Serial Number'
    #    , help="Lot/Serial Number")
    #
    #
    # @api.multi
    # @api.depends('alternative_serial','product_id')
    # def cal_lot_serial_collection(self):
    #   for rec in self:
    #     if rec.alternative_serial >0:
    #         rec.name = (str(rec.product_id.brand) + '/' + str(rec.product_id.category) + '/' + str(rec.alternative_serial))
    #     else:
    #         rec.name = (str(rec.product_id.brand) + '/' + str(rec.product_id.category) + '/' + '0')

    @api.multi
    @api.constrains('life_date')
    def _check_end_life_date(self):
        current_day =fields.Date.today()
        for record in self:
          if record.life_date:
            a = dateutil.parser.parse(str(record.life_date)).date()
            if a <= current_day:
                raise Warning("End of Life/Expiration Date can't be less than or equal Today Date!")

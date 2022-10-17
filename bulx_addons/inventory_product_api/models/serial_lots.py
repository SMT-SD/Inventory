from odoo import models, fields, api,tools, exceptions, _
from odoo.tools import dateutil


class StockProductionLotInherit(models.Model):
    _inherit="stock.production.lot"


    @api.multi
    @api.constrains('life_date')
    def _check_end_life_date(self):
        current_day =fields.Date.today()
        for record in self:
          if record.life_date:
            a = dateutil.parser.parse(str(record.life_date)).date()
            print(a)
            if a <= current_day:
                raise Warning("End of Life Date can't be less than or equal Today Date!")

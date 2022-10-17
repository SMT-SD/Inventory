from odoo import models, fields, api, tools, exceptions, _
from odoo.exceptions import ValidationError, UserError

class MainCyclingCountBulx(models.Model):
    _name = "main.cycling"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'location'

    location = fields.Many2one('stock.location', string='Location', store=True, copy=True, track_visibility='onchange',required=True)
    date = fields.Date(string='Date', default=fields.Date.today())
    search_serial = fields.Char(string='Scan Serial', store=True, copy=True)
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('done', "Done"),
    ], default='draft', track_visibility='onchange')
    cycling_lines_main = fields.One2many('cycling.count', 'invers_com', copy=True,store=True)

    @api.multi
    @api.onchange('search_serial')
    def compute_product_serial_scan_hh(self):
      for rec in self:
        list = []
        if rec.search_serial:
            check = self.env['stock.production.lot'].search(
                [('lot_location', '=', rec.location.id), ('name', '=', rec.search_serial)])
            # print(check)
            if check:
                for m in check:
                    if rec.cycling_lines_main:
                       for line in rec.cycling_lines_main:
                          # if line.serial == self.search_serial:
                          #    raise ValidationError('this serial you scanned before already exist!')
                          if  line.product_id == m.product_id and line.location==rec.location:
                            # line.counter +=1
                            line.serial = rec.search_serial

                    else:

                     list.append(
                        {
                            'product_id': m.product_id.id,
                            'location': m.lot_location.id,
                            'date': fields.Date.today(),
                            'search_serial': self.search_serial,
                            'counter': 1,
                        }
                    )
                    # print(list)
                    rec.cycling_lines_main = list
                        # for line in self.cycling_lines_main:
                        #     if line.serial_lot == self.search_serial:
                        #         raise ValidationError('this serial you scanned before already exist!')
                        #         break


                        # self.counter += 1

            else:
                # self.not_found += 1
                # if self.not_found >0:
                  raise ValidationError('Serial you entered does not exist!')
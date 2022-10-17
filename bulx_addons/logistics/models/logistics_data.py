from dateutil.relativedelta import relativedelta

from odoo.addons import decimal_precision as dp
from odoo import models, fields, api, tools, exceptions, _
from odoo.exceptions import ValidationError
from odoo.tools import datetime
import dateutil.parser



class LogisticStatusAppbulx(models.Model):
    _name = "logistic.status"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Many2one('res.partner',string='DA', copy=True, store=True, track_visibility='onchange')
    hub = fields.Many2one('hub.hub', string='Hub', copy=True, store=True, track_visibility='onchange')
    state = fields.Selection([
        ('handover_to_da', "Handover to DA"),
        ('in_delivery_progress', "In delivery progress"),
        ('in_delivery_progress_success', "In delivery progress success"),
        ('in_delivery_progress_failed', "In delivery progress failed"),
        ('delivered', "Delivered"),
        ('return_back_to_origin', "Return back to origin"),
        ('partial_delivery', "Partial delivery"),
    ], default='handover_to_da', track_visibility='onchange')
    failed_delivery_reasons = fields.Selection([
        ('cancel', "Cancelation"),
        ('rejection', "Rejection"),
        ('schedule', "Schedule Another Date"),
    ], default='cancel', track_visibility='onchange',string='Failed Delivery Reasons')

    rejection_reasons = fields.Selection([
        ('attitude', "Attitude issue from DA"),
        ('quality', "Quality products not meets the customer expectation"),
        ('wrong_item', "Wrong Item delivered and he reject the whole package"),
    ], default='quality', track_visibility='onchange',string='Rejection Reasons')
    amount_delivered = fields.Integer(string='Delivered Amount',default=1, copy=True, store=True, track_visibility='onchange')

    scheduling_date =fields.Date(string='Scheduling Date')
    scheduling_date2 = fields.Datetime(string='Scheduling Date')
    scheduling_date3 = fields.Date(string='Scheduling Date')

    @api.multi
    def action_view_payment(self):
        view_id = self.env.ref('account.view_account_payment_form').id
        # context = self._context.copy()
        asd = self.env['account.payment'].create({
            'partner_id': self.name.id,
            'amount': self.amount_delivered,
            # 'location_id': self.location.id,
            # 'location_dest_id': self.dest_location.id,

        })
        return {
            'name': 'Payment',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'account.payment',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': asd,
            # 'target': 'new',
            # 'context': context,

        }

    @api.constrains('amount_delivered','state')
    def cal_amount_delivered(self):
        if self.state=='delivered':
            if self.amount_delivered<1:
              raise ValidationError('Delivered Amount can not be 0 or negative')

    @api.constrains('scheduling_date')
    def cal_scheduling_date_period(self):
        if self.scheduling_date:
            self.scheduling_date2 = (datetime.strptime(str(fields.Date.today()), '%Y-%m-%d') + relativedelta(days=+ 5))
            x = self.scheduling_date2
            d =dateutil.parser.parse(str(x)).date()
            self.scheduling_date3 = d
            if self.scheduling_date >self.scheduling_date3 :
                raise ValidationError('you can not schedule date after 5 days from today')
            elif self.scheduling_date < fields.Date.today():
                raise ValidationError('date can not be before today')




    line_moves =fields.One2many('moves.lines_logistic','logistic_lines_inv')

    @api.multi
    def action_start(self):
        self.state='in_delivery_progress'

    @api.multi
    def action_success(self):
        self.state = 'in_delivery_progress_success'

    @api.multi
    def action_fail(self):
        self.state = 'in_delivery_progress_failed'

    @api.multi
    def action_partially(self):
        self.state = 'partial_delivery'


    @api.multi
    def action_confirm(self):
        self.state = 'delivered'

class MovesLinesLogisticBulxBridge(models.Model):
    _name = "moves.lines_logistic"

    product_id = fields.Many2one('product.product', string='Product')
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure')
    qty_done = fields.Float('Done', default=0.0, digits=dp.get_precision('Product Unit of Measure'), copy=False)
    product_uom_qty = fields.Float(
        'Reserved', default=0.0, digits=dp.get_precision('Product Unit of Measure'),
        copy=False, required=True)


    logistic_lines_inv = fields.Many2one('logistic.status')

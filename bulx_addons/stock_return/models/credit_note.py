from odoo import models, fields, api, tools, exceptions, _


class SaleOrderWizInherit(models.TransientModel):
    _name = "wiz.data"

    partner_id = fields.Many2one('res.partner',readonly=True)
    origin = fields.Char('Source Document', readonly=True)
    date = fields.Date('Date', default=fields.Date.today())
    reason = fields.Char('Reason')
    picking_id = fields.Many2one('stock.picking', readonly=True)
    account_id = fields.Many2one('account.account',readonly=True)
    is_po = fields.Boolean()
    is_so = fields.Boolean()

    @api.multi
    def action_create_credit_note(self):
        for line in self:
            if line.is_po ==True:
                inv = self.env['account.invoice'].create({
                    'partner_id': line.partner_id.id,
                    'origin': line.origin,
                    'date_invoice': line.date,
                    'type': 'in_refund',
                })
                for l in inv:
                    for rec in line.picking_id.move_ids_without_package:
                        l.write({
                            'invoice_line_ids': [(0, 0, {
                                'product_id': rec.product_id.id,
                                'quantity': rec.quantity_done,
                                'name': str(rec.product_id.name),
                                'price_unit': rec.price_unit,
                                'account_id': rec.product_id.categ_id.property_stock_account_input_categ_id.id,

                            })]
                        })
            if line.is_so == True:
                inv_so = self.env['account.invoice'].create({
                    'partner_id': line.partner_id.id,
                    'origin': line.origin,
                    'date_invoice': line.date,
                    'type': 'out_refund',
                })
                for l in inv_so:
                    for rec in line.picking_id.move_ids_without_package:
                        l.write({
                            'invoice_line_ids': [(0, 0, {
                                'product_id': rec.product_id.id,
                                'quantity': rec.quantity_done,
                                'name': str(rec.product_id.name),
                                'price_unit': rec.price_unit,
                                'account_id': rec.product_id.categ_id.property_stock_account_output_categ_id.id,

                            })]
                        })

    # @api.onchange('customer')
    # def _domain_operation(self):
    #     list = []
    #     asd = self.env['res.partner'].search([('parent_company', '=', self.partner_id.id)])
    #     if asd:
    #         for rec in asd:
    #             list.append(rec.name)
    #         print(list)
    #
    #     return {'domain': {'customer': [('name', 'in', list)]}}

    # @api.one
    # def your_function(self):
    #     self.partner_id=self._context['partner_id']

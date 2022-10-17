from odoo import models, fields, api, tools, exceptions, _
from odoo.exceptions import UserError


class PickingCustomerInfoInherit(models.Model):
    _inherit = "stock.picking"

    address_type = fields.Selection([
        ('Home', 'Home'),
        ("Business", "Business"), ])

    building_type = fields.Selection([
        ('Apartment', 'Apartment'),
        ('Villa_House', 'Villa_House')])

    payment_method = fields.Selection([('Cash', 'Cash'), ('POS', 'POS')], default="Cash",compute='compute_address_fields',store=True,copy=True)
    street = fields.Char(compute='compute_address_fields')
    land_mark = fields.Char(compute='compute_address_fields')
    latitude = fields.Float(compute='compute_address_fields')
    Longitude = fields.Float(compute='compute_address_fields')
    building_number = fields.Char(compute='compute_address_fields')
    villa_number = fields.Char(compute='compute_address_fields')
    floor_number = fields.Integer(compute='compute_address_fields')
    apartment_number = fields.Integer(compute='compute_address_fields')
    shipping_fees = fields.Float(compute='compute_address_fields')

    amount_untaxed = fields.Float(compute='compute_address_fields')
    amount_taxed = fields.Float(compute='compute_address_fields')
    total_amount = fields.Float(compute='compute_address_fields')
    # shipment_fees = fields.Float(compute='compute_address_fields')

    bulx_order_Id = fields.Char(compute='compute_address_fields')
    region_id = fields.Many2one('bulx.region', compute='compute_address_fields')

    order_status_in = fields.Selection([
        ('new', 'new'),
        ('prepare', "Preparing"),
        ('ship', "On the way"),
        ('deliver', "Delivered"),
        ('cancel', "Cancelled"),
    ], default='new', track_visibility='onchange', string='Order Status', compute='compute_address_fields')

    order_state = fields.Selection([
        ('new', 'new'),
        ('prepare', "Preparing"),
        ('ship', "On the way"),
        ('deliver', "Delivered"),
        ('cancel', "Cancelled"),
    ], default='new', track_visibility='onchange', string='Order Status', compute='compute_address_fields')

    @api.multi
    @api.depends('origin')
    def compute_address_fields(self):
        for rec in self:
            so = self.env['sale.order'].search(
                [('name', '=', rec.origin)])
            if so:
                print(so.name)
                rec.payment_method = so.payment_method
                rec.address_type = so.address_type
                rec.building_type = so.building_type
                rec.street = so.street
                rec.land_mark = so.land_mark
                rec.latitude = so.latitude
                rec.Longitude = so.Longitude
                rec.building_number = so.building_number
                rec.villa_number = so.villa_number
                rec.floor_number = so.floor_number
                rec.apartment_number = so.apartment_number

                rec.shipping_fees = so.shipping_fees
                rec.bulx_order_Id = so.bulx_order_Id
                rec.order_status_in = so.order_status_in
                rec.region_id = so.region_id
                rec.order_state = so.order_state
                rec.amount_untaxed = so.amount_total - so.shipping_fees
                # rec.amount_untaxed = so.amount_untaxed
                rec.amount_taxed = so.amount_tax
                rec.total_amount = so.amount_total
                # rec.total_amount = rec.amount_untaxed - rec.shipping_fees
                for line in so.order_line:
                    for sec in rec.move_ids_without_package:
                        if line.product_id.id == sec.product_id.id:
                            sec.price_unit_move = line.price_unit
                            sec.price_subtotal_move = line.price_subtotal
        return self.env.ref('stock.action_report_delivery').report_action(self)


class PickingStockMoveInfoInherit(models.Model):
    _inherit = "stock.move"

    price_unit_move = fields.Float(store=True)
    price_subtotal_move = fields.Float(store=True)
    origin_inv = fields.Char(related='picking_id.origin')

    @api.multi
    @api.depends('origin_inv')
    def compute_prices_from_so(self):
        for rec in self:
            so = self.env['sale.order'].search(
                [('name', '=', rec.origin_inv)])
            if so:
                for line in so.order_line:
                    print(so.name)
                    rec.price_unit_move = line.price_unit
                    rec.price_subtotal_move = line.price_subtotal


class StockQuantPackageInfoInherit(models.Model):
    _inherit = "stock.quant.package"

    def return_so_package(self):
        # action = self.env.ref('stock.action_picking_tree_all').read()[0]
        domain = ['|', ('result_package_id', 'in', self.ids), ('package_id', 'in', self.ids)]
        pickings = self.env['stock.move.line'].search(domain, limit=1).mapped('picking_id')
        if pickings:
            self.origin_so = pickings.origin
            self.address_type = pickings.address_type
            self.building_type = pickings.building_type
            self.street = pickings.street
            self.land_mark = pickings.land_mark
            self.latitude = pickings.latitude
            self.Longitude = pickings.Longitude
            self.building_number = pickings.building_number
            self.villa_number = pickings.villa_number
            self.floor_number = pickings.floor_number
            self.apartment_number = pickings.apartment_number
            self.partner_id = pickings.partner_id.id
            self.region_id = pickings.region_id.id
            self.payment_method =pickings.payment_method
            # self.amount_untaxed = pickings.amount_untaxed
            # self.amount_taxed = pickings.amount_taxed
            self.total_amount = pickings.total_amount
            self.shipping_fees = pickings.shipping_fees
            for line in pickings.move_line_ids:
                for sec in self.quant_ids:
                    if line.product_id.id == sec.product_id.id:
                        sec.price_unit_quant = line.move_id.price_unit_move
                        # sec.price_subtotal_quant = line.move_id.price_subtotal_move
        for line in self.quant_ids:
            line.price_subtotal_quant = line.price_unit_quant * line.quantity
            self.amount_untaxed += line.price_subtotal_quant
            self.total_amount = self.amount_untaxed + self.shipping_fees

    origin_so = fields.Char(compute='return_so_package', string='Source Document Number')
    partner_id = fields.Many2one('res.partner', compute='return_so_package')
    region_id = fields.Many2one('bulx.region', compute='return_so_package')
    payment_method = fields.Selection([('Cash', 'Cash'), ('POS', 'POS')], default="Cash",compute='return_so_package')
    shipping_fees = fields.Float(compute='return_so_package')
    address_type = fields.Selection([
        ('Home', 'Home'),
        ("Business", "Business"), ], compute='return_so_package')

    building_type = fields.Selection([
        ('Apartment', 'Apartment'),
        ('Villa_House', 'Villa_House')], compute='return_so_package')

    street = fields.Char(compute='return_so_package')
    land_mark = fields.Char(compute='return_so_package')
    latitude = fields.Float(compute='return_so_package')
    Longitude = fields.Float(compute='return_so_package')
    building_number = fields.Char(compute='return_so_package')
    villa_number = fields.Char(compute='return_so_package')
    floor_number = fields.Integer(compute='return_so_package')
    apartment_number = fields.Integer(compute='return_so_package')
    amount_untaxed = fields.Float(compute='cal_tot_amounts')
    # amount_taxed = fields.Float(compute='return_so_package')
    total_amount = fields.Float(compute='cal_tot_amounts')

    @api.depends
    def cal_tot_amounts(self):
        for line in self.quant_ids:
            self.amount_untaxed += line.price_subtotal_quant
            self.total_amount = self.amount_untaxed + self.shipping_fees


class StockQuantBulxInfoInherit(models.Model):
    _inherit = "stock.quant"

    price_unit_quant = fields.Float(store=True, copy=True)
    price_subtotal_quant = fields.Float(store=True, compute='cal_subtotal_amounts')

    @api.depends
    def cal_subtotal_amounts(self):
        for line in self:
            line.price_subtotal_quant = line.price_unit_quant * line.quantity


class StockMoveLinesPackageInfoInherit(models.Model):
    _inherit = 'stock.move.line'

    origin_source_doc = fields.Char(related='picking_id.origin', store=True)

# class ReportInvoiceuio(models.AbstractModel):
#     _name = 'report.sales_policy.car_reception_detection_temp'
#     @api.multi
#     def render_html(self, docids, data=None):
#         # docids = XYZ.invoice_ids.ids
#         docargs = {
#             'doc_ids': docids,
#             'doc_model': 'car.fix',
#             'docs': self.env['car.fix'].browse(docids),
#             'data': data,
#         }
#         return self.env['report'].render('sales_policy.car_reception_detection_temp', docargs).report_action(self)
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         # if not data.get('form'):
#         #     raise UserError(_("Form content is missing, this report cannot be printed."))
#
#         holidays_report = self.env['ir.actions.report']._get_report_from_name('sales_policy.car_reception_detection_temp')
#         holidays = self.env['car.fix'].browse(self.ids)
#         return {
#             'doc_ids': self.ids,
#             'doc_model': holidays_report.model,
#             'docs': holidays,
#             # 'get_header_info': self._get_header_info(data['form']['date_from'], data['form']['holiday_type']),
#             # 'get_day': self._get_day(data['form']['date_from']),
#             # 'get_months': self._get_months(data['form']['date_from']),
#             # 'get_data_from_report': self._get_data_from_report(data['form']),
#             # 'get_holidays_status': self._get_holidays_status(),
#         }

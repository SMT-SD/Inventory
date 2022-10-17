from odoo import models, fields, api, tools, exceptions, _


class AccountInvoiceInfoInherit(models.Model):
    _inherit = "account.invoice"

    stock_ref = fields.Many2one('stock.picking', string='Stock Move Reference', compute='compute_stock_ref')

    address_type = fields.Selection([
        ('Home', 'Home'),
        ("Business", "Business"), ])

    building_type = fields.Selection([
        ('Apartment', 'Apartment'),
        ('Villa_House', 'Villa_House')])

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
        print('hi')
        for rec in self:
            so = self.env['sale.order'].search(
                [('name', '=', rec.origin)])
            if so:
                print(so.name)
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
                rec.amount_untaxed = so.amount_untaxed
                rec.amount_taxed = so.amount_tax
                rec.total_amount = so.amount_total
                # for line in so.order_line:
                #     for sec in rec.move_ids_without_package:
                #         if line.product_id.id == sec.product_id.id:
                #             sec.price_unit_move = line.price_unit
                #             sec.price_subtotal_move = line.price_subtotal
        # return self.env.ref('stock.action_report_delivery').report_action(self)

    @api.multi
    @api.onchange('state')
    def compute_stock_ref(self):
        for rec in self:
            if rec.type == 'in_invoice':
                po = self.env['stock.picking'].search(
                    [('origin', '=', rec.origin)])
                if po:
                    for line in po:
                        if line.picking_type_id.code=='incoming':
                            rec.stock_ref = line.id
            elif rec.type == 'out_invoice':
                so = self.env['stock.picking'].search(
                    [('origin', '=', rec.origin)])
                if so:
                    for line in so:
                        if line.picking_type_id.code=='outgoing':
                            rec.stock_ref = line.id


from odoo import fields, models


class OrderAddress(models.Model):
    _name = 'bulx.address'

    address_type = fields.Selection([
        ('Home', 'Home'),
        ("Business", "Business"), ])

    building_type = fields.Selection([
        ('Apartment', 'Apartment'),
        ('Villa_House', 'Villa_House')])

    street = fields.Char()
    land_mark = fields.Char()
    latitude = fields.Float()
    Longitude = fields.Float()
    building_number = fields.Char()
    villa_number = fields.Char()
    floor_number = fields.Integer()
    apartment_number = fields.Integer()
    # shipping_fees = fields.Float()
    customer_id = fields.Many2one('res.partner', domain="[('customer','=',True)]")
    bulx_id = fields.Char()
    region_id = fields.Many2one('bulx.region')

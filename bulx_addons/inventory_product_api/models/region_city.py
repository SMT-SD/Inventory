from odoo import fields, models


class BulxCity(models.Model):
    _name = 'bulx.city'
    _rec_name = 'bulx_id'

    name = fields.Char(required=True)
    arabic_name = fields.Char(required=True)
    bulx_id = fields.Char()


class BulxRegion(models.Model):
    _name = 'bulx.region'

    name = fields.Char(required=True)
    arabic_name = fields.Char(required=True)
    is_active = fields.Boolean()
    city_id = fields.Many2one('bulx.city')
    bulx_id = fields.Char()

from odoo import models, fields, api, exceptions, _

class ResPartnerLogisticsModify(models.Model):
    _inherit = 'res.partner'

    is_da=fields.Boolean(string=' Is DA?')

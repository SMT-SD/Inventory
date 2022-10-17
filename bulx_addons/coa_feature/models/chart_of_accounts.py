from odoo import models, fields, api,tools, exceptions, _

class ChartOfAccountsInherit(models.Model):
    _inherit="account.account"

    arabic_name = fields.Char(string='Arabic Name')

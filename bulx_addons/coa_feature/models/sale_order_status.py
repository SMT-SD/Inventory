# from odoo import models, fields, api,tools, exceptions, _
# <<<<<<< HEAD
# import requests
# import logging
# # from ..bulx_tools import check_type
#
# _logger = logging.getLogger(__name__)
#
# class SaleOrder(models.Model):
# =======
#
# class ChartOfAccountsInherit(models.Model):
# >>>>>>> a092dedef1a1fff2b832d3b636e3621bfd349075
#     _inherit="sale.order"
#
#     order_status_in = fields.Selection([
#         ('preparing', "Preparing"),
#         ('on_the_way', "On the way"),
#         ('delivered', "Delivered"),
#         ('cancelled', "Cancelled"),
#     ], default='preparing', track_visibility='onchange',string='Order Status')
# <<<<<<< HEAD
#     bulx_di = fields.Char()
# =======
# >>>>>>> a092dedef1a1fff2b832d3b636e3621bfd349075

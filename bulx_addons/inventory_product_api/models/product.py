# from addons.website import tools
from odoo import models, fields, api


class ProductProductWafaInheritClass(models.Model):
    _inherit = "product.product"

    retail_price = fields.Float()


class ProducttemplateWafaInheritClass(models.Model):
    _inherit = "product.template"

    tracking = fields.Selection([
        ('serial', 'By Unique Serial Number'),
        ('lot', 'By Lots'),
        ('none', 'No Tracking')], string="Tracking",
        help="Ensure the traceability of a storable product in your warehouse.", default='serial', required=True)

    retail_price = fields.Float()
    bulx_id = fields.Char()
    image_medium_two = fields.Binary(
        "Medium-sized image2", attachment=True, copy=True, store=True,
        help="Medium-sized image of the product. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved, "
             "only when the image exceeds one of those sizes. Use this field in form views or some kanban views.")



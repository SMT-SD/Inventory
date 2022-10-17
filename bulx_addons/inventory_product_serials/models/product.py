# from addons.website import tools
import datetime
import json
import logging
import requests
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError, UserError
# from odoo.tools.pycompat import izip
from odoo.tools import float_compare, float_round, float_is_zero
from ..bulx_tools import check_type
from odoo.tools import dateutil

_logger = logging.getLogger(__name__)


class ProductProductWafaInheritClass(models.Model):
    _inherit = "product.product"

    brand = fields.Char(string='Brand', store=True, copy=True, track_visibility='onchange',
                        )
    category = fields.Char(string='category', store=True, copy=True, track_visibility='onchange',
                           related='categ_id.category_code')

    def _compute_product_quantities(self):
        res = self._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'),
                                            self._context.get('package_id'), self._context.get('from_date'),
                                            self._context.get('to_date'))
        qty_available = 0
        outgoing_qty = 0
        qty_real = 0
        real_real = 0
        for product in self:
            qty_available = res[product.id]['qty_available']
            outgoing_qty = res[product.id]['outgoing_qty']
            real_real = res[product.id]['virtual_available'] - res[product.id]['incoming_qty']
            qty_real = qty_available - outgoing_qty
            logging.warn(qty_real)
        return qty_available
    # image_medium_two = fields.Binary(
    #     "Medium-sized image", compute='_compute_images', inverse='_set_image_medium',
    #     help="Image of the product variant (Medium-sized image of product template if false).")
    #
    # @api.one
    # @api.depends('image_variant', 'product_tmpl_id.image')
    # def _compute_images(self):
    #     if self._context.get('bin_size'):
    #         self.image_medium = self.image_variant
    #         self.image_small = self.image_variant
    #         self.image = self.image_variant
    #         self.image_medium_two = self.image_variant
    #     else:
    #         resized_images = tools.image_get_resized_images(self.image_variant, return_big=True,
    #                                                         avoid_resize_medium=True)
    #         self.image_medium = resized_images['image_medium']
    #         self.image_medium_two = resized_images['image_medium']
    #         self.image_small = resized_images['image_small']
    #         self.image = resized_images['image']
    #     if not self.image_medium:
    #         self.image_medium = self.product_tmpl_id.image_medium
    #     if not self.image_medium_two:
    #         self.image_medium_two = self.product_tmpl_id.image_medium
    #     if not self.image_small:
    #         self.image_small = self.product_tmpl_id.image_small
    #     if not self.image:
    #         self.image = self.product_tmpl_id.image

class ProducttemplateWafaInheritClass(models.Model):
    _inherit = "product.template"

    brand = fields.Char(string='Brand', store=True, copy=True, track_visibility='onchange',
                        )
    category = fields.Char(string='category', store=True, copy=True, track_visibility='onchange',
                           related='categ_id.category_code')
    # image_medium_two = fields.Binary(
    #     "image2", attachment=True, copy=True, store=True,
    #     help="Medium-sized image of the product. It is automatically "
    #          "resized as a 128x128px image, with aspect ratio preserved, "
    #          "only when the image exceeds one of those sizes. Use this field in form views or some kanban views.")


# class PartnerXlsx(models.AbstractModel):
#     _name = 'report.inventory_product_serials.lots_serial_number'
#     _inherit = 'report.report_xlsx.abstract'
#
#     def generate_xlsx_report(self, workbook, data, partners):
#         sheet = workbook.add_worksheet("Lot/Serial Number")
#         format = workbook.add_format({'bold': False, 'align': 'center'})
#         sheet.write(0, 2, "Lot/Serial Number")
#         sheet.write(0, 3, "Barcode")
#         sheet.write(0, 4, "Product Brand")
#         sheet.write(0, 5, "Product Category")
#         sheet.write(0, 6, "Purchase Order")
#         line_number = 1
#         length = len(partners.move_line_ids)
#         print(length)
#
#         for line in partners.move_line_ids:
#             if length > 0:
#                 sheet.write(line_number, 2, line.lot_name , format)
#                 sheet.write(line_number, 3, str(line.product_id.barcode), format)
#                 sheet.write(line_number, 4, str(line.product_id.categ_id.name), format)
#                 sheet.write(line_number, 5, str(line.product_id.product_brand_id.name), format)
#                 sheet.write(line_number, 6, partners.origin, format)
#             # sheet.write(line_number, 6, line.sur_name, format)
#             # sheet.write(line_number, 7, str(line.date_str), format)
#             # sheet.write(line_number, 8, line.activity_classification, format)
#             # sheet.write(line_number, 9, line.location, format)
#             # sheet.write(line_number, 10, line.card, format)
#             # sheet.write(line_number, 11, str(line.tier_points), format)
#             # sheet.write(line_number, 12, str(line.miles_no), format)
#             line_number += 1
#             length -= 1
#         # sheet.write(line_number, 0, line.footer_collection, format)
class PartnerCSV(models.AbstractModel):
    _name = 'report.inventory_product_serials.lots_serial_number'
    _inherit = 'report.report_csv.abstract'

    def generate_csv_report(self, writer, data, partners):
        writer.writeheader()
        for obj in partners.move_line_ids:
            writer.writerow({
                'Lot_Serial_Number': obj.lot_name,
                'Barcode': obj.product_id.barcode,
                'Product_Brand': obj.product_id.categ_id.name,
                'Product_Category': obj.product_id.product_brand_id.name,
                'PO': partners.origin,
                'Description': obj.product_id.name,
            })

    def csv_report_options(self):
        res = super().csv_report_options()
        res['fieldnames'].append('Lot_Serial_Number')
        res['fieldnames'].append('Barcode')
        res['fieldnames'].append('Product_Brand')
        res['fieldnames'].append('Product_Category')
        res['fieldnames'].append('PO')
        res['fieldnames'].append('Description')
        res['delimiter'] = ';'
        # res['quoting'] = csv.QUOTE_ALL
        return res


class DetailedOperationInheritClass(models.Model):
    _inherit = "stock.move"

    location_select = fields.Many2one('stock.location', string='Destination Location', index=True, required=False)
    location_scan = fields.Char(string='Scan Location')
    dest_location_scan = fields.Char(string='Scan Destination Location')
    location_source = fields.Many2one('stock.location', string='Source Location', index=True, required=False)
    name = fields.Char('Description', index=True, required=False)
    quantity_to_generate = fields.Integer(string='Quantity To generate', store=True, copy=True,
                                          track_visibility='onchange')
    image_medium = fields.Binary("Product Sale image", attachment=True, related='product_id.image')
    image_medium_two = fields.Binary("Product Purchase image", attachment=True, related='product_id.image_medium_two')
    production_date = fields.Datetime(string='Production Date')
    code = fields.Selection([('incoming', 'Vendors'), ('outgoing', 'Customers'), ('internal', 'Internal')],
                            'Type of Operation', related='picking_id.code')
    is_pick = fields.Boolean('Is a Pick?', related='picking_id.picking_type_id.is_pick', store=True)
    is_internal = fields.Boolean('Is Internal?', related='picking_id.picking_type_id.is_internal', store=True)
    search_serial = fields.Char(string='Scan Serial', store=True, copy=True, track_visibility='onchange')
    is_generated = fields.Boolean('Is Generated')

    # state = fields.Selection([
    #     ('draft', 'New'), ('cancel', 'Cancelled'),
    #     ('waiting', 'Waiting Another Move'),
    #     ('confirmed', 'Waiting Availability'),
    #     ('partially_available', 'Partially Available'),
    #     ('assigned', 'Available'),
    #     ('done', 'Done'),
    #     ('generated', 'Generated')], string='Status',
    #     copy=False, default='draft', index=True, readonly=True,
    #     help="* New: When the stock move is created and not yet confirmed.\n"
    #          "* Waiting Another Move: This state can be seen when a move is waiting for another one, for example in a chained flow.\n"
    #          "* Waiting Availability: This state is reached when the procurement resolution is not straight forward. It may need the scheduler to run, a component to be manufactured...\n"
    #          "* Available: When products are reserved, it is set to \'Available\'.\n"
    #          "* Done: When the shipment is processed, the state is \'Done\'.")

    # @api.multi
    # @api.constrains('move_line_ids')
    # def check_location_dest_id(self):
    #     if self.picking_type_id.code == 'internal':
    #         for line in self.move_line_ids:
    #             if line.location_dest_id.is_main_stock == True:
    #                 raise ValidationError('you cant transfer to main stock')

    # @api.multi
    # @api.constrains('move_line_ids')
    # def check_reserved(self):
    #     if self.code == 'internal' and self.is_pick==True:
    #         for line in self.move_line_ids:
    #             if line.product_uom_qty <1:
    #                 raise ValidationError('you cant not add more lines than initial demand or save when reserved is less than 1!!')
    #     if self.code == 'outgoing':
    #         for line in self.move_line_ids:
    #             if line.product_uom_qty <1:
    #                 raise ValidationError('you cant not add more lines than initial demand or save when reserved is less than 1!!')

    @api.multi
    @api.onchange('location_scan','dest_location_scan')
    def compute_locations_from_scan(self):
        if self.code == 'internal' and self.is_pick == False and self.is_internal==False and self.location_scan:
            check = self.env['stock.location'].search(
                [('barcode', '=', self.location_scan)])
            if check:
                for line in check:
                    if line.is_main_stock == True:
                        raise ValidationError('you cant transfer to main stock')
                    else:

                        self.location_select = line.id
                        # self.search_serial = ''
            else:
                raise ValidationError('this barcode does not exist in any location')
            # else:
            #     mm = self.location_scan.split('/')
            #     if len(mm) == 2:
            #         check = self.env['stock.location'].search(
            #             [('name', '=', mm[1]), ('parent_name', '=', mm[0])])
            #         if check:
            #             self.location_select = check.id
            self.location_scan = ''
        if self.code == 'internal' and self.is_pick == False and self.is_internal==True :
            if self.location_scan:
                    check = self.env['stock.location'].search(
                        [('barcode', '=', self.location_scan)])
                    if check:
                        for line in check:
                            if line.is_main_stock == True:
                                raise ValidationError('you cant transfer form main stock')
                            else:
                                self.location_source = line.id
                                # self.search_serial = ''
                    else:
                        raise ValidationError('this barcode does not exist in any location')
                    self.location_scan = ''
            if self.dest_location_scan:
                pick = self.env['stock.location'].search(
                    [('barcode', '=', self.dest_location_scan)])
                if pick:
                    for line in pick:
                        if line.is_main_stock == True:
                            raise ValidationError('you cant transfer to main stock')
                        else:

                            self.location_select = line.id
                else:
                    raise ValidationError('this barcode does not exist in any location')
                self.dest_location_scan = ''

            # else:
            #     mm = self.location_scan.split('/')
            #     if len(mm) == 2:
            #         check = self.env['stock.location'].search(
            #             [('name', '=', mm[1]), ('parent_name', '=', mm[0])])
            #         if check:
            #             self.location_select = check.id
        elif self.code == 'internal' and self.is_pick == True and self.location_scan:
            check = self.env['stock.location'].search(
                [('barcode', '=', self.location_scan)])
            if check:
                for line in check:
                    if line.is_main_stock == True:
                        raise ValidationError('you cant transfer from main stock')
                    else:

                        self.location_source = line.id
                        # self.search_serial = ''
            else:
                raise ValidationError('this barcode does not exist in any location')
            self.location_scan = ''

    @api.multi
    @api.onchange('search_serial')
    def compute_lines_from_serial_scan(self):
        # for rec in self:
        l = []
        if self.code == 'outgoing' and self.search_serial:
            check = self.env['stock.production.lot'].search(
                [('product_id', '=', self.product_id.id), ('name', '=', self.search_serial)])
            if check:
                # for m in check:
                mm = check.name.split('/')
                ww = mm[2]
                bb = int(ww)
                # l.append(check.name)
                # list2 = set(l)
                # asd = []
                # print(list2)
                l = (
                    {
                        'product_id': self.product_id.id,
                        'generated_serial': bb,
                        # 'lot_id': str(str(self.product_id.brand)+str(self.product_id.category)+str(ww)),
                        'brand': self.product_id.brand,
                        'category': self.product_id.category,
                        'product_uom_id': self.product_uom.id,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'qty_done': 1,
                    }
                )
                list = []
                for rec in self.move_line_ids:
                    list.append(rec.lot_id.name)
                    if (rec.lot_id.name == self.search_serial and rec.qty_done < 1.0):
                        rec.update(l)
                        # self.search_serial = ''
                    elif (rec.lot_id.name == self.search_serial and rec.qty_done > 0.0):
                        raise ValidationError('Serial you entered already scanned!')

                if self.search_serial not in list:
                    raise ValidationError('Serial you entered does not exist in moves lines!')
                self.search_serial = ''

                # if self.search_serial not in list:
                #     raise ValidationError('Serial you entered does not exist!')

            else:
                raise ValidationError('Serial you entered does not exist!')
        elif self.code == 'internal' and self.search_serial:
            if not self.location_select and self.is_pick == False:
                raise ValidationError('Please Select Destination Location at first')
            if (not self.location_select or not self.location_source) and self.is_pick == False and self.is_internal==True:
                raise ValidationError('Please Select Source/Destination Location at first')
            if not self.location_source and self.is_pick == True:
                raise ValidationError('Please Select Source Location at first')

            else:
                check = self.env['stock.production.lot'].search(
                    [('product_id', '=', self.product_id.id), ('name', '=', self.search_serial)])
                if check:
                    # for m in check:
                    mm = check.name.split('/')
                    ww = mm[2]
                    bb = int(ww)
                    if self.is_pick == False and self.is_internal == True:
                        if self.location_select and self.location_source:
                            product_location = self.env['stock.quant'].search(
                                [('product_id', '=', self.product_id.id), ('lot_id', '=', check.id),
                                 ('location_id', '=', self.location_source.id), ('quantity', '=', 1),
                                 ])
                            # print('product_location',product_location)
                            product_loc_id = self.env['stock.quant'].search(
                                [('product_id', '=', self.product_id.id), ('lot_id', '=', check.id),
                                 ('quantity', '=', 1), ])
                            if not product_location:
                                raise ValidationError(
                                    'serial {} for product {} not found in location {} it is in location : {}'.format(
                                        check.name, self.product_id.name, self.location_source.name,
                                        product_loc_id.location_id.name))
                            list1 = {
                                # 'product_id': self.product_id.id,
                                'generated_serial': bb,
                                'lot_id': check.id,
                                'brand': self.product_id.brand,
                                'category': self.product_id.category,
                                'product_uom_id': self.product_uom.id,
                                'location_id': self.location_source.id,
                                'location_dest_id': self.location_select.id,
                                'qty_done': 1,
                            }
                            list = []
                            for rec in self.move_line_ids:
                                list.append(rec.lot_id.name)
                                if ((
                                        rec.lot_id.name == self.search_serial) and rec.qty_done > 0 and rec.location_dest_id == self.location_select):
                                    raise ValidationError('this serial scanned before')
                                elif (rec.lot_id.name == self.search_serial):
                                    rec.update(list1)
                            # self.search_serial = ''
                            if self.search_serial not in list:
                                for rec in self.move_line_ids:
                                    if (rec.lot_id.name != self.search_serial) and rec.qty_done == 0:
                                        rec.update(list1)
                                        # self.search_serial = ''
                                        break

                            self.search_serial = ''
                        else:
                            list4 = {
                                # 'product_id': self.product_id.id,
                                'generated_serial': bb,
                                # 'lot_id':check.id,
                                'brand': self.product_id.brand,
                                'category': self.product_id.category,
                                'product_uom_id': self.product_uom.id,
                                # 'location_id': self.location_id.id,
                                # 'location_dest_id': self.location_select.id,
                                'qty_done': 1,
                            }
                            list = []
                            for rec in self.move_line_ids:
                                list.append(rec.lot_id.name)
                                if ((rec.lot_id.name == self.search_serial) and rec.qty_done > 0):
                                    raise ValidationError('this serial scanned before')
                                elif (rec.lot_id.name == self.search_serial):
                                    rec.update(list4)

                            if self.search_serial not in list:
                                raise ValidationError('Serial you entered does not exist in move lines!')
                            self.search_serial = ''

                    elif self.is_pick == False and self.is_internal == False:
                        if self.location_select:
                            list1 = {
                                # 'product_id': self.product_id.id,
                                'generated_serial': bb,
                                # 'lot_id':check.id,
                                'brand': self.product_id.brand,
                                'category': self.product_id.category,
                                'product_uom_id': self.product_uom.id,
                                # 'location_id': self.location_id.id,
                                'location_dest_id': self.location_select.id,
                                'qty_done': 1,
                            }
                            list = []
                            for rec in self.move_line_ids:
                                list.append(rec.lot_id.name)
                                if ((
                                        rec.lot_id.name == self.search_serial) and rec.qty_done > 0 and rec.location_dest_id == self.location_select):
                                    raise ValidationError('this serial scanned before')
                                elif (rec.lot_id.name == self.search_serial):
                                    rec.update(list1)
                            # self.search_serial = ''
                            if self.search_serial not in list:
                                raise ValidationError('Serial you entered does not exist in moves lines!')
                            self.search_serial = ''
                        else:
                            list4 = {
                                # 'product_id': self.product_id.id,
                                'generated_serial': bb,
                                # 'lot_id':check.id,
                                'brand': self.product_id.brand,
                                'category': self.product_id.category,
                                'product_uom_id': self.product_uom.id,
                                # 'location_id': self.location_id.id,
                                # 'location_dest_id': self.location_select.id,
                                'qty_done': 1,
                            }
                            list = []
                            for rec in self.move_line_ids:
                                list.append(rec.lot_id.name)
                                if ((rec.lot_id.name == self.search_serial) and rec.qty_done > 0):
                                    raise ValidationError('this serial scanned before')
                                elif (rec.lot_id.name == self.search_serial):
                                    rec.update(list4)

                            if self.search_serial not in list:
                                raise ValidationError('Serial you entered does not exist in move lines!')
                            self.search_serial = ''

                    elif self.is_pick == True:
                        if self.location_source:
                            product_location = self.env['stock.quant'].search(
                                [('product_id', '=', self.product_id.id), ('lot_id', '=', check.id),
                                 ('location_id', '=', self.location_source.id), ('quantity', '=', 1),
                                 ])
                            # print('product_location',product_location)
                            product_loc_id = self.env['stock.quant'].search(
                                [('product_id', '=', self.product_id.id), ('lot_id', '=', check.id),
                                 ('quantity', '=', 1), ])
                            if not product_location:
                                raise ValidationError(
                                    'serial {} for product {} not found in location {} it is in location : {}'.format(
                                        check.name, self.product_id.name, self.location_source.name,
                                        product_loc_id.location_id.name))
                            list2 = {
                                # 'product_id': self.product_id.id,
                                'generated_serial': bb,
                                'lot_id': check.id,
                                'brand': self.product_id.brand,
                                'category': self.product_id.category,
                                'product_uom_id': self.product_uom.id,
                                'location_id': self.location_source.id,
                                # 'location_dest_id': self.location_select.id,

                                'qty_done': 1,
                            }
                            list = []
                            for rec in self.move_line_ids:
                                list.append(rec.lot_id.name)
                                if (rec.lot_id.name == self.search_serial and rec.qty_done > 0.0):
                                    raise ValidationError('Serial you entered already scanned!')

                                elif (rec.lot_id.name == self.search_serial):
                                    rec.update(list2)

                            if self.search_serial not in list:
                                for rec in self.move_line_ids:
                                    if (rec.lot_id.name != self.search_serial) and rec.qty_done == 0:
                                        rec.update(list2)
                                        # self.search_serial = ''
                                        break
                            self.search_serial = ''
                        else:
                            product_location = self.env['stock.quant'].search(
                                [('product_id', '=', self.product_id.id), ('lot_id', '=', check.id),
                                 ('quantity', '=', 1), ])
                            # print('no location 1', product_location)
                            if not product_location:
                                raise ValidationError(
                                    'serial {} for product {} not available '.format(check.name,
                                                                                     self.product_id.name, ))
                            list3 = {
                                # 'product_id': self.product_id.id,
                                'generated_serial': bb,
                                'lot_id': check.id,
                                'brand': self.product_id.brand,
                                'category': self.product_id.category,
                                'product_uom_id': self.product_uom.id,
                                # 'location_id': self.location_id.id,
                                # 'location_dest_id': self.location_select.id,
                                'qty_done': 1,
                            }

                            list = []
                            for rec in self.move_line_ids:
                                list.append(rec.lot_id.name)
                                if (rec.lot_id.name == self.search_serial):
                                    product_location = self.env['stock.quant'].search(
                                        [('product_id', '=', self.product_id.id), ('lot_id', '=', check.id),
                                         ('location_id', '=', rec.location_id.id), ('quantity', '=', 1),
                                         ('reserved_quantity', '=', 0)])
                                    # print(' no location', product_location)
                                    if not product_location:
                                        raise ValidationError(
                                            'serial {} for product {} not found in location {}'.format(check.name,
                                                                                                       self.product_id.name,
                                                                                                       rec.location_id.name))
                                    rec.update(list3)
                                    self.search_serial = ''

                            if self.search_serial not in list:
                                for rec in self.move_line_ids:
                                    if (rec.lot_id.name != self.search_serial) and rec.qty_done == 0:
                                        product_location = self.env['stock.quant'].search(
                                            [('product_id', '=', self.product_id.id), ('lot_id', '=', check.id),
                                             ('location_id', '=', rec.location_id.id), ('quantity', '=', 1),
                                             ('reserved_quantity', '=', 0)])
                                        # print(' no location', product_location)
                                        if not product_location:
                                            raise ValidationError(
                                                'serial {} for product {} not found in location {}'.format(check.name,
                                                                                                           self.product_id.name,
                                                                                                           rec.location_id.name))
                                        rec.update(list3)
                                        self.search_serial = ''
                                        break
                            # if self.search_serial not in list:
                            #     raise ValidationError('Serial you entered does not exist in list 3!')


                else:
                    raise ValidationError('Serial you entered does not exist!')
        else:
            raise ValidationError('Serial you entered does not exist !')

        # elif self.code == 'internal' and self.search_serial:
        #     check = self.env['stock.production.lot'].search(
        #         [('product_id', '=', self.product_id.id), ('name', '=', self.search_serial)])
        #     if check:
        #         # for m in check:
        #         mm = check.name.split('/')
        #         ww = mm[2]
        #         bb = int(ww)
        #         # l.append(check.name)
        #         # list2 = set(l)
        #         # asd = []
        #         # print(list2)
        #         if self.location_select:
        #             l = {
        #                 # 'product_id': self.product_id.id,
        #                 'generated_serial': bb,
        #                 # 'lot_id': str(str(self.product_id.brand)+str(self.product_id.category)+str(ww)),
        #                 'brand': self.product_id.brand,
        #                 'category': self.product_id.category,
        #                 'product_uom_id': self.product_uom.id,
        #                 # 'location_id': self.location_id.id,
        #                 'location_dest_id': self.location_select.id,
        #                 'qty_done': 1,
        #             }
        #         else:
        #             l = {
        #                 # 'product_id': self.product_id.id,
        #                 'generated_serial': bb,
        #                 # 'lot_id': str(str(self.product_id.brand)+str(self.product_id.category)+str(ww)),
        #                 'brand': self.product_id.brand,
        #                 'category': self.product_id.category,
        #                 'product_uom_id': self.product_uom.id,
        #                 # 'location_id': self.location_id.id,
        #                 # 'location_dest_id': self.location_select.id,
        #                 'qty_done': 1,
        #             }
        #
        #     list = []
        #     for rec in self.move_line_ids:
        #         if (rec.lot_id.name == self.search_serial):
        #             # rec.id=l
        #             rec.update(l)
        #     print(list)
        #     self.search_serial=''
        #     # if self.search_serial not in list:
        #     #     raise ValidationError('Serial you entered does not exist!')
        #     # elif self.search_serial in list:
        #     #     raise ValidationError('Serial you entered already scanned!')

    # @api.multi
    # @api.depends('move_line_ids')
    # def button_print_serials(self):
    #     return self.env.ref('inventory_product_serials.lots_serial_numbers_report').report_action(self)

    @api.multi
    @api.depends('move_line_ids')
    def button_print_serials(self):
        return self.env.ref('inventory_product_serials.lots_serial_numbers_report').report_action(self)

    # @api.multi
    # @api.onchange('quantity_to_generate')
    # def _check_quantity_to_generate(self):
    #     for record in self:
    #         if record.quantity_to_generate > record.product_uom_qty:
    #             raise Warning("quantity to generate can't be greater than the Initial Demand!")

    def action_show_details(self):
        """ Returns an action that will open a form view (in a popup) allowing to work on all the
        move lines of a particular move. This form view is used when "show operations" is not
        checked on the picking type.
        """
        self.ensure_one()

        # If "show suggestions" is not checked on the picking type, we have to filter out the
        # reserved move lines. We do this by displaying `move_line_nosuggest_ids`. We use
        # different views to display one field or another so that the webclient doesn't have to
        # fetch both.
        if self.picking_id.picking_type_id.show_reserved:
            view = self.env.ref('stock.view_stock_move_operations')
        else:
            view = self.env.ref('stock.view_stock_move_nosuggest_operations')

        picking_type_id = self.picking_type_id or self.picking_id.picking_type_id
        return {
            'name': _('Detailed Operations'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.move',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            # 'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context,
                show_lots_m2o=self.has_tracking != 'none' and (
                        picking_type_id.use_existing_lots or self.state == 'done' or self.origin_returned_move_id.id),
                # able to create lots, whatever the value of ` use_create_lots`.
                show_lots_text=self.has_tracking != 'none' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
                show_source_location=self.location_id.child_ids and self.picking_type_id.code != 'incoming',
                show_destination_location=self.location_dest_id.child_ids and self.picking_type_id.code != 'outgoing',
                show_package=not self.location_id.usage == 'supplier',
                show_reserved_quantity=self.state != 'done'
            ),
        }

    @api.one
    @api.depends('move_line_ids')
    def generate_serial(self):
        for m in self:
            if m.production_date and m.product_id:
                current_day = fields.Date.today()
                b = dateutil.parser.parse(str(m.production_date)).date()
                # planned = (datetime.datetime.strptime(str(rec.production_date),'%Y-%m-%d') + datetime.timedelta(days=rec.product_id.life_time)).strftime('%Y-%m-%d')
                planned = m.production_date + datetime.timedelta(m.product_id.life_time)
                exp_date = planned
                if m.product_id.life_time < 1 or m.product_id.use_time < 1 or m.product_id.removal_time < 1 or m.product_id.alert_time < 1:
                    raise ValidationError("Product (life time/Use Time/Removal Time/Alert Time) can't be less than 1!")
                if b > current_day:
                    raise ValidationError("Production Date can't be after Today Date!")
                if exp_date:
                    a = dateutil.parser.parse(str(exp_date)).date()
                    if a <= current_day:
                        raise ValidationError("End of Life/Expiration Date can't be less than or equal Today Date!")

            if m.move_line_ids:
                list_app = []
                for l in m.move_line_ids:
                    if not l.lot_name:
                        list_app.append(l.lot_name)
                print(len(list_app))
                if m.quantity_to_generate > len(list_app):
                    raise ValidationError(
                        _("quantity to generate can't be greater than {} .".format(len(list_app))))
            if m.quantity_to_generate > len(m.move_line_ids) or m.quantity_to_generate < 1:
                # raise Warning("quantity to generate can't be greater than Moves lines!")
                raise ValidationError(
                    _("quantity to generate can't be greater than Moves lines! or less than 1."))
            elif m.quantity_to_generate > m.product_uom_qty:
                raise ValidationError("quantity to generate can't be greater than the Initial Demand!")
            else:
                # asd = m.env['stock.production.lot']
                counter = 0
                a = 1
                i = m.quantity_to_generate
                list = []
                check = m.env['stock.production.lot'].search(
                    [('name', '!=', False), ('product_id', '=', m.product_id.id)])
                move = m.env['stock.move.line'].search(
                    [('lot_name', '!=', False), ('product_id', '=', m.product_id.id), ('state', '=', 'assigned')])
                # .search([('product_id', '=', m.product_id.id)])
                if move and check:
                    for line in move:
                        mm = line.lot_name.split('/')
                        ww = mm[2]
                        gg = int(ww)
                        list.append(gg)
                    generated_serial1 = int(max(list))
                    for rec in check:
                        mm = rec.name.split('/')
                        if len(mm) != 3:
                            raise ValidationError(
                                'Please check the correct format of serial recorded with this product to be consists of this format barcode/barcode/generated serial for product {}'.format(
                                    rec.product_id.name))
                        else:
                            ww = mm[2]
                            barcode1 = mm[0]
                            barcode2 = mm[1]
                            if ww == '':
                                raise ValidationError(
                                    'Please check the correct format of the third part of the serial recorded with this product (generated serial) must be intger not empty')
                            else:
                                for l in str(ww):
                                    if l not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                                        raise ValidationError(
                                            'Please check the correct format of the third part of the serial recorded with this product (generated serial) must be intger')
                                    else:
                                        gg = int(ww)
                                        br = str(barcode1)
                                        cat = str(barcode2)
                                        if str(m.product_id.barcode) == br and str(m.product_id.barcode) == cat:
                                            list.append(gg)
                                            # print('hi')
                                        else:
                                            list.append(0)
                                            # print(list)
                    generated_serial2 = int(max(list))
                    if generated_serial1 > generated_serial2:
                        counter = generated_serial1 + 1
                    elif generated_serial2 > generated_serial1:
                        counter = generated_serial2 + 1
                    elif generated_serial2 == generated_serial1:
                        counter = generated_serial2 + 1
                    list_mix = []
                    print(counter)
                    for l in m.move_line_ids:
                        if not l.lot_name:
                            if 0 < i <= m.quantity_to_generate:
                                l.generated_serial = counter
                                # l.production_date = l.move_id.production_date
                                counter = counter + 1
                                i = i - 1
                    for l in m.move_line_ids:
                        if l.lot_name:
                            list_mix.append(l.lot_name)
                    print(len(list_mix))
                    if m.product_uom_qty == len(list_mix):
                        # m.state='generated'
                        m.is_generated = True
                elif move:
                    for line in move:
                        mm = line.lot_name.split('/')
                        ww = mm[2]
                        gg = int(ww)
                        list.append(gg)
                    cc = int(max(list))
                    counter = cc + 1
                    lis = []
                    for l in m.move_line_ids:
                        if not l.lot_name:
                            if 0 < i <= m.quantity_to_generate:
                                l.generated_serial = counter
                                # l.production_date = l.move_id.production_date
                                counter = counter + 1
                                i = i - 1
                    for l in m.move_line_ids:
                        if l.lot_name:
                            lis.append(l.lot_name)
                    print(len(lis))
                    if m.product_uom_qty == len(lis):
                        # m.state='generated'
                        m.is_generated = True
                elif check:
                    # print('hi')
                    for rec in check:
                        mm = rec.name.split('/')
                        if len(mm) != 3:
                            raise ValidationError(
                                'Please check the correct format of serial recorded with this product to be consists of this format barcode/barcode/generated serial for product {}'.format(
                                    rec.product_id.name))
                        else:
                            ww = mm[2]
                            barcode1 = mm[0]
                            barcode2 = mm[1]
                            if ww == '':
                                raise ValidationError(
                                    'Please check the correct format of the third part of the serial recorded with this product (generated serial) must be intger not empty')
                            else:
                                for l in str(ww):
                                    if l not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                                        raise ValidationError(
                                            'Please check the correct format of the third part of the serial recorded with this product (generated serial) must be intger')
                                    else:
                                        gg = int(ww)
                                        br = str(barcode1)
                                        cat = str(barcode2)
                                        if str(m.product_id.barcode) == br and str(m.product_id.barcode) == cat:
                                            list.append(gg)
                                            # print('hi')
                                        else:
                                            list.append(0)
                                            # print(list)
                    cc = int(max(list))
                    counter = cc + 1
                    lis2 = []
                    for l in m.move_line_ids:
                        if not l.lot_name:
                            if 0 < i <= m.quantity_to_generate:
                                l.generated_serial = counter
                                # l.production_date = l.move_id.production_date
                                counter = counter + 1
                                i = i - 1
                    for l in m.move_line_ids:
                        if l.lot_name:
                            lis2.append(l.lot_name)
                    print(len(lis2))
                    if m.product_uom_qty == len(lis2):
                        # m.state='generated'
                        m.is_generated = True
                        # if l.product_id and l.lot_name:
                        #     vals = ({
                        #         'alternative_serial': str(l.generated_serial),
                        #         'product_id': l.product_id.id,
                        #     })
                        #     asd.create(vals)
                else:
                    lis3 = []
                    for l in m.move_line_ids:
                        if not l.lot_name:
                            if 0 < i <= m.quantity_to_generate:
                                l.generated_serial = a
                                a = a + 1
                                i = i - 1
                    for l in m.move_line_ids:
                        if l.lot_name:
                            lis3.append(l.lot_name)
                    print(len(lis3))
                    if m.product_uom_qty == len(lis3):
                        # m.state='generated'
                        m.is_generated = True
                        # if l.product_id and l.lot_name:
                        #     vals = ({
                        #         'alternative_serial': str(l.generated_serial),
                        #         'product_id': l.product_id.id,
                        #     })
                        #     asd.create(vals)

                # return {
                #     "type": "ir.actions.do_nothing",
                # }
        # return {
        #     "type": "ir.actions.do_nothing",
        # }

        # @api.multi

    # @api.multi
    # @api.onchange('production_date')
    # def compute_expiration_date_from_production(self):
    #     for rec in self:
    #         if rec.production_date and rec.product_id:
    #             current_day = fields.Date.today()
    #             # planned = (datetime.datetime.strptime(str(rec.production_date),'%Y-%m-%d') + datetime.timedelta(days=rec.product_id.life_time)).strftime('%Y-%m-%d')
    #             planned = rec.production_date + datetime.timedelta(rec.product_id.life_time)
    #             exp_date = planned
    #             if exp_date:
    #                 a = dateutil.parser.parse(str(exp_date)).date()
    #                 if a <= current_day:
    #
    #                     raise ValidationError("End of Life/Expiration Date can't be less than or equal Today Date!")


# def create_serial_numbers_for_products(self):
#     for rec in self:
#         asd = rec.env['stock.production.lot']
#         for l in rec.move_line_ids:
#           if l.product_id and l.lot_name:
#             vals = ({
#                 'name': str(l.lot_name),
#                 'product_id': l.product_id.id,
#             })
#             asd.create(vals)
class StockMoveLineInheritClass(models.Model):
    _inherit = "stock.move.line"

    brand = fields.Char(string='Brand', store=True, copy=True, track_visibility='onchange',
                        default='0', related='product_id.brand')
    category = fields.Char(string='category', default='0', store=True, copy=True, track_visibility='onchange',
                           related='product_id.category')
    barcode1 = fields.Char(string='Barcode1', store=True, copy=True, track_visibility='onchange',
                           default='0', related='product_id.barcode')
    barcode2 = fields.Char(string='Barcode2', default='0', store=True, copy=True, track_visibility='onchange',
                           related='product_id.barcode')
    generated_serial = fields.Integer(string='Generated serial', store=True, copy=True, track_visibility='onchange',
                                      )
    production_date = fields.Datetime(string='Production Date', related='move_id.production_date')
    exp_date = fields.Datetime(string='Expiration Date', compute='compute_expiration_date')
    use_date = fields.Datetime(string='Use Date', compute='compute_expiration_date')
    removal_date = fields.Datetime(string='Removal Date', compute='compute_expiration_date')
    alert_date = fields.Datetime(string='Alert Date', compute='compute_expiration_date')

    lot_name = fields.Char('Lot/Serial Number', store='True', copy=True, track_visibility='onchange',
                           compute='serial_collect')

    qty_done = fields.Float('Done', default=0.0, digits=dp.get_precision('Product Unit of Measure'),
                            compute='compute_done_from_serial', copy=False)
    code = fields.Selection([('incoming', 'Vendors'), ('outgoing', 'Customers'), ('internal', 'Internal')],
                            'Type of Operation', related='move_id.code')
    is_pick = fields.Boolean('Is a Pick?', related='move_id.is_pick', store=True)

    @api.multi
    @api.constrains('lot_id')
    def check_lot_id_exists(self):
        if self.move_id.picking_type_id.code != 'incoming':
            for line in self:
                if not line.lot_id:
                    raise ValidationError('you cant not save when lot id is empty!!')

    @api.multi
    @api.depends('barcode1', 'barcode2', 'generated_serial', 'product_id')
    def serial_collect(self):
        for rec in self:
            if rec.generated_serial > 0:
                rec.lot_name = (str(rec.barcode1) + '/' + str(rec.barcode2) + '/' + str(rec.generated_serial))

    @api.multi
    @api.depends('lot_name', 'qty_done','lot_id')
    def compute_done_from_serial(self):
        for rec in self:
            # if rec.move_id.picking_type_id.use_existing_lots ==True and (rec.move_id.code =='outgoing' or rec.move_id.code =='internal'):
            #     if rec.lot_id:
            #         rec.qty_done = 1
            # elif rec.move_id.picking_type_id.use_create_lots == True and rec.move_id.code =='incoming':
            #     if rec.lot_name:
            #         rec.qty_done = 1
            # else:
            if rec.lot_name:
                rec.qty_done = 1

    @api.multi
    @api.depends('product_id', 'production_date')
    def compute_expiration_date(self):
        for rec in self:
            if rec.production_date and rec.product_id:
                # planned = (datetime.datetime.strptime(str(rec.production_date),'%Y-%m-%d') + datetime.timedelta(days=rec.product_id.life_time)).strftime('%Y-%m-%d')
                planned = rec.production_date + datetime.timedelta(rec.product_id.life_time)
                rec.exp_date = planned
                planned = rec.production_date + datetime.timedelta(rec.product_id.use_time)
                rec.use_date = planned
                planned = rec.production_date + datetime.timedelta(rec.product_id.removal_time)
                rec.removal_date = planned
                planned = rec.production_date + datetime.timedelta(rec.product_id.alert_time)
                rec.alert_date = planned

    def _action_done(self):
        """ This method is called during a move's `action_done`. It'll actually move a quant from
        the source location to the destination location, and unreserve if needed in the source
        location.

        This method is intended to be called on all the move lines of a move. This method is not
        intended to be called when editing a `done` move (that's what the override of `write` here
        is done.
        """
        Quant = self.env['stock.quant']

        # First, we loop over all the move lines to do a preliminary check: `qty_done` should not
        # be negative and, according to the presence of a picking type or a linked inventory
        # adjustment, enforce some rules on the `lot_id` field. If `qty_done` is null, we unlink
        # the line. It is mandatory in order to free the reservation and correctly apply
        # `action_done` on the next move lines.
        ml_to_delete = self.env['stock.move.line']
        for ml in self:
            # Check here if `ml.qty_done` respects the rounding of `ml.product_uom_id`.
            uom_qty = float_round(ml.qty_done, precision_rounding=ml.product_uom_id.rounding, rounding_method='HALF-UP')
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            qty_done = float_round(ml.qty_done, precision_digits=precision_digits, rounding_method='HALF-UP')
            if float_compare(uom_qty, qty_done, precision_digits=precision_digits) != 0:
                raise UserError(_('The quantity done for the product "%s" doesn\'t respect the rounding precision \
                                  defined on the unit of measure "%s". Please change the quantity done or the \
                                  rounding precision of your unit of measure.') % (
                    ml.product_id.display_name, ml.product_uom_id.name))

            qty_done_float_compared = float_compare(ml.qty_done, 0, precision_rounding=ml.product_uom_id.rounding)
            if qty_done_float_compared > 0:
                if ml.product_id.tracking != 'none':
                    picking_type_id = ml.move_id.picking_type_id
                    if picking_type_id:
                        if picking_type_id.use_create_lots:
                            # If a picking type is linked, we may have to create a production lot on
                            # the fly before assigning it to the move line if the user checked both
                            # `use_create_lots` and `use_existing_lots`.
                            if ml.lot_name and not ml.lot_id:
                                lot = self.env['stock.production.lot'].create(
                                    {
                                        'name': ml.lot_name,
                                        'product_id': ml.product_id.id,
                                        'life_date': ml.exp_date,
                                        'use_date': ml.use_date,
                                        'removal_date': ml.removal_date,
                                        'alert_date': ml.alert_date,
                                        'lot_location': ml.location_dest_id.id,
                                        'exp_date': ml.exp_date,
                                        'production_date': ml.production_date,
                                    }
                                )
                                ml.write({'lot_id': lot.id})
                        elif not picking_type_id.use_create_lots and not picking_type_id.use_existing_lots:
                            # If the user disabled both `use_create_lots` and `use_existing_lots`
                            # checkboxes on the picking type, he's allowed to enter tracked
                            # products without a `lot_id`.
                            continue
                    elif ml.move_id.inventory_id:
                        # If an inventory adjustment is linked, the user is allowed to enter
                        # tracked products without a `lot_id`.
                        continue

                    if not ml.lot_id:
                        raise UserError(
                            _('You need to supply a Lot/Serial number for product %s.') % ml.product_id.display_name)
            elif qty_done_float_compared < 0:
                raise UserError(_('No negative quantities allowed'))
            else:
                ml_to_delete |= ml
        ml_to_delete.unlink()

        # Now, we can actually move the quant.
        done_ml = self.env['stock.move.line']
        for ml in self - ml_to_delete:
            if ml.product_id.type == 'product':
                rounding = ml.product_uom_id.rounding

                # if this move line is force assigned, unreserve elsewhere if needed
                if not ml.location_id.should_bypass_reservation() and float_compare(ml.qty_done, ml.product_uom_qty,
                                                                                    precision_rounding=rounding) > 0:
                    qty_done_product_uom = ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id,
                                                                               rounding_method='HALF-UP')
                    extra_qty = qty_done_product_uom - ml.product_qty
                    ml._free_reservation(ml.product_id, ml.location_id, extra_qty, lot_id=ml.lot_id,
                                         package_id=ml.package_id, owner_id=ml.owner_id, ml_to_ignore=done_ml)
                # unreserve what's been reserved
                if not ml.location_id.should_bypass_reservation() and ml.product_id.type == 'product' and ml.product_qty:
                    Quant._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=ml.lot_id,
                                                    package_id=ml.package_id, owner_id=ml.owner_id, strict=True)

                # move what's been actually done
                quantity = ml.product_uom_id._compute_quantity(ml.qty_done, ml.move_id.product_id.uom_id,
                                                               rounding_method='HALF-UP')
                available_qty, in_date = Quant._update_available_quantity(ml.product_id, ml.location_id, -quantity,
                                                                          lot_id=ml.lot_id, package_id=ml.package_id,
                                                                          owner_id=ml.owner_id)
                if available_qty < 0 and ml.lot_id:
                    # see if we can compensate the negative quants with some untracked quants
                    untracked_qty = Quant._get_available_quantity(ml.product_id, ml.location_id, lot_id=False,
                                                                  package_id=ml.package_id, owner_id=ml.owner_id,
                                                                  strict=True)
                    if untracked_qty:
                        taken_from_untracked_qty = min(untracked_qty, abs(quantity))
                        Quant._update_available_quantity(ml.product_id, ml.location_id, -taken_from_untracked_qty,
                                                         lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id)
                        Quant._update_available_quantity(ml.product_id, ml.location_id, taken_from_untracked_qty,
                                                         lot_id=ml.lot_id, package_id=ml.package_id,
                                                         owner_id=ml.owner_id)
                Quant._update_available_quantity(ml.product_id, ml.location_dest_id, quantity, lot_id=ml.lot_id,
                                                 package_id=ml.result_package_id, owner_id=ml.owner_id, in_date=in_date)
            done_ml |= ml
        # Reset the reserved quantity as we just moved it to the destination location.
        (self - ml_to_delete).with_context(bypass_reservation_update=True).write({
            'product_uom_qty': 0.00,
            'date': fields.Datetime.now(),
        })


class StockPickingBulxInheritClass(models.Model):
    _inherit = "stock.picking"

    code = fields.Selection([('incoming', 'Vendors'), ('outgoing', 'Customers'), ('internal', 'Internal')],
                            'Type of Operation', related='picking_type_id.code')
    qty_updated = fields.Boolean()

    def update_bulx_stock(self, updated_list):
        access_token = check_type.get_bulx_authintecation()
        data = {
            "productStocks": updated_list
        }
        logging.warn(data)
        try:
            request = requests.post(
                'https://bulxperformancetest.azurewebsites.net/api/v1/Catalog/Products/update-stock',
                json=data, headers={'Authorization': 'Bearer %s' % access_token, 'Content-Type': 'application/json'})
            text_val = request.text
            res = json.loads(text_val)
            logging.warn(res)
            logging.warn(request.status_code)
            if request.status_code == 400:
                raise ValidationError(request.text)
            request.raise_for_status()
        except requests.HTTPError as e:
            _logger.debug("request failed with code: %r, msg: %r, content: %r",
                          e.response.status_code, e.response.reason, e.response.content)

    def get_products_list(self):
        products_list = []
        for line in self.move_ids_without_package:
            product_guid = line.product_id.bulx_id
            product_qty = line.product_id._compute_product_quantities()
            item = {'productId': product_guid, 'stock': int(product_qty)}
            products_list.append(item)
        logging.warn(products_list)
        self.update_bulx_stock(products_list)
        self.qty_updated = True

    def button_validate(self):
        valid = super(StockPickingBulxInheritClass, self).button_validate()
        # self.get_products_list()
        return valid


class ProductCategoryBulxInherit(models.Model):
    _inherit = "product.category"

    category_code = fields.Char(string='category Code', default='0', store=True, copy=True, track_visibility='onchange')


class StockLocationBulxMain(models.Model):
    _inherit = "stock.location"

    is_main_stock = fields.Boolean(string='Is Main Location?', store=True, copy=True, track_visibility='onchange')
    parent_name = fields.Char('pn', related='location_id.name')


class OperationTypeInheritBulx(models.Model):
    _inherit = "stock.picking.type"

    is_pick = fields.Boolean('Is a Pick?')
    is_internal = fields.Boolean('Is Internal?')


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _update_reserved_quantity(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None,
                                  strict=False):
        """ Increase the reserved quantity, i.e. increase `reserved_quantity` for the set of quants
        sharing the combination of `product_id, location_id` if `strict` is set to False or sharing
        the *exact same characteristics* otherwise. Typically, this method is called when reserving
        a move or updating a reserved move line. When reserving a chained move, the strict flag
        should be enabled (to reserve exactly what was brought). When the move is MTS,it could take
        anything from the stock, so we disable the flag. When editing a move line, we naturally
        enable the flag, to reflect the reservation according to the edition.

        :return: a list of tuples (quant, quantity_reserved) showing on which quant the reservation
            was done and how much the system was able to reserve on it
        """
        self = self.sudo()
        rounding = product_id.uom_id.rounding
        quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id,
                              strict=strict)
        reserved_quants = []

        if float_compare(quantity, 0, precision_rounding=rounding) > 0:
            # if we want to reserve
            available_quantity = sum(
                quants.filtered(lambda q: float_compare(q.quantity, 0, precision_rounding=rounding) > 0).mapped(
                    'quantity')) - sum(quants.mapped('reserved_quantity'))
            if float_compare(quantity, available_quantity, precision_rounding=rounding) > 0:
                raise UserError(
                    _('It is not possible to reserve more products of %s than you have in stock.') % product_id.display_name)
        elif float_compare(quantity, 0, precision_rounding=rounding) < 0:
            # if we want to unreserve
            available_quantity = sum(quants.mapped('reserved_quantity'))
            if float_compare(abs(quantity), available_quantity, precision_rounding=rounding) > 0:
                print("It is not possible to unreserve more products of")
                pass
                # raise UserError(
                #     _('It is not possible to unreserve more products of %s than you have in stock.') % product_id.display_name)
        else:
            return reserved_quants

        for quant in quants:
            if float_compare(quantity, 0, precision_rounding=rounding) > 0:
                max_quantity_on_quant = quant.quantity - quant.reserved_quantity
                if float_compare(max_quantity_on_quant, 0, precision_rounding=rounding) <= 0:
                    continue
                max_quantity_on_quant = min(max_quantity_on_quant, quantity)
                quant.reserved_quantity += max_quantity_on_quant
                reserved_quants.append((quant, max_quantity_on_quant))
                quantity -= max_quantity_on_quant
                available_quantity -= max_quantity_on_quant
            else:
                max_quantity_on_quant = min(quant.reserved_quantity, abs(quantity))
                quant.reserved_quantity -= max_quantity_on_quant
                reserved_quants.append((quant, -max_quantity_on_quant))
                quantity += max_quantity_on_quant
                available_quantity += max_quantity_on_quant

            if float_is_zero(quantity, precision_rounding=rounding) or float_is_zero(available_quantity,
                                                                                     precision_rounding=rounding):
                break
        return reserved_quants
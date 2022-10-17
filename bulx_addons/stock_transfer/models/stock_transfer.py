from odoo import models, fields, api, tools, exceptions, _
from odoo.exceptions import ValidationError


class PickingStockTransferInherit(models.Model):
    _inherit = "stock.picking"

    location_select = fields.Many2one('stock.location', string='Destination Location', index=True, required=False)
    location_scan = fields.Char(string='Scan Location')
    location_source = fields.Many2one('stock.location', string='Source Location', index=True, required=False)
    name = fields.Char('Description', index=True, required=False)
    quantity_to_generate = fields.Integer(string='Quantity To generate', store=True, copy=True,
                                          track_visibility='onchange')
    production_date = fields.Datetime(string='Production Date')
    code = fields.Selection([('incoming', 'Vendors'), ('outgoing', 'Customers'), ('internal', 'Internal')],
                            'Type of Operation', related='picking_type_id.code')
    is_pick = fields.Boolean('Is a Pick?', related='picking_type_id.is_pick', store=True)
    search_serial = fields.Char(string='Scan Serial', store=True, copy=True, track_visibility='onchange')
    scan_serial = fields.Char(string='Scan a Serial', store=True, copy=True, track_visibility='onchange')
    is_generated = fields.Boolean('Is Generated')
    filter_locations = fields.Many2many('stock.location', string='Locations Filter')
    scanned_serials = fields.Many2many('stock.production.lot', store=True, string='Scanned Serials')
    collect_products = fields.Many2many('product.product', store=True, string='Collect Products',
                                        compute='collect_moves_products')

    @api.multi
    @api.depends('move_ids_without_package', 'is_pick')
    def collect_moves_products(self):
        for rec in self:
            list = []
            if rec.is_pick == True:
                for line in rec.move_ids_without_package:
                    list.append(line.product_id.id)

                rec.collect_products = list

    @api.multi
    @api.onchange('location_scan')
    def compute_locations_from_scan(self):
        if self.code == 'internal' and self.is_pick == True and self.location_scan:
            check = self.env['stock.location'].search(
                [('barcode', '=', self.location_scan)])
            if check:
                for line in check:
                    if line.is_main_stock == True:
                        raise ValidationError('you cant transfer from main stock')
                    else:

                        self.location_source = check.id
                        # self.search_serial = ''
            else:
                raise ValidationError('this barcode does not exist in any location')
            self.location_scan = ''

    @api.multi
    @api.onchange('search_serial')
    def compute_lines_from_serial_scan(self):
        # for rec in self:
        if self.code == 'internal' and self.search_serial:
            if not self.location_source and self.is_pick == True:
                raise ValidationError('Please Select Source Location at first')
            # if self.is_generated ==True:
            #     raise ValidationError('you can not scan items more than initial demand')
            else:
                self.collect_moves_products()
                serial_id = self.env['stock.production.lot'].search(
                    [('name', '=', self.search_serial)])
                if not serial_id:
                    raise ValidationError('Serial you entered does not exist!')
                if serial_id.product_id not in self.collect_products:
                    raise ValidationError('Serial you entered does not exist in this order!')
                for record in self.move_ids_without_package:
                    check = False
                    if serial_id.product_id == record.product_id:
                        check = serial_id
                    else:
                        continue
                    print(check)
                    if check:
                        # for m in check:
                        mm = check.name.split('/')
                        ww = mm[2]
                        bb = int(ww)

                        if self.is_pick == True:

                            if self.location_source:
                                Quant = self.env['stock.quant']
                                product_location = self.env['stock.quant'].search(
                                    [('product_id', '=', record.product_id.id), ('lot_id', '=', check.id),
                                     ('location_id', '=', self.location_source.id), ('quantity', '=', 1),
                                     ])
                                # print('product_location',product_location)
                                product_loc_id = self.env['stock.quant'].search(
                                    [('product_id', '=', record.product_id.id), ('lot_id', '=', check.id),
                                     ('quantity', '=', 1), ])

                                if not product_location:
                                    raise ValidationError(
                                        'serial {} for product {} not found in location {} it is in location : {}'.format(
                                            check.name, record.product_id.name, self.location_source.name,
                                            product_loc_id.location_id.name))
                                list2 = {
                                    # 'product_id': self.product_id.id,
                                    'generated_serial': bb,
                                    'lot_id': check.id,
                                    'brand': record.product_id.brand,
                                    'category': record.product_id.category,
                                    'product_uom_id': record.product_uom.id,
                                    'location_id': self.location_source.id,
                                    # 'location_dest_id': self.location_dest_id.id,

                                    'qty_done': 1,
                                }
                                vals = {
                                    'reserved_quantity': 0,

                                }
                                list = []
                                scanned = []
                                for rec in record.move_line_ids:
                                    list.append(rec.lot_id.name)
                                    if (rec.lot_id.name == self.search_serial and rec.qty_done > 0.0):
                                        raise ValidationError('Serial you entered already scanned!')

                                    elif (rec.lot_id.name == self.search_serial and rec.qty_done == 0):
                                        rec.update(list2)
                                        rec.write(list2)
                                        record.scanned_quantites += 1
                                        scanned.append(rec.lot_id.id)
                                        self.scanned_serials = scanned

                                if self.search_serial not in list:
                                    for rec in record.move_line_ids:
                                        quant2 = self.env['stock.quant'].search(
                                            [('product_id', '=', rec.product_id.id), ('lot_id', '=', rec.lot_id.id),
                                             ('quantity', '=', 1),
                                             ('reserved_quantity', '=', 1),
                                             ])
                                        print(quant2.lot_id.name, quant2.reserved_quantity, 'ghghghgh')
                                        if (rec.lot_id.name != self.search_serial) and rec.qty_done == 0:
                                            # Quant._update_reserved_quantity(rec.product_id, rec.location_id,
                                            #                                 -1, lot_id=rec.lot_id,
                                            #                                 package_id=rec.package_id,
                                            #                                 owner_id=rec.owner_id, strict=False)
                                            if rec.lot_id.id == quant2.lot_id.id:
                                                quant2.sudo().write(vals)
                                                print(quant2.lot_id.name, quant2.reserved_quantity, 'after function')

                                            rec.update(list2)
                                            print(quant2.lot_id.name, quant2.reserved_quantity, 'after update')
                                            rec.write(list2)
                                            print(quant2.lot_id.name, quant2.reserved_quantity, 'after write')
                                            record.scanned_quantites += 1
                                            scanned.append(rec.lot_id.id)
                                            self.scanned_serials = scanned
                                            # self.scanned_serials = self.search_serial
                                            # record.qty_done += 1
                                            # self.search_serial = ''
                                            break
                                self.search_serial = ''
                                # list_mix =[]
                                # for l in record.move_line_ids:
                                #     if l.lot_name:
                                #         list_mix.append(l.lot_name)
                                # print(len(list_mix))
                                # if record.product_uom_qty == len(list_mix):
                                #     # m.state='generated'
                                #     self.is_generated = True
                            else:
                                product_location = self.env['stock.quant'].search(
                                    [('product_id', '=', record.product_id.id), ('lot_id', '=', check.id),
                                     ('quantity', '=', 1), ])
                                # print('no location 1', product_location)
                                if not product_location:
                                    raise ValidationError(
                                        'serial {} for product {} not available '.format(check.name,
                                                                                         record.product_id.name, ))
                                list3 = {
                                    # 'product_id': self.product_id.id,
                                    'generated_serial': bb,
                                    'lot_id': check.id,
                                    'brand': record.product_id.brand,
                                    'category': record.product_id.category,
                                    'product_uom_id': record.product_uom.id,
                                    # 'location_id': self.location_id.id,
                                    # 'location_dest_id': self.location_select.id,
                                    'qty_done': 1,
                                }

                                list = []
                                for rec in record.move_line_ids:
                                    list.append(rec.lot_id.name)
                                    if (rec.lot_id.name == self.search_serial):
                                        product_location = self.env['stock.quant'].search(
                                            [('product_id', '=', record.product_id.id), ('lot_id', '=', check.id),
                                             ('location_id', '=', rec.location_id.id), ('quantity', '=', 1),
                                             ('reserved_quantity', '=', 0)])
                                        # print(' no location', product_location)
                                        if not product_location:
                                            raise ValidationError(
                                                'serial {} for product {} not found in location {}'.format(check.name,
                                                                                                           record.product_id.name,
                                                                                                           rec.location_id.name))
                                        rec.write(list3)
                                        self.search_serial = ''
                                        # list_mix = []
                                        # for l in record.move_line_ids:
                                        #     if l.lot_name:
                                        #         list_mix.append(l.lot_name)
                                        # print(len(list_mix))
                                        # if record.product_uom_qty == len(list_mix):
                                        #     # m.state='generated'
                                        #     self.is_generated = True

                                if self.search_serial not in list:
                                    for rec in record.move_line_ids:
                                        if (rec.lot_id.name != self.search_serial) and rec.qty_done == 0:
                                            product_location = self.env['stock.quant'].search(
                                                [('product_id', '=', record.product_id.id), ('lot_id', '=', check.id),
                                                 ('location_id', '=', rec.location_id.id), ('quantity', '=', 1),
                                                 ('reserved_quantity', '=', 0)])
                                            # print(' no location', product_location)
                                            if not product_location:
                                                raise ValidationError(
                                                    'serial {} for product {} not found in location {}'.format(
                                                        check.name,
                                                        record.product_id.name,
                                                        rec.location_id.name))
                                            rec.update(list3)
                                            self.search_serial = ''
                                            # list_mix = []
                                            # for l in record.move_line_ids:
                                            #     if l.lot_name:
                                            #         list_mix.append(l.lot_name)
                                            # print(len(list_mix))
                                            # if record.product_uom_qty == len(list_mix):
                                            #     # m.state='generated'
                                            #     self.is_generated = True
                                            break
                                # if self.search_serial not in list:
                                #     raise ValidationError('Serial you entered does not exist in list 3!')

        # else:
        #     raise ValidationError('Serial you entered does not exist !')

    @api.multi
    @api.onchange('scan_serial')
    def compute_lines_from_serial_scan_delivery(self):
        if self.code == 'outgoing' and self.scan_serial:
            # check = self.env['stock.production.lot'].search(
            #     [('product_id', '=', self.product_id.id), ('name', '=', self.scan_serial)])
            # if not check:
            #     raise ValidationError('Serial you entered does not exist!')
            serial_id = self.env['stock.production.lot'].search(
                [('name', '=', self.scan_serial)])
            if not serial_id:
                raise ValidationError('Serial you entered does not exist  first!')
            for record in self.move_ids_without_package:
                check = False
                if serial_id.product_id == record.product_id:
                    check = serial_id
                else:
                    continue
                if check:
                    # for m in check:
                    mm = check.name.split('/')
                    ww = mm[2]
                    bb = int(ww)
                    l = (
                        {
                            'product_id': record.product_id.id,
                            'generated_serial': bb,
                            # 'lot_id': str(str(self.product_id.brand)+str(self.product_id.category)+str(ww)),
                            'brand': record.product_id.brand,
                            'category': record.product_id.category,
                            'product_uom_id': record.product_uom.id,
                            'location_id': self.location_id.id,
                            'location_dest_id': self.location_dest_id.id,
                            'qty_done': 1,
                        }
                    )
                    list = []
                    for rec in record.move_line_ids:
                        list.append(rec.lot_id.name)
                        if (rec.lot_id.name == self.scan_serial and rec.qty_done < 1.0):
                            rec.update(l)
                            rec.write(l)
                            record.scanned_quantites += 1
                            # self.search_serial = ''
                        elif (rec.lot_id.name == self.scan_serial and rec.qty_done > 0.0):
                            raise ValidationError('Serial you entered already scanned!')

                    if self.scan_serial not in list:
                        raise ValidationError('Serial you entered does not exist in moves lines!')
                    self.scan_serial = ''


                else:
                    raise ValidationError('Serial you entered does not exist!')


class PickingStockMoveBulx(models.Model):
    _inherit = "stock.move"

    filter_locations = fields.Many2many('stock.location', string='Locations Filter', compute='compute_all_locations', )
    filter_serials = fields.Many2many('stock.production.lot', string='Serials Filter', compute='compute_all_locations')
    zone = fields.Many2one('location.zone', string='Zone', store=True, copy=True, track_visibility='onchange',
                           compute='compute_zone_from_locations')
    package = fields.Many2one('stock.quant.package', string='Packages', store=True, copy=True,
                              track_visibility='onchange',
                              compute='compute_all_packages')
    scanned_quantites = fields.Float('Scanned Quantities')
    returned_serials = fields.Many2many('stock.production.lot', string='Returned Serials', store=True)

    def recheck_availablety(self):
        vals = {
            'reserved_quantity': 0,
        }
        quant2 = self.env['stock.quant'].search(
            [('product_id', '=', self.product_id.id),
             ('quantity', '=', 1),
             ('reserved_quantity', '=', 1),
             ],limit=self.product_uom_qty)
        for lin in quant2:
            lin.write(vals)

    # @api.multi
    @api.depends('move_line_ids', 'is_pick', 'search_serial')
    def compute_all_locations(self):
        for rec in self:
            # if rec.is_pick == True or rec.code=='outgoing':
            mylist = []
            myserial = []
            for line in rec.move_line_ids:
                print("my serial my locations")
                mylist.append(line.location_id.id)
                if line.lot_id:
                    myserial.append(line.lot_id.id)
                print("after my serial my locations")
                # print(mylist)
            # mylist = list(dict.fromkeys(mylist))

            rec.filter_locations = mylist
            rec.filter_serials = myserial

    @api.depends('move_line_ids.result_package_id')
    def compute_all_packages(self):
        for rec in self:
            for line in rec.move_line_ids:
                if line.result_package_id:
                    rec.package = line.result_package_id.id

    @api.depends('move_line_ids', 'is_pick')
    def compute_zone_from_locations(self):
        for rec in self:
            if rec.is_pick == True:
                # if rec.filter_locations:

                # mylocation = []
                for line in rec.move_line_ids:
                    # mylocation.append(line.location_id.zone.id)
                    rec.zone = line.location_id.zone.id


class StockLocationBulxZone(models.Model):
    _inherit = "stock.location"

    zone = fields.Many2one('location.zone', string='Zone', store=True, copy=True, track_visibility='onchange')


class StockLocationZone(models.Model):
    _name = "location.zone"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Zone', store=True, copy=True, track_visibility='onchange')
    description = fields.Text(string='Description', store=True, copy=True, track_visibility='onchange')

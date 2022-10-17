import pandas as pd

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CyclingCountBulx(models.Model):
    _name = "cycling.count"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'search_serial'

    name = fields.Char(readonly=True, default="New")
    product_id = fields.Many2one('product.product', string='Product', store=True, copy=True,
                                 track_visibility='onchange')
    search_serial = fields.Char(string='Scan Serial', store=True, copy=True,
                                track_visibility='onchange', required=True)
    location = fields.Many2one('stock.location', string='Location', store=True, copy=True, track_visibility='onchange',
                               required=True)
    date = fields.Date(string='Date', default=fields.Date.today())
    dest_location = fields.Many2one('stock.location', string='Destination Location',
                                    domain="[('usage','=','inventory')]")
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type', domain="[('code','=','internal')]", )
    is_lost = fields.Boolean('Is Lost', compute='compute_lost_items_checkbox')
    is_replaced = fields.Boolean('Is Replaced', compute='compute_replaced_items_checkbox')
    # counter = fields.Integer(string='Founded Items', store=True, copy=True,
    #                          track_visibility='onchange', readonly=True)
    # lost_items = fields.Integer(string='Lost Items', store=True, copy=True,
    #                          track_visibility='onchange', readonly=True,compute='cal_lost_from_qty')
    cycling_lines = fields.One2many('cycling.lines', 'cycling_lines_inverse', copy=True, store=True)
    cycling_filter = fields.One2many('cycling.filter', 'cycling_filter_inverse', copy=True, store=True)
    cycling_update = fields.One2many('cycling.updates', 'cycling_update_inverse', copy=True, store=True)
    update_filter = fields.One2many('updates.filter', 'filter_update_inverse', copy=True, store=True)
    lost_items = fields.One2many('lost.items', 'lost_inverse', copy=True, store=True, compute='compute_lost_items')

    state = fields.Selection([
        ('draft', "Draft"),
        ('finish', "Finished"),
        ('lost_items', "Lost Items Moved"),
        ('update_items', "Replaced Items Updated"),
        ('confirm', "Confirmed"),
    ], default='draft', track_visibility='onchange')

    invers_com = fields.Many2one('main.cycling')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('cycling.count')
        return super(CyclingCountBulx, self).create(vals)

    @api.multi
    def action_finish(self):
        self.state = 'finish'

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        self.state = 'confirm'

    @api.multi
    def action_move_lost_items(self):
        for line in self.cycling_filter:
            stock_picking_obj = self.env['stock.picking'].create({
                'picking_type_id': self.picking_type_id.id,
                'location_id': self.location.id,
                'location_dest_id': self.dest_location.id,
            })
            # for rec in stock_picking_obj:
            stock_picking_obj.write({
                'move_ids_without_package': [(0, 0, {
                    'name': 'OP00',
                    'product_id': line.product.id,
                    'product_uom_qty': line.lost_items,
                    'product_uom': line.product.uom_id.id,
                    'location_id': self.location.id,
                    'location_dest_id': self.dest_location.id,
                })]
            })
            for record in stock_picking_obj.move_ids_without_package:
                for counter in range(len(self.lost_items)):
                    item_lost = self.lost_items[counter]
                    if item_lost.product.id == record.product_id.id:
                        mm = item_lost.serial.split('/')
                        ww = mm[2]
                        serial_code = int(ww)
                        # record.unlink()
                        stock_picking_obj.action_confirm()
                        stock_picking_obj.action_assign()
                        stock_picking_obj.move_line_ids[counter].write({
                            # 'name': record.product_id.name,
                            'generated_serial': serial_code,
                            'lot_id': item_lost.lot_reverse.id,
                            # 'product_id': record.product_id.id,
                            # 'product_uom_qty': 1,
                            # 'product_uom_id': record.product_id.uom_id.id,
                            # 'location_id': record.location_id.id or ' ',
                            # 'location_dest_id': record.location_dest_id.id,
                        })

            # for record in stock_picking_obj.move_ids_without_package:
            #     for hh in record.move_line_ids:
            #         if hh.generated_serial < 1:
            #             hh.unlink()

            # # list2=[]
            # for record in rec.move_ids_without_package:
            #     for sec in self.lost_items:
            #         if sec.product.id == record.product_id.id:
            #             mm = sec.serial.split('/')
            #             ww = mm[2]
            #             bb = int(ww)
            #             # list2=(
            #             #     {
            #             #         'name': record.product_id.name,
            #             #         'generated_serial': bb,
            #             #         'lot_id': sec.lot_reverse.id,
            #             #         'product_id': record.product_id.id,
            #             #         'product_uom_qty': 0,
            #             #         'product_uom_id': record.product_id.uom_id.id,
            #             #         'location_id': record.location_id.id or ' ',
            #             #         'location_dest_id': record.location_dest_id.id,
            #             #     }
            #             # )
            #     # print(list2)
            #     # record.move_line_ids.create(list2)
            #             record.update({
            #                 'move_line_ids': [(0, 0, {
            #                     'name': record.product_id.name,
            #                     'generated_serial': bb,
            #                     'lot_id': sec.lot_reverse.id,
            #                     'product_id': record.product_id.id,
            #                     'product_uom_qty': 0,
            #                     'product_uom_id': record.product_id.uom_id.id,
            #                     'location_id': record.location_id.id or ' ',
            #                     'location_dest_id': record.location_dest_id.id,
            #
            #                 })]
            #             })
            # #     for hh in record.move_line_ids:
            # #         if hh.qty_done < 1:
            # #             hh.unlink()
            # rec.action_confirm()
        self.state = 'lost_items'

    @api.multi
    def action_update_items(self):
        for line in self.update_filter:
            stock_picking_obj = self.env['stock.picking'].create({
                # 'partner_id': self.customer.id,
                'picking_type_id': self.picking_type_id.id,
                'location_id': line.location.id,
                'location_dest_id': self.location.id,
            })

            # for rec in stock_picking_obj:
            stock_picking_obj.write({
                'move_ids_without_package': [(0, 0, {
                    'name': line.product.name,
                    'product_id': line.product.id,
                    'product_uom_qty': line.counter,
                    'product_uom': line.product.uom_id.id,
                    'location_id': line.location.id or ' ',
                    'location_dest_id': self.location.id,
                })]
            })

            for record in stock_picking_obj.move_ids_without_package:
                for counter in range(len(self.cycling_update)):
                    cycling_update = self.cycling_update[counter]
                    if cycling_update.product.id == record.product_id.id and cycling_update.location.id == record.location_id.id:
                        mm = cycling_update.serial_lot.split('/')
                        ww = mm[2]
                        serial_code = int(ww)
                        stock_picking_obj.action_confirm()
                        stock_picking_obj.action_assign()
                        stock_picking_obj.move_line_ids[counter].write({
                            'generated_serial': serial_code,
                            'lot_id': cycling_update.lot_reverse.id,
                        })
                        # record.write({
                        #     'move_line_ids': [(0, 0, {
                        #         'name': record.product_id.name,
                        #         'generated_serial': bb,
                        #         'lot_id': sec.lot_reverse.id,
                        #         'product_id': record.product_id.id,
                        #         'product_uom_qty': 1,
                        #         'product_uom_id': record.product_id.uom_id.id,
                        #         'location_id': record.location_id.id or ' ',
                        #         'location_dest_id': record.location_dest_id.id,
                        #
                        #     })]
                        # })
            # rec.action_confirm()
            # for record in rec.move_ids_without_package:
            #     for hh in record.move_line_ids:
            #         if hh.generated_serial < 1:
            #             hh.unlink()
        # self.env['my.model'].some_method()
        self.state = 'update_items'

    @api.multi
    def action_filter_updates(self):
        lines = []
        self.update_filter.unlink()
        for rec in self.cycling_update:
            lines.append({
                'product': rec.product.id,
                'counter': rec.counter,
                'location': rec.location.id,
            })
        df = pd.DataFrame(lines)
        if lines:
            g = df.groupby(['product', 'location'], as_index=False)['counter'].sum()
            d = g.to_dict('r')
            self.update_filter = d
        else:
            raise ValidationError(_(" no lines."))

    @api.multi
    def action_filter(self):
        lines = []
        self.cycling_filter.unlink()
        for rec in self.cycling_lines:
            lines.append({
                'product': rec.product.id,
                'counter': rec.counter,
            })
        df = pd.DataFrame(lines)
        if lines:
            g = df.groupby('product', as_index=False)['counter'].sum()
            d = g.to_dict('r')
            self.cycling_filter = d

        for mm in self.cycling_lines:
            for rec in self.lost_items:
                if (mm.product.id == rec.product.id) and (mm.serial_lot == rec.serial):
                    rec.unlink()
        # else:
        #     raise ValidationError(_(" no lines."))

    @api.multi
    @api.depends('location')
    def compute_lost_items(self):
        items = []
        all_items = self.env['stock.production.lot'].search(
            [('lot_location', '=', self.location.id)])
        product_quant_ids = self.env['stock.quant'].search(
            [(), ('location_id', '=', self.location.id), ('quantity', '=', 1)])
        for item in product_quant_ids:
            items.append({'product': item.product_id.id,
                          'serial': item.lot_id.name,

                          })
        self.lost_items = items

    # @api.multi
    @api.onchange('search_serial')
    def compute_product_lines_serial_scan(self):
        # print("on change")
        list = []
        list_update = []
        # print(list)
        if self.search_serial and self.location:
            # print(self.search_serial)
            product_serial_id = self.env['stock.production.lot'].search([('name', '=', self.search_serial)])
            if not product_serial_id:
                raise ValidationError('Serial you entered does not exist!')
            # print(product_serial_id)
            product_quant_ids = self.env['stock.quant'].search([('lot_id', '=', product_serial_id.id), ])
            product_quant = self.env['stock.quant']
            # print(product_quant)
            for quat in product_quant_ids:
                if quat.location_id.usage == 'internal' and quat.quantity == 1:
                    product_quant = quat
                    # print(quat)
                if quat.location_id.usage == 'customer' and quat.quantity == 1:
                    raise ValidationError('it is delivered')
            #     i need to but it in delivered location
            # print(product_quant)
            if product_quant:
                list.append({'product': product_quant.product_id.id,
                             'serial_lot': product_serial_id.name,
                             'counter': 1, })
                for line in self.cycling_lines:
                    if line.serial_lot == self.search_serial:
                        raise ValidationError('this serial you scanned before already exist!')
                        break
                for line in self.cycling_update:
                    if line.serial_lot == self.search_serial:
                        # print(line.serial_lot)
                        raise ValidationError('this serial you scanned before already exist!')
                        break
                if product_quant.location_id == self.location:
                    # print("if location")
                    self.cycling_lines = list
                else:
                    # print("else location")
                    # print(list_update)
                    list_update = [
                        {'product': product_quant.product_id.id,
                         'serial_lot': product_serial_id.name,
                         'location': product_quant.location_id.id,
                         'counter': 1,
                         }
                    ]
                    # print("list", list_update)
                    self.cycling_update = list_update
                    # print("list", list_update)
            # else:
            #     # self.not_found += 1\
            #     check = self.env['stock.production.lot'].search(
            #         [('name', '=', self.search_serial)])
            #     if check:
            #         for m in check:
            #             list.append(
            #                 {
            #                     'product': m.product_id.id,
            #                     'serial_lot': m.name,
            #                     'location': m.lot_location.id,
            #                     'counter': 1,
            #                 }
            #             )
            #             print(list)
            #             for line in self.cycling_update:
            #                 if line.serial_lot == self.search_serial:
            #                     # print(line.serial_lot)
            #                     raise ValidationError('this serial you scanned before already exist!')
            #                     break
            # self.cycling_update = list
            # self.counter += 1

    @api.multi
    @api.depends('cycling_filter.lost_items')
    def compute_lost_items_checkbox(self):
        for line in self.cycling_filter:
            if line.lost_items > 0:
                self.is_lost = True

    @api.multi
    @api.depends('update_filter.counter')
    def compute_replaced_items_checkbox(self):
        for line in self.update_filter:
            if line.counter > 0:
                self.is_replaced = True


class CyclingCountBridgeBulx(models.Model):
    _name = "cycling.lines"
    _rec_name = 'product'

    product = fields.Many2one('product.product', string='Product', copy=True, store=True)
    serial_lot = fields.Char(string='Serial Number', copy=True, store=True)
    counter = fields.Integer(string='Founded Items', store=True, copy=True, default=1.0,
                             track_visibility='onchange', readonly=True)
    cycling_lines_inverse = fields.Many2one('cycling.count')


class CyclingCountFilter(models.Model):
    _name = "cycling.filter"
    _rec_name = 'product'

    product = fields.Many2one('product.product', string='Product', copy=True, store=True)
    counter = fields.Integer(string='Founded Items', store=True, copy=True, default=1.0,
                             track_visibility='onchange', readonly=True)
    lost_items = fields.Integer(string='Lost Items', store=True, copy=True,
                                track_visibility='onchange', readonly=True, compute='cal_lost_from_qty')
    location = fields.Many2one('stock.location', string='Location', store=True, copy=True, track_visibility='onchange',
                               related='cycling_filter_inverse.location')
    state = fields.Selection([
        ('draft', "Draft"),
        ('finish', "Finished"),
        ('confirm', "Confirmed"),
    ], default='draft', track_visibility='onchange', related='cycling_filter_inverse.state')
    qty_on_hand = fields.Integer('Quantity on hand', compute='cal_lost_from_qty')
    cycling_filter_inverse = fields.Many2one('cycling.count')

    @api.multi
    @api.depends('counter', 'qty_on_hand', 'product', 'location')
    def cal_lost_from_qty(self):
        for rec in self:
            list = []
            check_qty_hand = self.env['stock.quant'].search(
                [('product_id', '=', rec.product.id), ('location_id', '=', rec.location.id)])
            if check_qty_hand:
                for every_qty in check_qty_hand:
                    list.append(every_qty.quantity)
                # print(list)
                rec.qty_on_hand = int(sum(list))
                rec.lost_items = rec.qty_on_hand - rec.counter


class CyclingUpdatesBridgeBulx(models.Model):
    _name = "cycling.updates"
    _rec_name = 'product'

    product = fields.Many2one('product.product', string='Product', copy=True, store=True)
    serial_lot = fields.Char(string='Serial Number', copy=True, store=True)
    counter = fields.Integer(string='Founded Items', store=True, copy=True, default=1.0,
                             track_visibility='onchange', readonly=True)
    location = fields.Many2one('stock.location', string='Location', store=True, copy=True, track_visibility='onchange')
    lot_reverse = fields.Many2one('stock.production.lot', string='Serial', store=True, copy=True,
                                  track_visibility='onchange', compute='com_serial_from_exist')

    cycling_update_inverse = fields.Many2one('cycling.count')

    @api.multi
    @api.depends('serial_lot')
    def com_serial_from_exist(self):
        for rec in self:
            if rec.serial_lot:
                check = self.env['stock.production.lot'].search(
                    [('name', '=', rec.serial_lot)])
                if check:
                    rec.lot_reverse = check.id


class CyclingUpdatesFilterBulx(models.Model):
    _name = "updates.filter"
    _rec_name = 'product'

    product = fields.Many2one('product.product', string='Product', copy=True, store=True)
    counter = fields.Integer(string='Founded Items', store=True, copy=True, default=1.0,
                             track_visibility='onchange', readonly=True)
    location = fields.Many2one('stock.location', string='Location', store=True, copy=True, track_visibility='onchange')
    filter_update_inverse = fields.Many2one('cycling.count')


class LostFilterBulx(models.Model):
    _name = "lost.items"
    _rec_name = 'product'

    product = fields.Many2one('product.product', string='Product', copy=True, store=True)
    serial = fields.Char(string='Serial Number', copy=True, store=True)
    lot_reverse = fields.Many2one('stock.production.lot', string='Serial', store=True, copy=True,
                                  track_visibility='onchange', compute='com_ser_from_exist')

    @api.multi
    @api.depends('serial')
    def com_ser_from_exist(self):
        for rec in self:
            if rec.serial:
                check = self.env['stock.production.lot'].search(
                    [('name', '=', rec.serial)])
                if check:
                    rec.lot_reverse = check.id

    # counter = fields.Integer(string='Founded Items', store=True, copy=True, default=1.0,
    #                          track_visibility='onchange', readonly=True)
    # location = fields.Many2one('stock.location', string='Location', store=True, copy=True, track_visibility='onchange')
    lost_inverse = fields.Many2one('cycling.count')

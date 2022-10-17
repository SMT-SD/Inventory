from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MoveStockLineTransferInherit(models.Model):
    _inherit = "stock.move.line"

    # lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number',compute='_domain_lot_id',readonly=False)
    reason = fields.Many2one('return.reason', string='Reason')

    # @api.onchange('lot_id')
    # def _domain_lot_id(self):
    #     list=[]
    #     for rec in self:
    #         # if rec.lot_id:
    #             for line in rec.move_id.returned_serials:
    #                 list.append(line.name)
    #
    #     return {'domain': {'lot_id': [('name', 'in', list)]}}
    # list = []
    # asd = self.env['res.partner'].search([('parent_company', '=', self.partner_id.id)])
    # if asd:
    #     for rec in asd:
    #         list.append(rec.name)
    #


class MoveStockTransferInherit(models.Model):
    _inherit = "stock.move"

    return_ratio = fields.Float('Return Ratio', store=True, compute='compute_return_ratio')
    reason = fields.Many2many('return.reason', string='Reason', store=True, compute='compute_all_reasons')

    reason_scan = fields.Many2one('return.reason', string='Reason Select', store=True, copy=True)
    returned_serials = fields.Many2many('stock.production.lot', string='Returned Serials', compute='do_print_')
    is_return = fields.Boolean('Is Return?', related='picking_id.is_return')

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
                print("=====================", l)
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
            if (
                    not self.location_select or not self.location_source) and self.is_pick == False and self.is_internal == True:
                raise ValidationError('Please Select Source/Destination Location at first')
            if not self.location_source and self.is_pick == True:
                raise ValidationError('Please Select Source Location at first')
            else:
                check = self.env['stock.production.lot'].search(
                    [('product_id', '=', self.product_id.id), ('name', '=', self.search_serial)])
                if check:
                    mm = check.name.split('/')
                    ww = mm[2]
                    bb = int(ww)
                    if self.is_pick == False and self.is_internal == True:
                        if self.location_select and self.location_source:
                            product_location = self.env['stock.quant'].search(
                                [('product_id', '=', self.product_id.id), ('lot_id', '=', check.id),
                                 ('location_id', '=', self.location_source.id), ('quantity', '=', 1),
                                 ])
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

                    elif self.is_pick == False and self.is_return == False and self.is_internal == False:
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
                            print("is pick = fasle , is_Return = False, is_internal = False")
                            print(list1)
                            list = []
                            for rec in self.move_line_ids:
                                list.append(rec.lot_id.name)
                                if ((
                                        rec.lot_id.name == self.search_serial) and rec.qty_done > 0 and rec.location_dest_id == self.location_select):
                                    raise ValidationError('this serial scanned before')
                                elif (rec.lot_id.name == self.search_serial):
                                    rec.update(list1)
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
                                    rec.write(list4)

                            if self.search_serial not in list:
                                raise ValidationError('Serial you entered does not exist in move lines!')
                            self.search_serial = ''

                    elif self.is_pick == False and self.is_internal == False and self.is_return == True:
                        if self.location_select:
                            if not self.reason_scan:
                                raise ValidationError('Please Select reason at first')
                            list1 = {
                                'product_id': self.product_id.id,
                                'generated_serial': bb,
                                'lot_id': check.id,
                                'brand': self.product_id.brand,
                                'category': self.product_id.category,
                                'product_uom_id': self.product_uom.id,
                                # 'location_id': self.location_id.id,
                                'location_dest_id': self.location_select.id,
                                'reason': self.reason_scan.id,
                                'qty_done': 1, }
                            print(list1)
                            list = []
                            for rec in self.returned_serials:
                                list.append(rec.name)
                            print('hello emad', list)
                            if self.search_serial in list:
                                done = False
                                for rec in self.move_line_ids:
                                    print(rec.lot_id.name,"first")
                                    if (
                                            rec.lot_id.name == self.search_serial and rec.qty_done > 0 and rec.location_dest_id == self.location_select):
                                        raise ValidationError('this serial scanned before')
                                    print("=======================")
                                    if rec.qty_done == 0.0 and rec.lot_id.name == self.search_serial:
                                        print("second ----")
                                        rec.update(list1)
                                        print("after update")
                                        res = rec.onchange_serial_number()
                                        print("onchange")
                                        if res:
                                            return res
                                        rec.compute_done_from_serial()
                                        done = True
                                        break
                                if not done:
                                    for rec in self.move_line_ids:
                                        print("======------======")
                                        if rec.qty_done < 1.0:
                                            rec.update(list1)
                                            print("======------======","afterupdate")
                                            res = rec.onchange_serial_number()
                                            print("afer on chanage")
                                            if res:
                                                return res

                                            rec.compute_done_from_serial()
                                            print("after compute")
                                            break
                            elif self.search_serial not in list:
                                raise ValidationError('Serial you entered does not exist in Returned serials!')
                            print("bedore serial")
                            self.search_serial = ''
                            print("after remove")
                        # else:
                        #     list4 = {
                        #         # 'product_id': self.product_id.id,
                        #         'generated_serial': bb,
                        #         # 'lot_id':check.id,
                        #         'brand': self.product_id.brand,
                        #         'category': self.product_id.category,
                        #         'product_uom_id': self.product_uom.id,
                        #         # 'location_id': self.location_id.id,
                        #         # 'location_dest_id': self.location_select.id,
                        #         'qty_done': 1,
                        #     }
                        #     list = []
                        #     for rec in self.move_line_ids:
                        #         list.append(rec.lot_id.name)
                        #         if ((rec.lot_id.name == self.search_serial) and rec.qty_done > 0):
                        #             raise ValidationError('this serial scanned before')
                        #         elif (rec.lot_id.name == self.search_serial):
                        #             rec.update(list4)
                        #
                        #     if self.search_serial not in list:
                        #         raise ValidationError('Serial you entered does not exist in move lines!')
                        #     self.search_serial = ''

                    elif self.is_pick == True:
                        if self.location_source:
                            product_location = self.env['stock.quant'].search(
                                [('product_id', '=', self.product_id.id), ('lot_id', '=', check.id),
                                 ('location_id', '=', self.location_source.id), ('quantity', '=', 1),
                                 ])
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
        #     self.search_serial=''
        #     # if self.search_serial not in list:
        #     #     raise ValidationError('Serial you entered does not exist!')
        #     # elif self.search_serial in list:
        #     #     raise ValidationError('Serial you entered already scanned!')

    @api.multi
    @api.depends('picking_id')
    def do_print_(self):
        for rec in self:
            rec.picking_id.do_pr_picking()

    @api.multi
    @api.depends('product_uom_qty', 'product_id')
    def compute_return_ratio(self):
        for rec in self:
            if rec.product_uom_qty and rec.product_id:
                # pass
                rec.return_ratio = rec.product_uom_qty * rec.product_id.uom_id.factor_inv

    @api.multi
    @api.depends('move_line_ids', 'is_return', 'search_serial')
    def compute_all_reasons(self):
        for rec in self:
            if rec.is_return == True:
                mylist = []
                for line in rec.move_line_ids:
                    print("mylist",mylist)
                    if line.reason:
                        mylist.append(line.reason.id)
                        print("append ",line.reason.name)
                rec.reason = mylist


class PickingStockTransferInherit(models.Model):
    _inherit = "stock.picking"

    origin_return = fields.Char('Source Document Return')
    code_pick = fields.Selection([('incoming', 'Vendors'), ('outgoing', 'Customers'), ('internal', 'Internal')],
                                 'Type of Operation', related='picking_type_id.code')
    sum_initial = fields.Float(compute='cal_total_initial_demand')
    hide_return = fields.Boolean()
    hide_credit_button = fields.Boolean()
    is_po = fields.Boolean(compute='cal_po_or_so_return')
    is_so = fields.Boolean(compute='cal_po_or_so_return')

    @api.multi
    @api.depends('is_return', 'origin_return')
    def cal_po_or_so_return(self):
        for rec in self:
            if rec.is_return == True:
                if rec.origin_return:
                    if rec.origin_return.startswith('P'):
                        rec.is_po = True
                        rec.is_so = False
                    if rec.origin_return.startswith('S'):
                        rec.is_so = True
                        rec.is_po = False

    @api.multi
    @api.onchange('hide_return', 'origin', 'is_return', 'origin_return', 'state')
    def do_pr_picking(self):
        if self.is_return == True:
            mm = self.origin.split('Return of ')
            ww = mm[1]
            check = self.env['stock.picking'].search(
                [('origin', '=', self.origin_return), ('state', '=', 'done'),
                 (('name', '=', ww))])
            # ('code', '=', 'outgoing')
            if check:
                for line in check.move_ids_without_package:
                    for rec in self.move_ids_without_package:
                        if line.product_id.id == rec.product_id.id:
                            rec.returned_serials = line.filter_serials

            else:
                print('no')

    def action_inv(self):
        for rec in self:
            if rec.is_po == True:
                check_po = self.env['purchase.order'].search(
                    [('name', '=', rec.origin_return)])
                if check_po:
                    for line in check_po.order_line:
                        for record in rec.move_ids_without_package:
                            if line.product_id.id == record.product_id.id:
                                vals = {
                                    'price_unit': line.price_unit,
                                }
                                record.update(vals)
            elif rec.is_so == True:
                check_so = self.env['sale.order'].search(
                    [('name', '=', rec.origin_return)])
                if check_so:
                    for line in check_so.order_line:
                        for record in rec.move_ids_without_package:
                            if line.product_id.id == record.product_id.id:
                                vals = {
                                    'price_unit': line.price_unit,
                                }
                                record.update(vals)
        return {
            'name': 'Credit Note',
            'type': 'ir.actions.act_window',
            'res_model': 'wiz.data',
            'view_mode': 'form',
            'view_type': 'form',
            # 'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
            'context': {'default_origin': self.origin_return, 'default_partner_id': self.partner_id.id,
                        'default_picking_id': self.id, 'default_is_po': self.is_po, 'default_is_so': self.is_so},
            # 'key': self.id

        }

    @api.one
    @api.depends('move_ids_without_package')
    def cal_total_initial_demand(self):
        for line in self.move_ids_without_package:
            self.sum_initial = self.sum_initial + line.product_uom_qty

    @api.multi
    def action_done(self):
        """Changes picking state to done by processing the Stock Moves of the Picking

        Normally that happens when the button "Done" is pressed on a Picking view.
        @return: True
        """
        # TDE FIXME: remove decorator when migration the remaining
        todo_moves = self.mapped('move_lines').filtered(
            lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
        # Check if there are ops not linked to moves yet
        for pick in self:
            # # Explode manually added packages
            # for ops in pick.move_line_ids.filtered(lambda x: not x.move_id and not x.product_id):
            #     for quant in ops.package_id.quant_ids: #Or use get_content for multiple levels
            #         self.move_line_ids.create({'product_id': quant.product_id.id,
            #                                    'package_id': quant.package_id.id,
            #                                    'result_package_id': ops.result_package_id,
            #                                    'lot_id': quant.lot_id.id,
            #                                    'owner_id': quant.owner_id.id,
            #                                    'product_uom_id': quant.product_id.uom_id.id,
            #                                    'product_qty': quant.qty,
            #                                    'qty_done': quant.qty,
            #                                    'location_id': quant.location_id.id, # Could be ops too
            #                                    'location_dest_id': ops.location_dest_id.id,
            #                                    'picking_id': pick.id
            #                                    }) # Might change first element
            # # Link existing moves or add moves when no one is related
            for ops in pick.move_line_ids.filtered(lambda x: not x.move_id):
                # Search move with this product
                moves = pick.move_lines.filtered(lambda x: x.product_id == ops.product_id)
                moves = sorted(moves, key=lambda m: m.quantity_done < m.product_qty, reverse=True)
                if moves:
                    ops.move_id = moves[0].id
                else:
                    new_move = self.env['stock.move'].create({
                        'name': _('New Move:') + ops.product_id.display_name,
                        'product_id': ops.product_id.id,
                        'product_uom_qty': ops.qty_done,
                        'product_uom': ops.product_uom_id.id,
                        'location_id': pick.location_id.id,
                        'location_dest_id': pick.location_dest_id.id,
                        'picking_id': pick.id,
                        'picking_type_id': pick.picking_type_id.id,
                    })
                    ops.move_id = new_move.id
                    new_move = new_move._action_confirm()
                    todo_moves |= new_move
                    # 'qty_done': ops.qty_done})
        todo_moves._action_done()
        self.write({'date_done': fields.Datetime.now()})
        if self.is_return == True:
            mm = self.origin.split('Return of ')
            ww = mm[1]
            check = self.env['stock.picking'].search(
                [('origin', '=', self.origin_return), ('code', '=', 'incoming'), ('state', '=', 'done'),
                 (('name', '=', ww))])
            return_check = self.env['stock.picking'].search(
                [('origin', '=', self.origin), ('state', '!=', 'cancel')])
            list = []
            if check:
                if return_check:
                    for rec in return_check:
                        list.append(rec.sum_initial)
                    total = sum(list)

                    if total == check.sum_initial:
                        check.hide_return = True
                    elif total + self.sum_initial == check.sum_initial:
                        check.hide_return = True
                else:
                    print('no return check')
            else:
                print('no check')
            check_po = self.env['purchase.order'].search(
                [('name', '=', self.origin_return)])
            if check_po:
                po = []
                pick = []
                result = []
                for line in check_po.order_line:
                    # dict1={
                    #     'product_id': line.product_id.id,
                    #     'returned_quantity': line.returned_quantity,
                    #
                    # }
                    po.append({
                        'product_id': line.product_id.id,
                        'returned_quantity': line.returned_quantity,
                    })
                for rec in self.move_ids_without_package:
                    pick.append({
                        'product_id': rec.product_id.id,
                        'quantity_done': rec.quantity_done,
                    })
                for p in po:
                    for pic in pick:
                        if p['product_id'] == pic['product_id']:
                            result.append({
                                'product_id': p['product_id'],
                                'returned_quantity': p['returned_quantity'] + pic['quantity_done'],
                            })
                dict1 = {}
                for item in result:
                    # returned_quantity = item['returned_quantity']
                    dict1[item['product_id']] = item['returned_quantity']
                    # dict1['returned_quantity'] = item['returned_quantity']
                for line in check_po.order_line:
                    if line.product_id.id == line.product_id.id in dict1 and dict1[line.product_id.id]:
                        line.returned_quantity = dict1[line.product_id.id]

                inv_case1 = self.env['account.invoice'].search(
                    [('origin', '=', self.origin_return), ('state', '=', 'draft')])
                inv_case2 = self.env['account.invoice'].search(
                    [('origin', '=', self.origin_return), ('state', 'in', ('open', 'paid', 'in_payment'))])
                inv_case_so = self.env['account.invoice'].search(
                    [('origin', '=', self.origin_return)], limit=1)
                if self.is_po == True:
                    if inv_case1:
                        for inv in inv_case1:
                            for line in inv.invoice_line_ids:
                                for rec in check_po.order_line:
                                    if line.product_id.id == rec.product_id.id:
                                        line.quantity = rec.qty_received
                    elif inv_case2:
                        self.hide_credit_button = True
                    # raise ValidationError(
                    #     'there is a non draft invoice exist for this po!! you should ask for credit note')
                    # continue
                    # self.action_inv()
                    # return {
                    #     'name': 'Company Invoice',
                    #     'type': 'ir.actions.act_window',
                    #     'res_model': 'wiz.data',
                    #     'view_mode': 'form',
                    #     'view_type': 'form',
                    #     # 'res_id': self.id,
                    #     'views': [(False, 'form')],
                    #     'target': 'new',
                    #     # 'context': {'default_so_id': self.id, 'default_partner_id': self.partner_id.id},
                    #     # 'key': self.id
                    #
                    # }
                    # for inv in inv_case1:
                    #     for line in inv.invoice_line_ids:
                    #         for rec in check_po.order_line:
                    #             if line.product_id.id == rec.product_id.id:

                    #                 line.quantity = rec.qty_received
                elif self.is_so == True:
                    if inv_case_so:
                        self.hide_credit_button = True

        return True


class StockPickingReturnInherit(models.TransientModel):
    _inherit = "stock.return.picking"

    right_check = fields.Boolean()

    # seq = fields.Char('Seq')

    # @api.model
    # def default_get(self, fields):
    #     if len(self.env.context.get('active_ids', list())) > 1:
    #         raise UserError(_("You may only return one picking at a time."))
    #     res = super(StockPickingReturnInherit, self).default_get(fields)
    #
    #     move_dest_exists = False
    #     product_return_moves = []
    #     picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
    #     if picking:
    #         res.update({'picking_id': picking.id})
    #         if picking.state != 'done':
    #             raise UserError(_("You may only return Done pickings."))
    #         # In case we want to set specific default values (e.g. 'to_refund'), we must fetch the
    #         # default values for creation.
    #         line_fields = [f for f in self.env['stock.return.picking.line']._fields.keys()]
    #         product_return_moves_data_tmpl = self.env['stock.return.picking.line'].default_get(line_fields)
    #         for move in picking.move_lines:
    #             if move.state == 'cancel':
    #                 continue
    #             if move.scrapped:
    #                 continue
    #             if move.move_dest_ids:
    #                 move_dest_exists = True
    #             quantity = move.product_qty - sum(
    #                 move.move_dest_ids.filtered(lambda m: m.state in ['partially_available', 'assigned', 'done']). \
    #                 mapped('move_line_ids').mapped('product_qty'))
    #             quantity = float_round(quantity, precision_rounding=move.product_id.uom_id.rounding)
    #             product_return_moves_data = dict(product_return_moves_data_tmpl)
    #             product_return_moves_data.update({
    #                 'product_id': move.product_id.id,
    #                 'quantity': quantity,
    #                 'move_id': move.id,
    #                 'uom_id': move.product_id.uom_id.id,
    #                 'returned_serials': move.filter_serials.ids,
    #             })
    #             product_return_moves.append((0, 0, product_return_moves_data))
    #
    #         if not product_return_moves:
    #             raise UserError(
    #                 _("No products to return (only lines in Done state and not fully returned yet can be returned)."))
    #         if 'product_return_moves' in fields:
    #             res.update({'product_return_moves': product_return_moves})
    #         if 'move_dest_exists' in fields:
    #             res.update({'move_dest_exists': move_dest_exists})
    #         if 'parent_location_id' in fields and picking.location_id.usage == 'internal':
    #             res.update({
    #                            'parent_location_id': picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.view_location_id.id or picking.location_id.location_id.id})
    #         if 'original_location_id' in fields:
    #             res.update({'original_location_id': picking.location_id.id})
    #         if 'location_id' in fields:
    #             location_id = picking.location_id.id
    #             if picking.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
    #                 location_id = picking.picking_type_id.return_picking_type_id.default_location_dest_id.id
    #             res['location_id'] = location_id
    #     return res

    def _create_returns(self):
        # TODO sle: the unreserve of the next moves could be less brutal
        for return_move in self.product_return_moves.mapped('move_id'):
            return_move.move_dest_ids.filtered(lambda m: m.state not in ('done', 'cancel'))._do_unreserve()

        # create new picking for returned products
        picking_type_id = self.picking_id.picking_type_id.return_picking_type_id.id or self.picking_id.picking_type_id.id
        new_picking = self.picking_id.copy({
            'move_lines': [],
            'picking_type_id': picking_type_id,
            'state': 'draft',
            'origin': _("Return of %s") % self.picking_id.name,
            'origin_return': self.picking_id.origin,
            'location_id': self.picking_id.location_dest_id.id,
            'location_dest_id': self.location_id.id})
        new_picking.message_post_with_view('mail.message_origin_link',
                                           values={'self': new_picking, 'origin': self.picking_id},
                                           subtype_id=self.env.ref('mail.mt_note').id)
        returned_lines = 0
        for return_line in self.product_return_moves:
            if not return_line.move_id:
                raise UserError(_("You have manually created product lines, please delete them to proceed."))
            # TODO sle: float_is_zero?
            # <<<<<<< HEAD
            #             # if return_line.quantity:
            #             if return_line.is_return == True:
            #                 if return_line.quantity > return_line.move_id.product_uom_qty:
            #                     raise ValidationError('Quantity can not be greater than initial demand')
            #                 else:
            #                         returned_lines += 1
            #                         vals = self._prepare_move_default_values(return_line, new_picking)
            #                         r = return_line.move_id.copy(vals)
            #                         vals = {}
            #
            #                         # +--------------------------------------------------------------------------------------------------------+
            #                         # |       picking_pick     <--Move Orig--    picking_pack     --Move Dest-->   picking_ship
            #                         # |              | returned_move_ids              ↑                                  | returned_move_ids
            #                         # |              ↓                                | return_line.move_id              ↓
            #                         # |       return pick(Add as dest)          return toLink                    return ship(Add as orig)
            #                         # +--------------------------------------------------------------------------------------------------------+
            #                         move_orig_to_link = return_line.move_id.move_dest_ids.mapped('returned_move_ids')
            #                         # link to original move
            #                         move_orig_to_link |= return_line.move_id
            #                         # link to siblings of original move, if any
            #                         move_orig_to_link |= return_line.move_id \
            #                             .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel')) \
            #                             .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel'))
            #                         move_dest_to_link = return_line.move_id.move_orig_ids.mapped('returned_move_ids')
            #                         # link to children of originally returned moves, if any. Note that the use of
            #                         # 'return_line.move_id.move_orig_ids.returned_move_ids.move_orig_ids.move_dest_ids'
            #                         # instead of 'return_line.move_id.move_orig_ids.move_dest_ids' prevents linking a
            #                         # return directly to the destination moves of its parents. However, the return of
            #                         # the return will be linked to the destination moves.
            #                         move_dest_to_link |= return_line.move_id.move_orig_ids.mapped('returned_move_ids') \
            #                             .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel')) \
            #                             .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel'))
            #                         vals['move_orig_ids'] = [(4, m.id) for m in move_orig_to_link]
            #                         vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
            #                         r.write(vals)
            #                         check_lines = self.env['stock.picking'].search(
            #                             [('origin', '=', self.picking_id.origin),('code_pick','=','internal')])
            #                         for check in check_lines:
            #                             for line in check.move_ids_without_package:
            #                                 if line.product_id == return_line.product_id:
            #                                     vals = {
            #                                         # 'product_id': return_line.product_id.id,
            #                                         # 'reason': return_line.reason.id,
            #                                         'product_uom_qty': line.product_uom_qty-return_line.quantity,
            #                                         'product_uom': return_line.product_id.uom_id.id,
            #                                         # 'picking_id': new_picking.id,
            #                                         # 'state': 'draft',
            #                                         # 'date_expected': fields.Datetime.now(),
            #                                         # 'location_id': return_line.move_id.location_dest_id.id,
            #                                         # 'location_dest_id': self.location_id.id or return_line.move_id.location_id.id,
            #                                         # 'picking_type_id': new_picking.picking_type_id.id,
            #                                         # 'warehouse_id': self.picking_id.picking_type_id.warehouse_id.id,
            #                                         # 'origin_returned_move_id': return_line.move_id.id,
            #                                         # 'procure_method': 'make_to_stock',
            #                                     }
            #                                     line.update(vals)
            #                                     break
            #             else:
            #                 raise ValidationError(_("Please check at least one line to return."))
            # =======
            if return_line.is_return == True:
                self.right_check = True
                if return_line.quantity:
                    if return_line.quantity > return_line.move_id.product_uom_qty:
                        raise ValidationError('Quantity can not be greater than initial demand')
                    else:
                        returned_lines += 1
                        vals = self._prepare_move_default_values(return_line, new_picking)
                        r = return_line.move_id.copy(vals)
                        vals = {}

                        # +--------------------------------------------------------------------------------------------------------+
                        # |       picking_pick     <--Move Orig--    picking_pack     --Move Dest-->   picking_ship
                        # |              | returned_move_ids              ↑                                  | returned_move_ids
                        # |              ↓                                | return_line.move_id              ↓
                        # |       return pick(Add as dest)          return toLink                    return ship(Add as orig)
                        # +--------------------------------------------------------------------------------------------------------+
                        move_orig_to_link = return_line.move_id.move_dest_ids.mapped('returned_move_ids')
                        # link to original move
                        move_orig_to_link |= return_line.move_id
                        # link to siblings of original move, if any
                        move_orig_to_link |= return_line.move_id \
                            .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel')) \
                            .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel'))
                        move_dest_to_link = return_line.move_id.move_orig_ids.mapped('returned_move_ids')
                        # link to children of originally returned moves, if any. Note that the use of
                        # 'return_line.move_id.move_orig_ids.returned_move_ids.move_orig_ids.move_dest_ids'
                        # instead of 'return_line.move_id.move_orig_ids.move_dest_ids' prevents linking a
                        # return directly to the destination moves of its parents. However, the return of
                        # the return will be linked to the destination moves.
                        move_dest_to_link |= return_line.move_id.move_orig_ids.mapped('returned_move_ids') \
                            .mapped('move_orig_ids').filtered(lambda m: m.state not in ('cancel')) \
                            .mapped('move_dest_ids').filtered(lambda m: m.state not in ('cancel'))
                        vals['move_orig_ids'] = [(4, m.id) for m in move_orig_to_link]
                        vals['move_dest_ids'] = [(4, m.id) for m in move_dest_to_link]
                        r.write(vals)
                        check = self.env['stock.picking'].search(
                            [('origin', '=', self.picking_id.origin), ('code_pick', '=', 'internal')])
                        check_lines = self.env['stock.picking'].search(
                            [('origin', '=', self.picking_id.origin), ('code_pick', '=', 'internal')])
                        for check in check_lines:

                            if check:
                                for line in check.move_ids_without_package:
                                    if line.product_id == return_line.product_id:
                                        vals = {
                                            # 'product_id': return_line.product_id.id,
                                            # 'reason': return_line.reason.id,
                                            'product_uom_qty': line.product_uom_qty - return_line.quantity,
                                            'product_uom': return_line.product_id.uom_id.id,
                                            # 'picking_id': new_picking.id,
                                            # 'state': 'draft',
                                            # 'date_expected': fields.Datetime.now(),
                                            # 'location_id': return_line.move_id.location_dest_id.id,
                                            # 'location_dest_id': self.location_id.id or return_line.move_id.location_id.id,
                                            # 'picking_type_id': new_picking.picking_type_id.id,
                                            # 'warehouse_id': self.picking_id.picking_type_id.warehouse_id.id,
                                            # 'origin_returned_move_id': return_line.move_id.id,
                                            # 'procure_method': 'make_to_stock',
                                        }
                                        line.update(vals)
        if self.right_check == False:
            raise ValidationError(_("Please check at least one line to return."))
        # >>>>>>> 0ece8c16465a55cad4d182b75fb15cdbc40f1754
        if not returned_lines:
            raise UserError(_("Please specify at least one non-zero quantity."))

        new_picking.action_confirm()
        new_picking.action_assign()
        return new_picking.id, picking_type_id

    def _prepare_move_default_values(self, return_line, new_picking):
        vals = {
            'product_id': return_line.product_id.id,
            # 'reason': return_line.reason.id,
            'product_uom_qty': return_line.quantity,
            'product_uom': return_line.product_id.uom_id.id,
            'picking_id': new_picking.id,
            'state': 'draft',
            'date_expected': fields.Datetime.now(),
            'location_id': return_line.move_id.location_dest_id.id,
            'location_dest_id': self.location_id.id or return_line.move_id.location_id.id,
            'picking_type_id': new_picking.picking_type_id.id,
            'warehouse_id': self.picking_id.picking_type_id.warehouse_id.id,
            'origin_returned_move_id': return_line.move_id.id,
            'procure_method': 'make_to_stock',
            'to_refund': return_line.to_refund,
            'returned_serials': return_line.move_id.filter_serials.ids,
        }
        return vals


class StockPickingReturnLineInherit(models.TransientModel):
    _inherit = "stock.return.picking.line"

    # product_id = fields.Many2one('product.product', string="Product", required=True,domain=False)
    # uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id', readonly=False)
    # seq = fields.Integer('Seq',related='wizard_id.id')
    reason = fields.Many2one('return.reason', string='Reason', copy=True)
    is_return = fields.Boolean(string='Return')
    to_refund = fields.Boolean(string="To Refund (update SO/PO)", default=True,
                               help='Trigger a decrease of the delivered/received quantity in the associated Sale Order/Purchase Order')
    # move_id = fields.Many2one('stock.move', "Move",compute='cal_move_id_from_product')
    # returned_serials = fields.Many2many('stock.production.lot',string='Returned Serials')

    # @api.multi
    # @api.depends('product_id')
    # def cal_move_id_from_product(self):
    #     for line in self:
    #         if not line.move_id:
    #             check = self.env['stock.return.picking.line'].search(
    #                 [('product_id', '=', line.product_id.id), ('wizard_id', '=',self.wizard_id.id)],limit=1)
    #             if check:
    #                 for ss in check:
    #
    #                     line.move_id = ss.move_id
    #                 break
    #
    #             else:
    #


class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order.line"

    returned_quantity = fields.Float(string='Returned Quantity')
    sale_uom_id = fields.Many2one('uom.uom', 'Sales UOM',related='product_id.uom_id')

    # @api.multi
    # @api.depends('product_qty','qty_received')
    # def cal_returned_quantity(self):
    #     for rec in self:
    #         if rec.product_qty and rec.qty_received:
    #             rec.returned_quantity =rec.product_qty - rec.qty_received


class StockPickingReturnReasonInherit(models.Model):
    _name = 'return.reason'

    name = fields.Char(string='Name')
    ss = fields.Many2many('reason.reason', string='SS')

    # @api.multi
    # @api.depends('ss')
    # def collect_reasons(self):
    #     list= []
    #     for line in self:
    #         for rec in line.ss:
    #             list.append(rec.name)
    #
    #         sent_str = ""
    #         for i in list:
    #             sent_str += str(i) + "-"
    #         sent_str = sent_str[:-1]
    #
    #         line.name = sent_str


class StockurnReasonInherit(models.Model):
    _name = 'reason.reason'

    name = fields.Char('Name')

from odoo import api, fields, models
from odoo.tools import float_round


class StockMoveBuluxpppIking(models.Model):
    _inherit = 'stock.move'


    res_res = fields.Float()

    # def _run_valuation(self, quantity=None):
    #     self.ensure_one()
    #     value_to_return = 0
    #     if self._is_in():
    #         valued_move_lines = self.move_line_ids.filtered(lambda ml: not ml.location_id._should_be_valued() and ml.location_dest_id._should_be_valued() and not ml.owner_id)
    #         valued_quantity = 0
    #         for valued_move_line in valued_move_lines:
    #             valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, self.product_id.uom_id)
    #
    #         # Note: we always compute the fifo `remaining_value` and `remaining_qty` fields no
    #         # matter which cost method is set, to ease the switching of cost method.
    #         vals = {}
    #         price_unit = self._get_price_unit()
    #         value = price_unit * (quantity or valued_quantity)
    #         value_to_return = value if quantity is None or not self.value else self.value
    #         vals = {
    #             'price_unit': price_unit,
    #             'value': value_to_return,
    #             'remaining_value': value if quantity is None else self.remaining_value + value,
    #         }
    #         vals['remaining_qty'] = valued_quantity if quantity is None else self.remaining_qty + quantity
    #
    #         if self.product_id.cost_method == 'standard':
    #             value = self.product_id.standard_price * (quantity or valued_quantity)
    #             value_to_return = value if quantity is None or not self.value else self.value
    #             vals.update({
    #                 'price_unit': self.product_id.standard_price,
    #                 'value': value_to_return,
    #             })
    #         self.write(vals)
    #     elif self._is_out():
    #         valued_move_lines = self.move_line_ids.filtered(lambda ml: ml.location_id._should_be_valued() and not ml.location_dest_id._should_be_valued() and not ml.owner_id)
    #         valued_quantity = 0
    #         for valued_move_line in valued_move_lines:
    #             valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, self.product_id.uom_id)
    #         value_to_return = self.env['stock.move']._run_fifo(self, quantity=quantity)
    #         if self.product_id.cost_method in ['standard', 'average']:
    #             curr_rounding = self.company_id.currency_id.rounding
    #             value = -float_round(self.product_id.standard_price * (valued_quantity if quantity is None else quantity), precision_rounding=curr_rounding)
    #             value_to_return = value if quantity is None else self.value + value
    #             if valued_quantity == 0 :
    #                 self.write({
    #                     'value': value_to_return,
    #                     'price_unit': 0,
    #                 })
    #             else:
    #                 self.write({
    #                     'value': value_to_return,
    #                     'price_unit': value / valued_quantity or 0,
    #                 })
    #     elif self._is_dropshipped() or self._is_dropshipped_returned():
    #         curr_rounding = self.company_id.currency_id.rounding
    #         if self.product_id.cost_method in ['fifo']:
    #             price_unit = self._get_price_unit()
    #             # see test_dropship_fifo_perpetual_anglosaxon_ordered
    #             self.product_id.standard_price = price_unit
    #         else:
    #             price_unit = self.product_id.standard_price
    #         value = float_round(self.product_qty * price_unit, precision_rounding=curr_rounding)
    #         value_to_return = value if self._is_dropshipped() else -value
    #         # In move have a positive value, out move have a negative value, let's arbitrary say
    #         # dropship are positive.
    #         self.write({
    #             'value': value_to_return,
    #             'price_unit': price_unit if self._is_dropshipped() else -price_unit,
    #         })
    #     return value_to_return

    # @api.multi
    # def fff(self):
    #     for  rec in self.move_line_ids:
    #         if rec.qty_done <1:
    #             rec.unlink()

    # @api.multi
    # @api.depends('move_line_ids.product_qty')
    # def _compute_reserved_availability(self):
    #     """ Fill the `availability` field on a stock move, which is the actual reserved quantity
    #     and is represented by the aggregated `product_qty` on the linked move lines. If the move
    #     is force assigned, the value will be 0.
    #     """
    #     result = {data['move_id'][0]: data['product_qty'] for data in
    #               self.env['stock.move.line'].read_group([('move_id', 'in', self.ids)], ['move_id', 'product_qty'],
    #                                                      ['move_id'])}
    #     for rec in self:
    #         if rec.res_res ==0:
    #             rec.reserved_availability=0
    #         else:
    #          rec.reserved_availability = rec.product_id.uom_id._compute_quantity(result.get(rec.id, 0.0),
    #                                                                             rec.product_uom,
    #                                                                             rounding_method='HALF-UP')


class StockMoveLineBuluxppp(models.Model):
    _inherit = 'stock.move.line'


    # @api.one
    # @api.depends('product_id', 'product_uom_id', 'product_uom_qty')
    # def _compute_product_qty(self):
    #     if self.generated_serial==0:
    #         self.product_qty = 0
    #         self.product_uom_qty = 0
    #         self.qty_done=0
    #     else:
    #      self.product_qty = self.product_uom_id._compute_quantity(self.product_uom_qty, self.product_id.uom_id, rounding_method='HALF-UP')


class StockpickingBuluxpppIking(models.Model):
    _inherit = 'stock.picking'

    user_id = fields.Many2one('res.users',string='User')

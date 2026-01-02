from odoo import api, fields, models


class TMSOrder(models.Model):
    _inherit = "tms.order"

    stop_ids = fields.One2many(
        "tms.order.stop",
        "order_id",
        string="Delivery Stops",
        help="Multiple delivery stops for this order",
    )
    total_weight = fields.Float(
        compute="_compute_totals",
        store=True,
    )
    total_volume = fields.Float(
        compute="_compute_totals",
        store=True,
    )
    total_stops = fields.Integer(
        compute="_compute_totals",
        store=True,
    )
    estimated_total_time = fields.Float(
        string="Estimated Total Time (hours)",
        compute="_compute_estimated_time",
        store=False,
    )

    @api.depends("stop_ids", "stop_ids.weight", "stop_ids.volume")
    def _compute_totals(self):
        for order in self:
            order.total_weight = sum(order.stop_ids.mapped("weight"))
            order.total_volume = sum(order.stop_ids.mapped("volume"))
            order.total_stops = len(order.stop_ids)

    @api.depends("stop_ids", "stop_ids.unloading_time")
    def _compute_estimated_time(self):
        for order in self:
            total_unloading_time = sum(order.stop_ids.mapped("unloading_time"))
            # Convert minutes to hours
            order.estimated_total_time = total_unloading_time / 60.0

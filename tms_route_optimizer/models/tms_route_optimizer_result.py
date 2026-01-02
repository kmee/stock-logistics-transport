from odoo import fields, models


class TMSRouteOptimizerResult(models.TransientModel):
    _name = "tms.route.optimizer.result"
    _description = "TMS Route Optimizer Result"

    optimizer_id = fields.Many2one(
        "tms.route.optimizer",
        string="Optimizer",
        required=True,
        ondelete="cascade",
    )
    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="Vehicle",
        required=True,
    )
    vehicle_type_id = fields.Many2one(
        "fleet.vehicle.type",
        related="vehicle_id.vehicle_type_id",
        string="Vehicle Type",
        readonly=True,
    )
    order_id = fields.Many2one(
        "tms.order",
        string="Created Order",
    )
    stop_ids = fields.Many2many(
        "tms.order.stop",
        string="Delivery Stops",
    )
    stop_count = fields.Integer()
    total_distance = fields.Float(
        string="Total Distance (km)",
    )
    total_time = fields.Float(
        string="Total Time (hours)",
    )
    total_weight = fields.Float(
        string="Total Weight (kg)",
    )
    total_volume = fields.Float(
        string="Total Volume (m³)",
    )
    weight_utilization = fields.Float(
        string="Weight Utilization (%)",
    )
    volume_utilization = fields.Float(
        string="Volume Utilization (%)",
    )
    route_cost = fields.Float()
    cost_per_km = fields.Float(
        string="Cost per KM",
    )
    google_maps_url = fields.Char(
        string="Google Maps URL",
    )
    waze_url = fields.Char(
        string="Waze URL",
    )
    route_sequence = fields.Text(
        string="Route Sequence (JSON)",
    )

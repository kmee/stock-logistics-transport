from odoo import api, fields, models


class TMSOrderStop(models.Model):
    _name = "tms.order.stop"
    _description = "TMS Order Delivery Stop"
    _order = "order_id, sequence"

    order_id = fields.Many2one(
        "tms.order",
        string="Order",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(
        default=10,
        help="Order of the stop in the route",
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Delivery Partner",
        required=True,
        help="Recipient of the delivery",
    )
    weight = fields.Float(
        help="Weight of the delivery",
    )
    weight_uom_id = fields.Many2one(
        "uom.uom",
        string="Weight UoM",
        domain=[("category_id.name", "=", "Weight")],
        help="Unit of measure for weight",
    )
    volume = fields.Float(
        help="Volume of the delivery",
    )
    volume_uom_id = fields.Many2one(
        "uom.uom",
        string="Volume UoM",
        domain=[("category_id.name", "=", "Volume")],
        help="Unit of measure for volume",
    )
    unloading_time = fields.Float(
        string="Unloading Time (minutes)",
        default=30,
        help="Minimum unloading time in minutes",
    )
    scheduled_date = fields.Datetime(
        help="Scheduled delivery date/time",
    )
    latitude = fields.Float(
        related="partner_id.partner_latitude",
        string="Latitude",
        readonly=True,
    )
    longitude = fields.Float(
        related="partner_id.partner_longitude",
        string="Longitude",
        readonly=True,
    )
    address_complete = fields.Char(
        string="Complete Address",
        compute="_compute_address_complete",
        store=False,
    )
    display_address = fields.Char(
        compute="_compute_address_complete",
        store=False,
        help="Address formatted for display in map view",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("scheduled", "Scheduled"),
            ("delivered", "Delivered"),
            ("skipped", "Skipped"),
        ],
        default="draft",
    )

    @api.depends("partner_id", "order_id", "sequence")
    def _compute_display_name(self):
        for stop in self:
            if stop.partner_id:
                name_parts = []
                if stop.order_id:
                    name_parts.append(stop.order_id.name)
                name_parts.append(f"Stop {stop.sequence}")
                name_parts.append(stop.partner_id.display_name)
                stop.display_name = " - ".join(name_parts)
            else:
                stop.display_name = f"Stop {stop.id}"

    @api.depends("partner_id")
    def _compute_address_complete(self):
        for stop in self:
            if stop.partner_id:
                address_parts = []
                if stop.partner_id.street:
                    address_parts.append(stop.partner_id.street)
                if stop.partner_id.street2:
                    address_parts.append(stop.partner_id.street2)
                if stop.partner_id.city:
                    address_parts.append(stop.partner_id.city)
                if stop.partner_id.state_id:
                    address_parts.append(stop.partner_id.state_id.name)
                if stop.partner_id.zip:
                    address_parts.append(stop.partner_id.zip)
                if stop.partner_id.country_id:
                    address_parts.append(stop.partner_id.country_id.name)
                address_str = ", ".join(address_parts)
                stop.address_complete = address_str
                stop.display_address = address_str
            else:
                stop.address_complete = ""
                stop.display_address = ""

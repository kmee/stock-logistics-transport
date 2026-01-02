import json
import time
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .tms_route_optimizer_ortools import RouteOptimizerHelper


class TMSRouteOptimizer(models.TransientModel):
    _name = "tms.route.optimizer"
    _description = "TMS Route Optimizer Wizard"

    name = fields.Char(
        default=lambda self: (
            f"Optimization {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        ),
    )
    team_id = fields.Many2one(
        "tms.team",
        string="Team",
        required=True,
    )
    date_from = fields.Datetime(
        required=True,
        default=fields.Datetime.now,
    )
    date_to = fields.Datetime(
        required=True,
        default=fields.Datetime.now,
    )
    delivery_stop_ids = fields.Many2many(
        "tms.order.stop",
        string="Delivery Stops",
        help="Stops to optimize (auto-filled based on date range)",
    )
    optimization_date = fields.Date(
        required=True,
        default=fields.Date.today,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("optimizing", "Optimizing"),
            ("done", "Done"),
            ("error", "Error"),
        ],
        default="draft",
    )
    optimization_result = fields.Text(
        string="Optimization Result (JSON)",
    )
    total_cost = fields.Float()
    total_distance = fields.Float(
        string="Total Distance (km)",
    )
    total_vehicles_used = fields.Integer()
    optimization_time = fields.Float(
        string="Optimization Time (seconds)",
    )
    result_ids = fields.One2many(
        "tms.route.optimizer.result",
        "optimizer_id",
        string="Results",
    )
    error_message = fields.Text()

    @api.onchange("team_id", "date_from", "date_to")
    def _onchange_dates(self):
        """Auto-fill delivery stops based on date range"""
        if self.team_id and self.date_from and self.date_to:
            stops = self.env["tms.order.stop"].search(
                [
                    ("scheduled_date", ">=", self.date_from),
                    ("scheduled_date", "<=", self.date_to),
                    ("order_id.tms_team_id", "=", self.team_id.id),
                    ("state", "=", "draft"),
                ]
            )
            self.delivery_stop_ids = stops

    def action_run_optimization(self):
        """Run the route optimization"""
        self.state = "optimizing"

        try:
            start_time = time.time()

            # Validate data
            if not self.delivery_stop_ids:
                raise UserError(_("No delivery stops to optimize"))

            if not self.team_id:
                raise UserError(_("Team is required"))

            # Check geolocation
            for stop in self.delivery_stop_ids:
                if not stop.latitude or not stop.longitude:
                    raise UserError(
                        _("Stop %s has no geolocation coordinates")
                        % stop.partner_id.name
                    )

            # Get vehicles for team, filtered by allowed vehicle types
            vehicle_domain = [("tms_team_id", "=", self.team_id.id)]
            if self.team_id.allowed_vehicle_type_ids:
                vehicle_domain.append(
                    ("vehicle_type_id", "in", self.team_id.allowed_vehicle_type_ids.ids)
                )
            vehicles = self.env["fleet.vehicle"].search(vehicle_domain)

            if not vehicles:
                raise UserError(_("No vehicles available for this team"))

            # Prepare data for optimization
            depot_lat = (
                self.team_id.default_depot_location_id.partner_latitude or -23.5505
            )
            depot_lon = (
                self.team_id.default_depot_location_id.partner_longitude or -46.6333
            )

            locations = [(depot_lat, depot_lon)]  # Depot is first
            stop_weights = []
            stop_volumes = []
            stop_ids = []

            for stop in self.delivery_stop_ids:
                locations.append((stop.latitude, stop.longitude))
                stop_weights.append(stop.weight or 0)
                stop_volumes.append(stop.volume or 0)
                stop_ids.append(stop.id)

            # Calculate distance matrix
            distance_matrix = RouteOptimizerHelper.calculate_distance_matrix(locations)

            # Prepare vehicle data
            vehicle_capacities_weight = []
            vehicle_capacities_volume = []
            cost_per_km = []
            minimum_trip_cost = []

            for vehicle in vehicles:
                vehicle_capacities_weight.append(vehicle.weight_capacity or 1000)
                vehicle_capacities_volume.append(vehicle.volume_capacity or 10)
                cost_per_km.append(vehicle.cost_per_km or 5.0)
                minimum_trip_cost.append(vehicle.minimum_trip_cost or 100.0)

            # Get config parameters
            max_time = float(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("tms.route_optimizer.max_time_seconds", "300")
            )

            # Solve VRP
            solution = RouteOptimizerHelper.solve_vrp(
                distance_matrix,
                vehicle_capacities_weight,
                vehicle_capacities_volume,
                stop_weights,
                stop_volumes,
                cost_per_km,
                minimum_trip_cost,
                max_time_seconds=max_time,
            )

            if not solution:
                raise UserError(
                    _("No feasible solution found for the given constraints")
                )

            # Store results
            self.optimization_result = json.dumps(solution, indent=2)
            self.total_cost = solution["total_cost"]
            self.total_distance = solution["total_distance"]
            self.total_vehicles_used = solution["num_vehicles_used"]
            self.optimization_time = time.time() - start_time

            # Create result records
            for _route_idx, route in enumerate(solution["routes"]):
                vehicle = vehicles[route["vehicle_id"]]
                # Get stops in route order, preserving sequence
                route_stops = []
                for node in route["route"][1:-1]:  # Exclude depot (first and last)
                    stop_idx = node - 1  # Convert to stop index (0-based)
                    if 0 <= stop_idx < len(stop_ids):
                        stop_id = stop_ids[stop_idx]
                        stop = self.delivery_stop_ids.filtered(
                            lambda s, sid=stop_id: s.id == sid
                        )
                        if stop:
                            route_stops.append(stop[0])

                result = self.env["tms.route.optimizer.result"].create(
                    {
                        "optimizer_id": self.id,
                        "vehicle_id": vehicle.id,
                        "vehicle_type_id": vehicle.vehicle_type_id.id
                        if vehicle.vehicle_type_id
                        else False,
                        "stop_ids": [(6, 0, [s.id for s in route_stops])],
                        "stop_count": len(route_stops),
                        "total_distance": route["distance"],
                        "total_weight": route["weight"],
                        "total_volume": route["volume"],
                        "weight_utilization": (
                            (route["weight"] / vehicle.weight_capacity * 100)
                            if vehicle.weight_capacity
                            else 0
                        ),
                        "volume_utilization": (
                            (route["volume"] / vehicle.volume_capacity * 100)
                            if vehicle.volume_capacity
                            else 0
                        ),
                        "route_cost": route["cost"],
                        "cost_per_km": route["cost"] / route["distance"]
                        if route["distance"] > 0
                        else 0,
                    }
                )

                # Generate maps URLs
                route_coords = [locations[node] for node in route["route"]]
                result.google_maps_url = RouteOptimizerHelper.generate_google_maps_url(
                    route_coords
                )
                if route_coords:
                    # Use last coordinate as destination for Waze
                    last_lat, last_lon = route_coords[-1]
                    result.waze_url = RouteOptimizerHelper.generate_waze_url(
                        last_lat, last_lon
                    )

                # Store route sequence as JSON
                result.route_sequence = json.dumps(
                    [{"lat": lat, "lon": lon} for lat, lon in route_coords]
                )

            self.state = "done"

        except Exception as e:
            self.state = "error"
            self.error_message = str(e)
            raise UserError(_("Optimization failed: %s") % str(e)) from e

    def action_create_orders(self):
        """Create TMS orders from optimization results"""
        if self.state != "done":
            raise UserError(_("Optimization must be completed before creating orders"))

        created_orders = []

        for result in self.result_ids:
            if not result.stop_ids:
                continue

            # Create order first
            depot_location_id = False
            if self.team_id.default_depot_location_id:
                depot_location_id = self.team_id.default_depot_location_id.id
            order_vals = {
                "name": f"Route {result.vehicle_id.name} - {self.optimization_date}",
                "tms_team_id": self.team_id.id,
                "vehicle_id": result.vehicle_id.id,
                "depot_location_id": depot_location_id,
            }
            order = self.env["tms.order"].create(order_vals)

            # Create stops in sequence order (One2many relationship)
            # Get stops in the order they appear in result.stop_ids (already sorted)
            for seq, stop in enumerate(result.stop_ids, start=1):
                stop_vals = {
                    "order_id": order.id,
                    "partner_id": stop.partner_id.id,
                    "sequence": seq * 10,  # Use multiples of 10 for easier reordering
                    "weight": stop.weight,
                    "weight_uom_id": stop.weight_uom_id.id
                    if stop.weight_uom_id
                    else False,
                    "volume": stop.volume,
                    "volume_uom_id": stop.volume_uom_id.id
                    if stop.volume_uom_id
                    else False,
                    "unloading_time": stop.unloading_time,
                    "scheduled_date": stop.scheduled_date,
                    "state": "scheduled",
                }
                self.env["tms.order.stop"].create(stop_vals)

            # Update original stop states (if they had an order_id before)
            result.stop_ids.write({"state": "scheduled"})

            # Link result to created order
            result.order_id = order.id

            created_orders.append(order.id)

        # Return action to view created orders
        return {
            "type": "ir.actions.act_window",
            "name": "Created Orders",
            "res_model": "tms.order",
            "view_mode": "list,form",
            "domain": [("id", "in", created_orders)],
        }

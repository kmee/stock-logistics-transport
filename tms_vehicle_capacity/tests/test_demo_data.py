# Copyright (C) 2024 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestTMSVehicleCapacityDemo(TransactionCase):
    """Test TMS Vehicle Capacity using demo data"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Vehicle types
        cls.van_type = cls.env.ref("tms_vehicle_capacity.fleet_vehicle_type_van")
        cls.vuc_type = cls.env.ref("tms_vehicle_capacity.fleet_vehicle_type_vuc")
        cls.toco_type = cls.env.ref("tms_vehicle_capacity.fleet_vehicle_type_toco")
        # Demo vehicles
        cls.van_1 = cls.env.ref("tms_vehicle_capacity.demo_vehicle_van_1")
        cls.vuc_1 = cls.env.ref("tms_vehicle_capacity.demo_vehicle_vuc_1")
        cls.toco_1 = cls.env.ref("tms_vehicle_capacity.demo_vehicle_toco_1")
        # Demo teams
        cls.team_1 = cls.env.ref("tms.demo_team_1")
        cls.team_2 = cls.env.ref("tms.demo_team_2")
        # Brazil team
        cls.brazil_team = cls.env.ref("tms_route_optimizer.demo_team_brazil_small")

    def test_demo_vehicle_types_exist(self):
        """Test that demo vehicle types exist"""
        for vtype in [self.van_type, self.vuc_type, self.toco_type]:
            self.assertTrue(vtype)
            self.assertGreater(vtype.default_weight_capacity, 0)
            self.assertGreater(vtype.default_volume_capacity, 0)
            self.assertGreater(vtype.default_cost_per_km, 0)
            self.assertGreater(vtype.default_minimum_trip_cost, 0)

    def test_demo_vehicles_have_capacity(self):
        """Test that demo vehicles have capacity data"""
        for vehicle in [self.van_1, self.vuc_1, self.toco_1]:
            self.assertTrue(vehicle.vehicle_type_id)
            self.assertGreater(vehicle.weight_capacity, 0)
            self.assertGreater(vehicle.volume_capacity, 0)
            self.assertGreater(vehicle.cost_per_km, 0)
            self.assertGreater(vehicle.minimum_trip_cost, 0)

    def test_demo_vehicles_have_depot(self):
        """Test that demo vehicles have depot location"""
        for vehicle in [self.van_1, self.vuc_1, self.toco_1]:
            self.assertTrue(vehicle.depot_location_id)
            self.assertIsNotNone(vehicle.depot_location_id.partner_latitude)
            self.assertIsNotNone(vehicle.depot_location_id.partner_longitude)

    def test_demo_team_has_allowed_vehicle_types(self):
        """Test that demo teams have allowed vehicle types"""
        self.assertTrue(self.team_1.allowed_vehicle_type_ids)
        self.assertIn(self.van_type, self.team_1.allowed_vehicle_type_ids)
        self.assertIn(self.vuc_type, self.team_1.allowed_vehicle_type_ids)
        self.assertIn(self.toco_type, self.team_1.allowed_vehicle_type_ids)

    def test_demo_team_has_depot(self):
        """Test that demo teams have default depot"""
        self.assertTrue(self.team_1.default_depot_location_id)
        self.assertTrue(self.team_2.default_depot_location_id)

    def test_demo_brazil_team_exists(self):
        """Test that Brazil demo team exists"""
        self.assertTrue(self.brazil_team)
        self.assertIn("Brasil", self.brazil_team.name)
        self.assertTrue(self.brazil_team.allowed_vehicle_type_ids)

    def test_demo_brazil_team_vehicle_types(self):
        """Test that Brazil team only allows small vehicles"""
        self.assertIn(self.van_type, self.brazil_team.allowed_vehicle_type_ids)
        self.assertIn(self.vuc_type, self.brazil_team.allowed_vehicle_type_ids)
        self.assertNotIn(self.toco_type, self.brazil_team.allowed_vehicle_type_ids)

    def test_demo_brazil_vehicles_exist(self):
        """Test that Brazil demo vehicles exist"""
        brazil_van_1 = self.env.ref("tms_route_optimizer.demo_vehicle_brazil_van_1")
        brazil_van_2 = self.env.ref("tms_route_optimizer.demo_vehicle_brazil_van_2")
        brazil_vuc_1 = self.env.ref("tms_route_optimizer.demo_vehicle_brazil_vuc_1")
        self.assertTrue(brazil_van_1)
        self.assertTrue(brazil_van_2)
        self.assertTrue(brazil_vuc_1)
        self.assertEqual(brazil_van_1.tms_team_id, self.brazil_team)
        self.assertEqual(brazil_van_2.tms_team_id, self.brazil_team)
        self.assertEqual(brazil_vuc_1.tms_team_id, self.brazil_team)

    def test_demo_brazil_vehicles_capacity(self):
        """Test that Brazil vehicles have correct capacity"""
        brazil_van_1 = self.env.ref("tms_route_optimizer.demo_vehicle_brazil_van_1")
        brazil_vuc_1 = self.env.ref("tms_route_optimizer.demo_vehicle_brazil_vuc_1")
        # Van should have smaller capacity
        self.assertLess(brazil_van_1.weight_capacity, brazil_vuc_1.weight_capacity)
        self.assertLess(brazil_van_1.volume_capacity, brazil_vuc_1.volume_capacity)

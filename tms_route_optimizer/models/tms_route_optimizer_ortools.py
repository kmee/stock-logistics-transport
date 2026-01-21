import math

try:
    from ortools.constraint_solver import pywrapcp, routing_enums_pb2
except ImportError:
    pywrapcp = None
    routing_enums_pb2 = None


class RouteOptimizerHelper:
    """
    Helper class for OR-Tools route optimization.

    Provides static methods for:
    - Calculating distances between geographic coordinates (Haversine)
    - Generating distance matrices for multiple locations
    - Solving Vehicle Routing Problems (VRP) with capacity constraints
    - Generating Google Maps navigation URLs
    """

    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """
        Calculate distance between two coordinates using Haversine formula.

        Args:
            lat1: Latitude of first point
            lon1: Longitude of first point
            lat2: Latitude of second point
            lon2: Longitude of second point

        Returns:
            Distance in kilometers (0.0 if any coordinate is missing)
        """
        if not all([lat1, lon1, lat2, lon2]):
            return 0.0

        R = 6371  # Earth's radius in kilometers
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        return R * c

    @staticmethod
    def calculate_distance_matrix(locations):
        """
        Calculate distance matrix between all locations using Haversine formula.

        Args:
            locations: List of (latitude, longitude) tuples

        Returns:
            2D list of distances in km (symmetric matrix with zeros on diagonal)
        """
        n = len(locations)
        distance_matrix = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i != j:
                    lat1, lon1 = locations[i]
                    lat2, lon2 = locations[j]
                    distance_matrix[i][j] = RouteOptimizerHelper.haversine_distance(
                        lat1, lon1, lat2, lon2
                    )

        return distance_matrix

    @staticmethod
    def solve_vrp(
        distance_matrix,
        vehicle_capacities_weight,
        vehicle_capacities_volume,
        stop_weights,
        stop_volumes,
        cost_per_km,
        minimum_trip_cost,
        max_time_seconds=300,
        max_stops_per_vehicle=0,
    ):
        """
        Solve Vehicle Routing Problem using OR-Tools.

        Args:
            distance_matrix: 2D list of distances in km between locations
            vehicle_capacities_weight: List of weight capacities per vehicle (kg)
            vehicle_capacities_volume: List of volume capacities per vehicle (m³)
            stop_weights: List of weights for each stop (kg)
            stop_volumes: List of volumes for each stop (m³)
            cost_per_km: List of costs per km for each vehicle
            minimum_trip_cost: List of minimum trip costs per vehicle
            max_time_seconds: Maximum time for optimization (default: 300)
            max_stops_per_vehicle: Maximum stops per vehicle, 0 means no limit

        Returns:
            dict with solution data containing:
            - routes: List of route dictionaries with vehicle_id, route, distance,
              cost, weight, volume
            - total_distance: Total distance of all routes (km)
            - total_cost: Total cost of all routes
            - num_vehicles_used: Number of vehicles with actual stops
            None if no solution found
        """
        if not pywrapcp:
            raise ImportError("ortools is not installed")

        num_stops = len(stop_weights)
        num_vehicles = len(vehicle_capacities_weight)
        depot = 0

        # Create routing index manager
        manager = pywrapcp.RoutingIndexManager(num_stops + 1, num_vehicles, depot)
        routing = pywrapcp.RoutingModel(manager)

        # Create distance callback
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(distance_matrix[from_node][to_node] * 1000)  # Convert to meters

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add weight dimension
        # Use unary callback for demand (weight is added when arriving at node)
        def weight_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            if from_node == depot:
                return 0
            return int(stop_weights[from_node - 1] * 1000)  # Convert to grams

        weight_callback_index = routing.RegisterUnaryTransitCallback(weight_callback)
        # Use individual vehicle capacities for weight
        weight_capacities = [int(cap * 1000) for cap in vehicle_capacities_weight]
        routing.AddDimensionWithVehicleCapacity(
            weight_callback_index,
            0,  # slack
            weight_capacities,  # vehicle capacities (list, one per vehicle)
            True,  # start cumul to zero
            "Weight",
        )

        # Add volume dimension
        # Use unary callback for demand (volume is added when arriving at node)
        def volume_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            if from_node == depot:
                return 0
            return int(stop_volumes[from_node - 1] * 1000)  # Convert to liters

        volume_callback_index = routing.RegisterUnaryTransitCallback(volume_callback)
        # Use individual vehicle capacities for volume
        volume_capacities = [int(cap * 1000) for cap in vehicle_capacities_volume]
        routing.AddDimensionWithVehicleCapacity(
            volume_callback_index,
            0,  # slack
            volume_capacities,  # vehicle capacities (list, one per vehicle)
            True,  # start cumul to zero
            "Volume",
        )

        # Add stop count dimension (if max_stops_per_vehicle > 0)
        if max_stops_per_vehicle > 0:

            def stop_count_callback(from_index):
                """Each stop (except depot) counts as 1"""
                from_node = manager.IndexToNode(from_index)
                return 0 if from_node == depot else 1

            count_callback_index = routing.RegisterUnaryTransitCallback(
                stop_count_callback
            )

            # Add dimension with max stops per vehicle
            routing.AddDimensionWithVehicleCapacity(
                count_callback_index,
                0,  # slack
                [max_stops_per_vehicle] * num_vehicles,  # max per vehicle
                True,  # start cumul to zero
                "StopCount",
            )

        # Set search parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = int(max_time_seconds)

        # Solve
        solution = routing.SolveWithParameters(search_parameters)

        if not solution:
            return None

        # Extract solution
        routes = []
        total_distance = 0
        total_cost = 0

        for vehicle_id in range(num_vehicles):
            index = routing.Start(vehicle_id)
            route = []
            route_distance = 0
            route_weight = 0
            route_volume = 0

            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route.append(node_index)

                if node_index > 0:
                    route_weight += stop_weights[node_index - 1]
                    route_volume += stop_volumes[node_index - 1]

                previous_index = index
                index = solution.Value(routing.NextVar(index))

                if node_index > 0 or not routing.IsEnd(index):
                    route_distance += distance_matrix[
                        manager.IndexToNode(previous_index)
                    ][manager.IndexToNode(index)]

            route.append(manager.IndexToNode(index))  # Add depot at end

            if len(route) > 2:  # Only add routes with actual stops
                route_cost = minimum_trip_cost[vehicle_id] + (
                    route_distance * cost_per_km[vehicle_id]
                )
                routes.append(
                    {
                        "vehicle_id": vehicle_id,
                        "route": route,
                        "distance": route_distance,
                        "cost": route_cost,
                        "weight": route_weight,
                        "volume": route_volume,
                    }
                )
                total_distance += route_distance
                total_cost += route_cost

        return {
            "routes": routes,
            "total_distance": total_distance,
            "total_cost": total_cost,
            "num_vehicles_used": len([r for r in routes if len(r["route"]) > 2]),
        }

    @staticmethod
    def generate_google_maps_url(coordinates):
        """
        Generate Google Maps URL for a route with waypoints.

        Args:
            coordinates: List of (latitude, longitude) tuples

        Returns:
            Google Maps URL string or None if insufficient coordinates
        """
        if not coordinates or len(coordinates) < 2:
            return None

        origin = f"{coordinates[0][0]},{coordinates[0][1]}"
        destination = f"{coordinates[-1][0]},{coordinates[-1][1]}"

        waypoints = []
        for lat, lon in coordinates[1:-1]:
            waypoints.append(f"{lat},{lon}")

        waypoints_str = "|".join(waypoints) if waypoints else ""

        url = (
            f"https://www.google.com/maps/dir/?api=1"
            f"&origin={origin}&destination={destination}"
        )
        if waypoints_str:
            url += f"&waypoints={waypoints_str}"

        return url

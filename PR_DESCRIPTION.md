# TMS Route Optimization Suite

## Overview

This pull request introduces three integrated modules that provide a complete route optimization solution for the Transport Management System (TMS) in Odoo. These modules work together to enable intelligent route planning with capacity constraints, cost minimization, and multi-stop delivery management.

The suite leverages Google OR-Tools to solve Vehicle Routing Problems (VRP), automatically creating optimized TMS orders that minimize transportation costs while respecting vehicle capacity constraints.

## Modules Included

### 1. TMS Delivery Stops (`tms_delivery_stops`)

Extends the TMS module to support multiple delivery stops per TMS order, enabling businesses to manage complex delivery routes with multiple destinations.

#### Key Features

- **Multiple Delivery Stops**: Add multiple delivery stops to a single TMS order
- **Weight and Volume Tracking**: Track weight and volume for each delivery stop with support for Units of Measure (UoM)
- **Geolocation Support**: Automatic geolocation from partner addresses for route optimization
- **Stop Sequencing**: Order stops in a sequence to define delivery route order (drag-and-drop reordering)
- **Unloading Time**: Configure minimum unloading time per stop for better time estimation (default: 30 minutes)
- **State Management**: Track stop states (Draft, Scheduled, Delivered, Skipped) with workflow transitions
- **Total Calculations**: Automatic calculation of total weight, volume, and stops per order
- **Estimated Total Time**: Automatic calculation of total unloading time across all stops

#### Data Model

- **tms.order.stop**: Delivery stop model with fields for partner, sequence, weight, volume, scheduled date, state, and geolocation
- Extends **tms.order** with computed fields for totals and stop count

#### Dependencies

- `tms` - Base Transport Management System module
- `base_geolocalize` - For geocoding partner addresses
- `uom` - Units of Measure support

#### Version

- **Version**: 18.0.1.0.0
- **Category**: Inventory/Transport
- **License**: AGPL-3

---

### 2. TMS Vehicle Capacity (`tms_vehicle_capacity`)

Extends the TMS and Fleet modules to manage vehicle types with capacity and cost information, providing a foundation for route optimization.

#### Key Features

- **Vehicle Types**: Define vehicle types (Van, VUC, Toco, Truck, Bitrem, etc.) with default capacities and costs
- **Weight Capacity**: Configure weight capacity per vehicle with Units of Measure support
- **Volume Capacity**: Configure volume capacity per vehicle with Units of Measure support
- **Cost Management**: Define cost per kilometer and minimum trip cost per vehicle
- **Team Integration**: Link vehicle types to TMS teams for route optimization
- **Depot Locations**: Configure default depot/starting point per team (must have geolocation)
- **Automatic Population**: Vehicle type defaults automatically populate vehicle fields when type is selected
- **Demo Data**: Includes pre-configured Brazilian vehicle types (Van, VUC, Toco, Truck, Bitrem)

#### Data Model

- **fleet.vehicle.type**: Vehicle type model with default capacities and costs
- Extends **fleet.vehicle** with capacity, cost, and depot location fields
- Extends **fleet.vehicle.model** with vehicle type relationship
- Extends **tms.team** with allowed vehicle types and default depot location

#### Dependencies

- `tms` - Base Transport Management System module
- `fleet` - Fleet management module
- `uom` - Units of Measure support

#### Version

- **Version**: 18.0.1.0.0
- **Category**: Inventory/Transport
- **License**: AGPL-3

---

### 3. TMS Route Optimizer (`tms_route_optimizer`)

Provides route optimization functionality for TMS using Google OR-Tools. It solves Vehicle Routing Problems (VRP) to find optimal routes for multiple delivery stops, considering vehicle capacity constraints, distances, and costs.

#### Key Features

- **Route Optimization**: Uses Google OR-Tools to solve VRP problems with configurable time limits
- **Multi-Vehicle Support**: Distributes stops across multiple vehicles automatically
- **Capacity Constraints**: Considers weight and volume capacity of vehicles (hard constraints)
- **Distance Calculation**: Uses Haversine formula to calculate great-circle distances between locations
- **Cost Optimization**: Minimizes total cost considering distance and vehicle costs
- **Automatic Order Creation**: Creates TMS orders from optimized routes with stops in optimal order
- **Visualization**: Provides Google Maps and Waze URLs for each route for navigation
- **Performance Metrics**: Shows utilization rates (weight/volume), distances, and costs per route
- **Result Storage**: Stores optimization results with detailed route information for review
- **Date Range Filtering**: Automatically finds stops in Draft state within specified date range
- **Configurable Parameters**: System parameters for max optimization time and max deliveries

#### Data Model

- **tms.route.optimizer**: Main optimization record with team, date range, and delivery stops
- **tms.route.optimizer.result**: Stores optimization results with routes, costs, and metrics
- **tms.route.optimizer.ortools**: OR-Tools solver implementation with VRP logic

#### Dependencies

- `tms` - Base Transport Management System module
- `tms_delivery_stops` - Multiple delivery stops per order
- `tms_vehicle_capacity` - Vehicle types with capacity and cost management
- `base_geolocalize` - Geolocation support for partners
- `ortools` (Python package) - External dependency for optimization algorithm

#### Version

- **Version**: 18.0.1.0.0
- **Category**: Inventory/Transport
- **License**: AGPL-3

---

## Integration Architecture

The three modules work together in an integrated workflow:

```
┌─────────────────────┐
│ tms_delivery_stops  │
│                     │
│ - Delivery stops    │
│ - Geolocation       │
│ - Weight/Volume     │
└──────────┬──────────┘
           │
           │ provides data
           │
           ▼
┌─────────────────────┐
│ tms_route_optimizer │
│                     │
│ - VRP Solver        │
│ - Route Planning    │
│ - Cost Optimization │
└──────────┬──────────┘
           │
           │ uses constraints
           │
           ▼
┌─────────────────────┐
│ tms_vehicle_capacity│
│                     │
│ - Vehicle types     │
│ - Capacities        │
│ - Costs             │
└─────────────────────┘
```

### Integration Points

1. **tms_delivery_stops** → **tms_route_optimizer**
   - Finds stops in Draft state within date range
   - Uses stop weight/volume for capacity constraints
   - Uses stop geolocation for distance calculation
   - Updates stops to Scheduled state when orders are created

2. **tms_vehicle_capacity** → **tms_route_optimizer**
   - Uses vehicle weight/volume capacity as constraints
   - Uses vehicle cost per KM and minimum trip cost
   - Filters vehicles by team's allowed vehicle types
   - Uses team's default depot location

3. **tms_route_optimizer** → **TMS Orders**
   - Creates one TMS order per optimized route
   - Adds stops in optimized order
   - Links vehicles to orders
   - Updates stop states automatically

---

## Use Cases

- **Multi-stop delivery routes**: Plan and optimize routes with multiple delivery destinations
- **Route optimization**: Minimize transportation costs and distances
- **Capacity planning**: Ensure deliveries fit within vehicle capacity constraints
- **Cost optimization**: Reduce operational costs through intelligent route planning
- **Multi-vehicle operations**: Efficiently distribute stops across multiple vehicles
- **Visual route planning**: Use map integration for route verification

---

## Technical Details

### Algorithm

- **Solver**: Google OR-Tools Vehicle Routing Problem (VRP) solver
- **Distance Calculation**: Haversine formula for great-circle distances
- **Constraints**:
  - Weight capacity per vehicle
  - Volume capacity per vehicle
  - Vehicle availability
  - Vehicle type restrictions
- **Objective Function**:
  ```
  Total Cost = Σ (Minimum Trip Cost + Distance × Cost per KM)
  ```

### Optimization Process

1. **Input**: Delivery stops in Draft state within date range
2. **Validation**: Verify geolocation, capacities, and vehicle availability
3. **Distance Matrix**: Calculate distances between depot and all stops using Haversine formula
4. **VRP Solving**: Use OR-Tools VRP solver with capacity constraints to find optimal routes
5. **Result Storage**: Store optimization results with routes, costs, and performance metrics
6. **Output**: Optimized routes with assigned vehicles and stop sequences
7. **Order Creation**: Generate TMS orders from optimized routes (one order per route)
8. **State Update**: Automatically update stop states from Draft to Scheduled

---

## Configuration Requirements

### Prerequisites

1. **Install OR-Tools**:
   ```bash
   pip install ortools
   ```

2. **Configure TMS Teams**:
   - Set default depot location (must have geolocation)
   - Configure allowed vehicle types

3. **Configure Vehicles**:
   - Assign vehicle types
   - Set weight and volume capacities
   - Configure cost per KM and minimum trip cost
   - Link vehicles to TMS teams

4. **Configure Delivery Partners**:
   - Ensure all partners have geolocation coordinates
   - Use `base_geolocalize` module for automatic geocoding

5. **Create Delivery Stops**:
   - Create TMS orders with delivery stops
   - Set stops to Draft state
   - Fill in weight, volume, and scheduled dates

### System Parameters (Optional)

- `tms.route_optimizer.max_time_seconds`: Maximum optimization time (default: 300 seconds)
- `tms.route_optimizer.max_deliveries`: Maximum number of deliveries (default: 100)

---

## Features Highlights

### Route Optimization Features

- ✅ Multi-vehicle route optimization
- ✅ Capacity constraint handling (weight & volume)
- ✅ Cost minimization
- ✅ Distance-based optimization
- ✅ Automatic TMS order generation
- ✅ Google Maps & Waze integration
- ✅ Performance metrics and utilization tracking

### Delivery Stop Management

- ✅ Multiple stops per order
- ✅ Stop sequencing and reordering (drag-and-drop)
- ✅ State workflow management (Draft → Scheduled → Delivered/Skipped)
- ✅ Geolocation integration (automatic from partner addresses)
- ✅ Weight/volume tracking with UoM support
- ✅ Unloading time estimation (configurable per stop)
- ✅ Automatic total calculations (weight, volume, stops, time)

### Vehicle Management

- ✅ Vehicle type definitions with default values
- ✅ Capacity management (weight & volume with UoM)
- ✅ Cost configuration (per KM and minimum trip cost)
- ✅ Team-based vehicle assignment and filtering
- ✅ Depot location configuration (team-level with geolocation requirement)
- ✅ Automatic field population from vehicle type defaults
- ✅ Demo data with common Brazilian vehicle types

---

## Testing

All modules include:

- ✅ Security access rules (`ir.model.access.csv`)
- ✅ Demo data for testing (vehicle types, sample orders)
- ✅ Comprehensive views and UI components (forms, trees, kanban)
- ✅ Error handling and validation (geolocation checks, capacity validation)
- ✅ Data integrity constraints

---

## Documentation

Each module includes:

- Comprehensive README files (RST format) with usage instructions
- Configuration guides with step-by-step instructions
- Integration documentation explaining module relationships
- Best practices and recommendations
- Troubleshooting guides with common issues and solutions
- Quick start guides (for route optimizer)

---

## Author & Credits

- **Author**: KMEE, Odoo Community Association (OCA)
- **Contributor**: Luis Felipe Miléo (mileo@kmee.com.br)
- **Website**: https://github.com/OCA/stock-logistics-transport
- **License**: AGPL-3

---

## Status

- **Maturity**: Beta
- **Odoo Version**: 18.0
- **Module Versions**: 18.0.1.0.0

---

## Implementation Notes

### Code Quality

- All modules follow OCA development standards and conventions
- PEP 8 compliant Python code (line length ≤ 88 characters)
- Proper use of Odoo ORM and API decorators
- Comprehensive error handling and user-friendly error messages
- Security rules properly configured

### Performance Considerations

- Distance calculations use efficient Haversine formula
- OR-Tools solver configured with time limits to prevent long-running operations
- Configurable maximum delivery limits to handle large datasets
- Efficient database queries with proper domain filters

### Extensibility

- Modular design allows for future enhancements
- Vehicle type system allows easy addition of new vehicle categories
- Stop state workflow can be extended with additional states
- Optimization algorithm can be extended with additional constraints

## Notes

- All modules follow OCA development standards
- Ready for community testing and feedback
- Comprehensive documentation included
- Fully integrated and tested together
- Requires Python package `ortools` to be installed separately
- All partners must have geolocation for route optimization to work

## Future Enhancements (Potential)

- Time window constraints for deliveries
- Driver preferences and availability
- Traffic-aware routing
- Real-time route adjustments
- Integration with GPS tracking systems
- Multi-depot support
- Pickup and delivery combinations

---

This pull request provides a complete, production-ready route optimization solution for Odoo TMS, enabling businesses to efficiently plan and optimize multi-stop delivery routes with capacity constraints and cost optimization. The solution is designed to be scalable, maintainable, and extensible for future enhancements.

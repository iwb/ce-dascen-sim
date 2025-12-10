"""
File: product.py
Location: /src/product.py
Description: Product, group, and component classes for disassembly simulation
Author: Patrick Jordan
Version: 2025-10

Contains classes representing physical entities in the disassembly process:
- product: Incoming products to be disassembled
- group: Component groups resulting from disassembly operations
- component: Individual components from disassembly

Each class handles:
- Unique identification and tracking
- Hierarchical relationships (parent/component structure)
- Condition and quality attributes
- Transport and blocking relationships
- Structure loading from JSON variant files
"""

# Standard library imports
import datetime
import json
from contextlib import ExitStack
import copy

# Third-party imports
import simpy

# Local application imports
import functions
import helper_functions
from src.g import *


class product:
    """Represents incoming products in the disassembly system.

    Each instance represents a single product with unique characteristics such as ID,
    type, condition, etc. The product's details are loaded from a variant JSON file,
    which contains information about the product's structure and condition limits.

    When initialized, the product's delivery time is recorded, its condition is
    randomly set based on the specified limits, and the number of parts is counted.

    Attributes:
        ID (int): Unique identifier of the product
        caseID (int): Identifier for tracking in the eventlog (same as ID)
        parent (product): Parent product (self-reference for top-level products)
        content (dict): Properties loaded from the variant JSON file
        type (str): Product variant type (e.g., 'variant1')
        delivery_time (float): Time when the product entered the system
        condition (float): Condition value from 0 (worst) to 1 (best)
        parts_count (int): Total number of parts that can be disassembled
        level_of_disassembly (float): Progress from 0 (none) to 1 (fully disassembled)
        transport_units (int): Transport capacity required by the product
        components_to_scan (list): Components whose disassembly hasn't been attempted
    """

    def __init__(self, env, ID, variant_path, simulation=None):
        # Store the numeric ID first, then create the string ID with variant
        self.numeric_id = ID  # Store numeric ID for groups/components to use
        self.caseID = ID
        self.parent = self

        # Deep copy of the variant data (prevents issues if running multiple runs)
        # Prevents modifications from affecting other products
        with open(variant_path) as f:
            variant_data = json.load(f)["variant"]
        self.content = copy.deepcopy(variant_data)

        self.type = self.content["type"]

        # CREATE THE ID WITH VARIANT NAME
        self.ID = f"prod_{ID:03d}_{self.type}"  # NEW: e.g., "prod_001_Variant1"
        # Variant tracking for easier access
        self.variant = self.type  # NEW: Store variant explicitly

        self.parent_type = self.type
        # Explicitly initialize parent_component (products have no parent)
        self.parent_component = None
        # Add component attribute that is the same as type for top-level products
        self.component = self.type
        # set delivery time to current simulation time
        self.delivery_time = env.now

        # Set product condition based on behavior mode
        if SimulationConfig.behavior_mode == SimulationBehavior.DETERMINISTIC:
            # Use mode value
            self.condition = self.content["condition_mu"]
        else:
            # SEEDED  -> set condition based on triangular distribution specified for this variant
            self.condition = SimulationConfig.rng_quality.triangular(
                self.content["condition_min"],
                self.content["condition_mu"],
                self.content["condition_max"],
            )

        self.parts_count = helper_functions.count_parts(self.content["structure"])
        self.level_of_disassembly = 0
        self.transport_units = self.content["transport_units"]
        self.components_to_scan = helper_functions.list_components(
            self.content["structure"]
        )
        # NEW:
        # Store original component list for variant (never modified, used for inspection logic)
        self.original_variant_components = set(
            helper_functions.list_components(self.content["structure"])
        )
        # Store original DIRECT children (top-level only) for inspection missing component check
        self.original_direct_children = set(self.content["structure"].keys())

        # NEW: Add routing plan (dynamic, based on product structure and factory config)
        if simulation:
            self.routing_plan = self._determine_routing_plan(simulation)
            self.current_route_index = 0
        else:
            # Fallback for backward compatibility
            self.routing_plan = []
            self.current_route_index = 0

    # Error handling in case the file is missing (debugging).
    def _load_variant(self, variant_path):
        try:
            with open(variant_path) as variant_file:
                return json.load(variant_file)["variant"]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading variant from {variant_path}: {e}")
            return {}

    def _determine_routing_plan(self, simulation):
        """Dynamically determine routing plan based on product structure and factory config.

        This creates a route by matching product components to station capabilities.
        Excludes parallel stations (multiple stations with same predecessor).

        Args:
            simulation: Simulation instance with stations and storages

        Returns:
            list: Ordered list of station/storage names to visit
        """
        routing = []

        # Get all components in this product (flatten nested structure)
        product_components = self._get_all_components(self.content.get("structure", {}))

        # Get all stations from simulation
        available_stations = simulation.stations

        # Find parallel stations (stations that share the same predecessors)
        parallel_stations = self._detect_parallel_stations(available_stations)

        # Build routing plan by matching components to stations
        for station in available_stations:
            # Check if this station can process ANY component in the product
            station_components = station.step_names  # From config

            # Does this product have components this station can handle?
            can_process_here = any(
                comp in station_components for comp in product_components
            )

            # Exclude parallel stations from routing plan (they pull from buffers)
            is_parallel = station in parallel_stations

            if can_process_here and not is_parallel:
                routing.append(station.name)

        # Add storages and parallel station groups
        parallel_groups = {}  # storage_name -> [parallel_station_names]

        for storage in simulation.storages:
            # Check if this storage is a predecessor to any parallel station
            for parallel_station in parallel_stations:
                if storage in parallel_station.predecessors:
                    # Check if product needs to visit any of the parallel stations
                    parallel_can_process = any(
                        comp in parallel_station.step_names
                        for comp in product_components
                    )
                    if parallel_can_process:
                        # Track parallel stations for this storage
                        if storage.name not in parallel_groups:
                            parallel_groups[storage.name] = []
                        if parallel_station.name not in parallel_groups[storage.name]:
                            parallel_groups[storage.name].append(parallel_station.name)

        # Add storage + parallel station groups to routing
        for storage_name, parallel_list in parallel_groups.items():
            # Add the storage first
            routing.append(storage_name)
            # Then add parallel station group
            parallel_display = "[" + "|".join(sorted(parallel_list)) + "]"
            routing.append(parallel_display)

        return routing

    def _detect_parallel_stations(self, stations):
        """Detect which stations are parallel (share same predecessors).

        Args:
            stations: List of station objects

        Returns:
            set: Set of stations that are part of parallel groups
        """
        # Group stations by their predecessors
        predecessor_groups = {}
        for station in stations:
            if hasattr(station, "predecessors") and station.predecessors:
                # Create a hashable key from predecessor names
                pred_key = tuple(sorted([p.name for p in station.predecessors]))
                if pred_key not in predecessor_groups:
                    predecessor_groups[pred_key] = []
                predecessor_groups[pred_key].append(station)

        # Identify parallel stations (groups with more than one station)
        parallel_stations = set()
        for pred_key, station_group in predecessor_groups.items():
            if len(station_group) > 1:
                # Multiple stations with same predecessor = parallel
                parallel_stations.update(station_group)

        return parallel_stations

    def _get_all_components(self, structure, components=None):
        """Recursively extract all component names from nested structure.

        Args:
            structure: Product structure dict from variant JSON
            components: Set to accumulate component names

        Returns:
            set: All component names in the structure
        """
        if components is None:
            components = set()

        for key, value in structure.items():
            # Add this component
            components.add(key)

            # If it has nested structure, recurse
            if isinstance(value, dict) and "structure" in value:
                self._get_all_components(value["structure"], components)

        return components

    def get_next_station(self):
        """Get next station in route.

        Returns:
            str: Name of next station, or None if route complete
        """
        if self.current_route_index < len(self.routing_plan):
            return self.routing_plan[self.current_route_index]
        return None

    def advance_route(self):
        """Move to next station in route."""
        self.current_route_index += 1

    def get_remaining_route(self):
        """Get list of remaining stations in route.

        Returns:
            list: Remaining station names
        """
        return self.routing_plan[self.current_route_index :]


class group:
    """Represents component groups resulting from disassembly operations."""

    def __init__(self, type, parent, content):
        # self.ID = str(parent.caseID) + "_" + type
        self.ID = (
            f"group_{parent.caseID:03d}_{type}"  # e.g., "group_017_battery_assembly1"
        )
        self.caseID = parent.caseID
        self.parent = parent
        self.delivery_time = parent.delivery_time

        # Deep copy of the content (prevents issues from multiple runs)
        # This prevents modifications from affecting the parent's structure
        self.content = copy.deepcopy(content)

        self.parent_type = parent.parent_type
        self.type = self.parent_type + "_" + type
        self.transport_units = self.content["transport_units"]

        # NEW: Add variant tracking
        if hasattr(parent, "variant"):
            self.variant = parent.variant  # Inherit from parent product
        elif hasattr(parent, "parent_type"):
            self.variant = parent.parent_type  # Fallback to parent_type
        else:
            self.variant = None  # Safety fallback

        # Component hierarchy tracking attributes
        self.component = type  # Component name is just the type without parent prefix
        self.parent_component = (
            parent.component
        )  # Parent's component becomes this group's parent

        self.condition = None  # is set in generator
        self.level_of_disassembly = 0
        self.parts_count = helper_functions.count_parts(self.content["structure"])
        self.components_to_scan = helper_functions.list_components(
            self.content["structure"]
        )
        # Store original DIRECT children for inspection missing component check
        self.original_direct_children = set(self.content["structure"].keys())


class component:
    """Represents individual components resulting from disassembly operations.

    Each instance represents a single component created by disassembling a parent
    product or group. The component inherits details from its parent, such as
    delivery time and type.

    At initialization, the component's condition is not set. This is determined later
    in the generator based on the parent's condition and random variation.

    Attributes:
        ID (str): Unique identifier combining parent ID and component type
        caseID (int): Original parent product's ID for tracking
        parent (product/group): Parent from which this was disassembled
        delivery_time (float): Time when the parent product entered the system
        type (str): Combined parent type and component type identifier
        transport_units (int): Transport capacity required by the component
        blocked_by (list): Components that must be removed before this one
        condition (float): Value from 0 to 1, initially None until set
        parent_component (str): For hierarchical tracking
    """

    def __init__(self, parent, comp_key, comp_values):
        self.ID = str(parent.caseID) + "_" + comp_key
        self.caseID = parent.caseID
        self.parent = parent
        self.delivery_time = parent.delivery_time
        self.parent_type = parent.parent_type
        self.type = self.parent_type + "_" + comp_key

        # NEW: Add variant tracking
        if hasattr(parent, "variant"):
            self.variant = parent.variant  # Inherit variant from parent
        else:
            self.variant = None

        self.transport_units = comp_values["transport_units"]
        self.blocked_by = comp_values["blocked_by"]
        self.condition = None  # is set in generator
        # Set component name to the specific component (not the full type)
        self.component = comp_key
        # Set parent_component to the parent's component value
        self.parent_component = parent.component

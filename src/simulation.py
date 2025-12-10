"""
File: simulation.py
Location: /src/simulation.py
Description: Core simulation engine and orchestrator for disassembly factory
Author: Patrick Jordan
Version: 2025-10

This module implements the main simulation logic for the disassembly system.
It handles setup, execution and monitoring of the simulation environment
based on configuration files.

The simulation is structured as coordinated processes:
- Factory setup and validation
- Resource allocation and management
- Process coordination and monitoring
- Data collection and logging

Key Components:
- Simulation class: Main simulation manager
- _setup_simulation(): Initializes all components
- _run_simulation(): Executes simulation until completion
- Component setup methods for stations, storage, resources, vehicles
"""

# Standard Library Imports
import json
import os

import time
from datetime import datetime
from typing import Dict, List, Optional


# Third-Party Imports
import simpy
import pandas as pd


# Local Imports
from src.breakdowns import Breakdowns
from src.breaks import Breaks
from src.g import g, SimulationConfig
from src.product import product
from src.source import Source
from src.station import Station
from src.storage import Storage
from src.vehicle import Vehicle
from src.simulation_monitor import SimulationMonitor
import helper_functions
from src.station_state import StationState


class Simulation:
    """Core simulation manager for the disassembly system.

    This class manages the complete simulation environment including:
    - Loading and validating factory configurations
    - Setting up processing stations and storage
    - Managing resources (workers, equipment)
    - Coordinating material flow and processing
    - Collecting performance data

    Attributes:
        env (simpy.Environment): The simulation environment
        monitor (SimulationMonitor): Performance monitoring system
        stations (List[Station]): Processing stations in the simulation
        storages (List[Storage]): Storage units in the simulation
        all_predecessors (List): Elements that are predecessors to others
        ends_of_line (List): Elements at the end of processing lines
        incoming_storage (Storage): System entry point storage
        outgoing_storage (Storage): System exit point storage
        supply (Source): Product generator/supply source
        global_equipment (Dict): Global equipment resources
        global_employees (Dict): Global employee resources
        vehicles (List[Vehicle]): Transportation vehicles
        breakdowns (List[Breakdowns]): Equipment breakdown handlers
        breaks (Breaks): Work shifts and breaks manager
        maintenance (simpy.PreemptiveResource): Maintenance resource
        start_of_day (float): Daily shift start time
        end_of_day (float): Daily shift end time
        maintenance_capacity (int): Available maintenance capacity
        vehicle_requests (Dict): Vehicle request tracking
        log_vehicles (Dict): Vehicle usage logging by location
    """

    # Core Methods
    def __init__(self) -> None:
        """Initialize simulation environment."""
        try:
            # Initialize environment
            self.env = simpy.Environment()

            # Set up monitoring
            self.monitor = SimulationMonitor(self.env, self)

            # Initialize empty containers - Create instance attributes
            self.stations = []
            self.storages = []
            self.all_predecessors = []
            self.ends_of_line = []

        except Exception as e:
            print(f"Simulation initialization failed: {e}")
            raise

    def run(self: object) -> None:
        """Execute the complete simulation process.
        This method coordinates the simulation execution through setup and running phases.
        It's the main entry point after the Simulation object is created.

        Raises:
            Exception: If any simulation operation fails"""
        try:
            # Initialize debug logging
            helper_functions.init_debug_log()

            # Setup phase
            self._setup_simulation()

            # Execution phase
            self._run_simulation()

            # Close debug log
            helper_functions.close_debug_log()

        except Exception as e:
            # Make sure to close debug log even on error
            helper_functions.close_debug_log()
            print(f"Simulation execution failed: {e}")
            raise

    def _setup_simulation(self) -> None:
        # Load and validate configuration

        # ==========================================
        # PHASE 1: Load configuration
        # ==========================================
        print("Loading simulation configuration...")
        structure = self._load_configuration()

        # ==========================================
        # PHASE 2: Initialize components
        # ==========================================
        print("Initializing simulation components...")
        self._setup_stations(structure)
        self._setup_storage_system(structure)
        self._setup_resources(structure)
        self._setup_vehicles(structure)

        # ==========================================
        # PHASE 3: Configure network
        # ==========================================
        print("Configuring process network...")
        self._configure_network(structure)

        # DEBUG: Uncomment to trace network predecessor relationships
        # print("\nDEBUG: Station predecessors:")
        # for station in self.stations:
        #     pred_names = [p.name for p in station.predecessors]
        #     print(f"  {station.name} <- {pred_names}")

        # print("\nDEBUG: Storage predecessors:")
        # for storage in self.storages:
        #     pred_names = [p.name for p in storage.predecessors] if storage.predecessors else []
        #     print(f"  {storage.name} <- {pred_names}")

        # ==========================================
        # PHASE 4: Initialize tracking
        # ==========================================
        print("Initializing tracking columns...")
        self._initialize_tracking_columns()

        # ==========================================
        # PHASE 5: Start processes
        # ==========================================
        print("Starting simulation processes...")
        self._initialize_processes()
        self._setup_product_generators()

        # Initialize detailed monitoring now that components exist
        self.monitor.initialize_detailed_monitoring()

    def _run_simulation(self) -> None:
        """Execute simulation until completion."""
        print("Starting simulation execution...")
        self.env.run(until=SimulationConfig.time_to_simulate)

        # Final calculation pass for all products
        self._calculate_all_product_times()

        # Record final state if in debug mode
        self.monitor.record_final_state()

        # Export state logs for all stations
        for station in self.stations:
            station.state.export_logs()

        # Check state consistency if in debug mode
        if SimulationConfig.time_consistency_checks:
            self.check_state_consistency()

    def check_state_consistency(self) -> None:
        """Check the state consistency of all stations"""
        # Skip if state tracking is disabled
        if not SimulationConfig.station_state_tracking:
            return

        print("\nChecking state consistency for all stations...")
        overall_consistent = True

        for station in self.stations:
            # Call station's time consistency check
            station_consistent = station.check_time_consistency()
            overall_consistent = overall_consistent and station_consistent

        if overall_consistent:
            print("\nAll stations have consistent time accounting")
        else:
            print("\nWARNING: Some stations have inconsistent time accounting!")
            print("Check the individual station logs for details")

    # Setup Methods
    def _load_configuration(self) -> Dict:
        """
        Load and validate factory structure from JSON configuration.

        Reads the factory configuration file and validates its structure.
        Sets up basic simulation parameters from the configuration.

        Returns:
            Dict: Complete factory configuration including:
                - Global parameters
                - Station definitions
                - Storage configurations
                - Resource specifications

        Raises:
            FileNotFoundError: If structure file doesn't exist
            json.JSONDecodeError: If JSON format is invalid
            ValueError: If required configuration is missing
        """

        try:
            # Construct path to structure file
            structure_file = os.path.join(
                SimulationConfig.file_path,
                SimulationConfig.structure_path,
                SimulationConfig.structure_file,
            )

            # Load and parse configuration file
            with open(structure_file) as f:
                structure = json.load(f)

            # Set global simulation parameters
            self._set_global_parameters(structure)

            return structure

        except FileNotFoundError:
            raise FileNotFoundError(f"Structure file not found: {structure_file}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in structure file: {structure_file}")

    def _set_global_parameters(self, structure: Dict) -> None:
        """Set global simulation parameters from configuration."""
        # Ensure all required parameters exist
        required_params = ["start_of_day", "end_of_day", "maintenance_capacity"]

        for param in required_params:
            if param not in structure["factory"]["global_parameters"]:
                raise ValueError(f"Missing required global parameter: {param}")

        # Set parameters
        params = structure["factory"]["global_parameters"]
        self.start_of_day = params["start_of_day"]
        self.end_of_day = params["end_of_day"]
        self.maintenance_capacity = params["maintenance_capacity"]

    def _validate_structure(self, structure: Dict) -> None:
        """
        Validate the loaded factory structure configuration.

        Checks for presence and validity of:
        - Required top-level sections
        - Global parameters
        - Station configurations
        - Resource definitions

        Args:
            structure: Factory configuration dictionary

        Raises:
            ValueError: If any required configuration is missing
        """
        # Check Required Sections
        if "factory" not in structure:
            raise ValueError("Missing top-level 'factory' section in configuration")

        factory = structure["factory"]
        required_sections = ["global_parameters", "stations", "global_resources"]

        for section in required_sections:
            if section not in factory:
                raise ValueError(
                    f"Missing required section '{section}' in factory configuration"
                )

        # Validate Global Parameters
        required_globals = ["start_of_day", "end_of_day", "maintenance_capacity"]
        for param in required_globals:
            if param not in factory["global_parameters"]:
                raise ValueError(f"Missing global parameter: {param}")

        # Validate Stations
        if not factory["stations"]:
            raise ValueError("No stations defined in configuration")

    def _setup_stations(self, structure: Dict) -> None:
        """
        Initialize and configure all processing stations.

        Creates station instances based on configuration including:
        - Processing steps for each station
        - Required equipment
        - Required employees
        - Station connections

        Args:
            structure: Factory configuration dictionary containing station definitions

        Note:
            Stations are initialized with temporary predecessor None,
            which will be set later during network configuration
        """

        # Initialize Stations List
        self.stations = []

        # Iterate through station configurations
        for station_key, station_values in structure["factory"]["stations"].items():
            # Parse station configuration
            station_config = self._parse_station_config(station_values)

            # Override capacities for push mode to prevent deadlocks (otherwise unload of vehicle might get stuck)
            if getattr(SimulationConfig, "material_flow_mode", "pull") == "push":
                station_values = (
                    station_values.copy()
                )  # Make a copy (in case overriden with push values)
                station_values["entry_capacity"] = float("inf")
                station_values["outbuf_to_next_capacity"] = float("inf")
                station_values["outbuf_to_store_capacity"] = float("inf")

            # Create station instance
            new_station = Station(
                self.env,
                station_key,
                None,  # Predecessor assigned later
                station_config["steps"],
                self,
                station_values,
                station_config["equipment"],
                station_config["employees"],
            )

            # Add to station list
            self.stations.append(new_station)

            # Add station to inventory logging
            helper_functions.add_to_inventory_log(station_key)

    def _parse_station_config(self, station_values: Dict) -> Dict:
        """Parse station configuration from structure file."""
        return {
            "steps": [
                (
                    step_key,
                    [(k, v) for k, v in step_values["equipment"].items()],
                    [(k, v) for k, v in step_values["employees"].items()],
                    step_values["min_condition"],
                )
                for step_key, step_values in station_values["steps"].items()
            ],
            "equipment": [
                (k, v) for k, v in station_values["resources"]["equipment"].items()
            ],
            "employees": [
                (k, v) for k, v in station_values["resources"]["employees"].items()
            ],
        }

    def _setup_storage_system(self, structure: Dict) -> None:
        """
        Initialize and configure all storage components of the system.

        Creates and configures:
        - Incoming storage (system entry point)
        - Intermediate storage locations
        - Outgoing storage (system exit point)

        Args:
            structure: Factory configuration dictionary containing storage definitions

        Note:
            - Incoming storage has infinite capacity
            - Outgoing storage has infinite capacity
            - Intermediate storages use configured capacities
        """
        # Create incoming storage with infinite capacity
        self.incoming_storage = self._create_incoming_storage()
        # Initialize logging for incoming storage
        helper_functions.add_to_inventory_log(self.incoming_storage.name)

        # Create supply source connected to incoming storage
        # self.supply = Source(self.env, self.incoming_storage.outbuf_to_next)
        self.supply = Source(self.env, self.incoming_storage.entry, simulation=self)

        # Create intermediate storage
        self.storages = self._create_intermediate_storage(structure)

        # Create outgoing storage
        self.outgoing_storage = self._create_outgoing_storage()

    def _create_incoming_storage(self) -> Storage:
        """Create incoming storage with infinite capacity."""
        return Storage(
            self.env,
            self,
            "incoming_storage",
            float("inf"),  # Infinite entry capacity
            float("inf"),  # Infinite order threshold
            float("inf"),  # Infinite storage capacity
            float("inf"),  # Infinite exit capacity
            None,  # No predecessor
            0,  # No handling time
        )

    def _create_intermediate_storage(self, structure: Dict) -> List[Storage]:
        """Create intermediate storage locations from configuration."""
        storages = []
        for storage_key, storage_values in structure["factory"]["storages"].items():
            # Override capacities for push mode
            if getattr(SimulationConfig, "material_flow_mode", "pull") == "push":
                entry_cap = float("inf")
                storage_cap = float("inf")
                exit_cap = float("inf")
            else:
                entry_cap = storage_values["entry_capacity"]
                storage_cap = storage_values["storage_capacity"]
                exit_cap = storage_values["exit_capacity"]

            new_storage = Storage(
                self.env,
                self,
                storage_key,
                entry_cap,
                storage_values["entry_order_threshold"],
                storage_cap,
                exit_cap,
                None,  # Predecessor assigned later
                storage_values["handling_time"],
            )

            # Add storage to list
            storages.append(new_storage)

            # Initialize logging
            helper_functions.add_to_inventory_log(storage_key)
        return storages

    def _create_outgoing_storage(self) -> Storage:
        """Create outgoing storage with infinite capacity."""
        return Storage(
            self.env,
            self,
            "outgoing_storage",
            float("inf"),  # Infinite entry capacity
            float("inf"),  # Infinite order threshold
            float("inf"),  # Infinite exit capacity
            float("inf"),  # Infinite storage capacity
            self.stations,  # All stations can be predecessors
            0,  # No handling time
        )

    def _setup_resources(self, structure: Dict) -> None:
        """
        Initialize global equipment, employee and maintenance resources.

        Creates global resources defined in configuration:
        - Equipment resources (PreemptiveResource)
        - Employee resources (PreemptiveResource)
        - Maintenance capacity

        Args:
            structure: Factory configuration dictionary
        """
        # Initialize resource dictionaries
        self.global_equipment = {}
        self.global_employees = {}

        # Create equipment resources
        for equip_key, equip_value in structure["factory"]["global_resources"][
            "equipment"
        ].items():
            self.global_equipment[equip_key] = simpy.PreemptiveResource(
                self.env, capacity=equip_value
            )

        # Create employee resources
        for emp_key, emp_value in structure["factory"]["global_resources"][
            "employees"
        ].items():
            self.global_employees[emp_key] = simpy.PreemptiveResource(
                self.env, capacity=emp_value
            )

        # Create maintenance resource
        self.maintenance = simpy.PreemptiveResource(
            self.env,
            capacity=structure["factory"]["global_parameters"]["maintenance_capacity"],
        )

    def _setup_vehicles(self, structure: Dict) -> None:
        """
        Initialize transportation system and vehicle tracking.

        Creates:
        - Transport vehicles with configured capacities
        - Vehicle request tracking system
        - Vehicle logging system

        Args:
            structure: Factory configuration dictionary
        """
        # Initialize vehicle list
        self.vehicles = []
        self.vehicle_requests = {}  # Track how many times each vehicle is requested

        # Create vehicles from configuration
        # e.g., "v01_forklift": {"quantity": 2, "speed": 180, ...}
        for vehicle_key, vehicle_values in structure["factory"]["vehicles"].items():
            for i in range(vehicle_values["quantity"]):
                # Create vehicle instance with leading zero format (_01, _02, etc.)
                vehicle_name = f"{vehicle_key}_{i + 1:02d}"
                new_vehicle = Vehicle(
                    self.env,
                    vehicle_name,
                    "incoming_storage",  # Initial location of the vehicle
                    vehicle_values["speed"],
                    vehicle_values["load_capacity"],
                    vehicle_values[
                        "loading_time"
                    ],  # Time required to load/unload items
                )
                # Add vehicle to master list of all vehicles
                self.vehicles.append(new_vehicle)

                # Initialize vehicle request tracking (counter)
                self.vehicle_requests[new_vehicle] = 0

        # Initialize vehicle logging system: log vehicle usage by location
        # e.g. "station1": {"forklift1": 0, "forklift2": 0},
        self.log_vehicles = {
            element.name: {vehicle.name: 0 for vehicle in self.vehicles}
            # Combine all locations into one dictionary
            for element in (
                self.stations
                + self.storages
                + [self.incoming_storage, self.outgoing_storage]
            )
        }

    def _setup_breakdowns(self) -> List[Breakdowns]:
        """Set up equipment breakdown handlers."""
        breakdowns = []
        for station in self.stations:
            for element in station.equipment:
                for i, resource in enumerate(station.equipment[element], 1):
                    breakdowns.append(
                        Breakdowns(
                            self.env,
                            self,
                            station,
                            f"{element}_{i}",
                            resource,
                            SimulationConfig.MTBF_mu,
                            SimulationConfig.MTBF_sigma,
                            SimulationConfig.MTTR_mu,
                            SimulationConfig.MTTR_sigma,
                        )
                    )
        return breakdowns

    def _initialize_processes(self) -> None:
        """Initialize and start all simulation processes."""
        # Initialize breakdowns
        self.breakdowns = self._setup_breakdowns()

        # Initialize work shifts and breaks
        self.breaks = Breaks(self.env, self)

    def _configure_network(self, structure: dict) -> None:
        """Configure connections between simulation components."""
        # Configure station predecessors
        for station in self.stations:
            helper_functions.assign_predecessors(
                self, station, structure["factory"]["stations"][station.name]
            )

        # Configure storage predecessors
        for storage in self.storages:
            helper_functions.assign_predecessors(
                self, storage, structure["factory"]["storages"][storage.name]
            )

        # Clear and rebuild ends_of_line list
        self.ends_of_line.clear()  # Clear any existing entries

        # Identify end-of-line components
        for component in self.stations + self.storages:
            if component not in self.all_predecessors:
                self.ends_of_line.append(component)

    def _setup_product_generators(self) -> None:
        """Set up product generation processes based on the configuration."""
        # Get the delivery mode
        delivery_mode = SimulationConfig.delivery_mode

        # Load delivery schedule if needed
        if delivery_mode in ["scheduled", "mixed"]:
            delivery_schedule_file = getattr(
                SimulationConfig, "delivery_schedule_file", None
            )

            if delivery_schedule_file:
                try:
                    # Construct path to schedule file
                    schedule_path = os.path.join(
                        SimulationConfig.file_path,
                        "config",
                        "delivery_schedules",
                        delivery_schedule_file,
                    )

                    # Pass schedule to source
                    delivery_schedule_loaded = self.supply.load_delivery_schedule(
                        schedule_path
                    )

                    if not delivery_schedule_loaded:
                        print(
                            f"Failed to load delivery schedule '{delivery_schedule_file}'"
                        )
                        if delivery_mode == "scheduled":
                            print("Falling back to random delivery mode")
                            SimulationConfig.delivery_mode = "random"
                except Exception as e:
                    print(f"Error loading delivery schedule: {e}")
                    # Fall back to random mode if schedule can't be loaded
                    if delivery_mode == "scheduled":
                        print("Falling back to random delivery mode")
                        SimulationConfig.delivery_mode = "random"

        # Initialize generators based on delivery mode
        self.supply.initialize_generators()

    def _calculate_all_product_times(self):
        """Calculate processing times for all products after simulation completes."""
        print("\nCalculating product processing times...")

        # Convert events list to DataFrame if needed
        if SimulationConfig.events_list:
            eventlog_df = pd.DataFrame(SimulationConfig.events_list)
        else:
            eventlog_df = SimulationConfig.eventlog

        # Check which format we're dealing with
        if eventlog_df.empty:
            print("No events to process")
            return

        # Detect format based on columns
        is_new_format = "object_id" in eventlog_df.columns

        # For each unique case in the eventlog
        unique_cases = eventlog_df["caseID"].unique()

        for case_id in unique_cases:
            # Calculate times
            time_components = helper_functions.calculate_time_components_simple(
                case_id, eventlog_df, self
            )

            # Find the product ID for this case
            case_events = eventlog_df[eventlog_df["caseID"] == case_id]

            if is_new_format:
                # New format - look for product objects
                product_events = case_events[case_events["object_type"] == "product"]
                if len(product_events) > 0:
                    # Use the full object_id (e.g., "prod_001_Variant3")
                    product_id = product_events.iloc[0]["object_id"]
                else:
                    print(f"Warning: No product events found for case {case_id}")
                    continue
            else:
                # Old format - use objectID directly
                if len(case_events) > 0:
                    product_id = case_events.iloc[0]["objectID"]
                else:
                    print(f"Warning: No events found for case {case_id}")
                    continue

            # Update the log
            mask = SimulationConfig.log_disassembly["ID"] == product_id
            if mask.sum() > 0:
                for station, time in time_components["station_times"].items():
                    if station in SimulationConfig.log_disassembly.columns:
                        SimulationConfig.log_disassembly.loc[mask, station] = round(
                            time, 2
                        )

                for vehicle, time in time_components["vehicle_times"].items():
                    if vehicle in SimulationConfig.log_disassembly.columns:
                        SimulationConfig.log_disassembly.loc[mask, vehicle] = round(
                            time, 2
                        )
            else:
                print(f"Warning: Product ID {product_id} not found in log_disassembly")

        print("Product time calculation complete")

    def _initialize_tracking_columns(self) -> None:
        """Initialize columns in log_disassembly for all stations and vehicles.

        This ensures that all stations and vehicles have columns in the tracking
        DataFrame from the start, even if they don't process every product.
        """
        # Initialize columns for all stations
        for station in self.stations:
            if station.name not in SimulationConfig.log_disassembly.columns:
                SimulationConfig.log_disassembly[station.name] = 0.0

        # Initialize columns for all vehicles
        for vehicle in self.vehicles:
            if vehicle.name not in SimulationConfig.log_disassembly.columns:
                SimulationConfig.log_disassembly[vehicle.name] = 0.0

        print(
            f"  [OK] Initialized tracking for {len(self.stations)} stations and {len(self.vehicles)} vehicles"
        )

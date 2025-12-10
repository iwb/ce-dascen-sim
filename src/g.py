"""
File: g.py
Location: /src/g.py
Description: Global configuration manager and simulation state (SimulationConfig class)
Author: Patrick Jordan
Version: 2025-10

This module provides the global configuration management through the SimulationConfig class.
It manages all simulation parameters, random number generators, file paths, and logging structures.

Key Components:
- SimulationConfig: Main configuration class with hierarchical config loading
- SimulationBehavior: Enum for random behavior modes (SEEDED, RANDOM)
- SeededRandomGenerator: Deterministic random number generation
- g: Legacy alias for SimulationConfig (backward compatibility)

The configuration hierarchy:
1. default_config.json - Technical defaults
2. runtime_config.json - Output/visualization settings
3. experiment config - Experiment-specific settings
4. experiment overrides - Optional runtime overrides
"""

# Standard library imports
import json
import os
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

# Third-party imports
import pandas as pd


class DeterministicRNG:
    """A deterministic replacement for random number generation"""

    def __init__(self, seed=None):
        """Initialize deterministic RNG"""
        # Seed is ignored - this class always returns fixed values
        pass

    def random(self):
        """Always return 0.5 for consistent results"""
        return 0.5

    def triangular(self, low, high, mode=None):
        """Always return the mode or middle value"""
        if mode is not None:
            return mode
        return (low + high) / 2

    def normalvariate(self, mu, sigma):
        """Always return the mean for consistent results"""
        return mu

    def randint(self, a, b):
        """Always return the first possible value"""
        return a


class SimulationBehavior:
    """
    Controls the stochastic behavior of the simulation.

    Modes:
    - DETERMINISTIC: Always use fixed values (means, modes) instead of random sampling
    - SEEDED: Use random number generators with fixed seeds for reproducible results
    """

    DETERMINISTIC = "deterministic"
    SEEDED = "seeded"


class RandomNumberGenerator:
    """
    Wrapper for random number generators that respects the simulation behavior setting.

    This class provides methods that mimic Python's random module but respect the
    current stochastic behavior setting.
    """

    def __init__(self, seed=None, name="generic"):
        """Initialize RNG with optional seed."""
        self.seed = seed
        self.name = name
        self._rng = random.Random(seed)

    def random(self):
        """Get random value between 0 and 1."""
        if SimulationConfig.behavior_mode == SimulationBehavior.DETERMINISTIC:
            return 0.5  # Always return middle value
        else:
            return self._rng.random()

    def triangular(self, low, high, mode=None):
        """
        Get random value from triangular distribution.

        In deterministic mode, returns the mode or middle value.
        """
        if SimulationConfig.behavior_mode == SimulationBehavior.DETERMINISTIC:
            return mode if mode is not None else (low + high) / 2
        else:
            return self._rng.triangular(low, high, mode)

    def normalvariate(self, mu, sigma):
        """
        Get random value from normal distribution.

        In deterministic mode, returns the mean.
        """
        if SimulationConfig.behavior_mode == SimulationBehavior.DETERMINISTIC:
            return mu
        else:
            return self._rng.normalvariate(mu, sigma)

    def randint(self, a, b):
        """
        Get random integer between a and b inclusive.

        In deterministic mode, returns the first value.
        """
        if SimulationConfig.behavior_mode == SimulationBehavior.DETERMINISTIC:
            return a
        else:
            return self._rng.randint(a, b)

    def choice(self, seq):
        """
        Choose random element from sequence.

        In deterministic mode, returns the first element.
        """
        if SimulationConfig.behavior_mode == SimulationBehavior.DETERMINISTIC:
            return seq[0] if seq else None
        else:
            return self._rng.choice(seq)

    def shuffle(self, x):
        """
        Shuffle a sequence in-place.

        In deterministic mode, does nothing.
        """
        if SimulationConfig.behavior_mode != SimulationBehavior.DETERMINISTIC:
            self._rng.shuffle(x)

    def reset(self):
        """Reset the RNG to use the original seed."""
        self._rng = random.Random(self.seed)


class SimulationConfig:
    """Global simulation configuration and shared state manager.

    This class manages all simulation parameters, file paths, and logging structures.
    It separates configuration from runtime data and provides validation methods.

    The class uses class methods exclusively and should not be instantiated.
    All parameters and data structures are stored as class variables.

    Class Attributes:
        runs (int): Number of simulation runs to execute
        weeks (int): Duration of each simulation run in weeks
        time_to_simulate (int): Total simulation time in minutes
        start_date (datetime): Reference start date for logging
        start_time (float): Actual execution start time
        monitoring_frequency (float): Interval for status updates
        element_entry_monitoring_frequency (int): Station monitoring interval

        # Process parameters
        MTBF_mu (float): Mean Time Between Failures (minutes)
        MTBF_sigma (float): Standard deviation for MTBF
        MTTR_mu (float): Mean Time To Repair (minutes)
        MTTR_sigma (float): Standard deviation for MTTR
        scale_disassembly_time (float): Max time multiplier for difficult disassembly
        handling_time (float): Base component handling time

        # Output flags
        visualize_structure (bool): Enable structure visualization
        timeseries_graphs (bool): Generate time series graphs
        export_eventlog (bool): Export detailed event logs

        # Random number generators
        rng_supply (random.Random): Supply process randomization
        rng_process_times (random.Random): Processing time variation
        rng_quality (random.Random): Quality-related randomization
        rng_breakdowns (random.Random): Equipment failure simulation

        # File paths
        file_path (str): Root directory path
        product_range_path (str): Path to product definitions
        structure_path (str): Path to factory structure files
        structure_file (str): Current structure file name
        distance_matrix_path (str): Path to distance matrix file
        distance_matrix (pd.DataFrame): Loaded distance matrix
        output_path (str): Path for output files

        # Logging frameworks
        log_disassembly (pd.DataFrame): Disassembly process tracking
        log_output (pd.DataFrame): Output component logging
        log_incoming_storage (pd.DataFrame): Storage content monitoring
        log_stations_abs (pd.DataFrame): Station utilization metrics (absolute)
        station_part_count_log (pd.DataFrame): Station product count over time
        inventory_log (pd.DataFrame): Inventory levels over time
        eventlog (pd.DataFrame): Detailed event log
        case_table (pd.DataFrame): Case information table
        output_table (pd.DataFrame): Final output components table
    """

    # Product variant information
    target_components_by_variant = {}  # Dict[product_type, Dict[component, quantity]]

    # Set default behavior mode
    behavior_mode = SimulationBehavior.SEEDED

    @classmethod
    def initialize_from_config(cls, config: Dict) -> None:
        """
        Initialize simulation configuration from a configuration dictionary.

        This is the main entry point for setting up all simulation parameters.
        The config comes from config_manager.py which merges:
        1. default_config.json (technical defaults)
        2. runtime_config.json (output/visualization settings)
        3. experiment config (experiment-specific settings)
        """

        # Initialize core simulation parameters
        cls._init_core_parameters(config)

        # Initialize process parameters
        cls._init_process_parameters(config)

        # Initialize resource parameters
        cls._init_resource_parameters(config)

        # Initialize output settings
        cls._init_output_settings(config)

        # Initialize visualization settings
        cls._init_visualization_settings(config)

        # Initialize monitoring settings
        cls._init_monitoring_settings(config)

        # Initialize material flow settings
        cls._init_material_flow_settings(config)

        # Initialize factory and product configurations (Disassembly scenario)
        cls._init_scenario_config(config)

        # Initialize delivery configuration
        cls._init_delivery_config(config)

        # Initialize experiment metadata
        cls._init_experiment_metadata(config)

        # Initialize random number generators
        cls._init_random_generators(config)

        # Initialize all logging structures
        cls._init_logging_structures()

        """# Final setup
        if cls.behavior_mode == SimulationBehavior.SEEDED:
            cls.reset_random_state()"""

        # Store the full configuration for reference
        cls.full_configuration = config

        # Print summary
        cls._print_config_summary()

    @classmethod
    def _init_core_parameters(cls, config: Dict) -> None:
        """Initialize core simulation parameters."""
        sim_config = config.get("simulation", {})

        # Basic run parameters (REQUIRED)
        cls.runs = sim_config.get(
            "runs", 1
        )  # Default to 1 (Logic removed to separate simulation runs)
        cls.weeks = sim_config.get("weeks", 1)
        cls.time_to_simulate = cls.weeks * 7 * 24 * 60  # Convert to minutes

        # Parse start date for timestamps in logs
        start_date_str = sim_config.get("start_date")
        try:
            cls.start_date = (
                datetime.fromisoformat(start_date_str)
                if start_date_str
                else datetime(2023, 6, 6)  # Default fallback
            )
        except (ValueError, TypeError):
            cls.start_date = datetime(2023, 6, 6)

        # Track execution time
        cls.start_time = time.time()

        # Generate timestamp for this simulation run (used in output filenames)
        cls.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Initialize paths
        cls._init_paths()

        # Behavior mode (Deterministic vs Random)
        cls.behavior_mode = sim_config.get("behavior_mode", SimulationBehavior.SEEDED)

    @classmethod
    def _init_process_parameters(cls, config: Dict) -> None:
        """Initialize process-related parameters."""
        process_config = config.get("simulation", {}).get("process", {})

        # Breakdown parameters (Mean Time Between Failures)
        cls.MTBF_mu = process_config.get("MTBF_mu", 7200)  # Default: 2 hours
        cls.MTBF_sigma = process_config.get("MTBF_sigma", 720)  # Default: 12 minutes

        # Repair parameters (Mean Time To Repair)
        cls.MTTR_mu = process_config.get("MTTR_mu", 60)  # Default: 1 hour
        cls.MTTR_sigma = process_config.get("MTTR_sigma", 10)  # Default: 10 minutes

        # Processing time scaling
        cls.scale_disassembly_time = process_config.get("scale_disassembly_time", 1.5)

        # Component handling time (minutes)
        cls.handling_time = process_config.get("handling_time", 0.5)

    @classmethod
    def _init_resource_parameters(cls, config: Dict) -> None:
        """Initialize resource-related parameters."""
        resource_config = config.get("simulation", {}).get("resources", {})

        # Vehicle parameters
        vehicle_config = resource_config.get("vehicle", {})
        cls.vehicle_speed = vehicle_config.get("speed", 2.0)  # m/s
        cls.vehicle_loading_time = vehicle_config.get("loading_time", 0.5)  # minutes
        cls.vehicle_unloading_time = vehicle_config.get("unloading_time", 0.5)

        # Maintenance parameters
        maintenance_config = resource_config.get("maintenance", {})
        cls.maintenance_response_time = maintenance_config.get("response_time", 5.0)

        # Global resource defaults
        cls.global_resource_defaults = resource_config.get("global_defaults", {})

    @classmethod
    def _init_output_settings(cls, config: Dict) -> None:
        """Initialize output-related settings"""
        output_config = config.get("simulation", {}).get("output", {})

        # Base output settings
        cls.base_output_path = output_config.get("base_output_path", "./output")

        # Core outputs (raw data)
        core = output_config.get("core_outputs", {})
        cls.export_eventlog = core.get("export_eventlog", True)
        cls.export_case_table = core.get("export_case_table", False)
        cls.export_output_table = core.get("export_output_table", False)

        # Derived outputs (computed from eventlog)
        derived = output_config.get("derived_outputs", {})
        cls.export_object_lookup = derived.get("export_object_lookup", False)
        cls.export_station_stats_absolute = derived.get(
            "export_station_stats_absolute", False
        )
        cls.export_product_time_analysis = derived.get(
            "export_product_time_analysis", False
        )
        cls.export_quality_analysis = derived.get("export_quality_analysis", False)

        # Parameter extraction (config data)
        params = output_config.get("parameter_extraction", {})
        cls.export_product_parameters = params.get("export_product_parameters", False)
        cls.export_system_parameters = params.get("export_system_parameters", False)

        # Debug outputs
        debug = output_config.get("debug_outputs", {})
        cls.export_merged_config = debug.get("export_merged_config", False)
        cls.create_debug_log = debug.get("create_debug_log", False)
        cls.time_consistency_checks = debug.get("time_consistency_checks", False)
        cls.station_state_tracking = debug.get("station_state_tracking", False)
        cls.export_monitoring_data = debug.get("export_monitoring_data", False)

    @classmethod
    def _init_visualization_settings(cls, config: Dict) -> None:
        """Initialize visualization settings."""
        viz_config = (
            config.get("simulation", {}).get("output", {}).get("visualization", {})
        )

        # Progress and structure visualization
        cls.show_progress_bar = viz_config.get("show_progress_bar", True)
        cls.visualize_structure = viz_config.get("show_structure", False)
        cls.timeseries_graphs = viz_config.get("show_timeseries_graphs", False)

        # Display settings
        display_config = (
            config.get("simulation", {}).get("output", {}).get("display", {})
        )
        cls.show_system_overview = display_config.get("show_system_overview", False)
        cls.show_production_metrics = display_config.get(
            "show_production_metrics", False
        )
        cls.show_resource_utilization = display_config.get(
            "show_resource_utilization", False
        )
        cls.show_logistics_performance = display_config.get(
            "show_logistics_performance", False
        )
        cls.show_technical_performance = display_config.get(
            "show_technical_performance", False
        )

    @classmethod
    def _init_monitoring_settings(cls, config: Dict) -> None:
        """Initialize monitoring settings."""
        monitoring_config = config.get("simulation", {}).get("monitoring", {})

        # How often to update progress (factor applied to time_to_simulate)
        cls.monitoring_frequency_factor = monitoring_config.get(
            "monitoring_frequency_factor", 100
        )
        cls.monitoring_frequency = (
            cls.time_to_simulate / cls.monitoring_frequency_factor
        )

        # How often to check station entry buffers
        cls.element_entry_monitoring_frequency = monitoring_config.get(
            "element_entry_monitoring_frequency", 60
        )

    @classmethod
    def _init_material_flow_settings(cls, config: Dict) -> None:
        """Initialize material flow settings."""
        material_flow_config = config.get("simulation", {}).get("material_flow", {})

        # Set material flow mode (pull or push)
        cls.material_flow_mode = material_flow_config.get("flow_mode", "pull")
        # DEBUG: Uncomment to trace material flow configuration
        # print(f"DEBUG: material_flow_config = {material_flow_config}")
        # print(f"DEBUG: material_flow_mode set to: {cls.material_flow_mode}")

        # Push-specific settings
        cls.push_check_frequency = material_flow_config.get("push_check_frequency", 30)

        # Dynamically set the ordering function in the functions module
        import functions

        if cls.material_flow_mode == "push":
            functions.ordering = functions.ordering_push
        else:
            # Default: Pull logic
            functions.ordering = functions.ordering_pull

    @classmethod
    def _init_scenario_config(cls, config: Dict) -> None:
        """Initialize factory structure and product configurations."""
        # Factory structure
        factory_config = config["factory_structure"]
        if factory_config:
            cls.structure_file = factory_config.get("file")
            cls.distance_matrix_file = factory_config.get("distance_matrix")
            cls.factory_data = factory_config.get("data", {})

            # Update distance matrix path
            cls._update_distance_matrix_path()

        # Product configuration
        if "products" not in config:
            raise ValueError("products configuration is required")

        if not config["products"]:
            raise ValueError("At least one product must be configured")

        cls.enabled_product_files = [p["file"] for p in config["products"]]
        cls.product_configurations = config["products"]

        # Store target components lookup (NEW)

        cls.target_components_by_variant = {}
        for product_config in config["products"]:
            variant_type = product_config["data"]["variant"]["type"]
            cls.target_components_by_variant[variant_type] = product_config[
                "target_components"
            ]

    @classmethod
    def _init_delivery_config(cls, config: Dict) -> None:
        """Initialize product delivery configuration."""
        delivery_config = config.get("product_delivery", {})

        # Delivery mode
        cls.delivery_mode = delivery_config.get("mode", "random")

        # Delivery schedule (if specified)
        cls.delivery_schedule_file = delivery_config.get("schedule_file")

    @classmethod
    def _init_experiment_metadata(cls, config: Dict) -> None:
        """Initialize experiment metadata."""
        experiment = config.get("experiment", {})

        cls.experiment_id = experiment.get("id", "unknown")
        cls.experiment_name = experiment.get("name", "")
        cls.experiment_description = experiment.get("description", "")
        cls.output_prefix = experiment.get("output_prefix", cls.experiment_id)

    @classmethod
    def _init_random_generators(cls, config: Dict) -> None:
        """Initialize random number generators with proper seeds."""
        # Get random seeds from configuration
        random_config = config.get("simulation", {}).get("random_seeds", {})

        # Store original seeds
        cls.original_seeds = {
            "supply": random_config.get("supply", 42),
            "process_times": random_config.get("process_times", 43),
            "quality": random_config.get("quality", 44),
            "breakdowns": random_config.get("breakdowns", 45),
            "transport": random_config.get("transport", 46),
            "components": random_config.get("components", 47),
        }

        # Create RNG instances with fixed seeds
        cls.rng_supply = RandomNumberGenerator(
            seed=cls.original_seeds["supply"], name="supply"
        )
        cls.rng_process_times = RandomNumberGenerator(
            seed=cls.original_seeds["process_times"], name="process_times"
        )
        cls.rng_quality = RandomNumberGenerator(
            seed=cls.original_seeds["quality"], name="quality"
        )
        cls.rng_breakdowns = RandomNumberGenerator(
            seed=cls.original_seeds["breakdowns"], name="breakdowns"
        )
        cls.rng_transport = RandomNumberGenerator(
            seed=cls.original_seeds["transport"], name="transport"
        )
        cls.rng_components = RandomNumberGenerator(
            seed=cls.original_seeds["components"], name="components"
        )

    @classmethod
    def _print_config_summary(cls):
        """Print a summary of the loaded configuration."""
        print("\nConfiguration Summary:")
        print("-" * 50)
        print(f"Experiment: {getattr(cls, 'experiment_id', 'Unknown')}")
        print(f"Runs: {cls.runs} x {cls.weeks} weeks")
        print(f"Material Flow: {getattr(cls, 'material_flow_mode', 'pull')}")
        print(f"Behavior: {cls.behavior_mode}")
        print("-" * 50)

    @classmethod
    def set_behavior_mode(cls, mode):
        """
        Set the stochastic behavior mode of the simulation.

        Args:
            mode: One of SimulationBehavior.DETERMINISTIC,
                 or SimulationBehavior.SEEDED
        """
        cls.behavior_mode = mode

        if mode == SimulationBehavior.SEEDED:
            # Reset RNGs to use original seeds
            cls.rng_supply.reset()
            cls.rng_process_times.reset()
            cls.rng_quality.reset()
            cls.rng_breakdowns.reset()

    """
    @classmethod
    def reset_random_state(cls):
        cls.rng_supply.reset()
        cls.rng_process_times.reset()
        cls.rng_quality.reset()
        cls.rng_breakdowns.reset()
        cls.rng_transport.reset()
        cls.events_list = []  # Reset events list"""

    @classmethod
    def _init_paths(cls) -> None:
        """
        Initialize and validate all file paths required for simulation.

        No defaults are set - all paths must exist or be creatable.

        Raises:
            FileNotFoundError: If required directories don't exist
        """
        # Determine root path from current file location
        cls.file_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # Set up input data paths
        cls.structure_path = os.path.join(cls.file_path, "config", "system_config")
        cls.product_range_path = os.path.join(cls.file_path, "config", "product_config")

        # Validate required directories exist
        if not os.path.exists(cls.structure_path):
            raise FileNotFoundError(f"Structure path not found: {cls.structure_path}")

        if not os.path.exists(cls.product_range_path):
            raise FileNotFoundError(
                f"Product range path not found: {cls.product_range_path}"
            )

        # Set up and create output directory
        cls.output_path = os.path.join(cls.file_path, "output/")
        os.makedirs(cls.output_path, exist_ok=True)

    @classmethod
    def _update_distance_matrix_path(cls) -> None:
        """Load the distance matrix from the specified file."""
        if not hasattr(cls, "distance_matrix_file") or not cls.distance_matrix_file:
            raise ValueError("distance_matrix must be specified in factory_structure")

        # Construct full path
        cls.distance_matrix_path = os.path.join(
            cls.file_path, "config", "system_config", cls.distance_matrix_file
        )

        # Load and validate distance matrix
        if not os.path.exists(cls.distance_matrix_path):
            raise FileNotFoundError(
                f"Distance matrix not found: {cls.distance_matrix_path}"
            )

        try:
            cls.distance_matrix = pd.read_csv(
                cls.distance_matrix_path, sep=";", index_col=0
            )
        except Exception as e:
            raise ValueError(
                f"Error loading distance matrix from {cls.distance_matrix_path}: {e}"
            )

    @classmethod
    def _init_logging_structures(cls) -> None:
        """
        Initialize all DataFrame structures used for logging simulation data.

        Creates empty DataFrames for:
        - Disassembly process tracking
        - Output component logging
        - Storage content monitoring
        - Station utilization metrics
        - Inventory tracking
        - Event logging
        """
        # Process tracking logs
        cls.log_disassembly = pd.DataFrame(
            columns=[
                "ID",
                "product_type",
                "entry_time",
                "done_time",
                "lead_time",
                "level_of_disassembly",
                "handling_time",
                "done",
            ]
        )

        cls.log_output = pd.DataFrame(
            columns=[
                "component_type",
                "parentID",
                "parent_entry_time",
                "exit_time",
                "lead_time",
            ]
        )

        # Storage and station monitoring
        cls.log_incoming_storage = pd.DataFrame(
            columns=["store", "product_type", "product_count"]
        )

        cls.log_stations_abs = pd.DataFrame(
            columns=[
                "station",
                "busy_time",
                "blocked_time",
                "waiting_time",
                "failure_time",
                "closed_time",
                "product_count",
            ]
        )

        # Time series data
        cls.station_part_count_log = pd.DataFrame(columns=["time", "station", "count"])
        cls.inventory_log = pd.DataFrame()

        # Main simulation logs
        cls.events_list = []  # Initialize the events list for the new event logging approach

        # Define the revised event log structure with component tracking
        cls.eventlog = pd.DataFrame(
            columns=[
                "caseID",
                "objectID",
                "object_type",
                "object_name",
                "timestamp",
                "resource_id",
                "action",
                "component",
                "parent_component",
            ]
        )

        cls.case_table = pd.DataFrame(
            columns=["caseID", "product_type", "delivery_time", "condition"]
        )

        cls.output_table = pd.DataFrame(
            columns=[
                "caseID",
                "objectID",
                "object_type",
                "object_name",
                "delivery_time",
                "output_time",
                "condition",
                "content",
            ]
        )

    @staticmethod
    def generate_filename(
        file_type: str,
        experiment_id: Optional[str] = None,
        run_number: Optional[int] = None,
        timestamp: Optional[str] = None,
        category: str = "raw",  # Categories: raw, comp, params, debug, config
    ) -> str:
        """
        Generate standardized filename with category prefix.

        Categories:
        - raw: Core simulation outputs (eventlog, case_table, output_table)
        - exp: Experiment configuration data
        - comp: Computed from raw data
        - params: Extracted parameters for analysis
        - debug: Debug outputs
        - config: merged config
        """
        parts = []

        # Add timestamp at first position for chronological sorting
        if timestamp:
            parts.append(timestamp)
        else:
            parts.append(datetime.now().strftime("%Y%m%d_%H%M%S"))

        # Add category
        parts.append(category)

        # Add file type
        parts.append(file_type)

        # Add experiment ID
        if experiment_id:
            parts.append(experiment_id)

        # Add run number
        if run_number is not None:
            parts.append(f"run{run_number + 1}")

        # Join with underscores
        filename = "_".join(parts)

        # Add appropriate extension
        if file_type in ["product_parameters", "system_parameters", "merged_config"]:
            filename += ".json"
        elif file_type == "debug_log":
            filename += ".txt"
        else:
            filename += ".csv"

        return filename

    @classmethod
    def get_experiment_info(cls) -> Dict:
        """Get experiment metadata."""
        return {
            "id": getattr(cls, "experiment_id", "unknown"),
            "name": getattr(cls, "experiment_name", ""),
            "description": getattr(cls, "experiment_description", ""),
            "output_prefix": getattr(cls, "output_prefix", ""),
        }

    @classmethod
    def get_product_config(cls, product_file: str) -> Optional[Dict]:
        """
        Get configuration for a specific product.

        Args:
            product_file: Product file name

        Returns:
            Product configuration dict or None
        """
        if not hasattr(cls, "product_configurations"):
            return None

        for product in cls.product_configurations:
            if product["file"] == product_file:
                return product

        return None


# Alias for backward compatibility
g = SimulationConfig

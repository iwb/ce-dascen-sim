"""
File: config_manager.py
Location: Project root
Description: Configuration management system with hierarchical merging
Author: Patrick Jordan
Version: 2025-10

Handles configuration loading and merging from:
1. default_config.json - Technical defaults (process parameters, resources)
2. runtime_config.json - Output and visualization settings
3. experiment files - Experiment-specific settings (factory, products, duration)
4. experiment overrides - Optional overrides in experiment file

Configuration hierarchy: later overrides earlier
"""

import json
import os
from typing import Dict, List, Optional, Union
from datetime import datetime

import helper_functions


class ConfigurationManager:
    """Reorganized configuration management for disassembly simulation experiments.

    Configuration hierarchy (later overrides earlier):
    1. default_config.json - Technical defaults for processes
    2. runtime_config.json - Output/visualization settings
    3. experiment_config.json - Experiment-specific settings
    4. experiment overrides - Optional overrides in experiment file
    """

    def __init__(self, config_root: str):
        """Initialize configuration manager with root configuration directory.

        Args:
            config_root: Root directory containing all configuration files
        """
        self.config_root = config_root
        self.experiment_index = None
        self.current_experiment = None
        self.merged_config = {}

    def load_experiment(self, experiment_id: str) -> Dict:
        """Load complete configuration for a specific experiment.

        Args:
            experiment_id: ID of the experiment to load from exp_index.json

        Returns:
            Dict: Complete merged configuration for the experiment

        Raises:
            ValueError: If experiment_id not found or configuration invalid
            FileNotFoundError: If required configuration files missing
        """
        # Load experiment index
        self._load_experiment_index()

        # Find experiment in index
        experiment_entry = self._find_experiment(experiment_id)
        if not experiment_entry:
            raise ValueError(f"Experiment '{experiment_id}' not found in index")

        # Load experiment-specific configuration
        exp_config_path = os.path.join(
            self.config_root, "experiments", experiment_entry["config_file"]
        )
        experiment_config = self._load_json_file(exp_config_path)
        self.current_experiment = experiment_config

        # Build merged configuration with cleaner hierarchy
        merged_config = self._build_merged_config(experiment_config, experiment_entry)

        self.merged_config = merged_config
        return merged_config

    def _build_merged_config(
        self, experiment_config: Dict, experiment_entry: Dict
    ) -> Dict:
        """Build the merged configuration.

        Args:
            experiment_config: The experiment-specific configuration
            experiment_entry: The experiment entry from index

        Returns:
            Dict: Complete merged configuration
        """
        # Start with empty config
        merged_config = {"version": "2.0"}

        # 1. Load technical defaults (process parameters, resources)
        default_config_path = os.path.join(self.config_root, "default_config.json")
        if os.path.exists(default_config_path):
            default_config = self._load_json_file(default_config_path)
            # Add process and resource defaults to simulation section
            merged_config["simulation"] = {
                "process": default_config.get("process", {}),
                "resources": default_config.get("resources", {}),
                "behavior_mode": default_config.get("behavior_mode", "seeded"),
                "random_seeds": default_config.get("random_seeds", {}),
            }

        # 2. Load runtime config and map to where g.py expects settings
        runtime_config_path = os.path.join(self.config_root, "runtime_config.json")
        if os.path.exists(runtime_config_path):
            runtime_config = self._load_json_file(runtime_config_path)

            # Initialize output structure as expected by g.py
            if "output" not in merged_config["simulation"]:
                merged_config["simulation"]["output"] = {}

            # Map output settings with grouped structure (runtime_config v.04)
            if "output" in runtime_config:
                output = runtime_config["output"]

                # Map base settings
                merged_config["simulation"]["output"]["base_output_path"] = output.get(
                    "base_output_path", "./output"
                )

                # Map all output sections
                output_sections = [
                    "core_outputs",
                    "derived_outputs",
                    "parameter_extraction",
                    "debug_outputs",
                ]

                for section in output_sections:
                    if section in output:
                        merged_config["simulation"]["output"][section] = output[section]

            # Visualization settings
            if "visualization" in runtime_config:
                viz = runtime_config["visualization"]
                merged_config["simulation"]["output"]["visualization"] = {
                    "show_progress_bar": viz.get("show_progress_bar", True),
                    "show_structure": viz.get("show_structure", False),
                    "show_timeseries_graphs": viz.get("show_timeseries_graphs", False),
                }

            # Display settings
            if "display" in runtime_config:
                merged_config["simulation"]["output"]["display"] = runtime_config[
                    "display"
                ].copy()

            # Monitoring settings
            if "monitoring" in runtime_config:
                merged_config["simulation"]["monitoring"] = runtime_config["monitoring"]

            # Material flow settings
            if "material_flow" in runtime_config:
                merged_config["simulation"]["material_flow"] = runtime_config[
                    "material_flow"
                ]

            """# Map debug settings (g.py looks for these under simulation.debug)
            if "debug" in runtime_config:
                merged_config["simulation"]["debug"] = runtime_config["debug"]"""

            # Map performance settings
            if "performance" in runtime_config:
                merged_config["simulation"]["performance"] = runtime_config[
                    "performance"
                ]

        # 3. Apply experiment-specific settings
        # Add simulation parameters (runs, weeks, start_date)
        if "simulation" in experiment_config:
            for key, value in experiment_config["simulation"].items():
                merged_config["simulation"][key] = value

        # 4. Load factory structure
        factory_structure = self._load_factory_structure(experiment_config)
        merged_config["factory_structure"] = factory_structure

        # 5. Load product configurations
        products = self._load_product_configurations(experiment_config)
        merged_config["products"] = products

        # 6. Load delivery configuration
        if "product_delivery" in experiment_config:
            merged_config["product_delivery"] = experiment_config["product_delivery"]

        # 7. Apply any experiment-specific overrides
        if "overrides" in experiment_config:
            self._apply_overrides(merged_config, experiment_config["overrides"])

        # 8. Add experiment metadata
        merged_config["experiment"] = {
            "id": experiment_config["experiment_id"],
            "name": experiment_entry.get("name", ""),
            "description": experiment_entry.get("description", ""),
            "output_prefix": experiment_config.get(
                "output_prefix", experiment_config["experiment_id"]
            ),
        }

        return merged_config

    def _apply_overrides(self, config: Dict, overrides: Dict) -> None:
        """Apply experiment-specific overrides to the configuration.

        Uses deep merging to preserve nested settings.

        Args:
            config: The configuration to modify
            overrides: Dictionary of overrides to apply

        Raises:
            ValueError: If an unknown override section is encountered
        """
        # Define valid override sections and where they map to
        valid_sections = {
            "comment": None,  # Skip comments
            "process": "simulation",
            "resources": "simulation",
            "behavior_mode": "simulation",
            "random_seeds": "simulation",
            "monitoring": "simulation",
            "performance": "simulation",
            "material_flow": "simulation",
            "output": "simulation.output",
            "visualization": "simulation.output.visualization",
            "display": "simulation.output.display",
            "debug": "simulation.debug",
        }

        for section, settings in overrides.items():
            if section == "comment":
                continue

            # Check if this is a variant-specific override (e.g., "variant1", "variant2")
            if section.lower().startswith("variant"):
                # Store variant overrides in a dedicated location
                if "variant_overrides" not in config:
                    config["variant_overrides"] = {}
                config["variant_overrides"][section] = settings
                continue

            # Check if this is a valid override section
            if section not in valid_sections:
                raise ValueError(
                    f"Unknown override section '{section}'. Valid sections are: "
                    f"{', '.join([s for s in valid_sections.keys() if s != 'comment'])}"
                )

            # Get the target path for this section
            target_path = valid_sections[section]

            if target_path is None:
                # Skip sections like 'comment'
                continue

            # Navigate to the target location in config
            if "." in target_path:
                # Handle nested paths like 'simulation.output.visualization'
                path_parts = target_path.split(".")
                current = config

                for part in path_parts:
                    if part not in current:
                        current[part] = {}
                    current = current[part]

                # Apply the override with deep merge
                if isinstance(settings, dict) and isinstance(current, dict):
                    self._deep_merge_dict(current, settings)
                else:
                    # Complete replacement for non-dict values
                    parent = config
                    for part in path_parts[:-1]:
                        parent = parent[part]
                    parent[path_parts[-1]] = settings

            else:
                # Simple path like 'simulation'
                if target_path not in config:
                    config[target_path] = {}

                if section not in config[target_path]:
                    config[target_path][section] = {}

                # Apply the override
                if isinstance(settings, dict) and isinstance(
                    config[target_path].get(section), dict
                ):
                    self._deep_merge_dict(config[target_path][section], settings)
                else:
                    config[target_path][section] = settings

            # Special handling for visualization name mappings
            if section == "visualization":
                self._apply_visualization_mappings(config)

    def _apply_visualization_mappings(self, config: Dict) -> None:
        """Apply legacy name mappings for visualization settings."""
        viz_config = (
            config.get("simulation", {}).get("output", {}).get("visualization", {})
        )

        # Handle legacy names
        if "visualize_structure" in viz_config:
            viz_config["show_structure"] = viz_config.pop("visualize_structure")
        if "timeseries_graphs" in viz_config:
            viz_config["show_timeseries_graphs"] = viz_config.pop("timeseries_graphs")

    def _load_experiment_index(self) -> None:
        """Load the experiment index file."""
        index_path = os.path.join(self.config_root, "experiments", "exp_index.json")
        self.experiment_index = self._load_json_file(index_path)

    def _find_experiment(self, experiment_id: str) -> Optional[Dict]:
        """Find experiment entry in the index."""
        for exp in self.experiment_index.get("experiments", []):
            if exp["id"] == experiment_id:
                return exp
        return None

    def _load_json_file(self, file_path: str) -> Dict:
        """Load and parse a JSON file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {file_path}: {e}")

    def _load_factory_structure(self, experiment_config: Dict) -> Dict:
        """Load factory structure configuration."""
        if "factory_structure" not in experiment_config:
            raise ValueError("No factory structure specified in experiment")

        factory_struct = experiment_config["factory_structure"]

        # Check required fields
        if "file" not in factory_struct:
            raise ValueError("No factory structure file specified")
        if "distance_matrix" not in factory_struct:
            raise ValueError("No distance matrix specified in factory_structure")

        structure_file = factory_struct["file"]
        structure_path = os.path.join(self.config_root, "system_config", structure_file)

        structure_data = self._load_json_file(structure_path)

        return {
            "file": structure_file,
            "distance_matrix": factory_struct["distance_matrix"],
            "data": structure_data,
        }

    def _load_product_configurations(self, experiment_config: Dict) -> List[Dict]:
        """Load all product configurations specified in the experiment."""
        if "products" not in experiment_config:
            return []

        loaded_products = []
        for product_spec in experiment_config["products"]:
            if not product_spec.get("enabled", True):
                continue

            product_file = product_spec["file"]
            product_path = os.path.join(
                self.config_root, "product_config", product_file
            )

            product_data = self._load_json_file(product_path)

            # Extract target components ONCE per variant
            variant_type = product_data["variant"]["type"]
            target_components = helper_functions.get_target_components(
                product_data["variant"]["structure"]
            )

            loaded_product = {
                "file": product_file,
                "data": product_data,
                "target_components": target_components,
            }

            loaded_products.append(loaded_product)

        return loaded_products

    def get_value(self, key_path: str, default=None):
        """Get a configuration value using dot notation.

        Args:
            key_path: Dot-separated path to the value (e.g., "simulation.runs")
            default: Default value if key not found

        Returns:
            The configuration value or default
        """
        keys = key_path.split(".")
        value = self.merged_config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def validate_configuration(self) -> List[str]:
        """Validate the loaded configuration for completeness and consistency.

        Returns:
            List[str]: List of validation errors (empty if valid)
        """
        errors = []

        # Check required top-level keys
        required_keys = ["simulation", "factory_structure", "products"]
        for key in required_keys:
            if key not in self.merged_config:
                errors.append(f"Missing required configuration section: {key}")

        # Validate simulation parameters
        if "simulation" in self.merged_config:
            sim_config = self.merged_config["simulation"]

            # Use default of 1 for runs if not specified
            # (Removed to keep simulation environments separate)
            if sim_config.get("runs", 1) < 1:
                errors.append("Simulation runs must be at least 1")
            if sim_config.get("weeks", 0) < 0.1:
                errors.append("Simulation duration must be positive")

        # Validate products
        if "products" in self.merged_config:
            if not self.merged_config["products"]:
                errors.append("At least one product must be enabled")

        # Validate delivery configuration
        if "product_delivery" in self.merged_config:
            delivery = self.merged_config["product_delivery"]
            valid_modes = ["random", "scheduled", "mixed"]
            if delivery.get("mode") not in valid_modes:
                errors.append(f"Invalid delivery mode: {delivery.get('mode')}")

        return errors

    def export_merged_config(self, output_path: str) -> None:
        """Export the merged configuration to a file for debugging/documentation.

        Args:
            output_path: Path where to save the merged configuration
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.merged_config, f, indent=2, default=str)

        print(f"Merged configuration exported to: {output_path}")

    def print_config_sources(self) -> None:
        """Print information about where each configuration value comes from."""
        print("\nConfiguration Sources:")
        print("-" * 50)
        print("1. Technical Defaults (default_config.json):")
        print("   - Process parameters (MTBF, MTTR, times)")
        print("   - Resource defaults (vehicle, maintenance)")
        print("   - Random seeds")
        print("\n2. Runtime Settings (runtime_config.json):")
        print("   - Output configuration")
        print("   - Visualization settings")
        print("   - Monitoring parameters")
        print("   - Performance options")
        print("\n3. Experiment Settings (exp_*.json):")
        print("   - Simulation runs and duration")
        print("   - Factory structure selection")
        print("   - Product selection")
        print("   - Delivery mode")
        print("   - Optional overrides")

    def _deep_merge_dict(self, base_dict: Dict, override_dict: Dict) -> None:
        """Deep merge override_dict into base_dict in-place.

        Args:
            base_dict: The dictionary to merge into (modified in-place)
            override_dict: The dictionary with override values
        """
        for key, value in override_dict.items():
            if (
                key in base_dict
                and isinstance(base_dict[key], dict)
                and isinstance(value, dict)
            ):
                # Recursively merge nested dictionaries
                self._deep_merge_dict(base_dict[key], value)
            else:
                # Direct assignment for non-dict values or new keys
                base_dict[key] = value

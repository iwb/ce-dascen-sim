"""
File: validation.py
Location: /src/validation.py
Description: Input validation module for simulation configuration and files
Authors: Patrick Jordan, Lasse Streibel
Version: 2025-10

Validates all simulation inputs before execution:
- Directory structure and file existence
- Factory structure configuration format
- Product definition files and parameters
- Simulation parameters (runs, duration, etc.)
- Output configuration and directory access

Raises appropriate errors (FileNotFoundError, ValueError, OSError) if validation fails.
"""

import os
import json
import pandas as pd
from src.g import g, SimulationConfig


def validate_inputs():
    """
    Validate all required inputs before starting simulation runs.

    Performs hierarchical validation:
    1. Directory Structure: Checks if all required directories exist
    2. Structure File: Validates factory structure definition
    3. Product Files: Validates product definitions and parameters
    4. Simulation Parameters: Checks global simulation settings
    5. Output Configuration: Ensures output can be saved

    Raises:
        FileNotFoundError: If required files or directories are missing
        ValueError: If file contents or configurations are invalid
        OSError: If output directory cannot be created

    Returns:
        bool: True if all validations pass
    """

    # Check required config files exist
    config_dir = os.path.join(SimulationConfig.file_path, "config")
    required_files = [
        os.path.join(config_dir, "default_config.json"),
        os.path.join(config_dir, "runtime_config.json"),
    ]

    for file_path in required_files:
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"Required configuration file not found: {file_path}"
            )

    # Check base directory exists
    if not os.path.exists(g.file_path):
        raise FileNotFoundError(f"Base path not found: {g.file_path}")

    # Check factory structure directory exists
    structure_path = os.path.join(g.file_path, g.structure_path)
    if not os.path.exists(structure_path):
        raise FileNotFoundError(f"Structure path not found: {structure_path}")

    # Check product definitions directory exists
    product_range_path = os.path.join(
        SimulationConfig.file_path, "config", "product_config"
    )
    if not os.path.exists(product_range_path):
        raise FileNotFoundError(f"Product range path not found: {product_range_path}")

    # Verify structure file exists and has correct format
    structure_file = os.path.join(structure_path, SimulationConfig.structure_file)
    if not os.path.exists(structure_file):
        raise FileNotFoundError(f"Structure file not found: {structure_file}")

    # Attempt to load and validate structure file content
    try:
        with open(structure_file, "r") as f:
            structure_data = json.load(f)
            # Check for required top-level key
            if "factory" not in structure_data:
                raise ValueError("Invalid structure file format: missing 'factory' key")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in structure file: {structure_file}")

    # Product Files Validation
    # Get list of all JSON files in product range directory (including subdirectories)
    product_files = []
    for root, dirs, files in os.walk(product_range_path):
        for file in files:
            if file.endswith(".json"):
                product_files.append(os.path.join(root, file))

    if not product_files:
        raise FileNotFoundError(
            f"No product definition files found in {product_range_path}"
        )

    # Validate each product file
    for product_file_path in product_files:
        try:
            with open(product_file_path, "r") as f:
                product_data = json.load(f)
                # Check for required top-level structure
                if "variant" not in product_data:
                    raise ValueError(
                        f"Invalid product file format in {product_file_path}: missing 'variant' key"
                    )

                # Check for all required parameters in variant definition
                required_params = [
                    "type",  # Product type identifier
                    "volume_per_week_min",  # Minimum weekly volume
                    "volume_per_week_mu",  # Mean weekly volume
                    "volume_per_week_max",  # Maximum weekly volume
                    "structure",  # Product structure definition
                ]

                for param in required_params:
                    if param not in product_data["variant"]:
                        raise ValueError(
                            f"Missing required parameter '{param}' in {product_file_path}"
                        )
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in product file: {product_file_path}")

    # Simulation Parameters Validation
    # Verify number of simulation runs
    if not isinstance(g.runs, int) or g.runs <= 0:
        raise ValueError(f"Invalid number of runs: {g.runs}")

    # Verify simulation duration
    if not isinstance(g.time_to_simulate, (int, float)) or g.time_to_simulate <= 0:
        raise ValueError(f"Invalid simulation time: {g.time_to_simulate}")

    # Output Configuration Validation
    # Create output directory if event logging is enabled
    if g.export_eventlog:
        output_path = os.path.join(g.file_path, "output")
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
                print(f"Created output directory: {output_path}")
            except OSError as e:
                raise OSError(f"Cannot create output directory: {e}")

    print("Input validation completed successfully.")

    return True

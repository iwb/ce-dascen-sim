"""
File: run_simulation.py
Location: Project root
Description: Main experiment runner with CLI for the flexible disassembly simulation tool
Author: Patrick Jordan
Version: 2025-10

This script provides command-line interface to:
- List available experiments
- Run single experiments
- Run batch experiments
- Validate configurations (dry-run mode)

Usage:
    python run_simulation.py list
    python run_simulation.py run --experiment exp01_baseline_workshop_pull
    python run_simulation.py batch --experiments exp01 exp02 exp03
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

import helper_functions

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Import simulation modules
try:
    from config_manager import ConfigurationManager
    from src.g import SimulationConfig, g
    from src.simulation import Simulation
    import src.validation as validation
    import src.logging as logging

    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the project root directory")
    IMPORTS_AVAILABLE = False


class ExperimentRunner:
    """Manages the execution of simulation experiments."""

    def __init__(self, config_root: str = None):
        """Initialize the experiment runner.

        Args:
            config_root: Root directory for configuration files
        """
        if config_root is None:
            config_root = os.path.join(project_root, "config")

        self.config_root = config_root
        self.config_manager = ConfigurationManager(config_root)

    def list_experiments(self) -> None:
        """List all available experiments from the index."""
        try:
            # Load experiment index
            index_path = os.path.join(self.config_root, "experiments", "exp_index.json")
            with open(index_path, "r") as f:
                index = json.load(f)

            print("\nAvailable Experiments:")
            print("=" * 80)

            # Group by category
            categories = {}
            for exp in index["experiments"]:
                category = exp.get("category", "Uncategorized")
                if category not in categories:
                    categories[category] = []
                categories[category].append(exp)

            # Display by category
            for category, experiments in sorted(categories.items()):
                print(f"\n{category}:")
                print("-" * 40)

                for exp in experiments:
                    status = "[x]" if exp.get("active", True) else "[ ]"
                    print(f"  {status} {exp['id']:.<30} {exp.get('name', 'Unnamed')}")

                    if exp.get("description"):
                        # Wrap description text
                        desc_lines = self._wrap_text(exp["description"], 70, 6)
                        for line in desc_lines:
                            print(line)

            print("\n" + "=" * 80)
            print(f"Total experiments: {len(index['experiments'])}")
            print(
                "\nUse 'python run_simulation.py run --experiment <id>' to run an experiment"
            )

        except FileNotFoundError:
            print("Error: Experiment index not found!")
            print(f"Expected location: {index_path}")
        except Exception as e:
            print(f"Error listing experiments: {e}")

    def _wrap_text(self, text: str, width: int, indent: int) -> List[str]:
        """Wrap text to specified width with indentation."""
        words = text.split()
        lines = []
        current_line = " " * indent

        for word in words:
            if len(current_line) + len(word) + 1 <= width + indent:
                current_line += word + " "
            else:
                lines.append(current_line.rstrip())
                current_line = " " * indent + word + " "

        if current_line.strip():
            lines.append(current_line.rstrip())

        return lines

    def run_experiment(
        self, experiment_id: str, dry_run: bool = False, run_number: int = 1
    ) -> None:
        """Run a single experiment.

        Args:
            experiment_id: ID of the experiment to run
            dry_run: If True, only validate configuration without running
            run_number: Run number for output file naming (default: 1)
        """
        try:
            print(f"\n{'=' * 80}")
            print(f"Running Experiment: {experiment_id} (Run {run_number})")
            print(f"{'=' * 80}")

            # Load configuration
            print("\nLoading configuration...")
            config = self.config_manager.load_experiment(experiment_id)
            print("  [OK] Configuration loaded successfully")

            # Create output directory
            output_prefix = config["experiment"].get("output_prefix", experiment_id)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Include run number in directory name for clarity
            experiment_output_dir = os.path.join(
                project_root,
                "output",
                f"{timestamp}_{output_prefix}_run{run_number:03d}",
            )
            os.makedirs(experiment_output_dir, exist_ok=True)

            # Export merged configuration if requested
            export_merged = (
                config.get("simulation", {})
                .get("output", {})
                .get("debug_outputs", {})
                .get("export_merged_config", False)
            )
            if export_merged:
                debug_dir = os.path.join(experiment_output_dir, "debug")
                os.makedirs(debug_dir, exist_ok=True)

                filename = f"{timestamp}_config_merged_config_{output_prefix}.json"
                config_output_path = os.path.join(debug_dir, filename)

                self.config_manager.export_merged_config(config_output_path)
                print(f"  [OK] Merged configuration exported to debug/{filename}")

            # Override output path
            config["simulation"]["output"]["output_path"] = experiment_output_dir

            # Validation check
            print("\nValidating configuration...")
            errors = self.config_manager.validate_configuration()
            if errors:
                print("  [FAIL] Configuration validation failed:")
                for error in errors:
                    print(f"    - {error}")
                raise ValueError("Invalid configuration")
            print("  [OK] Configuration is valid")

            # Dry run check
            if dry_run:
                print("\nDry run completed - configuration is valid")
                return

            # Initialize SimulationConfig
            print("\nInitializing simulation environment...")
            SimulationConfig.initialize_from_config(config)
            SimulationConfig.output_path = experiment_output_dir

            # Validate all inputs
            print("Validating inputs...")
            validation.validate_inputs()
            print("  [OK] All inputs valid")

            # Run simulation
            print("\nStarting simulation...")
            print("-" * 80)

            weeks = config.get("simulation", {}).get("weeks", 1)
            print(f"Duration: {weeks} weeks")

            # Track timing
            run_start_time = time.time()

            # Create and run simulation
            sim = Simulation()
            sim.run()

            run_end_time = time.time()

            print(
                f"[OK] Simulation completed in {run_end_time - run_start_time:.2f} seconds"
            )

            # Log station data if needed
            if (
                SimulationConfig.export_station_stats_absolute
                or SimulationConfig.show_resource_utilization
            ):
                logging.log_station_data(sim)

            # Export data
            logging.export_to_csv_v2(
                run_number - 1,  # Use 0-based for backward compatibility
                output_path=experiment_output_dir,
                simulation_run=sim,
            )

            # Print export confirmation if anything was exported
            if any(
                [
                    SimulationConfig.export_eventlog,
                    SimulationConfig.export_case_table,
                    SimulationConfig.export_output_table,
                    SimulationConfig.export_object_lookup,
                    SimulationConfig.export_station_stats_absolute,
                    SimulationConfig.export_monitoring_data,
                ]
            ):
                print("[OK] Data exported")

            # Show results if enabled
            if any(
                [
                    SimulationConfig.show_system_overview,
                    SimulationConfig.show_production_metrics,
                    SimulationConfig.show_resource_utilization,
                    SimulationConfig.show_logistics_performance,
                    SimulationConfig.show_technical_performance,
                ]
            ):
                logging.print_results(run_number - 1, run_start_time, run_end_time, sim)

            # Show timeseries if enabled
            if SimulationConfig.timeseries_graphs:
                logging.plot_timeseries()

            # Show structure visualization if enabled
            if SimulationConfig.visualize_structure:
                structure_path = os.path.join(
                    SimulationConfig.file_path,
                    "config",
                    "system_config",
                    SimulationConfig.structure_file,
                )
                helper_functions.visualize_structure(
                    structure_path, sim.all_predecessors
                )

            print("\n" + "=" * 80)
            print(
                f"Experiment '{experiment_id}' Run {run_number} completed successfully!"
            )
            print(f"Results saved to: {experiment_output_dir}")

        except Exception as e:
            print(f"\n[ERROR] Error running experiment: {e}")
            raise

    def run_batch(
        self, experiment_ids: List[str], continue_on_error: bool = True
    ) -> None:
        """Run multiple experiments in sequence.

        Args:
            experiment_ids: List of experiment IDs to run
            continue_on_error: Whether to continue if an experiment fails
        """
        print(f"\n{'=' * 80}")
        print(f"Batch Execution: {len(experiment_ids)} experiments")
        print(f"{'=' * 80}")

        results = {"successful": [], "failed": []}

        for i, exp_id in enumerate(experiment_ids, 1):
            print(f"\n[{i}/{len(experiment_ids)}] ", end="")

            try:
                self.run_experiment(exp_id)
                results["successful"].append(exp_id)
            except Exception as e:
                results["failed"].append((exp_id, str(e)))
                if not continue_on_error:
                    print("\nBatch execution stopped due to error.")
                    break

        # Print summary
        print(f"\n{'=' * 80}")
        print("Batch Execution Summary")
        print(f"{'=' * 80}")
        print(f"Total: {len(experiment_ids)}")
        print(f"Successful: {len(results['successful'])}")
        print(f"Failed: {len(results['failed'])}")

        if results["failed"]:
            print("\nFailed experiments:")
            for exp_id, error in results["failed"]:
                print(f"  - {exp_id}: {error}")


def main():
    """Main entry point for the script."""
    if not IMPORTS_AVAILABLE:
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Run simulation experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all available experiments
  python run_simulation.py list

  # Run a single experiment
  python run_simulation.py run --experiment exp1_workshop_full

  # Run with dry-run (validation only)
  python run_simulation.py run --experiment exp1_workshop_full --dry-run

  # Run multiple experiments
  python run_simulation.py batch --experiments exp1_workshop_full exp2_workshop_reduced

  # Run batch with stop-on-error
  python run_simulation.py batch --experiments exp1 exp2 exp3 --stop-on-error
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List command
    list_parser = subparsers.add_parser("list", help="List available experiments")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a single experiment")
    run_parser.add_argument(
        "--experiment", "-e", required=True, help="Experiment ID to run"
    )
    run_parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Validate configuration without running simulation",
    )

    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Run multiple experiments")
    batch_parser.add_argument(
        "--experiments",
        "-e",
        nargs="+",
        required=True,
        help="List of experiment IDs to run",
    )
    batch_parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop batch execution if an experiment fails",
    )

    args = parser.parse_args()

    # Execute command
    runner = ExperimentRunner()

    if args.command == "list":
        runner.list_experiments()
    elif args.command == "run":
        runner.run_experiment(args.experiment, dry_run=args.dry_run)
    elif args.command == "batch":
        runner.run_batch(args.experiments, continue_on_error=not args.stop_on_error)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

"""
File: logging.py
Location: /src/logging.py
Description: Data export and results visualization module
Author: Patrick Jordan
Version: 2025-10

Handles all simulation output including:
- Event log export (OCEL 2.0 format for process mining)
- Case table and output table generation
- Station utilization statistics
- Performance metrics calculation
- Result visualization and graphs
- Monitoring data export
- Product and system parameter extraction

Key Functions:
- export_to_csv_v2(): Main export coordinator
- log_station_data(): Station performance tracking
- print_results(): Console output formatting
- export_product_parameters(): Product config extraction
"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import json

from src.g import SimulationConfig
from src.station_state import StationState
import helper_functions

from datetime import datetime


def log_station_abs_data(s):
    """Log absolute time data for a station with proper accounting for all time types."""
    # Calculate total simulation time
    total_simulation_time = SimulationConfig.time_to_simulate

    # Get all tracked times from state machine
    time_metrics = s.get_time_metrics()

    # Get all tracked times from state machine
    busy_time = max(0, time_metrics["busy"])
    blocked_time = max(0, time_metrics["blocked"])
    failure_time = max(0, time_metrics["failed"])
    closed_time = max(0, time_metrics["closed"])

    # Total of all tracked time
    accounted_time = busy_time + blocked_time + failure_time + closed_time

    # Calculate waiting time as remaining time, never negative
    waiting_time = max(0, total_simulation_time - accounted_time)

    # Log if we detect potential accounting issues
    time_sum = busy_time + blocked_time + waiting_time + failure_time + closed_time
    if (
        abs(time_sum - total_simulation_time) > 0.1
    ):  # Allow for floating point imprecision
        print(f"WARNING: Time accounting discrepancy detected in station {s.name}:")
        print(f"  Total time: {total_simulation_time:.2f}")
        print(f"  Busy time: {busy_time:.2f}")
        print(f"  Blocked time: {blocked_time:.2f}")
        print(f"  Failure time: {failure_time:.2f}")
        print(f"  Closed time: {closed_time:.2f}")
        print(f"  Waiting time: {waiting_time:.2f}")
        print(f"  Sum: {time_sum:.2f}")
        print(f"  Difference: {abs(time_sum - total_simulation_time):.2f}")

    # Create the data row
    new_row = pd.DataFrame(
        [
            {
                "station": s.name,
                "total_available_time": total_simulation_time,
                "busy_time": busy_time,
                "blocked_time": blocked_time,
                "waiting_time": waiting_time,
                "failure_time": failure_time,
                "closed_time": closed_time,
                "product_count": s.productcount,
            }
        ]
    )

    # Add row to global log
    SimulationConfig.log_stations_abs = pd.concat(
        [SimulationConfig.log_stations_abs, new_row], ignore_index=True
    )


def log_station_data(simulation_run):
    # Log stations
    for s in simulation_run.stations:
        log_station_abs_data(s)

    # Log vehicles
    log_vehicle_data(simulation_run)

    # Reorder columns
    if not SimulationConfig.log_stations_abs.empty:
        column_order = [
            "station",
            "total_available_time",
            "busy_time",
            "blocked_time",
            "waiting_time",
            "failure_time",
            "closed_time",
            "product_count",
        ]
        # Only include columns that exist
        existing_cols = [
            col
            for col in column_order
            if col in SimulationConfig.log_stations_abs.columns
        ]
        SimulationConfig.log_stations_abs = SimulationConfig.log_stations_abs[
            existing_cols
        ]

    # round all values in log_stations
    SimulationConfig.log_stations_abs = SimulationConfig.log_stations_abs.round(1)


def log_vehicle_data(simulation_run):
    """Log vehicle utilization data in the same format as stations."""
    total_simulation_time = SimulationConfig.time_to_simulate

    # Get eventlog - handle both list and DataFrame formats
    if hasattr(SimulationConfig, "events_list") and SimulationConfig.events_list:
        eventlog = pd.DataFrame(SimulationConfig.events_list)
    elif (
        hasattr(SimulationConfig, "eventlog") and SimulationConfig.eventlog is not None
    ):
        eventlog = SimulationConfig.eventlog
    else:
        print("No event log data available for vehicle tracking")
        return

    if eventlog.empty:
        return

    for vehicle in simulation_run.vehicles:
        # Calculate busy time from transport events
        vehicle_events = eventlog[eventlog["resource_id"] == vehicle.name]
        transport_events = vehicle_events[vehicle_events["activity"] == "transport"]

        busy_time = 0
        transport_count = 0

        # Calculate transport times
        loads = transport_events[transport_events["activity_state"] == "load"]
        unloads = transport_events[transport_events["activity_state"] == "unload"]

        for _, load in loads.iterrows():
            matching_unload = unloads[unloads["timestamp"] > load["timestamp"]]
            if not matching_unload.empty:
                # Handle both string and datetime timestamps
                if isinstance(load["timestamp"], str):
                    load_time = pd.to_datetime(load["timestamp"])
                    unload_time = pd.to_datetime(matching_unload.iloc[0]["timestamp"])
                    time_diff = (unload_time - load_time).total_seconds() / 60
                else:
                    time_diff = (
                        matching_unload.iloc[0]["timestamp"] - load["timestamp"]
                    ).total_seconds() / 60
                busy_time += time_diff
                transport_count += 1

        # Vehicles are either busy or idle (no blocked/failed/closed states)
        waiting_time = total_simulation_time - busy_time

        # Add to absolute stats only
        new_row_abs = pd.DataFrame(
            [
                {
                    "station": vehicle.name,  # Using "station" column for consistency
                    "total_available_time": total_simulation_time,
                    "busy_time": busy_time,
                    "blocked_time": 0,
                    "waiting_time": waiting_time,
                    "failure_time": 0,
                    "closed_time": 0,
                    "product_count": transport_count,  # Number of transports
                }
            ]
        )

        SimulationConfig.log_stations_abs = pd.concat(
            [SimulationConfig.log_stations_abs, new_row_abs], ignore_index=True
        )


def print_results(run_number, start_time, end_time, simulation_run):
    """Print simulation results based on output configuration settings."""
    # Always display run completion information
    display_run_number = run_number + 1
    print(
        f"Simulation {display_run_number} completed in {round(end_time - start_time, 3)} seconds"
    )

    # Filter data from output_table instead of log_output
    output_components = SimulationConfig.output_table[
        SimulationConfig.output_table["object_type"] == "component"
    ]
    output_products = SimulationConfig.output_table[
        SimulationConfig.output_table["object_type"] == "product"
    ]
    output_groups = SimulationConfig.output_table[
        SimulationConfig.output_table["object_type"] == "group"
    ]

    # ==========================================
    # SYSTEM OVERVIEW
    # ==========================================
    if SimulationConfig.show_system_overview:
        print("\n=============== SYSTEM OVERVIEW ===============")
        print(f"Run {display_run_number} of {SimulationConfig.runs}")

        # Simulation time in dd:hh:mm:ss format
        total_seconds = SimulationConfig.time_to_simulate * 60
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(
            f"Simulated time: {int(days):02d}:{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d} (dd:hh:mm:ss)"
        )

        # Summary of products processed
        print(
            f"Total products received: {SimulationConfig.log_disassembly['product_type'].count()}"
        )
        print(
            f"Products fully processed: {SimulationConfig.log_disassembly[SimulationConfig.log_disassembly['done'] == True]['product_type'].count()}"
        )

    # ==========================================
    #  PRODUCTION METRICS
    # ==========================================
    if SimulationConfig.show_production_metrics:
        print("\n=============== PRODUCTION METRICS ===============")

        # Product throughput
        products_generated_per_hour = SimulationConfig.log_disassembly[
            "product_type"
        ].count() / (SimulationConfig.time_to_simulate / 60)
        products_done = SimulationConfig.log_disassembly[
            SimulationConfig.log_disassembly["done"] == True
        ]["product_type"].count()

        print(
            f"Products received per hour: {round(products_generated_per_hour, 1)} (1 every {round(60 / products_generated_per_hour, 1)} min)"
        )
        print(
            f"Products processed per hour: {round(products_done / (SimulationConfig.time_to_simulate / 60), 1)}"
        )
        print(
            f"Processing completion rate: {round(products_done / SimulationConfig.log_disassembly['product_type'].count() * 100, 1)}%"
        )

        # Component output
        components_count = len(output_components)
        print(
            f"Components output per hour: {round(components_count / (SimulationConfig.time_to_simulate / 60), 1)}"
        )

        # Disassembly levels
        if (
            SimulationConfig.log_disassembly[
                SimulationConfig.log_disassembly["done"] == True
            ].shape[0]
            > 0
        ):
            disassembly_data = SimulationConfig.log_disassembly[
                SimulationConfig.log_disassembly["done"] == True
            ]
            print(
                f"Disassembly level (min/avg/max): {round(disassembly_data['level_of_disassembly'].min() * 100, 1)}%/{round(disassembly_data['level_of_disassembly'].mean() * 100, 1)}%/{round(disassembly_data['level_of_disassembly'].max() * 100, 1)}%"
            )

    # ==========================================
    #  RESOURCE UTILIZATION
    # ==========================================
    if SimulationConfig.show_resource_utilization:
        print("\n=============== RESOURCE UTILIZATION ===============")

        # Station utilization summary
        if not SimulationConfig.log_stations_abs.empty:
            for _, row in SimulationConfig.log_stations_abs.iterrows():
                total = row["total_available_time"]
                if total > 0:
                    print(
                        f"  {row['station']:<15} "
                        f"Busy: {(row['busy_time'] / total) * 100:>5.1f}%  "
                        f"Blocked: {(row['blocked_time'] / total) * 100:>5.1f}%  "
                        f"Idle: {(row['waiting_time'] / total) * 100:>5.1f}%  "
                        f"Failed: {(row['failure_time'] / total) * 100:>5.1f}%  "
                        f"Closed: {(row['closed_time'] / total) * 100:>5.1f}%"
                    )

    # ==========================================
    #  LOGISTICS PERFORMANCE
    # ==========================================
    if SimulationConfig.show_logistics_performance:
        print("\n=============== LOGISTICS PERFORMANCE ===============")

        # Vehicle utilization
        if hasattr(simulation_run, "vehicles") and simulation_run.vehicles:
            print("Vehicle utilization (%):")
            for vehicle in simulation_run.vehicles:
                utilization_pct = round(
                    (vehicle.busy_time / max(1, SimulationConfig.time_to_simulate)) * 100, 1
                )
                print(f"  {vehicle.name:<15} {utilization_pct:>5.1f}%")

        # Transport requests summary
        if hasattr(simulation_run, "log_vehicles"):
            log_vehicles = pd.DataFrame(simulation_run.log_vehicles).transpose()
            log_vehicles["Sum"] = log_vehicles.sum(axis=1)
            print("\nTransport requests by station:")
            for station, row in log_vehicles.iterrows():
                print(f"  {station:<15} {row['Sum']:>5.0f} requests")

    # ==========================================
    #  TECHNICAL PERFORMANCE
    # ==========================================
    if SimulationConfig.show_technical_performance:
        print("\n=============== TECHNICAL PERFORMANCE ===============")

        # Simulation speed metrics
        print(f"Runtime: {round(end_time - start_time, 3)} seconds")
        print(
            f"Simulation speed: {round(SimulationConfig.time_to_simulate / (end_time - start_time), 1)}x realtime"
        )

        # Event logging statistics
        if SimulationConfig.export_eventlog:
            print(f"Events generated: {len(SimulationConfig.eventlog)}")
            print(
                f"Events per second: {round(len(SimulationConfig.eventlog) / (end_time - start_time), 1)}"
            )


def plot_timeseries():
    """
    Generate time series plots based on simulation data and configuration settings.

    Only creates visualizations if time series graphs are enabled in the configuration.
    """
    # Only plot if timeseries_graphs is enabled
    if not SimulationConfig.timeseries_graphs:
        return

    try:
        # Create figure with subplots
        fig, ax = plt.subplots(2, 1, figsize=(6, 15))

        # First plot - station part counts over time
        if not SimulationConfig.station_part_count_log.empty:
            sns.lineplot(
                data=SimulationConfig.station_part_count_log,
                x="time",
                y="product_count",
                hue="station",
                ax=ax[0],
            )
            ax[0].set_title("Station Product Counts Over Time")
            ax[0].set_xlabel("Simulation Time (minutes)")
            ax[0].set_ylabel("Product Count")

        # Check if inventory_log exists and is not empty
        if (
            hasattr(SimulationConfig, "inventory_log")
            and not SimulationConfig.inventory_log.empty
        ):
            # Reset the index of inventory_log
            inventory_log = SimulationConfig.inventory_log.copy()
            inventory_log.reset_index(inplace=True)

            # Rename the new column to 'time'
            inventory_log.rename(columns={"index": "time"}, inplace=True)

            # Convert to long format for plotting
            inventory_log_long = inventory_log.melt(
                id_vars="time", var_name="storage", value_name="product_count"
            )

            # Filter out outgoing storage which might have very high values
            filtered_data = inventory_log_long[
                inventory_log_long["storage"] != "outgoing_storage"
            ]

            # Create the second plot - inventory levels over time
            if not filtered_data.empty:
                sns.lineplot(
                    data=filtered_data,
                    x="time",
                    y="product_count",
                    hue="storage",
                    ax=ax[1],
                )
                ax[1].set_title("Storage Inventory Levels Over Time")
                ax[1].set_xlabel("Simulation Time (minutes)")
                ax[1].set_ylabel("Inventory Count")

        # Adjust layout and display
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Error generating time series plots: {e}")


## 7. Export configuration update for logging.py
def export_data_v2(df, filename, output_path=None):
    """
    Export DataFrame to CSV with support for new event log structure.

    Args:
        df: DataFrame to export
        filename: Name of the output file
        output_path: Optional custom output path. If None, uses default from SimulationConfig.
    """
    # Use provided output_path or fall back to default
    if output_path is None:
        output_path = os.path.join(
            SimulationConfig.file_path, SimulationConfig.output_path
        )

    # Ensure the directory exists
    os.makedirs(output_path, exist_ok=True)

    full_path = os.path.join(output_path, filename)

    # Check if this is the event log with new structure
    if "event_id" in df.columns and "activity" in df.columns:
        # New event log structure - ensure all columns exist
        required_columns = [
            "event_id",
            "caseID",
            "object_id",
            "object_type",
            "activity",
            "activity_state",
            "resource_id",
            "resource_location",
            "timestamp",
            "related_objects",
        ]

        for col in required_columns:
            if col not in df.columns:
                df[col] = None
    else:
        # Legacy structure - maintain backward compatibility
        required_columns = [
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

        # For eventlog, ensure all required columns exist
        if "timestamp" in df.columns and "resource_id" in df.columns:
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None

    # Export with index=False to avoid adding an extra index column
    # Use na_rep="" to represent NaN values as empty strings
    df.to_csv(full_path, index=False, na_rep="")

    print(f"Exported {len(df)} rows to {filename}")


def export_to_csv_v2(run_number, prefix=None, output_path=None, simulation_run=None):
    """Export simulation data to CSV files with event log structure."""
    display_run_number = run_number + 1
    experiment_id = getattr(SimulationConfig, "experiment_id", None)
    timestamp = SimulationConfig.run_timestamp

    # Use provided output_path or fall back to default
    if output_path is None:
        output_path = os.path.join(
            SimulationConfig.file_path, SimulationConfig.output_path
        )

    # Export parameter data if enabled and simulation object provided
    if simulation_run is not None:
        export_product_parameters_if_enabled(output_path)
        export_system_parameters_if_enabled(simulation_run, output_path)

    # ==========================================
    # CORE OUTPUTS (raw data)
    # ==========================================

    # Export event log ONLY if enabled
    if SimulationConfig.export_eventlog:
        # Convert events list to DataFrame with NEW structure
        if SimulationConfig.events_list:
            print(
                f"Creating eventlog DataFrame from {len(SimulationConfig.events_list)} events"
            )
            SimulationConfig.eventlog = pd.DataFrame(SimulationConfig.events_list)

            # Check all required columns exist for new structure
            required_columns = [
                "event_id",
                "caseID",
                "object_id",
                "object_type",
                "activity",
                "activity_state",
                "resource_id",
                "resource_location",
                "timestamp",
                "related_objects",
            ]

            for col in required_columns:
                if col not in SimulationConfig.eventlog.columns:
                    print(
                        f"Warning: Column '{col}' was missing from eventlog and has been added"
                    )
                    SimulationConfig.eventlog[col] = None

        # Create an empty DataFrame with required columns if no events
        if SimulationConfig.eventlog.empty and not SimulationConfig.events_list:
            print("Warning: No events recorded in this simulation run")
            SimulationConfig.eventlog = pd.DataFrame(columns=required_columns)

        filename_eventlog = SimulationConfig.generate_filename(
            "eventlog",
            experiment_id,
            run_number,
            timestamp,
            category="raw",
        )
        export_data_v2(SimulationConfig.eventlog, filename_eventlog, output_path)

    # Export case table ONLY if enabled
    if SimulationConfig.export_case_table:
        filename_casetable = SimulationConfig.generate_filename(
            "casetable",
            experiment_id,
            run_number,
            timestamp,
            category="raw",
        )
        export_data_v2(SimulationConfig.case_table, filename_casetable, output_path)

    # Export output table ONLY if enabled
    if SimulationConfig.export_output_table:
        filename_outputtable = SimulationConfig.generate_filename(
            "outputtable",
            experiment_id,
            run_number,
            timestamp,
            category="raw",
        )

        export_data_v2(SimulationConfig.output_table, filename_outputtable, output_path)

    # ==========================================
    # COMPUTED OUTPUTS (from event log, case table, output table)
    # ==========================================

    # Export object lookup table ONLY if enabled
    if SimulationConfig.export_object_lookup:
        # Try the new method that generates from eventlog
        if hasattr(helper_functions, "create_object_lookup_table_from_eventlog"):
            object_lookup = helper_functions.create_object_lookup_table_from_eventlog()
            if not object_lookup.empty:
                filename_lookup = SimulationConfig.generate_filename(
                    "object_lookup",
                    experiment_id,
                    run_number,
                    timestamp,
                    category="comp",
                )
                export_data_v2(object_lookup, filename_lookup, output_path)
                print(f"Exported {len(object_lookup)} objects to lookup table")

        # Fall back to the registry method
        elif hasattr(helper_functions, "create_object_lookup_table"):
            object_lookup = helper_functions.create_object_lookup_table()
            if not object_lookup.empty:
                filename_lookup = SimulationConfig.generate_filename(
                    "object_lookup",
                    experiment_id,
                    run_number,
                    timestamp,
                    category="comp",
                )
                export_data_v2(object_lookup, filename_lookup, output_path)
                print(f"Exported {len(object_lookup)} objects to lookup table")

    # Export product time analysis ONLY if enabled
    if SimulationConfig.export_product_time_analysis:
        compute_product_time_analysis(experiment_id, run_number, timestamp, output_path)

    # Export quality analysis ONLY if enabled
    if SimulationConfig.export_quality_analysis:
        compute_quality_analysis(experiment_id, run_number, timestamp, output_path)

    # Export station statistics - absolute ONLY if enabled
    if SimulationConfig.export_station_stats_absolute:
        if (
            hasattr(SimulationConfig, "log_stations_abs")
            and not SimulationConfig.log_stations_abs.empty
        ):
            filename = SimulationConfig.generate_filename(
                "station_stats_absolute",
                experiment_id,
                run_number,
                timestamp,
                category="comp",
            )
            export_data_v2(SimulationConfig.log_stations_abs, filename, output_path)

    # ==========================================
    # MONITORING DATA
    # ==========================================

    if SimulationConfig.export_monitoring_data:
        print("Exporting monitoring data to debug folder...")

        # Create debug subdirectory within the experiment output
        debug_output_path = os.path.join(output_path, "debug")
        os.makedirs(debug_output_path, exist_ok=True)

        # Export time series data for station monitoring
        if (
            hasattr(SimulationConfig, "station_part_count_log")
            and len(SimulationConfig.station_part_count_log) > 0
        ):
            station_monitoring_df = pd.DataFrame(
                SimulationConfig.station_part_count_log
            )
            filename = SimulationConfig.generate_filename(
                "station_monitoring",
                experiment_id,
                run_number,
                timestamp,
                category="debug",
            )
            export_data_v2(station_monitoring_df, filename, debug_output_path)

        # Export inventory time series
        if (
            hasattr(SimulationConfig, "inventory_log")
            and not SimulationConfig.inventory_log.empty
        ):
            filename = SimulationConfig.generate_filename(
                "inventory_monitoring",
                experiment_id,
                run_number,
                timestamp,
                category="debug",
            )
            export_data_v2(SimulationConfig.inventory_log, filename, debug_output_path)

        # Export throughput data
        if (
            hasattr(SimulationConfig, "throughput_log")
            and len(SimulationConfig.throughput_log) > 0
        ):
            throughput_df = pd.DataFrame(SimulationConfig.throughput_log)
            filename = SimulationConfig.generate_filename(
                "throughput_monitoring", experiment_id, run_number, timestamp
            )
            export_data_v2(throughput_df, filename, debug_output_path)

        print(f"  [OK] Monitoring data exported to debug folder")


# Verification function
def verify_new_eventlog_format(output_path=None):
    """
    Verify that the exported event log has the correct new format.
    """
    if output_path is None:
        output_path = os.path.join(
            SimulationConfig.file_path, SimulationConfig.output_path
        )

    # Find the most recent eventlog file
    eventlog_files = [
        f for f in os.listdir(output_path) if "eventlog" in f and f.endswith(".csv")
    ]

    if eventlog_files:
        latest_file = sorted(eventlog_files)[-1]
        file_path = os.path.join(output_path, latest_file)

        # Read the file
        df = pd.read_csv(file_path)

        print(f"\nVerifying event log format in: {latest_file}")
        print(f"Total events: {len(df)}")
        print(f"Columns: {list(df.columns)}")

        # Check for new structure columns
        new_columns = [
            "event_id",
            "activity",
            "activity_state",
            "resource_location",
            "related_objects",
        ]
        missing = [col for col in new_columns if col not in df.columns]

        if missing:
            print(f"WARNING: Missing new columns: {missing}")
        else:
            print("[OK] All new structure columns present")

            # Show sample data
            print("\nSample events:")
            print(
                df[
                    [
                        "event_id",
                        "activity",
                        "activity_state",
                        "resource_id",
                        "resource_location",
                    ]
                ].head(10)
            )

            # Show activity distribution
            print(f"\nActivity distribution:")
            print(df["activity"].value_counts())

            # Show related objects usage
            related_obj_count = df["related_objects"].notna().sum()
            print(
                f"\nEvents with related objects: {related_obj_count} ({related_obj_count / len(df) * 100:.1f}%)"
            )
    else:
        print("No event log files found in output directory")


def extract_step_times_recursive(structure, prefix=""):
    """Helper function to extract step times from product structure."""
    times = {}

    for component, details in structure.items():
        component_key = f"{prefix}{component}" if prefix else component
        times[component_key] = {
            "time": details.get("time", 0),
            "quantity": details.get("quantity", 1),
            "mandatory": details.get("mandatory", False),
            "min_condition": details.get("min_condition", 0.0),
        }

        # Recurse into substructure
        if "structure" in details:
            sub_times = extract_step_times_recursive(
                details["structure"], f"{component_key}."
            )
            times.update(sub_times)

    return times


def export_system_parameters_if_enabled(simulation_run, output_path=None):
    """Export system parameters for Merkmalsklassen analysis."""
    from src.g import SimulationConfig
    import json

    # ==========================================
    # PHASE 1: Check if export is enabled
    # ==========================================
    if (
        not hasattr(SimulationConfig, "export_system_parameters")
        or not SimulationConfig.export_system_parameters
    ):
        return

    if output_path is None:
        output_path = SimulationConfig.output_path

    # ==========================================
    # PHASE 2: Extract system parameters
    # ==========================================

    # ------------------------------
    # 2.1: Volume and variant parameters
    # ------------------------------
    product_variant_count = len(getattr(SimulationConfig, "enabled_product_files", []))
    annual_volume = getattr(SimulationConfig, "volume_per_week_mu", 0) * 52
    weekly_volume_mu = getattr(SimulationConfig, "volume_per_week_mu", 0)
    weekly_volume_min = getattr(SimulationConfig, "volume_per_week_min", 0)
    weekly_volume_max = getattr(SimulationConfig, "volume_per_week_max", 0)
    lot_size = getattr(SimulationConfig, "lot_size", 1)

    # ------------------------------
    # 2.2: Station analysis
    # ------------------------------
    station_parameters = {}
    stations_by_steps = {}  # Group stations by their steps

    for station in simulation_run.stations:
        # Basic station info
        station_parameters[station.name] = {
            "entry_capacity": station.entry_capacity,
            "steps": station.step_names,
            "step_count": len(station.step_names),
            "equipment_types": list(station.equipment.keys()),
            "equipment_count": {
                k: v.capacity if hasattr(v, "capacity") else 1
                for k, v in station.equipment.items()
            },
            "employee_types": list(station.employees.keys()),
            "employee_count": {
                k: v.capacity if hasattr(v, "capacity") else 1
                for k, v in station.employees.items()
            },
            "predecessor_count": len(station.predecessors)
            if hasattr(station, "predecessors")
            else 0,
            "successor_count": len(station.successors)
            if hasattr(station, "successors")
            else 0,
            "predecessors": [p.name for p in station.predecessors]
            if hasattr(station, "predecessors")
            else [],
            "successors": [s.name for s in station.successors]
            if hasattr(station, "successors")
            else [],
        }

        # Group by steps for parallel station identification
        steps_key = tuple(sorted(station.step_names))
        if steps_key not in stations_by_steps:
            stations_by_steps[steps_key] = []
        stations_by_steps[steps_key].append(station.name)

    # Calculate parallel stations
    parallel_station_groups = []
    for steps, stations in stations_by_steps.items():
        if len(stations) > 1:
            parallel_station_groups.append(
                {"steps": list(steps), "stations": stations, "count": len(stations)}
            )

    # ------------------------------
    # 2.3: Vehicle parameters
    # ------------------------------
    vehicle_parameters = {}
    for vehicle in simulation_run.vehicles:
        vehicle_parameters[vehicle.name] = {
            "speed": vehicle.speed,
            "load_capacity": vehicle.load_capacity,
            "load_time": getattr(vehicle, "load_time", None),
            "unload_time": getattr(vehicle, "unload_time", None),
        }

    # ------------------------------
    # 2.4: System topology
    # ------------------------------
    # Calculate system stages (max path length)
    max_path_length = calculate_max_path_length(simulation_run)

    # Count station types
    single_stations = len([s for s in stations_by_steps.values() if len(s) == 1])
    parallel_groups = len([s for s in stations_by_steps.values() if len(s) > 1])

    # ==========================================
    # PHASE 3: Extract process parameters
    # ==========================================
    process_parameters = {
        "MTBF_mu": SimulationConfig.MTBF_mu,
        "MTBF_sigma": SimulationConfig.MTBF_sigma,
        "MTTR_mu": SimulationConfig.MTTR_mu,
        "MTTR_sigma": SimulationConfig.MTTR_sigma,
        "scale_disassembly_time": SimulationConfig.scale_disassembly_time,
        "handling_time": SimulationConfig.handling_time,
        "maintenance_capacity": simulation_run.maintenance_capacity,
    }

    # ==========================================
    # PHASE 4: Create output structure
    # ==========================================
    system_data = {
        "volume_parameters": {
            "product_variants": product_variant_count,
            "annual_volume": annual_volume,
            "weekly_volume_mu": weekly_volume_mu,
            "weekly_volume_min": weekly_volume_min,
            "weekly_volume_max": weekly_volume_max,
            "lot_size": lot_size,
        },
        "system_structure": {
            "station_count": len(simulation_run.stations),
            "vehicle_count": len(simulation_run.vehicles),
            "max_path_length": max_path_length,
            "single_stations": single_stations,
            "parallel_station_groups": parallel_groups,
            "parallel_stations_detail": parallel_station_groups,
        },
        "stations": station_parameters,
        "vehicles": vehicle_parameters,
        "process_parameters": process_parameters,
        "global_resources": {
            "equipment_types": list(simulation_run.global_equipment.keys()),
            "equipment_capacities": {
                k: v.capacity if hasattr(v, "capacity") else 0
                for k, v in simulation_run.global_equipment.items()
            },
            "employee_types": list(simulation_run.global_employees.keys()),
            "employee_capacities": {
                k: v.capacity if hasattr(v, "capacity") else 0
                for k, v in simulation_run.global_employees.items()
            },
        },
        "aggregated_metrics": {
            "total_station_capacity": sum(
                s.entry_capacity for s in simulation_run.stations
            ),
            "average_station_capacity": sum(
                s.entry_capacity for s in simulation_run.stations
            )
            / len(simulation_run.stations)
            if simulation_run.stations
            else 0,
            "total_vehicle_capacity": sum(
                v.load_capacity for v in simulation_run.vehicles
            ),
            "average_vehicle_capacity": sum(
                v.load_capacity for v in simulation_run.vehicles
            )
            / len(simulation_run.vehicles)
            if simulation_run.vehicles
            else 0,
        },
    }

    # ==========================================
    # PHASE 5: Save to file
    # ==========================================
    filename_sys_param = SimulationConfig.generate_filename(
        "system_parameters",
        getattr(SimulationConfig, "experiment_id", None),
        None,
        SimulationConfig.run_timestamp,
        category="params",
    )

    with open(os.path.join(output_path, filename_sys_param), "w") as f:
        json.dump(system_data, f, indent=2)

    print(f"Exported system parameters to {filename_sys_param}")


def export_product_parameters_if_enabled(output_path=None):
    """Export product parameters for Merkmalsklassen analysis."""
    from src.g import SimulationConfig
    import json

    # ==========================================
    # PHASE 1: Check if export is enabled
    # ==========================================
    if (
        not hasattr(SimulationConfig, "export_product_parameters")
        or not SimulationConfig.export_product_parameters
    ):
        return

    if output_path is None:
        output_path = SimulationConfig.output_path

    # ==========================================
    # PHASE 2: Initialize data structures
    # ==========================================
    product_parameters = {}
    portfolio_metrics = {
        "total_products": 0,
        "total_components": 0,
        "total_disassembly_time": 0,
        "max_depth": 0,
        "structure_types": [],
    }

    # ==========================================
    # PHASE 3: Analyze each product
    # ==========================================
    for product_file in getattr(SimulationConfig, "enabled_product_files", []):
        try:
            # ------------------------------
            # 3.1: Load product data
            # ------------------------------
            product_path = os.path.join(
                SimulationConfig.file_path,
                SimulationConfig.product_range_path,
                product_file,
            )

            with open(product_path, "r") as f:
                product_data = json.load(f)
                variant = product_data["variant"]
                product_type = variant["type"]
                structure = variant["structure"]

            # ------------------------------
            # 3.2: Extract structure metrics
            # ------------------------------
            depth = calculate_structure_depth(structure)
            component_count = count_components(structure)
            total_time = sum_disassembly_times(structure)
            mandatory_count = count_mandatory_components(structure)
            structure_type = analyze_structure_type(structure)

            # ------------------------------
            # 3.3: Store product parameters
            # ------------------------------
            product_parameters[product_type] = {
                "structure_metrics": {
                    "depth": depth,
                    "component_count": component_count,
                    "mandatory_components": mandatory_count,
                    "optional_components": component_count - mandatory_count,
                    "total_disassembly_time": total_time,
                    "average_time_per_component": total_time / component_count
                    if component_count > 0
                    else 0,
                    "structure_type": structure_type,
                },
                "metadata": {"source_file": product_file, "product_type": product_type},
            }

            # ------------------------------
            # 3.4: Update portfolio metrics
            # ------------------------------
            portfolio_metrics["total_products"] += 1
            portfolio_metrics["total_components"] += component_count
            portfolio_metrics["total_disassembly_time"] += total_time
            portfolio_metrics["max_depth"] = max(portfolio_metrics["max_depth"], depth)
            portfolio_metrics["structure_types"].append(structure_type)

        except Exception as e:
            print(f"Error analyzing product file {product_file}: {e}")

    # ==========================================
    # PHASE 4: Calculate portfolio parameters
    # ==========================================
    if portfolio_metrics["total_products"] > 0:
        avg_components = (
            portfolio_metrics["total_components"] / portfolio_metrics["total_products"]
        )
        avg_time = (
            portfolio_metrics["total_disassembly_time"]
            / portfolio_metrics["total_products"]
        )
        avg_depth = sum(
            p["structure_metrics"]["depth"] for p in product_parameters.values()
        ) / len(product_parameters)
    else:
        avg_components = avg_time = avg_depth = 0

    portfolio_parameters = {
        "product_count": portfolio_metrics["total_products"],
        "enabled_products": getattr(SimulationConfig, "enabled_product_files", []),
        "volume_distribution": {
            "volume_per_week_mu": getattr(SimulationConfig, "volume_per_week_mu", 0),
            "volume_per_week_min": getattr(SimulationConfig, "volume_per_week_min", 0),
            "volume_per_week_max": getattr(SimulationConfig, "volume_per_week_max", 0),
        },
        "condition_parameters": {
            "condition_mu": getattr(SimulationConfig, "condition_mu", 1.0),
            "condition_min": getattr(SimulationConfig, "condition_min", 0.0),
            "condition_max": getattr(SimulationConfig, "condition_max", 1.0),
            "condition_range": getattr(SimulationConfig, "condition_max", 1.0)
            - getattr(SimulationConfig, "condition_min", 0.0),
        },
        "aggregated_metrics": {
            "total_components": portfolio_metrics["total_components"],
            "average_components_per_product": avg_components,
            "total_disassembly_time": portfolio_metrics["total_disassembly_time"],
            "average_disassembly_time": avg_time,
            "max_depth": portfolio_metrics["max_depth"],
            "average_depth": avg_depth,
            "structure_type_distribution": {
                stype: portfolio_metrics["structure_types"].count(stype)
                for stype in set(portfolio_metrics["structure_types"])
            },
        },
    }

    # ==========================================
    # PHASE 5: Create output structure
    # ==========================================
    output_data = {"products": product_parameters, "portfolio": portfolio_parameters}

    # ==========================================
    # PHASE 6: Save to file
    # ==========================================
    filename_product_param = SimulationConfig.generate_filename(
        "product_parameters",
        getattr(SimulationConfig, "experiment_id", None),
        None,
        SimulationConfig.run_timestamp,
        category="params",
    )

    with open(os.path.join(output_path, filename_product_param), "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Exported product parameters to {filename_product_param}")


# ==========================================
# Helper functions to extract parameters
# ==========================================


def calculate_max_path_length(simulation_run):
    """Calculate maximum path length through the system."""
    max_length = 0

    # Find stations without predecessors (entry points)
    for station in simulation_run.stations:
        if not hasattr(station, "predecessors") or not station.predecessors:
            length = _calculate_path_from_station(station, 1)
            max_length = max(max_length, length)

    return max_length


def _calculate_path_from_station(station, current_length):
    """Recursively calculate path length from a station."""
    if not hasattr(station, "successors") or not station.successors:
        return current_length

    max_length = current_length
    for successor in station.successors:
        length = _calculate_path_from_station(successor, current_length + 1)
        max_length = max(max_length, length)

    return max_length


def calculate_structure_depth(structure, current_depth=0):
    """Calculate maximum depth of product structure."""
    if not structure:
        return current_depth

    max_depth = current_depth
    for component, details in structure.items():
        if "structure" in details:
            depth = calculate_structure_depth(details["structure"], current_depth + 1)
            max_depth = max(max_depth, depth)
        else:
            max_depth = max(max_depth, current_depth + 1)

    return max_depth


def count_components(structure):
    """Count total number of components in structure."""
    count = len(structure)

    for component, details in structure.items():
        if "structure" in details:
            count += count_components(details["structure"])

    return count


def sum_disassembly_times(structure):
    """Sum all disassembly times in structure."""
    total_time = 0

    for component, details in structure.items():
        total_time += details.get("time", 0) * details.get("quantity", 1)

        if "structure" in details:
            total_time += sum_disassembly_times(details["structure"])

    return total_time


def count_mandatory_components(structure):
    """Count components marked as mandatory."""
    count = 0

    for component, details in structure.items():
        if details.get("mandatory", False):
            count += 1
        if "structure" in details:
            count += count_mandatory_components(details["structure"])

    return count


def analyze_structure_type(structure):
    """Analyze structure type based on connections."""
    has_multiple_children = False
    has_multiple_quantities = False

    for component, details in structure.items():
        if "structure" in details and len(details["structure"]) > 1:
            has_multiple_children = True
        if details.get("quantity", 1) > 1:
            has_multiple_quantities = True

    if has_multiple_children and has_multiple_quantities:
        return "general"
    elif has_multiple_children:
        return "converging"
    elif has_multiple_quantities:
        return "diverging"
    else:
        return "linear"


def compute_product_time_analysis(experiment_id, run_number, timestamp, output_path):
    """
    Create a comprehensive time analysis for each product based on event log.
    Uses lean manufacturing terminology for time components.
    """
    # Get event log
    eventlog = SimulationConfig.eventlog.copy()
    if eventlog.empty:
        return

    # Convert timestamps if needed
    if isinstance(eventlog["timestamp"].iloc[0], str):
        eventlog["timestamp"] = pd.to_datetime(eventlog["timestamp"])

    # Get unique cases
    unique_cases = eventlog["caseID"].unique()

    # Get all stations and vehicles
    all_resources = eventlog["resource_id"].unique()

    # More flexible station detection - exclude known non-stations
    non_stations = ["source", "incoming_storage", "outgoing_storage", "maintenance"]
    vehicle_keywords = ["forklift", "vehicle", "pallet", "truck"]

    all_stations = sorted(
        [
            r
            for r in all_resources
            if r not in non_stations
            and not any(v in r.lower() for v in vehicle_keywords)
            and r  # not empty
            and not r.startswith("worker")  # exclude workers if any
        ]
    )

    all_vehicles = sorted(
        [r for r in all_resources if any(v in r.lower() for v in vehicle_keywords)]
    )

    # Prepare results
    results = []
    reference_time = None  # Track the reference time for conversion

    for case_id in unique_cases:
        case_events = eventlog[eventlog["caseID"] == case_id].sort_values("timestamp")

        # Initialize result for this product with lean terminology
        result = {
            "caseID": case_id,
            "product_type": "",
            "delivery_time": None,
            "production_start": None,
            "production_end": None,
            "exit_time": None,
            "throughput_time": 0,
            "active_production_time": 0,
            "value_creating_time_VT": 0,
            "nonvalue_creating_time_NCT": 0,
            "transport_time_TT": 0,
        }

        # Initialize all station and vehicle columns
        for station in all_stations:
            result[f"VT_{station}"] = 0
            result[f"NCT_{station}"] = 0
        for vehicle in all_vehicles:
            result[f"TT_{vehicle}"] = 0

        # Get product type from case table if available
        if (
            hasattr(SimulationConfig, "case_table")
            and not SimulationConfig.case_table.empty
        ):
            case_info = SimulationConfig.case_table[
                SimulationConfig.case_table["caseID"] == case_id
            ]
            if not case_info.empty:
                result["product_type"] = case_info.iloc[0]["product_type"]

        # Calculate system entry and exit times
        # System entry (matches case table's delivery_time)
        entry_events = case_events[
            (case_events["activity"] == "system")
            & (case_events["activity_state"] == "entry")
        ]
        if not entry_events.empty:
            result["delivery_time"] = entry_events.iloc[0]["timestamp"]

        # Production start: First transport load event
        pickup_events = case_events[
            (case_events["activity"] == "transport")
            & (case_events["activity_state"] == "load")
        ]
        if not pickup_events.empty:
            result["production_start"] = pickup_events.iloc[0]["timestamp"]

        # Production end: Last transport unload event
        delivery_events = case_events[
            (case_events["activity"] == "transport")
            & (case_events["activity_state"] == "unload")
        ]
        if not delivery_events.empty:
            result["production_end"] = delivery_events.iloc[-1]["timestamp"]

        # Exit: Last system exit event
        exit_events = case_events[
            (case_events["activity"] == "system")
            & (case_events["activity_state"] == "exit")
        ]
        if not exit_events.empty:
            result["exit_time"] = exit_events.iloc[-1]["timestamp"]

        # Set reference time on first iteration
        if reference_time is None and result["delivery_time"] is not None:
            reference_time = result["delivery_time"]

        # Convert all timestamps to minutes from reference
        for time_field in [
            "delivery_time",
            "production_start",
            "production_end",
            "exit_time",
        ]:
            if result[time_field] is not None and reference_time is not None:
                result[time_field] = round(
                    (result[time_field] - reference_time).total_seconds() / 60, 2
                )
            else:
                result[time_field] = None

        # Calculate throughput time and active production time (already in minutes)
        if result["delivery_time"] is not None and result["exit_time"] is not None:
            result["throughput_time"] = round(
                result["exit_time"] - result["delivery_time"], 2
            )

        if (
            result["production_start"] is not None
            and result["production_end"] is not None
        ):
            result["active_production_time"] = round(
                result["production_end"] - result["production_start"], 2
            )

        # Process each station
        for station in all_stations:
            station_events = case_events[case_events["resource_id"] == station]

            if station_events.empty:
                continue

            # Identify visits (a new visit starts after a gap of events at other resources)
            visits = []
            current_visit_start = None
            current_visit_end = None

            for idx, event in station_events.iterrows():
                if current_visit_start is None:
                    current_visit_start = event["timestamp"]
                    current_visit_end = event["timestamp"]
                else:
                    # Check if there are any events at other resources between this and last event
                    time_between = case_events[
                        (case_events["timestamp"] > current_visit_end)
                        & (case_events["timestamp"] < event["timestamp"])
                        & (case_events["resource_id"] != station)
                    ]

                    if (
                        len(time_between) > 10
                    ):  # Significant activity elsewhere = new visit
                        visits.append((current_visit_start, current_visit_end))
                        current_visit_start = event["timestamp"]
                        current_visit_end = event["timestamp"]
                    else:
                        current_visit_end = event["timestamp"]

            # Don't forget the last visit
            if current_visit_start is not None:
                visits.append((current_visit_start, current_visit_end))

            # Calculate times for all visits
            total_station_time = 0
            processing_time = 0

            for visit_start, visit_end in visits:
                # Total time for this visit
                visit_time = (visit_end - visit_start).total_seconds() / 60
                total_station_time += visit_time

                # Processing time: sum of disassembly times during this visit
                visit_events = station_events[
                    (station_events["timestamp"] >= visit_start)
                    & (station_events["timestamp"] <= visit_end)
                ]

                disassembly_events = visit_events[
                    visit_events["activity"] == "disassembly"
                ]
                starts = disassembly_events[
                    disassembly_events["activity_state"] == "start"
                ]
                completes = disassembly_events[
                    disassembly_events["activity_state"] == "complete"
                ]

                for _, start in starts.iterrows():
                    # Find matching complete
                    matching_complete = completes[
                        completes["timestamp"] > start["timestamp"]
                    ]
                    if not matching_complete.empty:
                        pt = (
                            matching_complete.iloc[0]["timestamp"] - start["timestamp"]
                        ).total_seconds() / 60
                        processing_time += pt

            # Calculate handling time
            handling_time = total_station_time - processing_time

            # Store results
            result[f"VT_{station}"] = processing_time
            result[f"NCT_{station}"] = handling_time
            result["value_creating_time_VT"] += processing_time
            result["nonvalue_creating_time_NCT"] += handling_time

        # Process logistics times
        for vehicle in all_vehicles:
            vehicle_events = case_events[case_events["resource_id"] == vehicle]

            if vehicle_events.empty:
                continue

            transport_events = vehicle_events[vehicle_events["activity"] == "transport"]
            loads = transport_events[transport_events["activity_state"] == "load"]
            unloads = transport_events[transport_events["activity_state"] == "unload"]

            logistics_time = 0

            for _, load in loads.iterrows():
                # Find matching unload
                matching_unload = unloads[unloads["timestamp"] > load["timestamp"]]
                if not matching_unload.empty:
                    lt = (
                        matching_unload.iloc[0]["timestamp"] - load["timestamp"]
                    ).total_seconds() / 60
                    logistics_time += lt

            result[f"TT_{vehicle}"] = logistics_time
            result["transport_time_TT"] += logistics_time

        results.append(result)

    # Create DataFrame
    df = pd.DataFrame(results)

    # Reorder columns with lean terminology
    base_cols = [
        "caseID",
        "product_type",
        "delivery_time",
        "production_start",
        "production_end",
        "exit_time",
        "throughput_time",
        "active_production_time",
        "value_creating_time_VT",
        "nonvalue_creating_time_NCT",
        "transport_time_TT",
    ]

    vt_cols = sorted(
        [c for c in df.columns if c.startswith("VT_") and c != "value_creating_time_VT"]
    )
    nct_cols = sorted(
        [
            c
            for c in df.columns
            if c.startswith("NCT_") and c != "nonvalue_creating_time_NCT"
        ]
    )
    tt_cols = sorted(
        [c for c in df.columns if c.startswith("TT_") and c != "transport_time_TT"]
    )

    final_cols = base_cols + vt_cols + nct_cols + tt_cols
    df = df[final_cols]

    # Round all numeric columns
    numeric_cols = [c for c in df.columns if c not in ["caseID", "product_type"]]
    df[numeric_cols] = df[numeric_cols].round(2)

    # Export
    filename = SimulationConfig.generate_filename(
        "product_time_analysis", experiment_id, run_number, timestamp, category="comp"
    )
    export_data_v2(df, filename, output_path)
    print(f"Exported product time analysis for {len(df)} products")


def compute_quality_analysis(experiment_id, run_number, timestamp, output_path):
    """
    Create quality analysis report showing:
    - Incoming product quality
    - Target components vs actually disassembled
    - Quality and creation time of each output component
    """
    # Check if required data available
    if not hasattr(SimulationConfig, "case_table") or SimulationConfig.case_table.empty:
        print("No case table data for quality analysis")
        return

    if (
        not hasattr(SimulationConfig, "output_table")
        or SimulationConfig.output_table.empty
    ):
        print("No output table data for quality analysis")
        return

    # Get incoming products
    incoming_products = SimulationConfig.case_table.copy()

    # Convert delivery_time to datetime (if string)
    if not incoming_products.empty and isinstance(incoming_products["delivery_time"].iloc[0], str):
        incoming_products["delivery_time"] = pd.to_datetime(
            incoming_products["delivery_time"]
        )

    # Get output components
    output_components = SimulationConfig.output_table[
        SimulationConfig.output_table["object_type"] == "component"
    ].copy()

    # Convert output_time to datetime if it's a string
    if not output_components.empty and isinstance(output_components["output_time"].iloc[0], str):
        output_components["output_time"] = pd.to_datetime(
            output_components["output_time"]
        )

    # Set reference time as the earliest delivery time
    reference_time = incoming_products["delivery_time"].min()

    # Prepare results
    results = []

    for _, product in incoming_products.iterrows():
        case_id = product["caseID"]

        # Parse target and missing components from JSON strings
        target_components = json.loads(product.get("target_components", "{}"))
        missing_components = json.loads(product.get("missing_components", "[]"))

        # Calculate actual target components
        actual_target_count = 0
        for comp_name, quantity in target_components.items():
            if comp_name not in missing_components:
                actual_target_count += quantity

        # Get all components from this product
        product_components = output_components[output_components["caseID"] == case_id]

        # Convert delivery time to minutes from reference
        delivery_time_minutes = round(
            (product["delivery_time"] - reference_time).total_seconds() / 60, 2
        )

        # Create base result
        result = {
            "caseID": case_id,
            "product_type": product["product_type"],
            "delivery_time": delivery_time_minutes,  # (product["delivery_time"] for timestamp
            "condition": round(product["condition"], 2),
            "target_components": actual_target_count,
            "components_out": len(product_components),
        }

        # Add individual component details
        component_details = []
        for _, comp in product_components.iterrows():
            # Use object_name field which should contain the actual component type
            comp_type = comp["object_name"] if "object_name" in comp else "Unknown"

            # If object_name is empty or generic, try to extract from object_type
            if not comp_type or comp_type == "Unknown":
                # object_type might be like "MixedProduct_ElectronicModule"
                if "_" in str(comp["object_type"]):
                    comp_type = comp["object_type"].split("_")[-1]
                else:
                    comp_type = comp["object_type"]

            # Convert output time to minutes from reference
            output_time_minutes = round(
                (comp["output_time"] - reference_time).total_seconds() / 60, 2
            )

            component_details.append(
                {
                    "component": comp_type,
                    "quality": round(comp["condition"], 2),
                    "output_time": output_time_minutes,  # comp["output_time"] for timestamp
                }
            )

        # Sort components by output time for chronological order
        component_details.sort(key=lambda x: x["output_time"])

        # Add component columns
        for i, detail in enumerate(component_details):
            result[f"component_{i + 1}"] = detail["component"]
            result[f"quality_{i + 1}"] = detail["quality"]
            result[f"output_time_{i + 1}"] = detail["output_time"]

        results.append(result)

    # Create DataFrame
    df = pd.DataFrame(results)

    # Fill missing component columns with 'none' instead of empty strings
    component_cols = [col for col in df.columns if col.startswith("component_")]
    quality_cols = [col for col in df.columns if col.startswith("quality_")]
    time_cols = [col for col in df.columns if col.startswith("output_time_")]

    for col in component_cols:
        df[col] = df[col].fillna("none")
    for col in quality_cols:
        df[col] = df[col].fillna("none")
    for col in time_cols:
        df[col] = df[col].fillna("none")

    # Export
    filename = SimulationConfig.generate_filename(
        "quality_analysis", experiment_id, run_number, timestamp, category="comp"
    )
    export_data_v2(df, filename, output_path)
    print(f"Exported quality analysis for {len(df)} products")

"""
File: simulation_monitor.py
Location: /src/simulation_monitor.py
Description: Simulation monitoring and progress tracking system
Author: Patrick Jordan
Version: 2025-10

Provides real-time monitoring and metrics collection:
- Progress bar display during simulation
- Station utilization tracking
- Vehicle usage statistics
- Storage occupancy monitoring
- Performance metrics aggregation

Supports two modes:
1. Debug mode: Full monitoring with detailed history
2. Performance mode: Minimal overhead for production runs
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
import simpy

from src.g import SimulationConfig, g
from src.station_state import StationState
import helper_functions


class SimulationMonitor:
    """
    Configurable monitoring system for simulation.

    Supports two modes:
    1. Debug mode: Full monitoring for system verification and debugging
    2. Performance mode: Minimal monitoring for production/data farming runs

    Args:
        env: SimPy environment
        simulation: Reference to main simulation instance
    """

    def __init__(self, env: simpy.Environment, simulation: object):
        # Initialize environment
        self.env = env

        # Set up monitoring with minimal initialization
        self.simulation = simulation

        # Basic initialization regardless of mode
        self.station_utilization = {}
        self.vehicle_stats = {}
        self.storage_history = []

        # Start progress bar (based on cofig setting)
        if SimulationConfig.show_progress_bar:
            self.env.process(self.monitor_progress())

    def initialize_detailed_monitoring(self) -> None:
        """Initialize detailed monitoring after simulation components exist."""
        # Initialize monitoring structures
        self.init_monitoring_data()

        # Start additional monitoring processes
        self.env.process(self.monitor_metrics())
        self.env.process(self._monitor_stations())

        print("Debug mode: Full monitoring and logging initialized")

    def init_monitoring_data(self) -> None:
        """Initialize data structures for monitoring."""
        # Performance tracking - # For each station, create a dictionary using station's name as key
        self.station_utilization = {
            station.name: {
                "busy_time": 0,  # Time station is actively processing
                "blocked_time": 0,  # Time station is blocked/waiting
                "failure_time": 0,  # Time station is down due to failures
                "total_products": 0,  # Count of products processed
            }
            for station in self.simulation.stations  # Loop through all stations in simulation
        }

        # Vehicle tracking
        self.vehicle_stats = {
            vehicle.name: {"total_distance": 0, "total_loads": 0, "busy_time": 0}
            for vehicle in self.simulation.vehicles
        }

        # Storage tracking
        self.storage_history = []

    # Core monitoring processes
    def monitor_progress(self) -> None:
        """
        Display simulation progress bar in console.

        Creates a visual progress indicator showing:
        - Percentage of simulation completed
        - Progress bar visualization
        - Time progression in hours

        Args:
            env: Current simulation environment

        Yields:
            SimPy timeout events for progress updates

        Note:
            Updates every 1% of total simulation time
            Progress bar length is fixed at 50 characters
        """
        while True:
            try:
                # Get current simulation state
                current_time = self.env.now
                percentage_completed = round(
                    (current_time / SimulationConfig.time_to_simulate) * 100, 0
                )

                # Configure progress bar
                progress_bar_length = 50
                progress_block = int(
                    round(progress_bar_length * percentage_completed / 100)
                )

                # Create progress bar string
                progress_bar = "#" * progress_block + "-" * (
                    progress_bar_length - progress_block
                )

                # Format complete progress display with time
                text = "\rProgress: [{0}] {1:.0f}% ({2:.1f} hrs)".format(
                    progress_bar,
                    percentage_completed,
                    current_time / 60,  # Convert minutes to hours for readability
                )
                print(text, end="\n")

                # Update frequency: every 1% of total simulation time
                yield self.env.timeout(SimulationConfig.time_to_simulate / 100)

            except Exception as e:
                # Log any errors in progress tracking
                print(f"Progress tracking error: {e}")

    def monitor_metrics(self) -> None:
        """
        Monitor and log simulation metrics at regular intervals.

        Tracks and logs various system metrics including:
        - Station inventory levels and product counts
        - Storage utilization across all storage types
        - Overall system state and progression

        Args:
            env: Current simulation environment
            simulation: Active simulation instance being monitored

        Yields:
            SimPy timeout events at monitoring frequency intervals
        """
        while True:
            try:
                # Station Metrics Collection
                station_part_counts = []

                # Collect metrics from each station
                for station in self.simulation.stations:
                    # Record current station state
                    station_part_counts.append(
                        {
                            "time": self.env.now,  # Current simulation time
                            "station": station.name,  # Station identifier
                            "product_count": station.productcount,  # Products processed
                        }
                    )

                # Batch update the station part count log for better performance
                if station_part_counts:  # Only update if there's data to process
                    SimulationConfig.station_part_count_log = pd.concat(
                        [
                            SimulationConfig.station_part_count_log,
                            pd.DataFrame(station_part_counts),
                        ],
                        ignore_index=True,
                    )

                # Inventory Monitoring
                # Update all inventory levels in one pass
                self._update_inventory_levels()

            except Exception as e:
                print(f"Monitoring error at time {self.env.now}: {e}")

            # Wait for next monitoring interval
            yield self.env.timeout(SimulationConfig.monitoring_frequency)

    def _update_inventory_levels(self) -> None:
        """
        Update inventory logs for all storage locations.

        Calculates and logs current inventory levels for:
        - Processing stations
        - Intermediate storage units
        - Incoming and outgoing storage

        Args:
            simulation: Current simulation instance
            current_time: Current simulation time in minutes

        Note:
            Inventory is calculated as sum of items in:
            - Entry buffer
            - Processing/storage area
            - Exit buffers (disassembly and outgoing)
        """
        current_time = self.env.now

        #  Station inventory -> monitor inventory levels at each station
        for station in self.simulation.stations:
            # Calculate total inventory across all station buffers
            inventory = sum(
                len(getattr(station, attr).items)
                for attr in [
                    "entry",  # Entry buffer
                    "workstation",  # Processing area
                    "outbuf_to_next",  # Exit to next station
                    "outbuf_to_store",  # Exit to final storage
                ]
            )
            # Update the inventory log for this station
            helper_functions.update_inventory_log(station.name, inventory, current_time)

        # Storage units inventory -> monitor inventory levels at intermediate storage locations
        for storage_unit in self.simulation.storages:
            # Calculate total inventory across all storage areas
            inventory = sum(
                len(getattr(storage_unit, attr).items)
                for attr in [
                    "entry",  # Entry buffer
                    "station_storage",  # Main storage area
                    "outbuf_to_next",  # Exit to processing
                    "outbuf_to_store",  # Exit to final storage
                ]
            )
            # Update the inventory log for this storage unit
            helper_functions.update_inventory_log(
                storage_unit.name, inventory, current_time
            )

        # System Boundary Storage (Incoming and Outgoing Storage)
        # Monitor incoming storage (system entry point)
        incoming_inventory = sum(
            len(getattr(self.simulation.incoming_storage, attr).items)
            for attr in [
                "entry",
                "station_storage",
                "outbuf_to_next",
                "outbuf_to_store",
            ]
        )

        helper_functions.update_inventory_log(
            "incoming_storage", incoming_inventory, current_time
        )

        # Monitor outgoing storage (system exit point)
        outgoing_inventory = sum(
            len(getattr(self.simulation.outgoing_storage, attr).items)
            for attr in [
                "entry",
                "station_storage",
                "outbuf_to_next",
                "outbuf_to_store",
            ]
        )
        helper_functions.update_inventory_log(
            "outgoing_storage", outgoing_inventory, current_time
        )

    def record_final_state(self):
        """Record final simulation state for analysis."""
        # Record incoming storage state
        incoming_storage = []
        for product_type in SimulationConfig.log_disassembly["product_type"].unique():
            count = sum(
                1
                for item in self.simulation.incoming_storage.outbuf_to_next.items
                if item.type == product_type
            )
            incoming_storage.append(
                {
                    "store": "incoming_storage",
                    "product_type": product_type,
                    "product_count": count,
                }
            )

        SimulationConfig.log_incoming_storage = pd.concat(
            [SimulationConfig.log_incoming_storage, pd.DataFrame(incoming_storage)],
            ignore_index=True,
        )

    # Additional specialized monitoring
    def _monitor_stations(self) -> None:
        """Monitor individual station performance."""
        while True:
            try:
                for station in self.simulation.stations:
                    # Get time metrics using state machine
                    time_metrics = station.get_time_metrics()

                    # Update station machines
                    self.station_utilization[station.name].update(
                        {
                            "busy_time": time_metrics["busy"],
                            "blocked_time": time_metrics["blocked"],
                            "failure_time": time_metrics["failed"],
                            "total_products": station.productcount,
                        }
                    )

                    # Calculate utilization percentage if simulation has been running
                    total_time = self.env.now
                    if total_time > 0:
                        utilization = (time_metrics["busy"] / total_time) * 100
                        self.station_utilization[station.name]["utilization"] = (
                            utilization
                        )

                    """
                    # Optional: Debug printing
                    print(f"\nStation {station.name} metrics at {self.env.now}:")
                    print(f"Busy time: {station.busy_time}")
                    print(f"Blocked time: {station.blocked_time}")
                    print(f"Total products: {station.productcount}")
                    if total_time > 0:
                        print(f"Utilization: {utilization:.2f}%")
                    """

                yield self.env.timeout(g.monitoring_frequency)

            except Exception as e:
                print(f"Station monitoring error: {e}")

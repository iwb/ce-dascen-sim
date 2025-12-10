"""
File: station_state.py
Location: /src/station_state.py
Description: Station state machine for accurate time tracking
Author: Patrick Jordan
Version: 2025-10

Implements a state machine to track different states of a disassembly station
throughout the simulation. Ensures accurate time accounting and prevents
double-counting of time spent in different states.

States:
- IDLE: Station is waiting for work
- BUSY: Station is actively processing an item
- BLOCKED: Station is waiting for downstream capacity
- FAILED: Station equipment has failed
- CLOSED: Station is outside working hours

Key Methods:
- enter_state(): Transition to new state with proper time accounting
- _enter_state_full(): Full-featured version with history tracking
- _enter_state_optimized(): Performance-optimized version
- get_state_time(): Get accumulated time in specific state
- get_all_times(): Get all state times
- export_state_history(): Export complete history for debugging

The class supports two modes:
1. Full mode: Complete history tracking for debugging
2. Optimized mode: Minimal overhead for production runs
"""

import os

import helper_functions


class StationState:
    """
    Manages the state of a station with proper time accounting.

    This class implements a state machine pattern to track how much time a station
    spends in different operational states. It ensures clean transitions between
    states and accurate time accounting.

    Attributes:
        env (simpy.Environment): The simulation environment
        station_name (str): The name of the station this state machine belongs to
        current_state (str): The current state of the station
        state_start_time (float): The time when the current state was entered
        time_in_states (dict): Accumulated time spent in each state
        state_history (list): Complete history of state transitions for debugging
    """

    # State constants
    IDLE = "idle"
    BUSY = "busy"
    BLOCKED = "blocked"
    FAILED = "failed"
    CLOSED = "closed"

    def __init__(self, env, station_name):
        """
        Initialize the state machine.

        Args:
            env (simpy.Environment): The simulation environment
            station_name (str): The name of the station this state machine belongs to
        """
        from src.g import SimulationConfig

        self.env = env
        self.station_name = station_name

        # Current state
        self.current_state = self.IDLE
        self.state_start_time = env.now

        # Accumulated times
        self.time_in_states = {
            self.IDLE: 0,
            self.BUSY: 0,
            self.BLOCKED: 0,
            self.FAILED: 0,
            self.CLOSED: 0,
        }

        # Initialize history only if tracking is enabled (set in config)
        self.state_history = []

        if SimulationConfig.station_state_tracking:
            # Initial state entry
            self.state_history.append(
                {
                    "entry_time": self.state_start_time,
                    "state": self.current_state,
                    "previous_state": None,
                    "context": "Initial state",
                }
            )

    def enter_state(self, new_state, context=""):
        """
        Transition to a new state with proper time accounting.

        This method routes to either the full-featured version or the
        performance-optimized version based on configuration settings.

        Args:
            new_state (str): The state to enter
            context (str): Description of the reason for this state change

        Returns:
            float: Time spent in the previous state
        """
        # Check if performance mode is enabled
        from src.g import SimulationConfig

        # Debug log state changes
        if new_state != self.current_state:
            helper_functions.debug_print(
                f"Station {self.station_name} state change: {self.current_state} -> {new_state} ({context})"
            )

        if (
            hasattr(SimulationConfig, "optimize_state_machine")
            and SimulationConfig.optimize_state_machine
        ):
            # Call optimized version (better performance)
            return self._enter_state_optimized(new_state, context)
        else:
            # Call full-featured version (good for debugging / during development)
            return self._enter_state_full(new_state, context)

    def _enter_state_full(self, new_state, context=""):
        """
        Transition to a new state with proper time accounting.

        Args:
            new_state (str): The state to enter
            context (str): Description of the reason for this state change

        Returns:
            float: Time spent in the previous state

        Raises:
            ValueError: If the new state is not valid
        """
        if new_state not in self.time_in_states:
            raise ValueError(f"Invalid state: {new_state}")

        # If  already in this state, log it and return 0
        if new_state == self.current_state:
            # Only add to history if tracking is enabled (set in config)
            from src.g import SimulationConfig

            if SimulationConfig.station_state_tracking:
                self.state_history.append(
                    {
                        "entry_time": self.env.now,
                        "state": new_state,
                        "previous_state": self.current_state,
                        "context": f"Remained in state: {context}",
                    }
                )
            return 0

        # Calculate time spent in previous state
        current_time = self.env.now
        time_spent = max(0, current_time - self.state_start_time)

        # Account for time spent in previous state
        self.time_in_states[self.current_state] += time_spent

        # Only log state history if tracking is enabled (set in config)
        from src.g import SimulationConfig

        if SimulationConfig.station_state_tracking:
            # Log the state exit for debugging
            self.state_history.append(
                {
                    "exit_time": current_time,
                    "state": self.current_state,
                    "duration": time_spent,
                    "context": f"Exiting {self.current_state}",
                }
            )

        # Enter new state
        old_state = self.current_state
        self.current_state = new_state
        self.state_start_time = current_time

        if SimulationConfig.station_state_tracking:
            # Log the state entry for debugging
            self.state_history.append(
                {
                    "entry_time": current_time,
                    "state": new_state,
                    "previous_state": old_state,
                    "context": context,
                }
            )

        # Return time spent in previous state for reference
        return time_spent

    def _enter_state_optimized(self, new_state, context=""):
        """
        Optimized state transition with minimal overhead.

        This is a performance-optimized version that skips non-essential
        operations while maintaining accurate time accounting.
        """
        # Skip redundant state changes completely - On average skips 50 % (optimization potential)
        if new_state == self.current_state:
            return 0

        # No validation in optimized mode - assumes valid states

        # Calculate time spent in previous state
        current_time = self.env.now
        time_spent = max(0, current_time - self.state_start_time)

        # Account for time spent in previous state
        self.time_in_states[self.current_state] += time_spent

        # Only the minimal required operations to change state
        self.current_state = new_state
        self.state_start_time = current_time

        # Return time spent in previous state for reference
        return time_spent

    def get_state_time(self, state):
        """
        Get total time spent in a particular state, including current state if active.

        Args:
            state (str): The state to get time for

        Returns:
            float: The total time spent in the state

        Raises:
            ValueError: If the state is not valid
        """
        if state not in self.time_in_states:
            raise ValueError(f"Invalid state: {state}")

        # Get accumulated time
        time = self.time_in_states[state]

        # Add current state time if we're in that state
        if self.current_state == state and self.state_start_time > 0:
            time += max(0, self.env.now - self.state_start_time)

        return time

    def export_logs(self, filename=None):
        """Export logs to debug folder."""
        from src.g import SimulationConfig

        # Create debug subdirectory within the experiment output
        debug_output_path = os.path.join(SimulationConfig.output_path, "debug")
        os.makedirs(debug_output_path, exist_ok=True)

        # Skip export if tracking is disabled
        if not SimulationConfig.station_state_tracking:
            return

        # Create debug subdirectory within the experiment output
        debug_output_path = os.path.join(SimulationConfig.output_path, "debug")
        os.makedirs(debug_output_path, exist_ok=True)

        if filename is None:
            experiment_id = getattr(SimulationConfig, "experiment_id", None)
            timestamp = SimulationConfig.run_timestamp
            filename = SimulationConfig.generate_filename(
                f"{self.station_name}_state_tracking",
                experiment_id,
                None,
                timestamp,
                category="debug",
            )

        log_path = os.path.join(debug_output_path, filename)

        try:
            with open(log_path, "w") as f:
                f.write(f"State tracking log for {self.station_name}\n")
                f.write("=" * 50 + "\n")

                for entry in self.state_history:
                    if "exit_time" in entry:
                        f.write(
                            f"Time {entry['exit_time']:.2f}: Exited state {entry['state']} "
                            f"after {entry['duration']:.2f} minutes. {entry['context']}\n"
                        )
                    else:
                        if entry["previous_state"] is None:
                            f.write(
                                f"Time {entry['entry_time']:.2f}: Started in state {entry['state']}. "
                                f"{entry['context']}\n"
                            )
                        else:
                            f.write(
                                f"Time {entry['entry_time']:.2f}: Entered state {entry['state']} "
                                f"from {entry['previous_state']}. {entry['context']}\n"
                            )

                # Add current state duration
                current_time = self.env.now
                current_duration = current_time - self.state_start_time
                f.write(
                    f"\nFinal state: {self.current_state} for {current_duration:.2f} minutes\n"
                )

                # Add summary of time in each state
                f.write("\nTime in each state:\n")
                total_time = 0
                for state, time in self.time_in_states.items():
                    if state == self.current_state:
                        time += current_duration
                    total_time += time
                    f.write(
                        f"  {state}: {time:.2f} minutes ({(time / max(1, current_time)) * 100:.1f}%)\n"
                    )

                f.write(f"\nTotal simulation time: {current_time:.2f} minutes\n")
                f.write(f"Total accounted time: {total_time:.2f} minutes\n")
                f.write(f"Difference: {total_time - current_time:.2f} minutes\n")

            print(f"State tracking log exported to {log_path}")
        except Exception as e:
            print(f"Error exporting state log: {e}")

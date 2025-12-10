"""
File: breakdowns.py
Location: /src/breakdowns.py
Description: Equipment breakdown and repair simulation module
Author: Patrick Jordan
Version: 2025-10

Implements equipment breakdown and repair system for the simulation.
Models random failures of equipment resources and their subsequent repair processes.
Updated to use the Station State Machine for proper state transitions.

Key Features:
- Stochastic breakdown generation based on MTBF (Mean Time Between Failures) distributions
- Resource preemption for equipment failure simulation
- Maintenance resource allocation and management
- Repair time modeling with interruption handling (e.g., shift changes)
- Proper state machine integration (IDLE/BUSY -> FAILED -> IDLE)

Process Flow:
1. Randomly generates time until next failure based on MTBF
2. When failure occurs, preempts the equipment resource
3. Transitions station to FAILED state
4. Requests maintenance resource for repair
5. Handles repair interruptions (shift end, etc.)
6. After repair completion, transitions back to IDLE state
7. Releases equipment back to service
"""

import random
from typing import Optional

import simpy

import helper_functions
from src.g import SimulationConfig, SimulationBehavior
from src.station_state import StationState


class Breakdowns:
    """
    Models equipment breakdowns and repairs in the simulation environment.

    Each instance represents the breakdown behavior of a specific piece of equipment
    at a specific station. The breakdown process follows these steps:
    1. Randomly generates time until next failure based on MTBF distribution
    2. When failure occurs, preempts the equipment resource
    3. Requests maintenance resource for repair
    4. After repair completion, releases equipment back to service

    The process handles interruptions due to shift changes and tracks all relevant times
    for analysis.

    Attributes:
        env (simpy.Environment): The simulation environment
        simulation (object): Reference to main simulation instance
        station (object): The station where the equipment is located
        name (str): Name identifier of the equipment
        resource (simpy.PreemptiveResource): The equipment resource that can fail
        MTBF (float): Mean Time Between Failures in minutes
        MTBF_sigma (float): Standard deviation of MTBF
        MTTR (float): Mean Time To Repair in minutes
        MTTR_sigma (float): Standard deviation of MTTR
        repair_time_start (float): Time when current repair started
        repair_time_done (float): Amount of repair time completed before interruption
        failure (bool): Current failure state of the equipment
        process (simpy.Process): The active breakdown generation process
    """

    def __init__(
        self,
        env: simpy.Environment,
        simulation: object,
        station: object,
        name: str,
        resource: object,
        MTBF: float,
        MTBF_sigma: float,
        MTTR: float,
        MTTR_sigma: float,
    ) -> None:
        """
        Initialize a new breakdown handler for a piece of equipment.

        Args:
            env: The simulation environment
            simulation: Reference to main simulation instance
            station: The station where the equipment is located
            name: Name identifier of the equipment
            resource: The equipment resource that can fail
            MTBF: Mean Time Between Failures in minutes
            MTBF_sigma: Standard deviation of MTBF
            MTTR: Mean Time To Repair in minutes
            MTTR_sigma: Standard deviation of MTTR
        """
        self.env = env
        self.simulation = simulation
        self.station = station
        self.name = name
        self.resource = resource
        self.MTBF = MTBF
        self.MTBF_sigma = MTBF_sigma
        self.MTTR = MTTR
        self.MTTR_sigma = MTTR_sigma

        # Tracking attributes
        self.repair_time_start = 0
        self.repair_time_done = 0
        self.failure = False

        # Start the breakdown generation process
        self.process = env.process(self.generate_breakdowns())

    def generate_breakdowns(self) -> None:
        """
        Continuously generates equipment breakdowns and manages repairs.

        This process:
        1. Generates random time until next failure
        2. Waits until failure occurs
        3. Manages the failure and repair process
        4. Handles interruptions due to shift changes

        The process repeats indefinitely throughout the simulation.

        The breakdowns are generated according to the specified mean time between failures
        and mean time to repair. A breakdown requests the affected resource with higher
        priority than the normal requests and therefore interrupts disassembly processes.
        Then a maintenance resource is requested and the repair process is started.
        After the repair is completed, the resource is released and the disassembly
        process can continue using the resource.

        Yields:
            env.timeout: A timeout representing the time until next breakdown, repair or
                        beginning of working hours.
            req_maintenance: A request for maintenance resources.
        """
        while True:
            # Generate time until next failure based on behavior mode
            if SimulationConfig.behavior_mode == SimulationBehavior.DETERMINISTIC:
                # Use mean value for deterministic behavior
                time_to_failure = self.MTBF
            else:
                # Use random distribution for seeded behavior
                # Note: max(0, ...) clamps negative values from normalvariate to 0,
                # meaning "breakdown happens immediately". This is rare but valid behavior.
                time_to_failure = max(
                    0,
                    SimulationConfig.rng_breakdowns.normalvariate(
                        self.MTBF, self.MTBF_sigma
                    ),
                )

            # Wait until next failure
            yield self.env.timeout(time_to_failure)

            # Check if breakdown occurs during working hours
            is_working_hours, current_hour, _ = helper_functions.is_working_hours(
                self.simulation
            )

            if not is_working_hours:
                # If breakdown is not during working hours, wait until beginning of next shift
                # Calculate time until next shift starts
                if current_hour < self.simulation.start_of_day:
                    closed_time = (self.simulation.start_of_day - current_hour) * 60
                else:
                    closed_time = (
                        self.simulation.start_of_day + 24 - current_hour
                    ) * 60
                yield self.env.timeout(closed_time + 1)

            # ==========================================
            # PHASE 1: Initiate breakdown
            # ==========================================
            # Initiate breakdown by requesting equipment with highest priority
            # (= priority 0) takes precedence over normal requests from disassembly processes
            with self.resource.request(priority=0, preempt=True) as req:
                # Track time of failure
                start_failure = self.env.now
                self.failure = True

                # Transition station to FAILED state
                self.station.state.enter_state(
                    StationState.FAILED, f"Breakdown of {self.name}"
                )

                # ==========================================
                # PHASE 2: Generate repair time
                # ==========================================
                # Generate repair time based on behavior mode
                if SimulationConfig.behavior_mode == SimulationBehavior.DETERMINISTIC:
                    # Use mean value for deterministic behavior
                    repair_time = self.MTTR
                else:
                    # Use random distribution for seeded behavior
                    repair_time = max(
                        0,
                        SimulationConfig.rng_breakdowns.normalvariate(
                            self.MTTR, self.MTTR_sigma
                        ),
                    )

                # DEBUG: Log breakdown
                helper_functions.debug_print(
                    f"BREAKDOWN: {self.name} at station {self.station.name} "
                    f"(MTBF was {time_to_failure:.1f} min, repair time: {repair_time:.1f} min)"
                )

                # Track if repair was interrupted
                interrupt_repair = False

                # ==========================================
                # PHASE 3: Repair process (with interruption handling)
                # ==========================================
                # Continue repair process until complete
                while self.failure:
                    try:
                        # Calculate remaining repair time, ensuring it's never negative
                        if interrupt_repair:
                            # Use recorded repair time if interrupted, with safety check
                            repair_time_remaining = max(
                                0, repair_time - self.repair_time_done
                            )
                        else:
                            # First attempt uses full repair time
                            repair_time_remaining = repair_time
                            self.repair_time_done = 0

                        # Request maintenance resource
                        with self.simulation.maintenance.request(
                            priority=1, preempt=True
                        ) as req_maintenance:
                            # Request maintenance resource to repair breakdown
                            yield req_maintenance

                            # Set repair start time and execute repair
                            self.repair_time_start = self.env.now
                            yield self.env.timeout(repair_time_remaining)

                            # ==========================================
                            # PHASE 4: Complete repair
                            # ==========================================
                            # Mark repair as complete
                            self.failure = False

                            # DEBUG: Log repair completion
                            helper_functions.debug_print(
                                f"REPAIR COMPLETE: {self.name} at station {self.station.name} "
                                f"(total downtime: {self.env.now - start_failure:.1f} min)"
                            )

                            # Transition back to IDLE state after repair
                            self.station.state.enter_state(
                                StationState.IDLE, f"Repaired {self.name}"
                            )

                    except simpy.Interrupt as interrupt:
                        # ==========================================
                        # PHASE 5: Handle interruption (e.g. shift end)
                        # ==========================================
                        interrupt_repair = True

                        # Calculate time spent on repair so far, ensuring it's non-negative
                        time_spent = max(0, self.env.now - self.repair_time_start)

                        # Never accumulate more repair time than the total needed
                        self.repair_time_done = min(time_spent, repair_time)

                        # DEBUG: Log interruption
                        helper_functions.debug_print(
                            f"REPAIR INTERRUPTED: {self.name} at station {self.station.name} "
                            f"(completed {self.repair_time_done:.1f}/{repair_time:.1f} min)"
                        )

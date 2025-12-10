"""
File: breaks.py
Location: /src/breaks.py
Description: Work shift and break management system
Author: Patrick Jordan
Version: 2025-10

Manages employee shifts and station operating hours:
- Daily shift start/end times
- Employee resource requests during breaks
- Station state transitions (OPEN <-> CLOSED)
- Working hours checking and enforcement

Integrated with station state machine for accurate time tracking.
Requests all employee resources with priority 0 during closed hours.
"""

from src.g import *
from src.product import *
from src.station_state import StationState
import helper_functions
from contextlib import ExitStack


class Breaks:
    """This class represents the breaks of employees in the simulation.
    It contains the process generate_breaks which generates breaks for all employees at once.
    Currently this class only generates breaks from the end of the day until the beginning of the next shift.

    Updated to use the station state machine for proper state transitions.

    Args:
        env (simpy.Environment): A reference to the simulation environment.
        simulation (object): A reference to the simulation in which the breaks and shifts are being modeled.
    """

    # Add to the Breaks class in breaks.py
    def __init__(self: object, env: simpy.Environment, simulation: object):
        self.env = env
        self.simulation = simulation

        # Check if simulation starts outside working hours and handle initial state
        is_working_hours, current_hour, _ = helper_functions.is_working_hours(
            self.simulation
        )
        if not is_working_hours:
            # Transition all stations to CLOSED state at start
            for s in self.simulation.stations:
                s.state.enter_state(
                    StationState.CLOSED, "Initial state - outside working hours"
                )

        # Start the break generation process
        self.process = env.process(self.generate_breaks())

    def generate_breaks(self: object) -> None:
        """Generates breaks and requests all employees during the breaks.
        Requests are made with priority 0, which takes precedence over normal requests from disassembly processes
        or maintenance requests.
        This method continuously checks whether it's working hours or not.
        If it's working hours, it will wait until the end of the day.
        If it's not working hours, it will request all local, global and maintenance employees
        until the beginning of the next shift. Transport vehicles are currently not requested during breaks,
        since they dont have a handling of interruptions implemented yet.

        This version has been updated to use the station state machine for accurate time tracking.

        Yields:
            env.timeout: A timeout representing the time until the end of the day or the beginning of the next shift.
            env.all_of: A request for all local, global and maintenance employees.
        """
        while True:
            # Check if working hours
            (
                is_working_hours,
                current_hour,
                current_day,
            ) = helper_functions.is_working_hours(self.simulation)

            # If working hours, wait until end of day
            if is_working_hours:
                working_time_left = (self.simulation.end_of_day - current_hour) * 60
                yield self.env.timeout(working_time_left)

                # DEBUG: Log shift ending
                helper_functions.debug_print(
                    f"SHIFT END: Working day ended at {current_hour:.1f}:00 "
                    f"(day {current_day})"
                )
            # If not working hours, request all employees until beginning of next shift
            else:
                # Get time until beginning of next shift
                if current_hour < self.simulation.start_of_day:
                    closed_time = (self.simulation.start_of_day - current_hour) * 60
                else:
                    closed_time = (
                        self.simulation.start_of_day + 24 - current_hour
                    ) * 60
                # DEBUG: Log break duration
                helper_functions.debug_print(
                    f"BREAK: Facility closed for {closed_time:.0f} minutes "
                    f"(until {self.simulation.start_of_day}:00)"
                )

                # Skip if closed time is zero or negative (shouldn't happen but to be safe)
                if closed_time <= 0:
                    print(f"WARNING: Calculated closed_time <= 0: {closed_time}")
                    # Wait a minimal time
                    yield self.env.timeout(1)
                    continue

                # Transition all stations to CLOSED state
                closed_stations = 0
                for s in self.simulation.stations:
                    if s.state.current_state != StationState.CLOSED:
                        s.state.enter_state(StationState.CLOSED, "End of shift")
                        closed_stations += 1

                # DEBUG: Log stations closed
                helper_functions.debug_print(
                    f"  Transitioned {closed_stations} stations to CLOSED state"
                )

                # Request all employees
                requests = []
                employee_count = 0

                with ExitStack() as stack:
                    # Request local employees from each station
                    for s in self.simulation.stations:
                        # Request all local employees
                        for employee_resources in s.employees.values():
                            for resource in employee_resources:
                                request = stack.enter_context(
                                    resource.request(priority=0, preempt=True)
                                )
                                requests.append(request)

                    # Count employees being requested
                    for s in self.simulation.stations:
                        for employee_resources in s.employees.values():
                            employee_count += len(employee_resources)

                    employee_count += self.simulation.maintenance_capacity

                    for employee_resource in self.simulation.global_employees.values():
                        employee_count += employee_resource.capacity

                    # DEBUG: Log employee requests
                    helper_functions.debug_print(
                        f"  Requested {employee_count} employees for break period"
                    )

                    # Request full capacity of maintenance
                    for _ in range(self.simulation.maintenance_capacity):
                        request = stack.enter_context(
                            self.simulation.maintenance.request(
                                priority=0, preempt=True
                            )
                        )
                        requests.append(request)

                    # Request all global employees
                    for employee_resource in self.simulation.global_employees.values():
                        for _ in range(employee_resource.capacity):
                            request = stack.enter_context(
                                employee_resource.request(priority=0, preempt=True)
                            )
                            requests.append(request)

                    # Handle if no requests were created
                    if not requests:
                        print("WARNING: No employee resources to request during break")
                        yield self.env.timeout(closed_time)
                    else:
                        yield self.env.all_of(requests)
                        # wait until beginning of next shift
                        yield self.env.timeout(closed_time)

                    # ==========================================
                    # After break ends
                    # ==========================================
                    # DEBUG: Log shift starting
                    helper_functions.debug_print(
                        f"SHIFT START: Working day started at {self.simulation.start_of_day}:00"
                    )
                    # Transition all stations back to IDLE
                    reopened_stations = 0
                    for s in self.simulation.stations:
                        if s.state.current_state == StationState.CLOSED:
                            s.state.enter_state(StationState.IDLE, "Start of shift")
                            reopened_stations += 1

                    # DEBUG: Log stations reopened
                    helper_functions.debug_print(
                        f"  Transitioned {reopened_stations} stations to IDLE state"
                    )

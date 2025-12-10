"""
File: functions.py
Location: Project root
Description: Core simulation process functions (transport and material flow)
Authors: Patrick Jordan, Lasse Streibel
Version: 2025-10

Contains main process functions:
- ordering() - Material flow control (pull/push mode)
- process_transport() - Transport process with vehicle management
- process_push_transport_simple() - Simplified push transport
- find_successors() - Routing logic for push mode
- can_element_process_item() - Component filtering for stations
"""

from contextlib import ExitStack

import helper_functions
from src.g import *


# Default ordering function - will be overridden by g.py based on material flow mode
def ordering(element, simulation, source, predecessors=None):
    """Base ordering function - dynamically assigned to push or pull mode."""
    # This will be overwritten by g.py initialization
    # Default to pull mode if not set
    return ordering_pull(element, simulation, source, predecessors)


def ordering_pull(element, simulation, source, predecessors=None):
    """Pull mode ordering. Default ordering mode."""
    # Debug: Log when ordering starts (only once per element)
    if not hasattr(element, "_ordering_started_logged"):
        # print(f"PULL ORDERING STARTED: {element.name} at time {element.env.now}")
        helper_functions.debug_print(
            f"PULL ORDERING STARTED: {element.name} at time {element.env.now}"
        )
        element._ordering_started_logged = True

    first_iteration = True  # Track first check to avoid initial delay

    while True:
        # Only wait AFTER first check, not before
        if not first_iteration:
            yield element.env.timeout(
                SimulationConfig.element_entry_monitoring_frequency
            )

        # Check if disassembly is open
        (is_working_hours, current_hour, _) = helper_functions.is_working_hours(
            element.simulation
        )

        # If disassembly is closed, wait until it is open again
        if not is_working_hours:
            if current_hour < simulation.start_of_day:
                closed_time = (simulation.start_of_day - current_hour) * 60
            else:
                closed_time = (simulation.start_of_day + 24 - current_hour) * 60

            # Debug: Log the wait (only on first iteration)
            if first_iteration:
                helper_functions.debug_print(
                    f"PULL: {element.name} waiting {closed_time + 1} min for factory to open (current_hour={current_hour}, start_of_day={simulation.start_of_day})"
                )

            # Debug before wait
            if element.name in ["ws-03_disassembly_01", "ws-04_disassembly_02"]:
                helper_functions.debug_print(
                    f"{element.name}: Waiting {closed_time} min for factory to open"
                )

            yield element.env.timeout(closed_time + 1)

            # Debug after wait
            if element.name in ["ws-03_disassembly_01", "ws-04_disassembly_02"]:
                helper_functions.debug_print(
                    f"{element.name}: Factory opened, continuing ordering loop at {element.env.now}"
                )

            # Mark first iteration complete after wait
            first_iteration = False
            continue

        # Mark first iteration complete if we reach here
        first_iteration = False

        # Define max orders allowed based on element type
        if element.name == "outgoing_storage":
            # Can order from both outbuf_to_next and outbuf_to_store once
            max_order_quantity = 2
        else:
            # Can order from outbuf_to_next or outbuf_to_store once
            max_order_quantity = 1

        # Also add debug right before the ordering check
        if element.name in ["ws-03_disassembly_01", "ws-04_disassembly_02"]:
            helper_functions.debug_print(
                f"{element.name}: About to check ordering at {element.env.now}, entry={len(element.entry.items)}/{element.order_threshold}"
            )

        # Check if ordering is necessary and allowed
        if (
            len(element.entry.items) < element.order_threshold
            and element.open_orders < max_order_quantity
        ):
            # Debug for key elements
            if element.name == "b-01_buffer_01":
                helper_functions.debug_print(
                    f"b-01: Ordering triggered at {element.env.now} | "
                    f"Entry: {len(element.entry.items)}/{element.order_threshold} | "
                    f"Predecessors: {[p.name for p in element.predecessors]}"
                )

            if element.name == "ws-01_fluids_01":
                pred_names = (
                    [p.name for p in element.predecessors]
                    if hasattr(element, "predecessors")
                    else []
                )
                helper_functions.debug_print(
                    f"ws-01: Ordering triggered at {element.env.now} | "
                    f"Entry: {len(element.entry.items)}/{element.order_threshold} | "
                    f"Predecessors: {pred_names}"
                )
                # Check incoming_storage specifically
                for p in element.predecessors:
                    if p.name == "incoming_storage" and hasattr(p, "outbuf_to_next"):
                        helper_functions.debug_print(
                            f"  -> incoming_storage has {len(p.outbuf_to_next.items)} items available"
                        )
                        break

            if element.name == "ws-02_battery_01":
                helper_functions.debug_print(
                    f"ws-02: Ordering at {element.env.now} | "
                    f"Entry: {len(element.entry.items)}/{element.order_threshold} | "
                    f"Open orders: {element.open_orders}"
                )

            # Log first check for any element
            if first_iteration:
                helper_functions.debug_print(
                    f"PULL FIRST CHECK: {element.name} at {element.env.now} | "
                    f"Entry: {len(element.entry.items)}/{element.order_threshold}"
                )

            # Determine what components this element can process
            processable_components = None
            if hasattr(element, "step_names"):
                # Access step_names (station attribte) to identify what can be processed
                processable_components = element.step_names

            # Start a new transport process with component filtering
            element.env.process(
                process_transport(
                    element, simulation, source, predecessors, processable_components
                )
            )


def ordering_push(element, simulation, source, predecessors=None):
    """Push mode ordering - monitors output buffer and pushes when items present."""
    helper_functions.debug_print(
        f"Push ordering started for {element.name} from {source}"
    )

    first_iteration = True

    while True:
        # Only wait AFTER first check, not before
        if not first_iteration:
            yield element.env.timeout(SimulationConfig.push_check_frequency)
        first_iteration = False

        # Check if disassembly is open
        (is_working_hours, current_hour, _) = helper_functions.is_working_hours(
            element.simulation
        )

        # If disassembly is closed, wait until it is open again
        if not is_working_hours:
            if current_hour < simulation.start_of_day:
                closed_time = (simulation.start_of_day - current_hour) * 60
            else:
                closed_time = (simulation.start_of_day + 24 - current_hour) * 60
            yield element.env.timeout(closed_time + 1)
            continue

        # Determine output buffer based on source
        output_buffer = None
        if source == "outbuf_to_next" and hasattr(element, "outbuf_to_next"):
            output_buffer = element.outbuf_to_next
        elif source == "outbuf_to_store" and hasattr(element, "outbuf_to_store"):
            output_buffer = element.outbuf_to_store

        # Debug: Check buffer status
        if output_buffer:
            helper_functions.debug_print(
                f"{element.name} checking {source}: {len(output_buffer.items)} items"
            )

        # If there are items in output buffer, push them
        if output_buffer and len(output_buffer.items) > 0:
            # Peek at first item to determine routing
            first_item = output_buffer.items[0] if output_buffer.items else None
            successors = find_successors(element, simulation, source, first_item)
            helper_functions.debug_print(
                f"PUSH: {element.name} has {len(output_buffer.items)} items, found {len(successors)} successors: {[s.name for s in successors]}"
            )
            helper_functions.debug_print(
                f"{element.name} found successors: {[s.name for s in successors]}"
            )
            if successors:
                # Select successor
                if len(successors) > 1:
                    # Multiple successors - use RNG for distribution
                    if (
                        SimulationConfig.behavior_mode
                        == SimulationBehavior.DETERMINISTIC
                    ):
                        # Deterministic: rotate through successors
                        if not hasattr(element, "_push_successor_index"):
                            element._push_successor_index = 0
                        successor = successors[
                            element._push_successor_index % len(successors)
                        ]
                        element._push_successor_index += 1
                    else:
                        # Seeded: random selection using trasnport rng
                        idx = SimulationConfig.rng_transport.randint(
                            0, len(successors) - 1
                        )
                        successor = successors[idx]
                else:
                    # Single successor
                    successor = successors[0]

                helper_functions.debug_print(
                    f"{element.name} pushing to {successor.name}"
                )

                # Process push transport to selected successor
                element.env.process(
                    process_push_transport_simple(
                        element, simulation, source, successor, output_buffer
                    )
                )

        # Wait before checking again -> Moved to start of loop
        # yield element.env.timeout(SimulationConfig.push_check_frequency)


def process_push_transport_simple(
    element, simulation, source, successor, output_buffer
):
    """Simplified push transport - no capacity checks, just push."""
    try:
        helper_functions.debug_print(
            f"Starting push transport from {element.name} to {successor.name}"
        )
        # Check if there are items to push
        if len(output_buffer.items) == 0:
            helper_functions.debug_print(f"No items in output buffer of {element.name}")
            return

        # Get item from output buffer
        item = yield output_buffer.get()
        helper_functions.debug_print(
            f"Got item {item.ID} from {element.name} output buffer"
        )

        # LOG: Item leaves buffer
        SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
            case_id=item.caseID,
            object_id=item.ID,
            object_type=type(item).__name__,
            activity="buffer",
            activity_state="exit",
            resource_id=element.name,
            resource_location=source,
            timestamp=element.env.now,
            related_objects=None,
        )

        # Find suitable vehicle
        fitting_vehicles = []
        for v in simulation.vehicles:
            if (
                v.load_capacity > v.transport_units_used
                and item.transport_units <= v.load_capacity - v.transport_units_used
            ):
                fitting_vehicles.append(v)

        if not fitting_vehicles:
            # Put item back if no vehicle available
            yield output_buffer.put(item)
            helper_functions.debug_print(
                f"No vehicle available for push from {element.name}"
            )
            return

        # Request vehicle
        with ExitStack() as stack:
            requests_vehicle = [
                stack.enter_context(f.create_request(priority=1, preempt=True))
                for f in fitting_vehicles
            ]
            result = yield element.env.any_of(requests_vehicle)
            done_event = next(iter(result))
            vehicle = done_event.vehicle

            # Release other vehicle requests
            for request in requests_vehicle:
                if request != done_event:
                    request.vehicle.release(request)

            # Record vehicle usage
            element.simulation.log_vehicles[element.name][vehicle.name] += 1
            element.simulation.vehicle_requests[vehicle] += 1
            start_busy = element.env.now

            # Drive to element location (if not already there)
            yield from vehicle.drive(element.name)

            # Load item
            yield vehicle.load_item(item)
            yield element.env.timeout(vehicle.load_time)

            # LOG: Loading
            SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                case_id=item.caseID,
                object_id=item.ID,
                object_type=type(item).__name__,
                activity="transport",
                activity_state="load",
                resource_id=vehicle.name,
                resource_location="vehicle",
                timestamp=element.env.now,
                related_objects=None,
            )

            # Drive to successor
            yield from vehicle.drive(successor.name)

            # Unload at successor
            item = yield vehicle.unload_item()

            # LOG: Unloading
            SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                case_id=item.caseID,
                object_id=item.ID,
                object_type=type(item).__name__,
                activity="transport",
                activity_state="unload",
                resource_id=vehicle.name,
                resource_location="vehicle",
                timestamp=element.env.now,
                related_objects=None,
            )

            yield element.env.timeout(vehicle.load_time)

            # PUSH WITHOUT CAPACITY CHECK - just put in successor's entry
            yield successor.entry.put(item)

            # LOG: Item received at successor
            SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                case_id=item.caseID,
                object_id=item.ID,
                object_type=type(item).__name__,
                activity="buffer",
                activity_state="enter",
                resource_id=successor.name,
                resource_location="inbuf",
                timestamp=element.env.now,
                related_objects=None,
            )

            # Update vehicle busy time
            end_busy = element.env.now
            vehicle.busy_time += end_busy - start_busy

            helper_functions.debug_print(
                f"Pushed {item.ID} from {element.name} to {successor.name}"
            )

    except Exception as e:
        helper_functions.debug_print(f"Error in push transport: {e}")


def process_transport(
    element, simulation, source, predecessors=None, processable_components=None
):
    """Handles a single transport process from start to finish.

    Now includes filtering to ensure only compatible components are transported.

    Args:
        element: The destination element (station/storage)
        simulation: The simulation instance
        source: The source type ("outbuf_to_next" or "outbuf_to_store")
        predecessors: List of predecessor elements
        processable_components: List of component types this element can process (None = accept all)
    """
    # ==========================================
    # PHASE 1: Initialize transport
    # ==========================================
    # Increment open orders counter
    element.open_orders += 1

    # DEBUG: Log transport request start
    helper_functions.debug_print(
        f"Transport process started for {element.name} from {source} "
        f"(open orders: {element.open_orders}, entry items: {len(element.entry.items)}/{element.entry_capacity})"
    )

    try:
        # Use provided predecessors or element's predecessors
        if predecessors is None:
            predecessors = element.predecessors

        # ==========================================
        # PHASE 2: Find compatible sources
        # ==========================================

        # WS-01 DEBUG
        if element.name == "ws-01_fluids_01":
            for p in predecessors:
                if p.name == "incoming_storage":
                    items = (
                        len(p.outbuf_to_next.items)
                        if hasattr(p, "outbuf_to_next")
                        else 0
                    )
                    helper_functions.debug_print(
                        f"ws-01 checking incoming_storage at {element.env.now}: {items} items available"
                    )
                    if (
                        items > 0 and element.env.now < 500
                    ):  # Only log details early in simulation
                        for item in p.outbuf_to_next.items[:2]:
                            helper_functions.debug_print(f"  - {item.ID}")
                    break

        # Check if ordering is still necessary -> early exit
        if len(element.entry.items) >= element.order_threshold:
            # element.open_orders -= 1  # ADD THIS
            # No longer needed
            return

        # Find available transport sources with compatible items
        transport_sources = []
        for p in predecessors:
            # DEBUG
            if element.name in ["ws-03_disassembly_01", "ws-04_disassembly_02"]:
                helper_functions.debug_print(
                    f"{element.name} checking predecessor {p.name} at {element.env.now}"
                )

            # Check each predecessor for compatible items
            if source == "outbuf_to_next":
                source_store = p.outbuf_to_next
            elif source == "outbuf_to_store":
                source_store = p.outbuf_to_store
            else:
                continue

            # DEBUG ws-03/ws-04
            if element.name in ["ws-03_disassembly_01", "ws-04_disassembly_02"]:
                helper_functions.debug_print(
                    f"  {p.name}.{source} has {len(source_store.items)} items"
                )
                if len(source_store.items) > 0:
                    helper_functions.debug_print(
                        f"    Items: {[item.ID for item in source_store.items[:2]]}"
                    )

            # Check if this source has compatible items
            has_compatible = False
            if processable_components is None:
                # No filtering - accept any items
                has_compatible = len(source_store.items) > 0
            else:
                # Check if source has items this element can process
                for item in source_store.items:
                    # if can_element_process_item(element, item, processable_components):
                    if can_element_process_item(
                        element, item, processable_components, p
                    ):  # 'p' (the predecessor)
                        has_compatible = True
                        break

            if has_compatible:
                transport_sources.append(p)

            # DEBUG: Log available sources
            helper_functions.debug_print(
                f"  Found {len(transport_sources)} compatible sources: {[s.name for s in transport_sources]}"
            )

        # WS-02 DEBUG
        if element.name == "ws-02_battery_01":
            helper_functions.debug_print(
                f"ws-02 TRANSPORT at {element.env.now}: Found {len(transport_sources)} compatible sources"
            )

            # Check what's actually in ws-01's buffer
            for p in predecessors:
                if p.name == "ws-01_fluids_01":
                    items_in_buffer = p.outbuf_to_next.items
                    helper_functions.debug_print(
                        f"  ws-01 has {len(items_in_buffer)} items in outbuf_to_next"
                    )
                    # Only log first few items to avoid log spam
                    for item in items_in_buffer[:3]:  # Limit to first 3 items
                        variant = getattr(item, "variant", item.type)
                        can_process = can_element_process_item(
                            element, item, processable_components, p
                        )
                        helper_functions.debug_print(
                            f"    {item.ID} ({variant}) - Can process: {can_process}"
                        )
                    if len(items_in_buffer) > 3:
                        helper_functions.debug_print(
                            f"    ... and {len(items_in_buffer) - 3} more items"
                        )
                    break

        # B-01 DEBUG
        if element.name == "b-01_buffer_01":
            helper_functions.debug_print(
                f"b-01 checking predecessors at {element.env.now}:"
            )
            for p in predecessors:
                if source == "outbuf_to_next":
                    source_store = p.outbuf_to_next
                elif source == "outbuf_to_store":
                    source_store = p.outbuf_to_store
                else:
                    continue

                items_count = len(source_store.items)
                helper_functions.debug_print(
                    f"  {p.name}: {items_count} items in {source}"
                )

                # Check if we found any compatible items
                has_compatible = False
                for item in source_store.items:
                    can_process = can_element_process_item(
                        element, item, processable_components, p
                    )
                    if can_process:
                        has_compatible = True
                        helper_functions.debug_print(f"    Found compatible: {item.ID}")
                        break

                if not has_compatible and items_count > 0:
                    helper_functions.debug_print(
                        f"    NO compatible items found despite having {items_count} items!"
                    )

        # If no transport sources with compatible items available, exit
        if len(transport_sources) == 0:
            if element.name == "ws-02_battery_01":
                helper_functions.debug_print(
                    "ws-02: No transport sources found - exiting"
                )
                # element.open_orders -= 1  # ADD THIS
            return

        # ==========================================
        # PHASE 3: Select source
        # ==========================================
        # Select a transport source based on behavior mode
        if SimulationConfig.behavior_mode == SimulationBehavior.DETERMINISTIC:
            transport_source = transport_sources[0]
        else:
            # idx = SimulationConfig.rng_supply.randint(0, len(transport_sources) - 1)
            idx = SimulationConfig.rng_transport.randint(0, len(transport_sources) - 1)
            transport_source = transport_sources[idx]

        # Set the correct store based on source type
        if source == "outbuf_to_next":
            transport_source_store = transport_source.outbuf_to_next
        elif source == "outbuf_to_store":
            transport_source_store = transport_source.outbuf_to_store

        # DEBUG: Log selected source
        helper_functions.debug_print(
            f"  Selected source: {transport_source.name} with {len(transport_source_store.items)} items"
        )

        # DEBUG
        if element.name == "b-01_buffer_01":
            helper_functions.debug_print(
                f"b-01 transport at {element.env.now}: Checking predecessors"
            )
            for p in predecessors:
                if source == "outbuf_to_next":
                    items_in_buffer = p.outbuf_to_next.items
                    helper_functions.debug_print(
                        f"  {p.name} has {len(items_in_buffer)} items in outbuf_to_next"
                    )
                    for item in items_in_buffer[:3]:  # Show first 3 items
                        variant = getattr(
                            item, "variant", getattr(item, "type", "unknown")
                        )
                        helper_functions.debug_print(
                            f"    - {item.ID} (variant: {variant})"
                        )

        # ==========================================
        # PHASE 4: Find suitable vehicle
        # ==========================================
        # Find suitable vehicles
        fitting_vehicles = []
        for v in element.simulation.vehicles:
            # ... check vehicle capacity ...
            # Skip if no capacity available
            if v.load_capacity <= v.transport_units_used:
                continue

            # Check if any compatible item fits
            for item in transport_source_store.items:
                # if processable_components and not can_element_process_item(element, item, processable_components):
                if processable_components and not can_element_process_item(
                    element,
                    item,
                    processable_components,
                    transport_source,  # Add transport_source
                ):
                    continue  # Skip incompatible items

                if item.transport_units <= v.load_capacity - v.transport_units_used:
                    fitting_vehicles.append(v)
                    break

        # If no suitable vehicles, exit
        if len(fitting_vehicles) == 0:
            # element.open_orders -= 1  # ADD THIS
            return

        # Prepare vehicle selection
        if SimulationConfig.behavior_mode != SimulationBehavior.DETERMINISTIC:
            # Shuffle vehicles based on RNG for seeded behavior
            temp_list = list(fitting_vehicles)
            # SimulationConfig.rng_supply.shuffle(temp_list)
            SimulationConfig.rng_transport.shuffle(temp_list)
            fitting_vehicles = temp_list

        # ==========================================
        # PHASE 5: Request and assign vehicle
        # ==========================================
        # DEBUG - Before requesting vehicle
        helper_functions.debug_print(
            f"{element.name}: About to request vehicle at {element.env.now}"
        )

        with ExitStack() as stack:
            requests_vehicle = [
                stack.enter_context(f.create_request(priority=1, preempt=True))
                for f in fitting_vehicles
            ]

            # DEBUG
            helper_functions.debug_print(
                f"{element.name}: Waiting for vehicle (any of {len(requests_vehicle)} vehicles)"
            )

            result = yield element.env.any_of(requests_vehicle)

            helper_functions.debug_print(
                f"{element.name}: Got vehicle at {element.env.now}"
            )

            done_event = next(iter(result))
            vehicle = done_event.vehicle

            # Release other vehicle requests
            for request in requests_vehicle:
                if request != done_event:
                    request.vehicle.release(request)

            # Record vehicle usage
            element.simulation.log_vehicles[element.name][vehicle.name] += 1
            element.simulation.vehicle_requests[vehicle] += 1
            start_busy = element.env.now

            # Calculate order quantity
            order_quantity = element.entry_capacity - len(element.entry.items)

            # ==========================================
            # PHASE 6: Transport to source
            # ==========================================
            # Drive to source
            yield from vehicle.drive(transport_source.name)

            # ==========================================
            # PHASE 7: Load items
            # ==========================================
            # Load items - with filtering
            items_loaded = 0
            while (
                vehicle.transport_units_used < vehicle.load_capacity
                and items_loaded < order_quantity
                and len(transport_source_store.items) > 0
            ):
                # ... load compatible items ...
                compatible_item = None
                for item in transport_source_store.items:
                    # if processable_components is None or can_element_process_item(element, item, processable_components):
                    if processable_components is None or can_element_process_item(
                        element,
                        item,
                        processable_components,
                        transport_source,  # Add transport_source
                    ):
                        compatible_item = item
                        break

                if compatible_item is None:
                    # No compatible items left
                    break

                # DEBUG
                if element.name == "b-01_buffer_01" and compatible_item:
                    variant = getattr(compatible_item, "variant", compatible_item.type)
                    helper_functions.debug_print(
                        f"b-01: Transporting {compatible_item.ID} (variant: {variant}) from {transport_source.name}"
                    )

                # SAFETY CHECK: Verify item still exists (race condition fix)
                if compatible_item not in transport_source_store.items:
                    helper_functions.debug_print(
                        f"{element.name}: Item {compatible_item.ID} no longer available (taken by another station)"
                    )
                    # Don't break or exit - just continue to check for other items
                    continue  # This will go back to the while loop and look for another compatible item

                # Get the specific compatible item
                try:
                    # DEBUG
                    helper_functions.debug_print(
                        f"{element.name}: About to get {compatible_item.ID} from {transport_source.name}"
                    )

                    item = yield transport_source_store.get(
                        lambda x: x == compatible_item
                    )

                    # DEBUG
                    helper_functions.debug_print(
                        f"{element.name}: Successfully got {item.ID}"
                    )

                except Exception as e:
                    helper_functions.debug_print(
                        f"{element.name}: Failed to get {compatible_item.ID}: {e}, continuing"
                    )
                    continue

                # Extract component information
                component_name = item.type
                if hasattr(item, "type") and "_" in item.type:
                    component_name = item.type.split("_")[-1]

                # Determine object type for clear tracking
                object_category = type(item).__name__

                # Handle special cases for dispatch logging

                SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                    case_id=item.caseID,
                    object_id=item.ID,
                    object_type=type(item).__name__,
                    activity="buffer",
                    activity_state="exit",
                    resource_id=transport_source.name,  # Station/storage name only
                    resource_location=source,  # Which buffer
                    timestamp=element.env.now,
                    related_objects=None,
                )

                # Load item and wait
                yield vehicle.load_item(item)
                yield element.env.timeout(vehicle.load_time)
                items_loaded += 1

                # LOG: LOADING OF COMPONENT
                SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                    case_id=item.caseID,
                    object_id=item.ID,
                    object_type=type(item).__name__,
                    activity="transport",
                    activity_state="load",
                    resource_id=vehicle.name,
                    resource_location="vehicle",
                    timestamp=element.env.now,
                    related_objects=None,  # Just loading, no parent tracking needed
                )

            # ==========================================
            # PHASE 8: Transport to destination
            # ==========================================
            # Drive to destination
            yield from vehicle.drive(element.name)

            # ==========================================
            # PHASE 9: Unload items
            # ==========================================
            # Unload items
            while len(vehicle.load.items) > 0:
                item = yield vehicle.unload_item()

                # LOG: UNLOADING OF COMPONENT
                SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                    case_id=item.caseID,
                    object_id=item.ID,
                    object_type=type(item).__name__,
                    activity="transport",
                    activity_state="unload",
                    resource_id=vehicle.name,
                    resource_location="vehicle",
                    timestamp=element.env.now,
                    related_objects=None,  # Just unloading, no parent tracking needed
                )

                # Wait for handling
                yield element.env.timeout(vehicle.load_time)

                yield element.entry.put(item)

                # LOG: COMPONENT RECEIVED AT BUFFER
                SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                    case_id=item.caseID,
                    object_id=item.ID,
                    object_type=type(item).__name__,
                    activity="buffer",
                    activity_state="enter",
                    resource_id=element.name,
                    resource_location="inbuf",
                    timestamp=element.env.now,
                    related_objects=None,
                )

            # Update vehicle busy time
            end_busy = element.env.now
            vehicle.busy_time += end_busy - start_busy

    except Exception as e:
        helper_functions.debug_print(f"Error in transport process: {e}")
    finally:
        # ==========================================
        # PHASE 10: Cleanup
        # ==========================================
        # Always decrement the open orders counter when done
        element.open_orders -= 1

        # DEBUG: Track open_orders for ws-03/ws-04
        if element.name in ["ws-03_disassembly_01", "ws-04_disassembly_02"]:
            helper_functions.debug_print(
                f"{element.name}: Transport process ended, open_orders now = {element.open_orders}"
            )


def can_element_process_item(element, item, processable_components, predecessor=None):
    """
    Check if an element can process an item based on variant routing.

    Args:
        element: The station/storage requesting the item
        item: The product/group/component to check
        processable_components: Components the element can process
        predecessor: The specific predecessor being checked
    """
    # Add debug for b-01_buffer_01
    if element.name == "b-01_buffer_01":
        item_variant = getattr(item, "variant", getattr(item, "type", "unknown"))
        pred_name = predecessor.name if predecessor else "None"
        helper_functions.debug_print(
            f"DEBUG b-01: Checking {item.ID} (variant: {item_variant}) from {pred_name}"
        )

        if hasattr(element, "variant_routing") and predecessor:
            if predecessor.name in element.variant_routing:
                allowed = element.variant_routing[predecessor.name]
                helper_functions.debug_print(f"  Variant routing: {predecessor.name} -> {allowed}")
                if allowed == []:
                    helper_functions.debug_print(f"  Result: ACCEPT (empty list = all)")
                elif item_variant not in allowed:
                    helper_functions.debug_print(f"  Result: REJECT ({item_variant} not in {allowed})")
                    return False
                else:
                    helper_functions.debug_print(f"  Result: ACCEPT ({item_variant} in {allowed})")

    # STEP 1: Check variant routing if configured
    if hasattr(element, "variant_routing") and predecessor:
        predecessor_name = (
            predecessor.name if hasattr(predecessor, "name") else str(predecessor)
        )

        if predecessor_name in element.variant_routing:
            allowed_variants = element.variant_routing[predecessor_name]

            # Extract variant from item
            # For groups, use type instead of variant (same logic as push mode)
            # Groups have variant="car_hd" but type="car_hd_FRONT_AXIS_GROUP"
            if type(item).__name__ == "group":
                item_variant = item.type
            elif hasattr(item, "variant"):
                # Direct variant attribute (for products)
                item_variant = item.variant
            elif hasattr(item, "type"):
                # Fallback to type
                item_variant = item.type
            else:
                item_variant = None

            # If allowed_variants is empty list, accept ALL variants
            if allowed_variants == []:
                pass  # Accept all
            elif item_variant and item_variant not in allowed_variants:
                return False  # This variant not allowed from this predecessor

    # STEP 2: Check if station can process item's components
    # (This allows products with missing components to still be pulled)
    if processable_components is None:
        return True

    # Check components_to_scan (includes missing components)
    if hasattr(item, "components_to_scan"):
        for component in item.components_to_scan:
            if component in processable_components:
                return True

    # Check structure for groups/components
    if hasattr(item, "content") and "structure" in item.content:
        item_components = list(item.content["structure"].keys())
        for component in item_components:
            if component in processable_components:
                return True

    # Check component type
    if hasattr(item, "component"):
        if item.component in processable_components:
            return True

    return False


def find_successors(element, simulation, source, item=None):
    """Find successor elements for push mode.

    Args:
        element: Current element that wants to push items
        simulation: Simulation instance
        source: Buffer type ("outbuf_to_next" or "outbuf_to_store")
        item: Item to push (for variant routing filtering)

    Returns:
        List of successor elements that can receive items
    """
    successors = []

    # For outbuf_to_store, successor is always outgoing_storage
    if source == "outbuf_to_store":
        return [simulation.outgoing_storage]

    # For outbuf_to_next, find stations/storages that have this element as predecessor
    all_elements = simulation.stations + simulation.storages

    for potential_successor in all_elements:
        # Debug for buffer_storage
        if element.name == "buffer_storage":
            helper_functions.debug_print(
                f"  Checking {potential_successor.name}: has predecessors={hasattr(potential_successor, 'predecessors')}, element in preds={element in potential_successor.predecessors if hasattr(potential_successor, 'predecessors') else 'N/A'}"
            )

        if (
            hasattr(potential_successor, "predecessors")
            and element in potential_successor.predecessors
        ):
            # Check variant routing if item provided
            if item is not None:
                # Check if successor has variant_routing configured
                if (
                    hasattr(potential_successor, "variant_routing")
                    and potential_successor.variant_routing
                ):
                    variant_routing = potential_successor.variant_routing
                    sender_name = element.name

                    # If sender is in variant routing config
                    if sender_name in variant_routing:
                        allowed_variants = variant_routing[sender_name]
                        # For groups, use type instead of variant
                        # Groups have variant="car_hd" but type="car_hd_FRONT_AXIS_GROUP"
                        if type(item).__name__ == "group":
                            item_variant = item.type
                        else:
                            item_variant = (
                                item.variant if hasattr(item, "variant") else item.type
                            )

                        helper_functions.debug_print(
                            f"  Variant routing check: {sender_name} -> {potential_successor.name}"
                        )
                        helper_functions.debug_print(f"    Item type: {type(item).__name__}, variant: {item_variant}")
                        helper_functions.debug_print(f"    Allowed: {allowed_variants}")

                        # Only add successor if variant is allowed
                        if item_variant in allowed_variants:
                            successors.append(potential_successor)
                            helper_functions.debug_print(f"    [OK] ACCEPTED")
                        else:
                            helper_functions.debug_print(f"    [X] REJECTED")
                        # else: skip this successor (variant not allowed)
                    else:
                        # Sender not in variant routing - don't add
                        pass
                else:
                    # No variant routing - add successor
                    successors.append(potential_successor)
            else:
                # No item provided - add successor (backward compatible)
                successors.append(potential_successor)

    # If no successors found and element is end-of-line, use outgoing_storage
    if not successors and element in simulation.ends_of_line:
        successors = [simulation.outgoing_storage]

    return successors

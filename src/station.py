"""
File: station.py
Location: /src/station.py
Description: Disassembly station implementation with state machine integration
Author: Patrick Jordan
Version: 2025-10

Implements disassembly stations where products are processed.
Each station can perform specific disassembly steps and manages resource allocation.
This version uses a state machine for accurate time tracking.

Key Components:
- Station class: Main station implementation with state machine
- working_process(): Continuous processing loop
- create_and_put_component_in_storage(): Component handling
- Helper functions for disassembly operations

Station states: IDLE, BUSY, BLOCKED, FAILED, CLOSED
"""

# Standard library imports
from contextlib import ExitStack

# Third-party imports
import simpy

# Local application imports
from src.g import *
from src.product import *
from src.station_state import StationState
import functions
import helper_functions


def create_and_put_component_in_storage(
    station, product, comp_key, comp_properties, storage
):
    """Create a component and put it in the specified storage.

    This function handles the creation of components with appropriate quantities
    and manages the product's disassembly level tracking.

    Args:
        station: The station instance performing the operation
        product: The product being disassembled
        comp_key: The component key/name
        comp_properties: Dictionary of component properties
        storage: The storage to put the component in

    Yields:
        Various SimPy events for timeouts and storage operations
    """
    for i in range(comp_properties["quantity"]):
        c = component(product, comp_key, comp_properties)
        if comp_properties["quantity"] > 1:
            c.ID = f"{c.ID}_{i + 1}"

        # condition adjusted with rng value
        c.condition = SimulationConfig.rng_components.triangular(0, 0.5, 1)
        c.parent_component = product.type  # Set parent component for tracking
        product.level_of_disassembly += 1 / product.parts_count

        # Update product disassembly information in log
        if type(product).__name__ == "product":  # Only update for actual products
            helper_functions.update_log_disassembly(
                product,
                "level_of_disassembly",
                product.level_of_disassembly,
                "equate",
            )

        # LOG: COMPONENT CREATED
        parent_id = product.ID if type(product).__name__ == "product" else product.ID

        SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
            case_id=c.caseID,
            object_id=c.ID,
            object_type=type(c).__name__,
            activity="creation",
            activity_state="complete",
            resource_id=station.name,
            resource_location="workstation",
            timestamp=station.env.now,
            related_objects=f"{parent_id}:parent",
        )

        yield from put_component_in_output_storage(station, c, storage)


def put_component_in_output_storage(station, component_item, storage):
    """Put a component in storage and update the event log.

    This function handles the physical movement of a component to storage,
    manages state transitions, and logs all relevant events.

    Args:
        station: The station instance performing the operation
        component_item: The component to store
        storage: The storage to put the component in

    Yields:
        SimPy events for handling time and storage operations
    """
    c = component_item

    # Handling time for moving to storage
    yield station.env.timeout(station.handling_time)

    # Transition to BLOCKED while waiting for storage capacity
    station.state.enter_state(StationState.BLOCKED, f"Waiting to store {c.ID}")

    # Put in storage (may block)
    yield storage.put(c)

    # Return to BUSY state after successful storage
    station.state.enter_state(StationState.BUSY, f"Completed storing {c.ID}")

    # LOG ENTRY TO OUTGOING BUFFER
    SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
        case_id=c.caseID,
        object_id=c.ID,
        object_type=type(c).__name__,
        activity="buffer",
        activity_state="enter",
        resource_id=station.name,
        resource_location="outbuf_to_store",
        timestamp=station.env.now,
        related_objects=None,  # Just moving to buffer, no parent tracking needed
    )

    # Request outgoing storage to pick up
    station.env.process(
        functions.ordering(
            station.simulation.outgoing_storage,
            station.simulation,
            "outbuf_to_store",
        )
    )

    # Mark product as done
    helper_functions.update_log_disassembly(
        c.parent, "done_time", station.env.now, "equate"
    )
    helper_functions.update_log_disassembly(c.parent, "done", True, "equate")


class Station:
    """Disassembly station where products are processed.

    A disassembly station consists of a workstation, incoming and outgoing storages,
    disassembly equipment, and employees. The station runs a continuous working
    process that checks products for components to disassemble and processes them
    if possible.

    This version uses a state machine for accurate time tracking.

    Attributes:
        env (simpy.Environment): The simulation environment
        name (str): Station identifier
        predecessors (list): Previous stations in the process flow
        entry_capacity (int): Capacity of the entry storage
        entry (simpy.FilterStore): Entry buffer for incoming items
        workstation (simpy.FilterStore): Processing area
        outbuf_to_next (simpy.FilterStore): Exit buffer for items needing further disassembly
        outbuf_to_store (simpy.FilterStore): Exit buffer for completed items
        simulation (object): Reference to the main simulation instance
        order_threshold (int): Entry inventory threshold for ordering
        state (StationState): State machine for tracking station states
        disassembly_time_station (float): Total disassembly time for current product
        handling_time (float): Time to move items in/out of station
        preparation_time (float): Setup time before disassembly
        productcount (int): Number of items processed
        step_names (list): Disassembly steps this station can perform
        step_equipment (list): Equipment required per step
        step_employees (list): Employees required per step
        step_conditions (list): Minimum quality requirement per step
        step_time_start (float): Current step start time
        step_time_done (float): Time completed on current step
        equipment (dict): Available equipment resources
        employees (dict): Available employee resources
        open_orders (int): Number of pending orders
        working_process (simpy.Process): Main working process
    """

    def __init__(
        self: object,
        env: simpy.Environment,
        name: str,
        predecessors: list,
        steps: list,
        simulation: object,
        station_values: dict,
        equipment: list,
        employees: list,
    ) -> None:
        self.env = env
        self.name = name
        self.predecessors = predecessors
        # NEW: Load variant routing configuration
        self.variant_routing = station_values.get("variant_routing", {})
        self.entry_capacity = station_values["entry_capacity"]
        self.entry = simpy.FilterStore(env, self.entry_capacity)
        self.workstation = simpy.FilterStore(env, capacity=float("inf"))
        self.outbuf_to_next = simpy.FilterStore(
            env, capacity=station_values["outbuf_to_next_capacity"]
        )
        self.outbuf_to_store = simpy.FilterStore(
            env, capacity=station_values["outbuf_to_store_capacity"]
        )
        self.simulation = simulation
        self.order_threshold = station_values["entry_order_threshold"]

        # Initialize state machine
        self.state = StationState(env, name)

        self.blocked = False
        self.blocked_time_start = 0

        self.disassembly_time_station = 0
        self.handling_time = SimulationConfig.handling_time
        self.preparation_time = station_values["preparation_time"]
        self.productcount = 0
        self.step_names = [step[0] for step in steps]
        self.step_equipment = [step[1] for step in steps]
        self.step_employees = [step[2] for step in steps]
        self.step_conditions = [step[3] for step in steps]
        self.step_time_start = 0
        self.step_time_done = 0
        self.open_orders = 0

        # Create each element
        self.equipment = {}
        for element in equipment:
            capacity = 1
            self.equipment[element[0]] = [
                simpy.PreemptiveResource(self.env, capacity) for _ in range(element[1])
            ]

        # Create each element
        self.employees = {}
        for element in employees:
            capacity = 1
            self.employees[element[0]] = [
                simpy.PreemptiveResource(self.env, capacity) for _ in range(element[1])
            ]

        # Start working process
        self.working_process = env.process(self.working())

        # Debug log initialization
        self.debug_time_log = []

        # Start ordering process for entry buffer (both pull and push modes)
        # This runs continuously to monitor when products are needed
        import functions

        self.entry_ordering_process = env.process(
            functions.ordering(self, simulation, "outbuf_to_next")
        )
        helper_functions.debug_print(f"Started entry ordering process for {self.name}")

        # In push mode, ALSO start ordering processes for output buffers
        if getattr(SimulationConfig, "material_flow_mode", "pull") == "push":
            # Start push process for outbuf_to_next (pushing TO successors)
            self.output_ordering_next = env.process(
                functions.ordering(self, simulation, "outbuf_to_next")
            )
            # Start push process for outbuf_to_store (pushing TO outgoing_storage)
            self.output_ordering_store = env.process(
                functions.ordering(self, simulation, "outbuf_to_store")
            )
            helper_functions.debug_print(f"Started push ordering processes for {self.name}")

    def working(self: object) -> None:
        """This method represents the continuously ongoing working process of a disassembly station.
        The process involves handling, disassembling, logging, and managing the transfer of products, components
        and groups within a workstation.

        Update: uses the state machine for accurate time tracking
        """
        while True:
            try:
                # ==========================================
                # PHASE 1: State management
                # ==========================================
                # Ensure that in the correct state (if machine not actively working)
                if self.state.current_state not in [
                    StationState.BUSY,
                    StationState.BLOCKED,
                    StationState.FAILED,
                    StationState.CLOSED,
                ]:
                    self.state.enter_state(StationState.IDLE, "Waiting for work")

                # ==========================================
                # PHASE 2A: Get work item
                # ==========================================
                # If workstation is not empty, get new object from workstation
                if len(self.workstation.items) > 0:
                    # Transition to BUSY for getting work
                    self.state.enter_state(
                        StationState.BUSY, "Getting item from workstation"
                    )
                    product = yield self.workstation.get()

                    # DEBUG
                    helper_functions.debug_print(
                        f"\nProcessing from workstation: {product.ID} type={type(product).__name__}"
                    )
                    if hasattr(product, "content") and "structure" in product.content:
                        helper_functions.debug_print(
                            f"  Remaining components: {list(product.content['structure'].keys())}"
                        )
                    if hasattr(product, "components_to_scan"):
                        helper_functions.debug_print(
                            f"  Components to scan: {product.components_to_scan}"
                        )

                # Get an object from station entry (ordering process runs separately)
                else:
                    # ==========================================
                    # PHASE 1B: Wait for new items
                    # ==========================================
                    # Ordering process handles requesting items from predecessors
                    # This just waits for items to arrive in entry buffer
                    product = yield self.entry.get()

                    # ==========================================
                    # PHASE 2: Handle incoming product
                    # ==========================================
                    # Transition to BUSY for handling
                    self.state.enter_state(
                        StationState.BUSY, f"Handling product {product.ID}"
                    )

                    # LOG: COMPONENTS LEAVES INCOMING BUFFER (product picked for processing at station)
                    SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                        case_id=product.caseID,
                        object_id=product.ID,
                        object_type=type(product).__name__,
                        activity="buffer",
                        activity_state="exit",
                        resource_id=self.name,
                        resource_location="inbuf",
                        timestamp=self.env.now,
                        related_objects=None,  # Leaving buffer, no parent tracking needed
                    )

                    # Put product in self.workstation
                    yield self.env.timeout(self.handling_time)
                    yield self.workstation.put(product)

                    # LOG: COMPONENT ENTERS STATION (= start handling component)
                    SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                        case_id=product.caseID,
                        object_id=product.ID,
                        object_type=type(product).__name__,
                        activity="handling",
                        activity_state="start",
                        resource_id=self.name,
                        resource_location="workstation",
                        timestamp=self.env.now,
                        related_objects=None,  # Just entering station, no parent tracking needed
                    )

                    # Wait for preparation time of station
                    yield self.env.timeout(self.preparation_time)

                # ==========================================
                # PHASE 4: Scan and disassemble
                # ==========================================
                # Reset disassembly_time for this product
                self.disassembly_time_station = 0

                # Scan and disassemble - method handles its own state transitions
                yield from self.scan_for_target_components(
                    product.content["structure"], product
                )

                # Count disassembled object
                self.productcount += 1

                # Update product disassembly information in log
                if (
                    type(product).__name__ == "product"
                ):  # Only update for actual products
                    helper_functions.update_log_disassembly(
                        product,
                        "level_of_disassembly",
                        product.level_of_disassembly,
                        "equate",
                    )

                # ==========================================
                # PHASE 5: Determine product destination/next steps based on remaining parts
                # ==========================================
                # Count remaining parts
                parts_count = helper_functions.count_parts(product.content["structure"])

                # HANDLE DIFFERENT CASES BASED ON PARTS COUNT
                if parts_count == 1:
                    # ==========================================
                    # CASE A: Single component left
                    # ==========================================
                    comp_key = list(product.content["structure"].keys())[0]
                    comp_properties = product.content["structure"][comp_key]

                    yield from create_and_put_component_in_storage(
                        self, product, comp_key, comp_properties, self.outbuf_to_store
                    )

                    # Remove product from workstation if it still exists there
                    if product in self.workstation.items:
                        yield self.workstation.get(lambda x: x == product)
                    del product

                elif parts_count == 0:
                    # ==========================================
                    # CASE B: No components left
                    # ==========================================
                    # Mark product as done in log
                    helper_functions.update_log_disassembly(
                        product, "done_time", self.env.now, "equate"
                    )
                    helper_functions.update_log_disassembly(
                        product, "done", True, "equate"
                    )

                    # Remove product from workstation if it still exists there
                    if product in self.workstation.items:
                        yield self.workstation.get(lambda x: x == product)
                    del product

                else:
                    # ==========================================
                    # CASE C: Multiple components remain (group)
                    # ==========================================
                    # Transition to BLOCKED while determining where to send the product
                    self.state.enter_state(
                        StationState.BLOCKED, "Deciding next destination"
                    )

                    # Check if group contains elements that are in step_names
                    group_done = True
                    for key, element in product.content["structure"].items():
                        if key in self.step_names and key in product.components_to_scan:
                            # Check if this component can actually be processed
                            # (not just in components_to_scan but also meets condition requirements)
                            component_condition = product.condition + element.get(
                                "condition_dev_mu", 0
                            )
                            component_condition = min(max(component_condition, 0), 1)
                            min_condition = self.step_conditions[
                                self.step_names.index(key)
                            ]

                            # Only put back if it's mandatory OR meets condition requirements
                            if (
                                element.get("mandatory", False)
                                or component_condition >= min_condition
                            ):
                                # If so, put group back in workstation for further disassembly
                                group_done = False

                                # Remove product from workstation to make sure it only exists once
                                if product in self.workstation.items:
                                    yield self.workstation.get(lambda x: x == product)

                                # DEBUG
                                helper_functions.debug_print(
                                    f"  Putting {product.ID} BACK in workstation for more processing"
                                )

                                # Put product back in workstation
                                yield self.workstation.put(product)

                                # Transition back to BUSY
                                self.state.enter_state(
                                    StationState.BUSY,
                                    "Product requires more processing",
                                )
                                break
                            else:
                                # Component can't be processed due to condition
                                # BUT: Only remove if it doesn't block other components in scan list
                                blocks_scanned_component = False
                                for other_key, other_element in product.content[
                                    "structure"
                                ].items():
                                    if (
                                        other_key in product.components_to_scan
                                        and key in other_element.get("blocked_by", [])
                                    ):
                                        blocks_scanned_component = True
                                        break

                                if blocks_scanned_component:
                                    # Keep in scan list - must be processed to unblock path
                                    helper_functions.debug_print(
                                        f"  {key} has low quality but blocks other components - keeping in scan list"
                                    )
                                elif key in product.components_to_scan:
                                    # Safe to remove - doesn't block anything important
                                    product.components_to_scan.remove(key)
                                    helper_functions.debug_print(
                                        f"  Removed {key} from components_to_scan - condition too low"
                                    )

                    if group_done:
                        # ==========================================
                        # CASE C1: Group finished at this station
                        # ==========================================
                        # If group is done, check if it has components whose disassembly has not yet been attempted
                        # For end-of-line stations: check if any progress can be made (prevents infinite loop)
                        # For mid-line stations: send downstream if components remain

                        should_send_to_storage = False

                        if len(product.components_to_scan) == 0:
                            # No components left to scan - product is done
                            should_send_to_storage = True
                        elif self in self.simulation.ends_of_line:
                            # End-of-line station: check if THIS station can make progress
                            # (prevents infinite loop when remaining components can't be processed)
                            can_process_remaining = False
                            for component in product.components_to_scan:
                                if (
                                    component in self.step_names
                                    and helper_functions.is_in_product(
                                        product.content["structure"], component
                                    )
                                ):
                                    # Check if it's blocked by components that can't be removed
                                    blocking = helper_functions.get_blocking_components(
                                        product.content["structure"], component
                                    )
                                    # Can process if: no blockers OR all blockers are also in components_to_scan
                                    if not blocking or all(
                                        b in product.components_to_scan
                                        for b in blocking
                                    ):
                                        can_process_remaining = True
                                        break

                            if not can_process_remaining:
                                should_send_to_storage = True
                        # else: Mid-line station with components remaining -> send to next station

                        if should_send_to_storage:
                            # ==========================================
                            # CASE C1a: All components checked OR no more progress possible - send to final storage
                            # ==========================================
                            # LOG: END OF HANDLING (Leaves workstation)
                            SimulationConfig.eventlog = (
                                helper_functions.add_to_eventlog_v3(
                                    case_id=product.caseID,
                                    object_id=product.ID,
                                    object_type=type(product).__name__,
                                    activity="handling",
                                    activity_state="end",
                                    resource_id=self.name,
                                    resource_location="workstation",
                                    timestamp=self.env.now,
                                    related_objects=None,  # Product itself released
                                )
                            )

                            # If all components have been checked, put product in outbuf_to_store
                            yield self.env.timeout(self.handling_time)
                            yield self.outbuf_to_store.put(product)

                            # DEBUG
                            if self.name == "ws-01_fluids_01":
                                variant = getattr(product, "variant", product.type)
                                helper_functions.debug_print(
                                    f"ws-01: Put {product.ID} ({variant}) in outbuf_to_store at {self.env.now}"
                                )

                            # Return to BUSY after handling output
                            self.state.enter_state(
                                StationState.BUSY, "Sent product to outgoing storage"
                            )

                            # LOG: COMPONENTS ENTERS OUTGOING BUFFER (MOVED TO FINAL STORAGE)
                            SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                                case_id=product.caseID,
                                object_id=product.ID,
                                object_type=type(product).__name__,
                                activity="buffer",
                                activity_state="enter",
                                resource_id=self.name,
                                resource_location="outbuf_to_store",
                                timestamp=self.env.now,
                                related_objects=None,  # Just moving to buffer, no parent tracking needed
                            )

                            # Order outgoing_storage to pick up component
                            self.env.process(
                                functions.ordering(
                                    self.simulation.outgoing_storage,
                                    self.simulation,
                                    "outbuf_to_store",
                                )
                            )

                            # Remove product from workstation if it still exists there
                            if product in self.workstation.items:
                                yield self.workstation.get(lambda x: x == product)

                        # If not all components have been checked, put product in outbuf_to_next
                        else:
                            # ==========================================
                            # CASE C1b: More components to check - send downstream
                            # ==========================================
                            # LOG: PRODUCT LEAVES STATION (= End of handling)
                            SimulationConfig.eventlog = (
                                helper_functions.add_to_eventlog_v3(
                                    case_id=product.caseID,
                                    object_id=product.ID,
                                    object_type=type(product).__name__,
                                    activity="handling",
                                    activity_state="end",
                                    resource_id=self.name,
                                    resource_location="workstation",
                                    timestamp=self.env.now,
                                    related_objects=None,  # Product itself released
                                )
                            )

                            # Put product in outbuf_to_next for further disassembly
                            yield self.env.timeout(self.handling_time)

                            # Advance routing plan to next station
                            if hasattr(product, "advance_route"):
                                product.advance_route()

                            yield self.outbuf_to_next.put(product)

                            # DEBUG
                            if self.name == "ws-01_fluids_01":
                                variant = getattr(product, "variant", product.type)
                                helper_functions.debug_print(
                                    f"ws-01: Put {product.ID} ({variant}) in outbuf_to_next at {self.env.now} | "
                                    f"Buffer now has {len(self.outbuf_to_next.items)} items"
                                )

                            # Return to BUSY after handling output
                            self.state.enter_state(
                                StationState.BUSY, "Sent product to disassembly"
                            )

                            # LOG: PRODUCT ENTERS OUTGOING BUFFER (Moves to next disassembly step)
                            SimulationConfig.eventlog = (
                                helper_functions.add_to_eventlog_v3(
                                    case_id=product.caseID,
                                    object_id=product.ID,
                                    object_type=type(product).__name__,
                                    activity="buffer",
                                    activity_state="enter",
                                    resource_id=self.name,
                                    resource_location="outbuf_to_next",
                                    timestamp=self.env.now,
                                    related_objects=None,  # Product itself released
                                )
                            )

                            # Order outbuf_to_next to pick up component if end of line
                            if self in self.simulation.ends_of_line:
                                self.env.process(
                                    functions.ordering(
                                        self.simulation.outgoing_storage,
                                        self.simulation,
                                        "outbuf_to_next",
                                    )
                                )

                            # Remove product from workstation if it still exists there
                            if product in self.workstation.items:
                                yield self.workstation.get(lambda x: x == product)

                            # Mark product as done in log_disassembly if this station is end of line
                            if self in self.simulation.ends_of_line:
                                helper_functions.update_log_disassembly(
                                    product, "done", True, "equate"
                                )

                # ==========================================
                # PHASE 6: Complete cycle and return to idle
                # ==========================================
                # Final state transition back to IDLE
                self.state.enter_state(StationState.IDLE, "Completed processing cycle")

            except Exception as e:
                helper_functions.debug_print(f"Error in station {self.name} working process: {e}")
                self.state.enter_state(StationState.IDLE, f"Error recovery: {str(e)}")

    def scan_for_target_components(self: object, structure: dict, object: object):
        """This method scans for target components in a product's structure and performs disassembly operations.
        It manages state transitions during the scanning process.
        Tracks whether any processing occurred."""

        # Safety check: if components_to_scan is empty, skip scanning (handle infinite loop)
        if not hasattr(object, "components_to_scan") or not object.components_to_scan:
            helper_functions.debug_print(
                f"No components to scan for product {object.ID}"
            )
            return

        # Debug log scanning start
        helper_functions.debug_print(
            f"Station {self.name} scanning product {object.ID} type={object.type}"
        )

        # Start with BUSY state for scanning
        self.state.enter_state(StationState.BUSY, f"Scanning product {object.ID}")

        # LOG: START IDENTIFYING COMPONENTS THAT SHOULD BE DISASSEMBLED
        SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
            case_id=object.caseID,
            object_id=object.ID,
            object_type=type(object).__name__,
            activity="inspection",
            activity_state="start",
            resource_id=self.name,
            resource_location="workstation",
            timestamp=self.env.now,
            related_objects=None,
        )

        # Initialize method variables
        self.disassembly_time_station = 0
        self.steps_todo = []  # initialize list for steps this station has do to
        self.steps_done = []  # initialize list for steps done

        # add all components and groups that are in steps and whose disassembly has not yet been attempted to steps_todo
        for key, element in structure.items():
            if key in self.step_names and key in object.components_to_scan:
                # ALWAYS add to steps_todo (mandatory components must be disassembled regardless of quality)
                self.steps_todo.append(key)
                helper_functions.debug_print(
                    f"  Station {self.name} can process component {key}"
                )

                # LOG: LIST COMPONENTS THAT SHOULD BE DISASSEMBLED (including quantity and quality info)
                # Get quantity
                quantity = element["quantity"]

                if "structure" in element:
                    # It's a group
                    identified_object_type = "group"
                else:
                    # It's a component (part)
                    identified_object_type = "comp"

                # Check quality level for logging purposes
                # Get component condition (with deviation)
                component_condition = object.condition + element.get(
                    "condition_dev_mu", 0
                )
                component_condition = min(max(component_condition, 0), 1)

                # Get minimum required condition for this component
                step_index = self.step_names.index(key)
                min_condition = self.step_conditions[step_index]

                # Determine relationship based on quality and quantity (for logging only)
                if component_condition < min_condition:
                    # Quality too low - log it but still process (mandatory components must be disassembled)
                    if quantity > 1:
                        identified_relationship = f"low_quality_qty{quantity}"
                    else:
                        identified_relationship = "low_quality"
                elif quantity > 1:
                    identified_relationship = f"identified_qty{quantity}"
                else:
                    identified_relationship = "identified"

                # Add blocking/mandatory flags to the relationship
                flags = []
                if element.get("mandatory", False):
                    flags.append("mandatory")

                # Check if this component is blocking any other components
                if "blocked_by" in element or any(
                    key in comp.get("blocked_by", [])
                    for comp in structure.values()
                    if isinstance(comp, dict)
                ):
                    # This component either has blockers OR blocks something else
                    # Check if it blocks something
                    blocks_others = any(
                        key in comp.get("blocked_by", [])
                        for comp in structure.values()
                        if isinstance(comp, dict)
                    )
                    if blocks_others:
                        flags.append("blocking")

                # Append flags to relationship if any
                if flags:
                    identified_relationship = (
                        f"{identified_relationship}_{'_'.join(flags)}"
                    )

                SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                    case_id=object.caseID,
                    object_id=object.ID,
                    object_type=type(object).__name__,
                    activity="inspection",
                    activity_state="complete",
                    resource_id=self.name,
                    resource_location="workstation",
                    timestamp=self.env.now,
                    related_objects=f"{identified_object_type}_{object.caseID:03d}_{key}:{identified_relationship}",  # Specifies WHICH component
                )

        # Check for MISSING components - only check direct children at current level
        present_components = set(structure.keys())

        # Get the original direct children at this level (not nested components)
        if hasattr(object, "original_direct_children"):
            original_direct_children = object.original_direct_children
        else:
            # Fallback: use current structure keys (shouldn't happen with updated product/group classes)
            original_direct_children = set(structure.keys())

        for component_name in self.step_names:
            if component_name not in present_components:
                # Only log as missing if it was a direct child at this level
                if component_name in original_direct_children:
                    SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                        case_id=object.caseID,
                        object_id=object.ID,
                        object_type=type(object).__name__,
                        activity="inspection",
                        activity_state="complete",
                        resource_id=self.name,
                        resource_location="workstation",
                        timestamp=self.env.now,
                        related_objects=f"comp_{object.caseID:03d}_{component_name}:missing",
                    )
                    # Remove missing component from components_to_scan
                    # Downstream stations shouldn't try to process missing components
                    if component_name in object.components_to_scan:
                        object.components_to_scan.remove(component_name)
                        helper_functions.debug_print(
                            f"  Removed missing component '{component_name}' from components_to_scan"
                        )
        # get mandatory components in product that this station can disassemble in own list to remove them first
        mandatory_components = helper_functions.get_mandatory_components(structure)

        # get highest root of each mandatory component
        mandatory_components_roots = [
            helper_functions.get_highest_parent(structure, c)
            for c in mandatory_components
        ]
        # filter mandatory_components_roots to only include those that are in steps_todo
        self.mandatory_steps = [
            c for c in mandatory_components_roots if c in self.steps_todo
        ]

        # start self.disassemble_if_not_blocked for all mandatory steps this station can perform
        while self.mandatory_steps:
            key = self.mandatory_steps[0]
            try:
                # Pass the product type as parent_component for top-level disassembly
                yield from self.disassemble_if_not_blocked(
                    structure,
                    key,
                    object,
                    target_mandatory=True,
                    parent_component=object.type,
                    checked_components=None,
                )
            # if disassembly fails, remove component from steps_todo and mandatory_steps so it is not attempted again
            except Exception as e:
                # print(e)
                self.steps_todo.remove(key)
                self.mandatory_steps.remove(key)

        # start self.disassemble_if_not_blocked for all remaining steps to do
        while self.steps_todo:
            key = self.steps_todo[0]
            try:
                # Pass the product type as parent_component for top-level disassembly
                yield from self.disassemble_if_not_blocked(
                    structure,
                    key,
                    object,
                    parent_component=object.type,
                    checked_components=None,
                )
            # if disassembly fails, remove component from steps_todo so it is not attempted again
            except Exception as e:
                # print(str(e))
                self.steps_todo.remove(key)

        # Return to BUSY state after scanning is complete
        self.state.enter_state(
            StationState.BUSY, f"Completed scanning product {object.ID}"
        )

    def disassemble_if_not_blocked(
        self: object,
        structure: dict,
        component: str,
        object: object,
        target_mandatory: bool = None,
        parent_component: str = None,
        checked_components: List[str] = None,
    ):
        """This method attempts to disassemble a target component and recursively calls itself for any
        components blocking the target component. It manages state transitions during this process.
        """
        # Remain in BUSY state for this operation
        # Track which components have already been checked
        if checked_components is None:
            checked_components = []  # Only create new list on first call

        if component in checked_components:
            return  # Already checked this component, avoid infinite loop

        checked_components.append(component)

        # set target_mandatory to value of component from first call of this method
        if target_mandatory is None:
            target_mandatory = structure[component]["mandatory"]

        # Get components that block the current one
        components_blocking = helper_functions.get_blocking_components(
            structure, component
        )
        # Filter those that are still in the product
        components_blocking_current = [
            c
            for c in components_blocking
            if helper_functions.is_in_product(structure, c)
        ]

        # If there are components that block the current one, look at them first
        if components_blocking_current:
            for c in components_blocking_current:
                # if component has not yet been checked
                if c not in self.checked_components:
                    # add component to checked_components to avoid checking it again
                    self.checked_components.append(c)

                    # recursively call this method for blocking components
                    # Pass the current component as parent for proper hierarchy tracking
                    yield from self.disassemble_if_not_blocked(
                        structure,
                        c,
                        object,
                        target_mandatory,
                        component,  # Pass current as parent
                        checked_components,  # Pass the checked list
                    )
        # If no components are blocking the current one, disassemble it
        else:
            # disassemble only if this station can perform this step
            if component in self.step_names:
                # disassemble only if this step has not yet been done
                if component in self.steps_todo:
                    # launch disassembly of component - pass parent_component for tracking
                    yield from self.disassemble(
                        component,
                        structure[component],
                        object,
                        target_mandatory,
                        parent_component,  # Pass parent_component for hierarchical tracking
                    )

                    # if blocking components from steps_todo were removed,
                    # their step was already done and doesn't need to be done again
                    if component in self.steps_todo:
                        # remove blocking component from self.steps_todo
                        self.steps_todo.remove(component)

                        # add blocking component to self.steps_done
                        self.steps_done.append(component)

                # step is already done
                else:
                    # step is mandatory
                    if component in self.mandatory_steps:
                        # remove blocking component from self.mandatory_steps
                        self.mandatory_steps.remove(component)

            # station cannot perform this step
            else:
                raise Exception("Cannot disassemble component " + component)

    def disassemble(
        self: object,
        comp_key: str,
        comp_properties: dict,
        product: object,
        target_mandatory: bool = None,
        parent_component: str = None,
    ) -> None:
        """Executes a single disassembly step."""
        # Enter BUSY state for this disassembly operation
        self.state.enter_state(StationState.BUSY, f"Disassembling {comp_key}")

        disassembled_quantity = 0

        # Disassemble component as often as specified by quantity in json
        for i in range(comp_properties["quantity"]):
            # determine random condition of component as superposition of product condition and random deviation
            min_deviation = comp_properties["condition_dev_min"]
            max_deviation = comp_properties["condition_dev_max"]
            likely_deviation = comp_properties["condition_dev_mu"]

            if SimulationConfig.behavior_mode == SimulationBehavior.DETERMINISTIC:
                # Deterministic -> always use mode value
                deviation = likely_deviation
            else:
                # Seeded -> use random number generator
                deviation = SimulationConfig.rng_components.triangular(
                    min_deviation, max_deviation, likely_deviation
                )
            component_condition = product.condition + deviation
            # Ensure the component condition is within the range [0, 1]
            component_condition = min(max(component_condition, 0), 1)

            # ==========================================
            # DISASSEMBLY DECISION
            # ==========================================
            # Check if this component blocks any other components
            blocks_other_component = False
            for other_key, other_element in product.content["structure"].items():
                if comp_key in other_element.get("blocked_by", []):
                    blocks_other_component = True
                    break

            # True if either target_mandatory or mandatory component
            # or blocking other components or a required minimum condtion is met
            disassembly_decision = (
                target_mandatory
                or comp_properties["mandatory"]
                or blocks_other_component
                or (
                    component_condition
                    >= self.step_conditions[self.step_names.index(comp_key)]
                )
            )

            # Debug log decision
            helper_functions.debug_print(
                f"  Disassembly decision for {comp_key}: {disassembly_decision} "
                f"(mandatory={target_mandatory or comp_properties['mandatory']}, "
                f"blocking={blocks_other_component}, "
                f"condition={component_condition:.2f} >= {self.step_conditions[self.step_names.index(comp_key)]:.2f})"
            )

            # Check if component should be disassembled
            if disassembly_decision:
                # Determine if a group or component is disassembled
                if "structure" in comp_properties:
                    target_object_type = "group"
                else:
                    target_object_type = "comp"

                # Build the target component ID
                # target_component_id = f"comp_{product.caseID:03d}_{comp_key}"
                target_component_id = (
                    f"{target_object_type}_{product.caseID:03d}_{comp_key}"
                )

                # Add quantity suffix if needed
                if comp_properties["quantity"] > 1:
                    target_suffix = f"_{i + 1}/{comp_properties['quantity']}"
                else:
                    target_suffix = ""

                SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                    case_id=product.caseID,
                    object_id=product.ID,  # The product/group being disassembled
                    object_type=type(product).__name__,
                    activity="disassembly",
                    activity_state="start",
                    resource_id=self.name,
                    resource_location="workstation",
                    timestamp=self.env.now,
                    related_objects=f"{target_component_id}{target_suffix}:target",
                )

                # Log how much time was already spent on this step (for interruptions)
                self.step_time_done = 0
                # Log if step was completed or interrupted (for interruptions)
                step_completed = False
                # Log if disassembly was interrupted (for interruptions)
                interrupt_disassembly = False

                # Read required resources for this step
                step_equipment = self.step_equipment[self.step_names.index(comp_key)]
                step_employees = self.step_employees[self.step_names.index(comp_key)]

                # Track disassembly time spend on this component (for debugging)
                disassembly_time = 0

                while not step_completed:
                    try:
                        with ExitStack() as stack:
                            # Iterate over each element in step_equipments:
                            for element in step_equipment:
                                # Check if equipment is avalaible at the station
                                if element[0] in self.equipment:
                                    # Request equipment locally
                                    requests_equipment = [
                                        stack.enter_context(
                                            self.equipment[element[0]][i].request(
                                                priority=1, preempt=True
                                            )
                                        )
                                        for i in range(element[1])
                                    ]
                                # If equipment is not available at the station, check globally
                                elif element[0] in self.simulation.global_equipment:
                                    global_capacity = self.simulation.global_equipment[
                                        element[0]
                                    ].capacity
                                    if global_capacity < element[1]:
                                        raise RuntimeError(
                                            f"Not enough {element[0]} available globally. Required: {element[1]}, Available: {global_capacity}"
                                        )
                                    # Request equipment globally
                                    requests_equipment = [
                                        stack.enter_context(
                                            self.simulation.global_equipment[
                                                element[0]
                                            ].request(priority=1, preempt=True)
                                        )
                                        for _ in range(element[1])
                                    ]
                                else:
                                    raise RuntimeError(
                                        f"Equipment {element[0]} is required but not available."
                                    )

                                yield self.env.all_of(requests_equipment)

                            # Request all employee resources required for this step
                            for element in step_employees:
                                if element[0] in self.employees:
                                    requests_employees = [
                                        stack.enter_context(
                                            self.employees[element[0]][i].request(
                                                priority=1, preempt=True
                                            )
                                        )
                                        for i in range(element[1])
                                    ]

                                elif element[0] in self.simulation.global_employees:
                                    # Not enough available globally
                                    if (
                                        self.simulation.global_employees[
                                            element[0]
                                        ].capacity
                                        < element[1]
                                    ):
                                        print(
                                            f"ERROR: employee {element[0]} is required {element[1]}x at the same time but only {self.simulation.global_employees[element[0]].capacity}x are available globally"
                                        )
                                    else:
                                        requests_employees = [
                                            stack.enter_context(
                                                self.simulation.global_employees[
                                                    element[0]
                                                ].request(
                                                    priority=1,
                                                    preempt=True,
                                                )
                                            )
                                            for i in range(element[1])
                                        ]

                                else:
                                    raise RuntimeError(
                                        f"Employee {element[0]} is required but not available."
                                    )

                                yield self.env.all_of(requests_employees)

                            # Disassembly is attempted for the first time
                            if not interrupt_disassembly:
                                # Get disassembly_time_ideal and add condition dependent deviation
                                disassembly_time_ideal = comp_properties["time"]
                                disassembly_time = (
                                    disassembly_time_ideal
                                    + (1 - component_condition)
                                    * (SimulationConfig.scale_disassembly_time - 1)
                                    * disassembly_time_ideal
                                )

                                # Log time of start of this step for tracking interruptions
                                self.step_time_start = self.env.now

                                # Wait for disassembly time
                                yield self.env.timeout(disassembly_time)

                            # Disassembly time already determined -> wait for remaining time
                            else:
                                # Ensure non-negative step_time_remaining
                                step_time_remaining = max(
                                    0, disassembly_time - self.step_time_done
                                )

                                # Log if we had to correct a negative value
                                if disassembly_time - self.step_time_done < 0:
                                    print(
                                        f"INFO: Corrected negative step_time_remaining in {self.name} for {comp_key}"
                                    )

                                # Update step tracking
                                self.step_time_start = self.env.now

                                # Wait for the remaining time
                                yield self.env.timeout(step_time_remaining)

                            step_completed = True

                            # LOG: DISASSEMBLY COMPLETED (= component removed)
                            # Build the removed component ID
                            removed_component_id = (
                                f"comp_{product.caseID:03d}_{comp_key}"
                            )

                            # Add quantity suffix if needed
                            if comp_properties["quantity"] > 1:
                                removed_suffix = (
                                    f"_{i + 1}/{comp_properties['quantity']}"
                                )
                            else:
                                removed_suffix = ""

                            # Before logging disassembly,complete:
                            if "structure" in comp_properties:
                                # It's going to be a group
                                removed_object_type = "group"
                            else:
                                # It's going to be a component
                                removed_object_type = "comp"

                            removed_component_id = (
                                f"{removed_object_type}_{product.caseID:03d}_{comp_key}"
                            )

                            SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                                case_id=product.caseID,
                                object_id=product.ID,
                                object_type=type(product).__name__,
                                activity="disassembly",
                                activity_state="complete",
                                resource_id=self.name,
                                resource_location="workstation",
                                timestamp=self.env.now,
                                related_objects=f"{removed_component_id}{removed_suffix}:removed",
                            )

                    # Interuption of disassembly by failure or end of working hours
                    except simpy.Interrupt as interrupt:
                        if disassembly_time == 0:
                            print("ERROR: disassembly_time = 0")
                            # Set a minimum value to avoid division by zero errors
                            disassembly_time = 0.1

                        # Mark that step interrupted
                        interrupt_disassembly = True

                        # Calculate how much time was spent on this step since last start
                        if self.env.now > self.step_time_start:
                            time_spent = self.env.now - self.step_time_start

                            # Add to accumulated step time done for this component
                            self.step_time_done += time_spent

                            # Make sure step_time_done doesn't exceed total disassembly_time
                            self.step_time_done = min(
                                self.step_time_done, disassembly_time
                            )

                # Group of components was disassembled
                if "structure" in comp_properties:
                    # Create group
                    c = group(comp_key, product, comp_properties)
                    # set parts_count of group
                    c.parts_count = helper_functions.count_parts(
                        comp_properties["structure"]
                    )
                    # Set component and parent_component -> tracking
                    c.component = comp_key
                    c.parent_component = product.component
                # Component was disassembled
                else:
                    # Create individual component
                    c = component(product, comp_key, comp_properties)
                    # Set component and parent_component -> tracking
                    c.component = comp_key
                    c.parent_component = product.component

                # add iterator to component ID if more than one component is created
                if comp_properties["quantity"] > 1:
                    c.ID = c.ID + "_" + str(i + 1)

                # set condition of created component or group
                c.condition = component_condition

                # add up disassembly_time for logging
                self.disassembly_time_station += disassembly_time

                # Transition to BLOCKED state when moving to storage
                self.state.enter_state(StationState.BLOCKED, f"Storing {comp_key}")

                # When handling a disassembled group
                if "structure" in comp_properties:
                    # Check if group contains elements that are in step_names
                    group_done = True
                    for key, element in comp_properties["structure"].items():
                        # If so put group in workstation for further disassembly
                        if (
                            key in self.step_names
                            and key in product.components_to_scan
                            and key != comp_key
                        ):
                            # If so, put group back in workstation for further disassembly
                            group_done = False
                            yield self.workstation.put(c)

                            # LOG: COMPONENT ENTERS STATION (Modeled as re-entering of reamining parts)
                            # Determine parent ID based on the product object type
                            if type(product).__name__ == "product":
                                # parent_id = f"prod_{product.ID:03d}"
                                parent_id = product.ID
                            elif type(product).__name__ == "group":
                                # For groups, ID is like "1_productname-groupname1"
                                # Cannot use :03d for formatting
                                if "_" in str(product.ID):
                                    parts = str(product.ID).split("_", 1)
                                    if parts[0].isdigit():
                                        # Reformat with leading zeros
                                        parent_id = (
                                            f"group_{int(parts[0]):03d}_{parts[1]}"
                                        )
                                    else:
                                        # If format is unexpected, use as is
                                        parent_id = f"group_{product.ID}"
                                else:
                                    # No underscore, try to format as number
                                    parent_id = f"group_{product.ID}"
                            else:
                                # Fallback
                                parent_id = f"obj_{product.ID}"

                            SimulationConfig.eventlog = (
                                helper_functions.add_to_eventlog_v3(
                                    case_id=c.caseID,
                                    object_id=c.ID,
                                    object_type=type(c).__name__,
                                    activity="object",
                                    activity_state="created",
                                    resource_id=self.name,
                                    resource_location="workstation",
                                    timestamp=self.env.now,
                                    related_objects=f"{parent_id}:parent",
                                )
                            )

                            break
                    # if group cant be disassembled further at this station,
                    # check if it has components whose disassembly has not yet been attempted
                    if group_done:
                        for key, element in comp_properties["structure"].items():
                            if key in product.components_to_scan and key != c.type:
                                group_done = False
                        # if not all components have been checked, put group in outbuf_to_next
                        if not group_done:
                            # put c in outbuf_to_next for further disassembly downstream
                            # LOG: HANDLING DONE (Component leaves station)
                            SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                                case_id=c.caseID,
                                object_id=c.ID,
                                object_type=type(c).__name__,
                                activity="handling",
                                activity_state="done",
                                resource_id=self.name,
                                resource_location="workstation",
                                timestamp=self.env.now,
                                related_objects=None,  # Just leaving - not tracking needed
                            )

                            yield self.env.timeout(self.handling_time)
                            yield self.outbuf_to_next.put(c)

                            # LOG: COMPONENT ENTERS OUTGOING BUFFER
                            SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                                case_id=c.caseID,
                                object_id=c.ID,
                                object_type=type(c).__name__,
                                activity="buffer",
                                activity_state="enter",
                                resource_id=self.name,
                                resource_location="outbuf_to_next",
                                timestamp=self.env.now,
                                related_objects=None,  # Just moving to buffer, no parent tracking needed
                            )

                            # order outbuf_to_next to pick up component if end of line
                            if self in self.simulation.ends_of_line:
                                self.env.process(
                                    functions.ordering(
                                        self.simulation.outgoing_storage,
                                        self.simulation,
                                        "outbuf_to_next",
                                    )
                                )

                            # clear c from workstation to make sure it only exists once
                            if c in self.workstation.items:
                                yield self.workstation.get(lambda x: x == c)

                        # All components have been checked, put group in outbuf_to_store
                        else:
                            SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                                case_id=c.caseID,
                                object_id=c.ID,
                                object_type=type(c).__name__,
                                activity="handling",
                                activity_state="end",
                                resource_id=self.name,
                                resource_location="workstation",
                                timestamp=self.env.now,
                                related_objects=None,  # Just leaving - not tracking needed
                            )

                            yield self.env.timeout(self.handling_time)
                            yield self.outbuf_to_store.put(c)

                            # LOG: COMPONENTS ENTERS OUTGOING BUFFER
                            SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                                case_id=c.caseID,
                                object_id=c.ID,
                                object_type=type(c).__name__,
                                activity="buffer",
                                activity_state="enter",
                                resource_id=self.name,
                                resource_location="outbuf_to_store",
                                timestamp=self.env.now,
                                related_objects=None,  # Just moving to buffer, no parent tracking needed
                            )

                            # order outgoing_storage to pick up component
                            self.env.process(
                                functions.ordering(
                                    self.simulation.outgoing_storage,
                                    self.simulation,
                                    "outbuf_to_store",
                                )
                            )

                            # clear c from workstation to make sure it only exists once
                            if c in self.workstation.items:
                                yield self.workstation.get(lambda x: x == c)

                # component without structure
                else:
                    # LOG: NEW COMPONENT CREATED FROM DISASSEMBLY PROCESS
                    if type(product).__name__ == "product":
                        # parent_id = f"prod_{product.ID:03d}"
                        parent_id = product.ID
                    elif type(product).__name__ == "group":
                        # For groups, ID is like "1_productname-groupname1"
                        # Cannot use :03d for formatting
                        if "_" in str(product.ID):
                            parts = str(product.ID).split("_", 1)
                            if parts[0].isdigit():
                                # Reformat with leading zeros
                                parent_id = f"group_{int(parts[0]):03d}_{parts[1]}"
                            else:
                                # If format is unexpected, use as is
                                parent_id = f"group_{product.ID}"
                        else:
                            # No underscore, try to format as number
                            parent_id = f"group_{product.ID}"
                    else:
                        # Fallback
                        parent_id = f"obj_{product.ID}"

                    SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                        case_id=c.caseID,
                        object_id=c.ID,
                        object_type=type(c).__name__,
                        activity="object",
                        activity_state="created",
                        resource_id=self.name,
                        resource_location="workstation",
                        timestamp=self.env.now,
                        related_objects=f"{parent_id}:parent",
                    )

                    # put component in outbuf_to_store
                    yield self.env.timeout(self.handling_time)
                    yield self.outbuf_to_store.put(c)

                    SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                        case_id=c.caseID,
                        object_id=c.ID,
                        object_type=type(c).__name__,
                        activity="buffer",
                        activity_state="enter",
                        resource_id=self.name,
                        resource_location="outbuf_to_store",
                        timestamp=self.env.now,
                        related_objects=None,  # Just moving to buffer, no parent tracking needed
                    )

                    # order outgoing_storage to pick up component
                    self.env.process(
                        functions.ordering(
                            self.simulation.outgoing_storage,
                            self.simulation,
                            "outbuf_to_store",
                        )
                    )

                # increase disassembled_quantity for logging
                disassembled_quantity += 1

                # Return to BUSY state after storing component
                self.state.enter_state(
                    StationState.BUSY, f"Finished processing {comp_key}"
                )

            # component not disassembled due to condition being too low
            else:
                # LOG: COMPONENT WAS SKIPPED (Due to low quality)
                SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                    case_id=product.caseID,
                    object_id=product.ID,
                    object_type=type(product).__name__,
                    activity="inspection",
                    activity_state="skipped",
                    resource_id=self.name,
                    resource_location="workstation",
                    timestamp=self.env.now,
                    related_objects=f"comp_{product.caseID:03d}_{comp_key}:skipped",
                )

                # Remove the component itself from components_to_scan
                # to prevent infinite loops
                if comp_key in product.components_to_scan:
                    product.components_to_scan.remove(comp_key)
                    helper_functions.debug_print(
                        f"  Removed {comp_key} from components_to_scan due to low condition"
                    )

                # get components blocked by this component
                blocked_components = helper_functions.get_components_blocked_by(
                    product.content["structure"], comp_key
                )

                # remove blocked components from components_to_scan and steps_todo of product
                # so they are not attempted again since they will be blocked by this component again
                for blocked_component in blocked_components:
                    if blocked_component in product.components_to_scan:
                        product.components_to_scan.remove(blocked_component)
                    if blocked_component in self.steps_todo:
                        self.steps_todo.remove(blocked_component)

        # increase level_of_disassembly of product by share of component in product structure
        if "structure" in comp_properties:
            product.level_of_disassembly += (
                helper_functions.count_parts(comp_properties["structure"])
                * (disassembled_quantity / comp_properties["quantity"])
                / product.parts_count
            )
        else:
            product.level_of_disassembly += (1 / product.parts_count) * (
                disassembled_quantity / comp_properties["quantity"]
            )

        # remove disassembled component from product structure only if it was fully disassembled
        if disassembled_quantity == comp_properties["quantity"]:
            # remove disassembled element from product
            del product.content["structure"][comp_key]
        else:
            # reduce quantity of disassembled element
            product.content["structure"][comp_key]["quantity"] -= disassembled_quantity

        # remove step from components_to_scan of product (to determine which components havent been checked yet)
        if comp_key in product.components_to_scan:
            product.components_to_scan.remove(comp_key)

        # Update derived times for backward compatibility logging
        # self.update_derived_times()

    def export_time_logs(self, filename=None):
        """Export time tracking logs to a file for analysis.

        This method exports both the legacy time tracking logs and the new state machine logs.

        Args:
            filename: Optional custom filename, defaults to station name
        """
        from src.g import SimulationConfig

        if filename is None:
            # Get experiment ID if available
            experiment_id = getattr(SimulationConfig, "experiment_id", None)

            # Use existing timestamp from config
            timestamp = SimulationConfig.run_timestamp

            filename = SimulationConfig.generate_filename(
                f"{self.name}_time_tracking", experiment_id, None, timestamp
            )

        # log_path = os.path.join(SimulationConfig.current_debug_logs_path, filename)
        log_path = os.path.join(SimulationConfig.debug_logs_path, filename)

        try:
            with open(log_path, "w") as f:
                f.write(f"Time tracking log for {self.name}\n")
                f.write("=" * 50 + "\n")
                for entry in self.debug_time_log:
                    f.write(f"{entry}\n")
            print(f"Time tracking log exported to {filename}")
        except Exception as e:
            print(f"Error exporting time log: {e}")

        # Also export state machine logs
        self.state.export_logs()

    def check_time_consistency(self):
        """Check if time tracking is consistent using only the state machine."""
        from src.g import SimulationConfig

        #  Skip check if tracking is disabled
        if not SimulationConfig.station_state_tracking:
            return True

        # Get current simulation time
        total_time = self.env.now

        # Get all tracked time components from state machine
        time_metrics = self.get_time_metrics()

        # Calculate total tracked time
        # tracked_time = busy_time + blocked_time + failure_time + closed_time + idle_time
        tracked_time = sum(time_metrics.values())

        # Perform consistency check
        print(f"\nTime consistency check for {self.name} at {self.env.now:.2f}:")
        for state, time in time_metrics.items():
            print(f"  {state.capitalize()} time: {time:.2f}")
            print(f"  Total tracked time: {tracked_time:.2f}")
            print(f"  Simulation time: {total_time:.2f}")
            print(f"  Difference: {tracked_time - total_time:.2f}")

        # Check for inconsistency - tracked time should match total time
        tolerance = 0.1  # Add small tolerance for floating point errors
        if abs(tracked_time - total_time) > tolerance:
            print(
                f"WARNING: Tracked time differs from simulation time by {tracked_time - total_time:.2f}"
            )
            return False

        return True

    def get_time_metrics(self):
        """Get all time metrics from state machine."""
        return {
            "busy": self.state.get_state_time(StationState.BUSY),
            "blocked": self.state.get_state_time(StationState.BLOCKED),
            "failed": self.state.get_state_time(StationState.FAILED),
            "closed": self.state.get_state_time(StationState.CLOSED),
            "idle": self.state.get_state_time(StationState.IDLE),
        }

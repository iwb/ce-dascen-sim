"""
File: storage.py
Location: /src/storage.py
Description: Storage units for material flow and buffering
Author: Patrick Jordan
Version: 2025-10

Implements storage units in the disassembly system:
- Incoming storage (system entry point)
- Intermediate storages (between stations)
- Outgoing storage (system exit point)

Each storage has:
- Entry buffer for incoming items
- Main storage area for inventory
- Two output buffers (to next station and to final storage)

Handles material flow, ordering from predecessors, and proper event logging.
"""

from contextlib import ExitStack

import simpy

import functions
import helper_functions
from src.g import *
from src.product import *


class Storage:
    """A class representing a storage unit in the simulation.
    This storage unit can receive, hold and deliver items based on specified conditions.
    It can be differentiated between the incoming storage (start of system), the outgoing storage (end of system)
    and a variable number of intermediate storages.
    All these types consist of an entry, a main storage area and one exit each towards the outgoing storage and downstream.
    Depending on the type of storage, processes for moving items between these areas are started.
    Also depending on the type of storage, processes for ordering new items from predecessors are started.

    Attributes:
        env (simpy.Environment): SimPy environment in which the storage unit operates.
        simulation (object): Instance of the simulation in which the storage is part of.
        name (str): The name of the storage unit.
        entry_capacity (int): The maximum number of items that can be held in the entry.
        storage_capacity (int): The maximum number of items that can be held in the storage.
        exit_capacity (int): The maximum number of items that can be held in the exits.
        entry (simpy.FilterStore): Filter store representing the entry point of the storage unit.
        station_storage (simpy.FilterStore): Filter store representing the main storage area.
        outbuf_to_next (simpy.FilterStore): Filter store representing the disassembly exit of the storage unit.
        outbuf_to_store (simpy.FilterStore): Filter store representing the outgoing exit of the storage unit.
        predecessors (list): List of predecessor storage units from which items can be ordered.
        handling_time (float): Time required to handle an item.
        order_threshold (int): The threshold for ordering new items.
        orders_open (int): The number of orders currently open.

    Methods:
        __init__(self, env, simulation, name, entry_capacity, storage_capacity, exit_capacity, predecessors, handling_time, entry_order_threshold): Initializes a new instance of the Storage class.
        put_into_storage(self): (intermediate storages) Continuously moves items from the entry to the main storage area.
        get_from_storage(self): (intermediate storages) Continuously moves items from the main storage area to the disassembly exit.
        put_into_outgoing_storage(self): (outgoing_storage) Continuously moves items from the entry to the main storage area of outgoing storage and logs them in log_output.

    """

    def __init__(
        self: object,
        env: simpy.Environment,
        simulation: object,
        name: str,
        entry_capacity: int,
        entry_order_threshold: int,
        storage_capacity: int,
        exit_capacity: int,
        predecessors: list,
        handling_time: float,
        variant_routing: dict = None,
    ) -> None:
        self.env = env
        self.simulation = simulation
        self.name = name
        self.entry_capacity = entry_capacity
        self.storage_capacity = storage_capacity
        self.exit_capacity = exit_capacity
        self.entry = simpy.FilterStore(env, self.entry_capacity)
        self.station_storage = simpy.FilterStore(env, self.storage_capacity)
        # DEBUG
        if self.name == "b-01_buffer_01":
            helper_functions.debug_print(f"b-01 initialized with storage_capacity={self.storage_capacity}")

        self.outbuf_to_next = simpy.FilterStore(env, self.exit_capacity)
        self.outbuf_to_store = simpy.FilterStore(env, self.exit_capacity)
        self.predecessors = predecessors
        # NEW: Load variant routing configuration
        self.variant_routing = variant_routing if variant_routing else {}
        self.handling_time = handling_time
        self.order_threshold = entry_order_threshold
        self.open_orders = 0

        # Debug: Check material flow mode
        helper_functions.debug_print(
            f"Initializing {name} - Material flow mode: {getattr(SimulationConfig, 'material_flow_mode', 'not set')}"
        )

        # Start working processes based on storage type
        if self.name == "incoming_storage":
            # Special process for incoming storage
            self.incoming_process = env.process(self.incoming_storage_process())

            # Debug: Check flow mode
            flow_mode = getattr(SimulationConfig, "material_flow_mode", "pull")
            helper_functions.debug_print(
                f"Incoming storage - flow_mode = '{flow_mode}', checking if equals 'push': {flow_mode == 'push'}"
            )

            # In push mode, start ordering process to push items downstream
            if getattr(SimulationConfig, "material_flow_mode", "pull") == "push":
                helper_functions.debug_print("Starting push ordering for incoming_storage...")
                import functions

                # Start push process for outbuf_to_next
                self.ordering_process = env.process(
                    functions.ordering(self, simulation, "outbuf_to_next")
                )
                helper_functions.debug_print("Push ordering process started for incoming_storage")
        elif self.name == "outgoing_storage":
            # Special process for outgoing storage
            self.put_into_storage_process = env.process(
                self.put_into_outgoing_storage()
            )
        else:
            # Normal intermediate storage processes
            if getattr(SimulationConfig, "material_flow_mode", "pull") == "push":
                # PUSH MODE: Direct flow + push ordering
                self.push_flow_process = env.process(self.push_flow_direct())

                import functions

                # Start push process for outbuf_to_next
                self.ordering_process_next = env.process(
                    functions.ordering(self, simulation, "outbuf_to_next")
                )
                # Start push process for outbuf_to_store
                self.ordering_process_store = env.process(
                    functions.ordering(self, simulation, "outbuf_to_store")
                )
                helper_functions.debug_print(
                    f"Started push ordering processes for {self.name}"
                )
                helper_functions.debug_print(f"PUSH MODE: Started ordering processes for {self.name}")
            else:
                # PULL MODE: Normal buffered flow
                self.put_into_storage_process = env.process(self.put_into_storage())
                self.get_from_storage_process = env.process(self.get_from_storage())

                # NEW: Add ordering process for intermediate storages
                import functions

                self.entry_ordering_process = env.process(
                    functions.ordering(self, simulation, "outbuf_to_next")
                )
                helper_functions.debug_print(f"Started entry ordering process for storage {self.name}")

    def _delayed_ordering_start(self):
        """Start ordering after a small delay to let initial products flow."""
        # DEBUG: Uncomment to trace storage ordering timing
        # print(f"DEBUG {self.name}: Waiting 30 minutes before starting ordering...")
        yield self.env.timeout(30)

        # DEBUG: Uncomment to trace storage ordering start time
        # print(
        #     f"DEBUG {self.name}: Delay complete, starting ordering at time {self.env.now}"
        # )
        import functions

        self.entry_ordering_process = self.env.process(
            functions.ordering(self, self.simulation, "outbuf_to_next")
        )
        helper_functions.debug_print(
            f"Started delayed ordering process for {self.name} at time {self.env.now}"
        )

    def push_flow_direct(self):
        """In push mode, move items directly from entry to outbuf_to_next"""
        helper_functions.debug_print(f"PUSH FLOW DIRECT: Started for {self.name}")
        while True:
            # Get item from entry
            helper_functions.debug_print(f"PUSH FLOW: {self.name} waiting for item in entry...")
            item = yield self.entry.get()
            helper_functions.debug_print(f"PUSH FLOW: {self.name} got item {item.ID}")

            # LOG: Item leaves entry buffer
            SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                case_id=item.caseID,
                object_id=item.ID,
                object_type=type(item).__name__,
                activity="buffer",
                activity_state="exit",
                resource_id=self.name,
                resource_location="inbuf",
                timestamp=self.env.now,
                related_objects=None,
            )

            # Minimal handling time
            yield self.env.timeout(self.handling_time)

            # Advance routing plan to next station if item has routing
            if hasattr(item, "advance_route"):
                item.advance_route()

            # Put directly in outbuf_to_next (skip station_storage)
            yield self.outbuf_to_next.put(item)
            helper_functions.debug_print(f"PUSH FLOW: {self.name} put item {item.ID} in outbuf_to_next")

            # LOG: Item enters output buffer
            SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                case_id=item.caseID,
                object_id=item.ID,
                object_type=type(item).__name__,
                activity="buffer",
                activity_state="enter",
                resource_id=self.name,
                resource_location="outbuf_to_next",
                timestamp=self.env.now,
                related_objects=None,
            )

    def put_into_storage(self: object) -> None:
        """This method represents a continuous process of moving items from the
        storage's entry to its main storage area.

        Args:
            self (Storage): An instance of the Storage class.

        Yields:
            entry.get(): getting an item from the entry.
            env.timeout: waiting due to handling an item.
            station_storage.put: putting an item into the storage's main area.
        """
        while True:
            #  DEBUG for b-01
            if self.name == "b-01_buffer_01":
                helper_functions.debug_print(
                    f"b-01 put_into_storage: Waiting for items in entry, "
                    f"entry has {len(self.entry.items)} items"
                )

            # Get item from entry
            item = yield self.entry.get()

            # DEBUG
            if self.name == "b-01_buffer_01":
                helper_functions.debug_print(
                    f"b-01: Got {item.ID} from entry, moving to station_storage"
                )

            # LOG: ITEM LEAVES INCOMING BUFFER OF STORAGE (-> gets stored)
            SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                case_id=item.caseID,
                object_id=item.ID,
                object_type=type(item).__name__,
                activity="buffer",
                activity_state="exit",
                resource_id=self.name,
                resource_location="inbuf",
                timestamp=self.env.now,
                related_objects=None,
            )

            yield self.env.timeout(self.handling_time)
            # Add debug and exception handling
            if self.name == "b-01_buffer_01":
                helper_functions.debug_print(
                    f"b-01: About to put {item.ID} in station_storage, "
                    f"capacity={self.station_storage.capacity}, "
                    f"items={len(self.station_storage.items)}"
                )

            try:
                yield self.station_storage.put(item)

                if self.name == "b-01_buffer_01":
                    helper_functions.debug_print(
                        f"b-01: Successfully put {item.ID} in station_storage"
                    )
            except Exception as e:
                helper_functions.debug_print(
                    f"ERROR in b-01 put_into_storage: {e} for item {item.ID}"
                )
                raise

            # LOG: COMPONENT STORED IN MAIN AREA OF STORAGE
            SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                case_id=item.caseID,
                object_id=item.ID,
                object_type=type(item).__name__,
                activity="storage",
                activity_state="enter",  # Item is now in storage
                resource_id=self.name,
                resource_location="inventory",
                timestamp=self.env.now,
                related_objects=None,
            )

    def get_from_storage(self: object) -> None:
        """This method represents a continuous process of moving items from the
        main storage area to its outbuf_to_next.

        In push mode: actively checks for items and pushes them
        In pull mode: waits for items as before
        """
        # DEBUG
        if self.name == "b-01_buffer_01":
            helper_functions.debug_print(
                f"b-01 get_from_storage process started at {self.env.now}"
            )

        while True:
            # In push mode, actively check for items
            if getattr(SimulationConfig, "material_flow_mode", "pull") == "push":
                # Check if there are items to push
                if (
                    len(self.station_storage.items) > 0
                    and len(self.outbuf_to_next.items) < self.exit_capacity
                ):
                    item = yield self.station_storage.get()

                    # LOG: COMPONENT PULLED FROM INVENTORY
                    SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                        case_id=item.caseID,
                        object_id=item.ID,
                        object_type=type(item).__name__,
                        activity="storage",
                        activity_state="exit",
                        resource_id=self.name,
                        resource_location="inventory",
                        timestamp=self.env.now,
                        related_objects=None,
                    )

                    yield self.env.timeout(self.handling_time)

                    # Advance routing plan to next station if item has routing
                    if hasattr(item, "advance_route"):
                        item.advance_route()

                    yield self.outbuf_to_next.put(item)

                    # COMPONENT PLACED IN BUFFER (for further disassembly)
                    SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                        case_id=item.caseID,
                        object_id=item.ID,
                        object_type=type(item).__name__,
                        activity="buffer",
                        activity_state="enter",
                        resource_id=self.name,
                        resource_location="outbuf_to_next",
                        timestamp=self.env.now,
                        related_objects=None,
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
                else:
                    # No items to push or output buffer full, wait a bit
                    yield self.env.timeout(SimulationConfig.push_check_frequency)
            else:
                # Pull mode - original behavior

                # DEBUG before get
                if self.name == "b-01_buffer_01":
                    helper_functions.debug_print(
                        f"b-01 get_from_storage: About to get from storage at {self.env.now}, "
                        f"storage has {len(self.station_storage.items)} items, "
                        f"outbuf has {len(self.outbuf_to_next.items)}/{self.exit_capacity}"
                    )

                item = yield self.station_storage.get()

                # DEBUG after get
                if self.name == "b-01_buffer_01":
                    helper_functions.debug_print(
                        f"b-01 get_from_storage: Got {item.ID}, moving to outbuf_to_next"
                    )

                # LOG: COMPONENT PULLED FROM INVENTORY
                SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                    case_id=item.caseID,
                    object_id=item.ID,
                    object_type=type(item).__name__,
                    activity="storage",
                    activity_state="exit",
                    resource_id=self.name,
                    resource_location="inventory",
                    timestamp=self.env.now,
                    related_objects=None,
                )

                yield self.env.timeout(self.handling_time)

                # Advance routing plan to next station if item has routing
                if hasattr(item, "advance_route"):
                    item.advance_route()

                yield self.outbuf_to_next.put(item)

                # COMPONENT PLACED IN BUFFER (for further disassembly)
                SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                    case_id=item.caseID,
                    object_id=item.ID,
                    object_type=type(item).__name__,
                    activity="buffer",
                    activity_state="enter",
                    resource_id=self.name,
                    resource_location="outbuf_to_next",
                    timestamp=self.env.now,
                    related_objects=None,
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

    def incoming_storage_process(self):
        """Special process for incoming storage - goes directly from entry to output buffer."""
        # Log once at start
        helper_functions.debug_print(
            f"incoming_storage process started at {self.env.now}"
        )

        while True:
            # Get product from entry (where Source puts them)
            item = yield self.entry.get()

            # Only log first few items
            if self.env.now < 500:
                helper_functions.debug_print(
                    f"incoming_storage: Processing {item.ID} at {self.env.now}"
                )

            # Minimal handling time
            yield self.env.timeout(self.handling_time)

            # Put directly in output buffer (skip main storage)
            yield self.outbuf_to_next.put(item)

            # Log ready for dispatch to shop floor
            SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                case_id=item.caseID,
                object_id=item.ID,
                object_type=type(item).__name__,
                activity="storage",
                activity_state="enter",
                resource_id="incoming_storage",
                resource_location="outbuf_to_next",
                timestamp=self.env.now,
                related_objects=None,
            )

    def put_into_outgoing_storage(self):
        """Continuously moves items from the entry to the main storage area of outgoing storage.
        Is only used for outgoing_storage, since it resembles the end of the system.

        Includes logic to mark products as done when they exit the system (enables the calculation of the lead time)
        """
        while True:
            # get output_item from entry
            output_item = yield self.entry.get()

            # Debug log item exit
            helper_functions.debug_print(
                f"Item {output_item.ID} type={output_item.type} exiting system "
                f"through outgoing storage (condition={output_item.condition:.2f})"
            )

            # Determine object type for clear tracking
            object_category = type(output_item).__name__  # product, component, or group

            # Extract component information consistently
            component_name = output_item.type
            if hasattr(output_item, "type") and "_" in output_item.type:
                component_name = output_item.type.split("_")[-1]

            # LOG: ITEM LEAVES INCOMING BUFFER (-> Placed into outgoing storage)
            SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                case_id=output_item.caseID,
                object_id=output_item.ID,
                object_type=type(output_item).__name__,
                activity="buffer",
                activity_state="exit",
                resource_id=self.name,
                resource_location="inbuf",
                timestamp=self.env.now,
                related_objects=None,
            )

            # put output_item in self.station_storage
            yield self.env.timeout(self.handling_time)
            yield self.station_storage.put(output_item)

            # WORKAROUND: Mark products as done when they exit through outgoing storage
            # This handles cases where products have unprocessed components that no station can handle
            if object_category == "product":
                # Check if product is not already marked as done
                done_status = (
                    SimulationConfig.log_disassembly.loc[
                        SimulationConfig.log_disassembly["ID"] == output_item.ID, "done"
                    ].iloc[0]
                    if len(
                        SimulationConfig.log_disassembly[
                            SimulationConfig.log_disassembly["ID"] == output_item.ID
                        ]
                    )
                    > 0
                    else False
                )

                # ALWAYS calculate times when product exits (remove the if not done_status check)
                # Convert events to DataFrame
                if SimulationConfig.events_list:
                    eventlog_df = pd.DataFrame(SimulationConfig.events_list)
                else:
                    eventlog_df = SimulationConfig.eventlog

                # Use the simple calculation method
                time_components = helper_functions.calculate_time_components_simple(
                    output_item.caseID, eventlog_df, self.simulation
                )

                # Update the log
                helper_functions.update_log_disassembly_enhanced(
                    output_item,
                    time_components,
                    {"enhanced_time_tracking": {"enabled": True}},
                    self.simulation,
                )

                # Mark as done
                helper_functions.update_log_disassembly(
                    output_item, "done_time", self.env.now, "equate"
                )
                helper_functions.update_log_disassembly(
                    output_item, "done", True, "equate"
                )

            # LOG: COMPONENT LEAVES OUTGOING STORAGE / SYSTEM (= final destination in the system)
            SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
                case_id=output_item.caseID,
                object_id=output_item.ID,
                object_type=type(output_item).__name__,
                activity="system",
                activity_state="exit",
                resource_id=self.name,
                resource_location="shipping",
                timestamp=self.env.now,
                related_objects=None,
            )

            # add "_remains" to output_item.type since it is the remains of a product
            if object_category == "product":
                output_item.type = output_item.type + "_remains"

            # log in output_table
            if object_category == "component":
                content = output_item.type
            else:
                content = str(
                    helper_functions.list_components(output_item.content["structure"])
                )

            # Create new row with all required columns
            new_row = pd.DataFrame(
                [
                    {
                        "caseID": output_item.caseID,
                        "objectID": output_item.ID,
                        "object_type": object_category,
                        "object_name": output_item.type,
                        "delivery_time": datetime.fromtimestamp(
                            output_item.delivery_time * 60
                            + SimulationConfig.start_date.timestamp()
                        ).strftime("%Y-%m-%dT%H:%M:%S"),
                        "output_time": datetime.fromtimestamp(
                            self.env.now * 60 + SimulationConfig.start_date.timestamp()
                        ).strftime("%Y-%m-%dT%H:%M:%S"),
                        "condition": round(output_item.condition, 2),
                        "content": content,
                    }
                ]
            )

            # Add to global log
            SimulationConfig.output_table = pd.concat(
                [SimulationConfig.output_table, new_row], ignore_index=True
            )

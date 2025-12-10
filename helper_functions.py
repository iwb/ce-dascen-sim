"""
File: helper_functions.py
Location: Project root
Description: Helper functions for simulation operations
Author: Patrick Jordan
Version: 2025-10

Contains utility functions for:
- Product structure analysis (counting parts, finding parents)
- Component blocking relationships
- Time calculations and conversions
- Event logging (OCEL 2.0 format)
- Data table management
- Visualization support
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Union

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from src.g import SimulationConfig, SimulationBehavior

# Global debug file handle
_debug_file = None
# Global object registry
_object_registry = {}


def init_debug_log():
    """Initialize debug log file for this simulation run."""
    global _debug_file
    from src.g import SimulationConfig

    # Only create if debug logging is enabled
    if not SimulationConfig.create_debug_log:
        return

    # Create debug subdirectory within the experiment output
    debug_output_path = os.path.join(SimulationConfig.output_path, "debug")
    os.makedirs(debug_output_path, exist_ok=True)

    # Create debug log filename
    experiment_id = getattr(SimulationConfig, "experiment_id", None)
    timestamp = SimulationConfig.run_timestamp

    # Create debug log filename
    debug_filename = SimulationConfig.generate_filename(
        "debug_log",
        experiment_id,
        None,
        timestamp,
        category="debug",
    )
    debug_path = os.path.join(debug_output_path, debug_filename)

    # Open file for writing
    _debug_file = open(debug_path, "w")
    _debug_file.write(f"Debug Log Started: {datetime.now()}\n")
    _debug_file.write(f"Experiment: {experiment_id}\n")
    _debug_file.write("=" * 80 + "\n\n")
    print(f"Debug log initialized: {debug_path}")


def debug_print(message):
    """Write debug message to file if debug logging is enabled."""
    from src.g import SimulationConfig

    # Check if debug logging is enabled
    if not SimulationConfig.create_debug_log:
        return

    global _debug_file
    if _debug_file:
        # Add simulation time if available
        try:
            if hasattr(SimulationConfig, "env") and SimulationConfig.env:
                sim_time = SimulationConfig.env.now
                _debug_file.write(f"[{sim_time:8.2f}] {message}\n")
            else:
                _debug_file.write(f"{message}\n")
        except Exception as e:
            # Log the error but continue writing the message
            _debug_file.write(f"[ERROR getting sim_time: {e}] {message}\n")
        _debug_file.flush()  # Ensure immediate write


def close_debug_log():
    """Close debug log file."""
    global _debug_file
    if _debug_file:
        _debug_file.write("\n" + "=" * 80 + "\n")
        _debug_file.write(f"Debug Log Ended: {datetime.now()}\n")
        _debug_file.close()
        _debug_file = None


def visualize_structure(structure_path: str, all_predecessors: list):
    """Visualizes the structure  of the factory (stations, storages and their connections) as a networkx graph,
    shows connection to outgoing_storage only for end of line stations for better readability.
    not ideal for large structures, can potentially be improved! good for testing if structure is correct.

    Args:
        structure_path (str): path to the json file containing the structure of the factory
        all_predecessors (list): list of all stations and storages that are the predecessor of another station or storage (therefore not end of line),
        not including incoming_storage because it is added every time and not explicitly stated in the json file
    """

    # Load the JSON file
    with open(structure_path, "r") as file:
        data = json.load(file)

    # Create a new directed graph
    G = nx.DiGraph()

    # Add nodes for incoming and outgoing storage because they are not explicitly stated in the json file
    G.add_node("incoming_storage")
    G.add_node("outgoing_storage")

    # Add nodes for all stations in the json file
    for station in data["factory"]["stations"].keys():
        G.add_node(station)

    # Add nodes for all storages in the json file
    for storage in data["factory"]["storages"].keys():
        G.add_node(storage)

    # Add edges for each predecessor of stations
    for station, details in data["factory"]["stations"].items():
        for predecessor in details.get("predecessors", []):
            G.add_edge(predecessor, station)

    # Add edges for each predecessor of storages
    for storage, details in data["factory"]["storages"].items():
        for predecessor in details.get("predecessors", []):
            G.add_edge(predecessor, storage)

    # Collect names of all predecessors from all_predecessors
    predecessor_names = [predecessor.name for predecessor in all_predecessors]

    # add edges to outgoing_storage for end of line stations
    for node in G.nodes():
        if node != "outgoing_storage" and node != "incoming_storage":
            if node not in predecessor_names:
                G.add_edge(node, "outgoing_storage")

    # Create the layout for the graph using spring layout
    pos = nx.spring_layout(G)

    # Draw the graph
    nx.draw(G, pos, with_labels=True, arrows=True)
    plt.show()


def is_working_hours(simulation: object) -> Tuple[bool, float, float]:
    """checks if the current time in a simulation is within the working hours of the factory,
    additionally returns the current hour and day of the simulation to calculate time until next opening/closing

    Args:
        simulation (main.simulation): instance of the simulation class, running with minute as time unit

    Returns:
        Tuple[bool, float, float]: tuple containing a boolean indicating if the current time is within the working hours,
        the current hour of the simulation and the current day of the simulation
    """

    # 1440 minutes a day, 60 minutes per hours
    current_day = simulation.env.now // 1440
    current_hour = (simulation.env.now % 1440) / 60
    return (
        simulation.start_of_day <= current_hour < simulation.end_of_day,
        current_hour,
        current_day,
    )


def get_driving_time(
    start_location: str,
    end_location: str,
    speed: float,
    distance_matrix: pd.DataFrame,
) -> float:
    """calculates the driving time between two locations based on the distance matrix and the speed of the vehicle

    Args:
        start_location (str): name of the start location as stated in the distance matrix
        end_location (str): name of the end location as stated in the distance matrix
        speed (float): speed of the vehicle in distance units per time unit (as stated in the distance matrix and the simulation)
        distance_matrix (pd.DataFrame): matrix containing the distances between all locations

    Returns:
        float: driving time between the two locations in time units
    """
    # get the distance between the two locations
    distance = distance_matrix.loc[start_location, end_location]
    driving_time = distance / speed  # calculate the driving time
    return driving_time


# Replace count_parts in helper_functions.py temporarily with this debug version:


def count_parts(component_group: Dict[str, Dict]) -> int:
    """counts the number of components and groups in a product structure or group structure,
    does not count the group itself,
    result is equal to the maximum number of disassembly steps that can be performed in the structure,
    recursively calls itself for each subgroup in the structure

    Args:
        component_group (Dict[str, Dict]): structure of a product or group as stated in the json file,
        consisting of names and properties of contained components and groups

    Returns:
        int: number of components and groups in the structure"""

    components_list = []
    groups_list = []
    # Loop through all components and groups in the structure and check if they have a substructure
    for (
        key,
        value,
    ) in component_group.items():
        try:
            value["structure"]
        # If there is no "structure" key, we know it's a component and add it to the components_list
        except KeyError:
            components_list.append({key: value})
        # If there is a "structure" key, we know it's a group and add it to the groups_list
        else:
            groups_list.append({key: value})

    # count all components in this level of the structure
    count = len(components_list)

    for sub_group in groups_list:
        for _, value in sub_group.items():
            # recursive call for all subgroups in this level of the structure
            count += count_parts(value["structure"])
            # add 1 for the group itself
            count += 1

    return count


def find_parent_in_structure(
    structure: Dict[str, Dict], target: str, parent: str = None
) -> str:
    """Determines the parent group of a target in a structure.

    This function searches through a hierarchical structure to find which group
    contains the target component or group.

    Args:
        structure (Dict[str, Dict]): structure of a product or group as stated in the json file
        target (str): name of the component or group to find the parent for
        parent (str, optional): current parent being examined. Defaults to None.

    Returns:
        str: name of the parent of the target, or None if target has no parent
    """
    # Loop through all components and groups in this level of the structure
    for key, component in structure.items():
        # If the target is found, return the current group as its parent
        if key == target:
            return parent

        # If the current component has a substructure, recursively search it
        if "structure" in component:
            found_parent = find_parent_in_structure(
                component["structure"], target, parent=key
            )
            # If the target was found in the substructure, return the parent
            if found_parent:
                return found_parent

    return None


def get_highest_parent(structure: Dict[str, Dict], target: str) -> str:
    """Determines the highest parent group of a component or group in a structure.

    This function finds the top-level group that contains the target, which is
    used to determine which groups and components have to be disassembled
    because they contain the target.

    Args:
        structure (Dict[str, Dict]): structure of a product or group as stated in the json file
        target (str): name of the component or group to find the highest parent group for

    Returns:
        str: name of the highest parent group of the target
    """
    # Find the immediate parent of the target within the structure
    highest_parent = find_parent_in_structure(structure, target)

    # Find the parent of the previously identified highest parent
    parent = find_parent_in_structure(structure, highest_parent)

    # Continue searching upward until we find the highest parent
    while parent:
        # The current parent becomes the new highest parent
        highest_parent = parent

        # Search for the parent of the new highest parent
        parent = find_parent_in_structure(structure, highest_parent)

    # Return the highest parent found
    return highest_parent


def update_inventory_log(name: str, amount: int, time: int):
    """updates the total inventory amount of a storage at a given time in the inventory log,
    inventory log is a pandas dataframe with the time as index and the storage inventory amounts as columns,
    can be used for debugging by plotting the inventory log as a time series

    Args:
        name (str): unique name of the storage
        amount (int): total amount of inventory in the storage
        time (int): current time of the simulation
    """
    if name in SimulationConfig.inventory_log.columns:
        SimulationConfig.inventory_log.loc[time, name] = amount


def add_to_inventory_log(name: str):
    """adds a new column to the inventory log for a new storage,
    inventory log is a pandas dataframe with the time as index and the total inventory amounts per storage as columns,

    Args:
        name (str): unique name of the storage
    """
    if name not in SimulationConfig.inventory_log.columns:
        SimulationConfig.inventory_log[name] = 0


def is_in_product(structure: Dict[str, Dict], target: str) -> bool:
    """checks if a target component or group is contained in a given structure,
    recursively calls itself for each subgroup in the structure

    Args:
        structure (Dict[str, Dict]): structure of a product or group as stated in the json file
        target (str): component or group to check if it is contained in the structure

    Returns:
        bool: True if the target is contained in the structure, False if not
    """

    # Loop through all components and groups in the product
    for key, component in structure.items():
        # If the target component is found at the current level of the structure
        if key == target:
            return True
        # If the current component has a substructure (is a subgroup)
        if "structure" in component:
            # Recursively search the substructure for the target component
            if is_in_product(component["structure"], target):
                return True

    # If the target component was not found in the product
    return False


# ==========================================
# BLOCKING COMPONENTS FUNCTIONS
# ==========================================
def find_blocking_components_recursive(
    structure: Dict[str, Dict], target: str
) -> List[str] | None:
    """Recursively searches a structure for a target and returns its blocking components.

    Args:
        structure (Dict[str, Dict]): structure to search
        target (str): component to find blocking components for

    Returns:
        Optional[List[str]]: list of component names that block the target, or None if not found
    """
    for key, component in structure.items():
        if key == target and "blocked_by" in component:
            return component["blocked_by"]
        if "structure" in component:
            blocking_components = find_blocking_components_recursive(
                component["structure"], target
            )
            if blocking_components is not None:
                return blocking_components
    return None


def get_blocking_components(structure: Dict[str, Dict], target: str) -> List[str]:
    """Identifies all components that block a target component in a given structure.

    Target doesn't have to be in highest level of structure, can be in a subgroup.

    Args:
        structure (Dict[str, Dict]): structure of a product or group as stated in the json file
        target (str): component or group to find the blocking components for

    Returns:
        List[str]: list of names of all components that block the target component
    """
    blocking_components = find_blocking_components_recursive(structure, target)
    return blocking_components if blocking_components is not None else []


# ==========================================
# COMPONENTS BLOCKED BY FUNCTIONS
# ==========================================
def find_components_blocked_by_recursive(
    structure: Dict[str, Dict], target: str, blocked_components: List[str]
) -> None:
    """Recursively identifies all components that are blocked by a target component.

    This function modifies the blocked_components list in place.

    Args:
        structure (Dict[str, Dict]): structure of a product or group
        target (str): component that might be blocking others
        blocked_components (List[str]): list to collect blocked component names
    """
    # Loop through all components and groups in the current level of the structure
    for key, component in structure.items():
        # If current element is blocked by target, add it to the list
        if "blocked_by" in component and target in component["blocked_by"]:
            blocked_components.append(key)
            # If current element has a substructure, add all components in it too
            if "structure" in component:
                blocked_components.extend(list_components(component["structure"]))
        # If current element is a group but not blocked by target, search its substructure
        elif "structure" in component:
            find_components_blocked_by_recursive(
                component["structure"], target, blocked_components
            )


def get_components_blocked_by(structure: Dict[str, Dict], target: str) -> List[str]:
    """Identifies all components that are blocked by a target component in a given structure.

    Target doesn't have to be in highest level of structure, can be in a subgroup.

    Args:
        structure (Dict[str, Dict]): structure of a product or group as stated in the json file
        target (str): component or group to find the blocked by components for

    Returns:
        List[str]: list of names of all components that are blocked by the target component
    """
    blocked_components = []
    find_components_blocked_by_recursive(structure, target, blocked_components)
    return blocked_components


def list_components(structure: Dict[str, Dict]) -> List[str]:
    """lists all components and groups in a given structure,
    recursively calls itself for each group in the structure

    Args:
        structure (Dict[str, Dict]): structure of a product or group as stated in the json file

    Returns:
        List[str]: list of names of all components and groups in the structure
    """
    components_list = []
    for key, value in structure.items():
        components_list.append(key)
        if "structure" in value:
            components_list.extend(list_components(value["structure"]))
    return components_list


# ==========================================
# MANDATORY COMPONENTS FUNCTIONS
# ==========================================
def find_mandatory_components_recursive(
    structure: Dict[str, Dict], mandatory_components: List[str]
) -> None:
    """Recursively identifies all mandatory components in a structure.

    This function modifies the mandatory_components list in place.

    Args:
        structure (Dict[str, Dict]): structure of a product or group
        mandatory_components (List[str]): list to collect mandatory component names
    """
    for key, component in structure.items():
        # Check if current component is mandatory
        if "mandatory" in component and component["mandatory"] == True:
            mandatory_components.append(key)
        # Check if current component has structure (is a group)
        if "structure" in component:
            find_mandatory_components_recursive(
                component["structure"], mandatory_components
            )


def get_mandatory_components(structure: Dict[str, Dict]) -> List[str]:
    """Identifies all mandatory components in a given structure.

    Recursively scans all substructures in the structure.

    Args:
        structure (Dict[str, Dict]): structure of a product or group as stated in the json file

    Returns:
        List[str]: list of names of all mandatory components in the structure
    """
    mandatory_components = []
    find_mandatory_components_recursive(structure, mandatory_components)
    return mandatory_components


def add_to_case_table(
    caseID: int,
    product_type: str,
    delivery_time: float,
    condition: float,
    target_components: Dict[str, int] = None,
    missing_components: List[str] = None,
) -> pd.DataFrame:
    """
    Add a new row to the case table DataFrame.

    Returns:
    pd.DataFrame: The updated DataFrame.
    """

    # Treat the timestamp as a delta in minutes
    delta = timedelta(minutes=delivery_time)

    # Add the delta to the start date and format as a string (ISO 8601)
    delivery_time = (SimulationConfig.start_date + delta).strftime("%Y-%m-%dT%H:%M:%S")

    # Convert to JSON strings for storage in DF
    target_components_str = json.dumps(target_components) if target_components else "{}"
    missing_components_str = (
        json.dumps(missing_components) if missing_components else "[]"
    )

    new_row = pd.DataFrame(
        data=[
            {
                "caseID": caseID,
                "product_type": product_type,
                "delivery_time": delivery_time,
                "condition": round(condition, 2),
                "target_components": target_components_str,
                "missing_components": missing_components_str,
            }
        ],
    )
    return pd.concat([SimulationConfig.case_table, new_row], ignore_index=True)


def add_to_output_table(
    caseID: int,
    objectID: int,
    object_type: str,
    object_name: str,
    delivery_time: float,
    output_time: float,
    condition: float,
    content: str,
) -> pd.DataFrame:
    """
    Add a new row to the output table DataFrame.

    Parameters:
    g (object): The global variables of the simulation.
    output_table (pd.DataFrame): The DataFrame to which the row should be added.
    caseID (int): The product ID to add.
    objectID (int): The object ID to add.
    object_type (str): The object type to add.
    object_name (str): The object name to add.
    delivery_time (float): The delivery time to add.
    condition (float): The condition to add.
    content (str): The content of the object to add.

    Returns:
    pd.DataFrame: The updated DataFrame.
    """

    # Treat the times as a delta in minutes
    delivery_time_delta = timedelta(minutes=delivery_time)
    output_time_delta = timedelta(minutes=output_time)

    # Add the delta to the start date and format as a string
    delivery_time = (SimulationConfig.start_date + delivery_time_delta).strftime(
        "%Y-%m-%dT%H:%M:%S"
    )
    output_time = (SimulationConfig.start_date + output_time_delta).strftime(
        "%Y-%m-%dT%H:%M:%S"
    )

    new_row = pd.DataFrame(
        data=[
            {
                "caseID": caseID,
                "objectID": objectID,
                "object_type": object_type,
                "object_name": object_name,
                "delivery_time": delivery_time,
                "output_time": output_time,
                "condition": round(condition, 2),
                "content": content,
            }
        ],
    )
    return pd.concat([SimulationConfig.output_table, new_row], ignore_index=True)


def remove_components(structure: dict):
    """
    Recursively removes components based on prob_missing.
    Returns list of removed component names.
    """
    removed_components = []

    # get all components in this component group
    components_list = []
    groups_list = []
    for key, value in structure.items():
        # check if current element has a "structure"
        try:
            value["structure"]
        # when there is no "structure", it is a component so add it to the components_list
        except KeyError:
            components_list.append({key: value})
        # when there is a "structure", it is a component group so add it to the groups_list
        else:
            groups_list.append({key: value})

    # Collect components to remove first (does not modify dict)
    components_to_remove = []

    # iterate through components_list and determine which to remove
    for component_dict in components_list:
        for component_name, component in component_dict.items():
            # Use appropriate behavior mode
            if SimulationConfig.behavior_mode == SimulationBehavior.DETERMINISTIC:
                # Deterministic version - remove if probability > 0.5
                if component["prob_missing"] > 0.5:
                    components_to_remove.append(component_name)
            else:
                # Random version - use random number generator (seeded)
                if SimulationConfig.rng_quality.random() < component["prob_missing"]:
                    components_to_remove.append(component_name)

    # Components are removed (tracked)
    for component_name in components_to_remove:
        structure.pop(component_name, None)
        removed_components.append(component_name)

    # Clean up blocked_by references to removed components
    for key, value in structure.items():
        if isinstance(value, dict) and "blocked_by" in value:
            # Remove any references to removed components
            value["blocked_by"] = [
                blocker
                for blocker in value["blocked_by"]
                if blocker not in components_to_remove
            ]

    # Subgroups: collect their removed components with prefix
    for group_dict in groups_list:
        for group_name, group in group_dict.items():
            sub_removed = remove_components(group["structure"])
            removed_components.extend([f"{group_name}_{comp}" for comp in sub_removed])

    return removed_components


def update_log_disassembly(product, column_name, value, typeofupdate):
    if typeofupdate == "add":
        SimulationConfig.log_disassembly.loc[
            (SimulationConfig.log_disassembly["ID"] == product.ID)
            & (SimulationConfig.log_disassembly["product_type"] == product.type),
            column_name,
        ] += value

    if typeofupdate == "equate":
        SimulationConfig.log_disassembly.loc[
            (SimulationConfig.log_disassembly["ID"] == product.ID)
            & (SimulationConfig.log_disassembly["product_type"] == product.type),
            column_name,
        ] = value


def assign_predecessors(self, instance, element):
    predecessors = []
    for predecessor in element["predecessors"]:
        # append all predecessors to storage_predecessors
        if predecessor == "incoming_storage":
            predecessors.append(self.incoming_storage)
        else:
            for s in self.stations:
                if s.name == predecessor:
                    predecessors.append(s)
            for l in self.storages:
                if l.name == predecessor:
                    predecessors.append(l)
    instance.predecessors = predecessors

    # add predecessors to all_predecessors if not already in it
    # (to determine which stations are end of line)
    for predecessor in predecessors:
        if predecessor not in self.all_predecessors:
            self.all_predecessors.append(predecessor)  # Modifies simulation's list


def calculate_time_components_simple(case_id, eventlog, simulation=None):
    """Calculate processing times - compatible with both old and new event log formats."""

    # Copy to avoid modifying the original
    eventlog = eventlog.copy()

    # Convert timestamp if needed
    if len(eventlog) > 0 and isinstance(eventlog["timestamp"].iloc[0], str):
        eventlog["timestamp"] = pd.to_datetime(eventlog["timestamp"], format="ISO8601")

    # Get all events for this case
    case_events = eventlog[eventlog["caseID"] == case_id].sort_values("timestamp")

    # Initialize result
    result = {"station_times": {}, "vehicle_times": {}, "handling_time": 0.0}

    # Initialize all stations with 0 if simulation provided
    if simulation:
        for station in simulation.stations:
            result["station_times"][station.name] = 0.0
        for vehicle in simulation.vehicles:
            result["vehicle_times"][vehicle.name] = 0.0

    # Check which format we're dealing with
    if "action" in eventlog.columns:
        # OLD FORMAT - use existing logic
        # Track processed events to avoid double counting
        processed_events = set()

        # Find all processing_start events
        start_events = case_events[case_events["action"] == "processing_start"]

        for idx, start_event in start_events.iterrows():
            # Skip if already processed
            if idx in processed_events:
                continue

            # Extract station name
            station = start_event["resource_id"].replace("_station", "")
            object_id = start_event["objectID"]
            component = start_event["component"]
            start_time = start_event["timestamp"]

            # Find the matching processing_complete
            complete_events = case_events[
                (case_events["action"] == "processing_complete")
                & (case_events["objectID"] == object_id)
                & (case_events["component"] == component)
                & (case_events["timestamp"] > start_time)
                & (case_events["resource_id"] == start_event["resource_id"])
            ]

            if len(complete_events) > 0:
                complete_event = complete_events.iloc[0]
                processing_time = (
                    complete_event["timestamp"] - start_time
                ).total_seconds() / 60

                # Add to station time
                if station not in result["station_times"]:
                    result["station_times"][station] = 0.0
                result["station_times"][station] += processing_time

                # Mark both events as processed
                processed_events.add(idx)
                # Get the index of the complete event
                for complete_idx in complete_events.index[:1]:
                    processed_events.add(complete_idx)

        # Calculate vehicle times (existing logic is fine)
        load_events = case_events[case_events["action"] == "load"]
        for idx, load_event in load_events.iterrows():
            vehicle = load_event["resource_id"]
            object_id = load_event["objectID"]

            unload_events = case_events[
                (case_events["action"] == "unload")
                & (case_events["objectID"] == object_id)
                & (case_events["resource_id"] == vehicle)
                & (case_events["timestamp"] > load_event["timestamp"])
            ]

            if len(unload_events) > 0:
                transport_time = (
                    unload_events.iloc[0]["timestamp"] - load_event["timestamp"]
                ).total_seconds() / 60
                if vehicle not in result["vehicle_times"]:
                    result["vehicle_times"][vehicle] = 0.0
                result["vehicle_times"][vehicle] += transport_time

    else:
        # NEW FORMAT - use activity and activity_state
        # Processing times (disassembly activities)
        disassembly_events = case_events[case_events["activity"] == "disassembly"]

        # Group by object_id to handle multiple components
        for obj_id in disassembly_events["object_id"].unique():
            obj_events = disassembly_events[disassembly_events["object_id"] == obj_id]
            starts = obj_events[obj_events["activity_state"] == "start"]
            completes = obj_events[obj_events["activity_state"] == "complete"]

            for idx, start in starts.iterrows():
                # Find matching complete
                matching_complete = completes[
                    (completes["resource_id"] == start["resource_id"])
                    & (completes["timestamp"] > start["timestamp"])
                ]

                if len(matching_complete) > 0:
                    complete = matching_complete.iloc[0]
                    time_diff = (
                        complete["timestamp"] - start["timestamp"]
                    ).total_seconds() / 60

                    station = start["resource_id"]
                    if station not in result["station_times"]:
                        result["station_times"][station] = 0
                    result["station_times"][station] += time_diff

        # Transport times
        transport_events = case_events[case_events["activity"] == "transport"]

        # Group by resource (vehicle)
        for vehicle in transport_events["resource_id"].unique():
            vehicle_events = transport_events[
                transport_events["resource_id"] == vehicle
            ]
            loads = vehicle_events[vehicle_events["activity_state"] == "load"]
            unloads = vehicle_events[vehicle_events["activity_state"] == "unload"]

            for idx, load in loads.iterrows():
                # Find matching unload
                matching_unload = unloads[
                    (unloads["object_id"] == load["object_id"])
                    & (unloads["timestamp"] > load["timestamp"])
                ]

                if len(matching_unload) > 0:
                    unload = matching_unload.iloc[0]
                    time_diff = (
                        unload["timestamp"] - load["timestamp"]
                    ).total_seconds() / 60

                    if vehicle not in result["vehicle_times"]:
                        result["vehicle_times"][vehicle] = 0
                    result["vehicle_times"][vehicle] += time_diff

    return result


def update_log_disassembly_enhanced(
    product, time_components, runtime_config, simulation=None
):
    """Update log_disassembly with time tracking."""

    # Find the product in log_disassembly
    mask = SimulationConfig.log_disassembly["ID"] == product.ID

    if mask.sum() == 0:
        # print(f"WARNING: Product {product.ID} not found in log_disassembly!")
        debug_print(f"WARNING: Product {product.ID} not found in log_disassembly!")
        return

    # Basic columns that should exist
    basic_columns = ["lead_time", "handling_time"]

    # Ensure basic columns exist as float
    for col in basic_columns:
        if col not in SimulationConfig.log_disassembly.columns:
            SimulationConfig.log_disassembly[col] = 0.0
        # Convert to float if not already
        SimulationConfig.log_disassembly[col] = pd.to_numeric(
            SimulationConfig.log_disassembly[col], errors="coerce"
        ).fillna(0.0)

    # Update handling time
    SimulationConfig.log_disassembly.loc[mask, "handling_time"] = round(
        time_components.get("handling_time", 0), 2
    )

    # Add ALL stations and vehicles
    if simulation:
        # Add columns for all stations
        for station in simulation.stations:
            station_col = station.name
            if station_col not in SimulationConfig.log_disassembly.columns:
                SimulationConfig.log_disassembly[station_col] = 0.0
            else:
                # Ensure it's numeric
                SimulationConfig.log_disassembly[station_col] = pd.to_numeric(
                    SimulationConfig.log_disassembly[station_col], errors="coerce"
                ).fillna(0.0)

            # Update with actual time
            station_time = time_components.get("station_times", {}).get(station.name, 0)
            SimulationConfig.log_disassembly.loc[mask, station_col] = round(
                station_time, 2
            )

        # Add columns for all vehicles
        for vehicle in simulation.vehicles:
            vehicle_col = vehicle.name
            if vehicle_col not in SimulationConfig.log_disassembly.columns:
                SimulationConfig.log_disassembly[vehicle_col] = 0.0
            else:
                # Ensure it's numeric
                SimulationConfig.log_disassembly[vehicle_col] = pd.to_numeric(
                    SimulationConfig.log_disassembly[vehicle_col], errors="coerce"
                ).fillna(0.0)

            # Update with actual time
            vehicle_time = time_components.get("vehicle_times", {}).get(vehicle.name, 0)
            SimulationConfig.log_disassembly.loc[mask, vehicle_col] = round(
                vehicle_time, 2
            )

    # Calculate and update lead time
    done_time = SimulationConfig.log_disassembly.loc[mask, "done_time"].iloc[0]
    entry_time = SimulationConfig.log_disassembly.loc[mask, "entry_time"].iloc[0]
    if pd.notna(done_time) and pd.notna(entry_time):
        lead_time = done_time - entry_time
        SimulationConfig.log_disassembly.loc[mask, "lead_time"] = round(lead_time, 2)

    # Mark as done
    SimulationConfig.log_disassembly.loc[mask, "done"] = True


def add_to_eventlog_v3(
    case_id: int,
    object_id: str,
    object_type: str,
    activity: str,
    activity_state: str,
    resource_id: str,
    resource_location: str,
    timestamp: float,
    related_objects: str = None,
) -> None:
    """
    Add a new row to the eventlog with clean parameter names and OCEL 2.0 structure.

    Migrated previous versions to new standard.

    Parameters:
    case_id (int): The case ID (product ID that entered the system)
    object_id (str): Clean object identifier (e.g., prod_001, comp_001)
    object_type (str): Object type (product, component, group)
    activity (str): Activity type (transport, buffer_wait, inspection, disassembly, etc.)
    activity_state (str): Activity state (start, complete, receive, release, etc.)
    resource_id (str): The resource performing the activity
    resource_location (str): Location at the resource (workstation, inbuf, outbuf, etc.)
    timestamp (float): Current simulation time in minutes
    related_objects (str): Related objects in format "object_id:relationship,..."
    """
    if SimulationConfig.export_eventlog:
        # Format object_id based on type and content
        if isinstance(object_id, str) and "_" in object_id:
            # e.g. "1_HousingPart" - split and reformat
            parts = object_id.split("_", 1)
            if parts[0].isdigit():
                num_part = int(parts[0])
                suffix = parts[1] if len(parts) > 1 else ""

                if object_type.lower() == "product":
                    clean_object_id = (
                        f"prod_{num_part:03d}_{suffix}"
                        if suffix
                        else f"prod_{num_part:03d}"
                    )
                elif object_type.lower() == "component":
                    clean_object_id = (
                        f"comp_{num_part:03d}_{suffix}"
                        if suffix
                        else f"comp_{num_part:03d}"
                    )
                else:
                    clean_object_id = (
                        f"{object_type.lower()}_{num_part:03d}_{suffix}"
                        if suffix
                        else f"{object_type.lower()}_{num_part:03d}"
                    )
            else:
                # Not a numeric prefix, use as-is with type prefix
                if object_type.lower() == "component" and not object_id.startswith(
                    "comp_"
                ):
                    clean_object_id = f"comp_{object_id}"
                else:
                    clean_object_id = object_id
        elif isinstance(object_id, int) or (
            isinstance(object_id, str) and object_id.isdigit()
        ):
            # Simple numeric ID
            num_id = int(object_id)
            if object_type.lower() == "product":
                clean_object_id = f"prod_{num_id:03d}"
            elif object_type.lower() == "component":
                clean_object_id = f"comp_{num_id:03d}"
            else:
                clean_object_id = f"{object_type.lower()}_{num_id:03d}"
        else:
            # Use as-is
            clean_object_id = object_id

        # Rest of function...
        delta = timedelta(minutes=timestamp)
        timestamp_str = (SimulationConfig.start_date + delta).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )

        event_count = len(SimulationConfig.events_list) + 1
        event_id = f"e{event_count:06d}"

        event = {
            "event_id": event_id,
            "caseID": case_id,
            "object_id": clean_object_id,
            "object_type": object_type,
            "activity": activity,
            "activity_state": activity_state,
            "resource_id": resource_id,
            "resource_location": resource_location,
            "timestamp": timestamp_str,
            "related_objects": related_objects,
        }

        SimulationConfig.events_list.append(event)


def register_object(object_id: str, object_info: dict) -> None:
    """
    Register an object in the global registry for lookup.

    Args:
        object_id: Clean object ID (e.g., prod_001, comp_001_Fluide)
        object_info: Dictionary with object details
    """
    global _object_registry
    _object_registry[object_id] = object_info


def get_object_info(object_id: str) -> dict:
    """Get object information from registry."""
    return _object_registry.get(object_id, {})


def create_object_lookup_table() -> pd.DataFrame:
    """Create a DataFrame with all registered objects."""
    if not _object_registry:
        return pd.DataFrame()

    records = []
    for obj_id, info in _object_registry.items():
        records.append(
            {
                "object_id": obj_id,
                "object_name": info.get("name", ""),
                "object_class": info.get("class", ""),
                "case_id": info.get("case_id", ""),
                "original_id": info.get("original_id", ""),
                "parent_object": info.get("parent", ""),
                "created_time": info.get("created_time", ""),
                "attributes": str(info.get("attributes", {})),
            }
        )

    return pd.DataFrame(records)


## 6. Updated KPI calculation function
def calculate_time_components_v2(case_id, eventlog, simulation=None):
    """Calculate times with new event structure."""
    case_events = eventlog[eventlog["caseID"] == case_id].copy()

    # Convert timestamp if needed
    if len(case_events) > 0 and isinstance(case_events["timestamp"].iloc[0], str):
        case_events["timestamp"] = pd.to_datetime(
            case_events["timestamp"], format="ISO8601"
        )

    result = {
        "processing_time": 0,
        "handling_time": 0,
        "logistics_time": 0,
        "station_times": {},
        "vehicle_times": {},
        "buffer_times": {},
    }

    # Initialize all stations/vehicles with 0 if simulation provided
    if simulation:
        for station in simulation.stations:
            result["station_times"][station.name] = 0.0
        for vehicle in simulation.vehicles:
            result["vehicle_times"][vehicle.name] = 0.0

    # 1. Processing times (disassembly activities)
    disassembly_events = case_events[case_events["activity"] == "disassembly"]

    # Group by object_id to handle multiple components
    for obj_id in disassembly_events["object_id"].unique():
        obj_events = disassembly_events[disassembly_events["object_id"] == obj_id]
        starts = obj_events[obj_events["activity_state"] == "start"]
        completes = obj_events[obj_events["activity_state"] == "complete"]

        for idx, start in starts.iterrows():
            # Find matching complete
            matching_complete = completes[
                (completes["resource_id"] == start["resource_id"])
                & (completes["timestamp"] > start["timestamp"])
            ]

            if len(matching_complete) > 0:
                complete = matching_complete.iloc[0]
                time_diff = (
                    complete["timestamp"] - start["timestamp"]
                ).total_seconds() / 60

                station = start["resource_id"]
                if station not in result["station_times"]:
                    result["station_times"][station] = 0
                result["station_times"][station] += time_diff
                result["processing_time"] += time_diff

    # 2. Transport times
    transport_events = case_events[case_events["activity"] == "transport"]

    # Group by resource (vehicle)
    for vehicle in transport_events["resource_id"].unique():
        vehicle_events = transport_events[transport_events["resource_id"] == vehicle]
        loads = vehicle_events[vehicle_events["activity_state"] == "load"]
        unloads = vehicle_events[vehicle_events["activity_state"] == "unload"]

        for idx, load in loads.iterrows():
            # Find matching unload
            matching_unload = unloads[
                (unloads["object_id"] == load["object_id"])
                & (unloads["timestamp"] > load["timestamp"])
            ]

            if len(matching_unload) > 0:
                unload = matching_unload.iloc[0]
                time_diff = (
                    unload["timestamp"] - load["timestamp"]
                ).total_seconds() / 60

                if vehicle not in result["vehicle_times"]:
                    result["vehicle_times"][vehicle] = 0
                result["vehicle_times"][vehicle] += time_diff
                result["logistics_time"] += time_diff

    # 3. Buffer waiting times
    buffer_events = case_events[case_events["activity"] == "buffer_wait"]

    # Group by location
    for location in buffer_events["resource_location"].unique():
        loc_events = buffer_events[buffer_events["resource_location"] == location]
        receives = loc_events[loc_events["activity_state"] == "receive"]
        releases = loc_events[loc_events["activity_state"] == "release"]

        total_wait = 0
        for idx, receive in receives.iterrows():
            matching_release = releases[
                (releases["object_id"] == receive["object_id"])
                & (releases["timestamp"] > receive["timestamp"])
            ]

            if len(matching_release) > 0:
                release = matching_release.iloc[0]
                wait_time = (
                    release["timestamp"] - receive["timestamp"]
                ).total_seconds() / 60
                total_wait += wait_time

        if location not in result["buffer_times"]:
            result["buffer_times"][location] = 0
        result["buffer_times"][location] += total_wait

    # 4. Handling time (station receive/release)
    handling_events = case_events[case_events["activity"] == "handling"]
    # Calculate handling time between receive and release at workstation

    return result


def create_object_lookup_table_from_eventlog() -> pd.DataFrame:
    """Create object lookup table from eventlog data."""
    if SimulationConfig.eventlog.empty and not SimulationConfig.events_list:
        return pd.DataFrame()

    # Convert events list to DataFrame if needed
    if SimulationConfig.events_list:
        eventlog = pd.DataFrame(SimulationConfig.events_list)
    else:
        eventlog = SimulationConfig.eventlog

    # Get unique objects from eventlog
    objects = {}

    # Find all object creation events
    creation_events = eventlog[
        (eventlog["activity"] == "object") & (eventlog["activity_state"] == "created")
    ]

    for _, event in creation_events.iterrows():
        obj_id = event["object_id"]
        if obj_id not in objects:
            # Parse parent from related_objects
            parent = None
            if pd.notna(event["related_objects"]) and ":parent" in str(
                event["related_objects"]
            ):
                parent = str(event["related_objects"]).split(":")[0]

            objects[obj_id] = {
                "object_id": obj_id,
                "object_type": event["object_type"],
                "case_id": event["caseID"],
                "parent_object": parent,
                "created_time": event["timestamp"],
                "resource_id": event["resource_id"],
            }

    # Also add products from system entry events
    entry_events = eventlog[
        (eventlog["activity"] == "system") & (eventlog["activity_state"] == "entry")
    ]

    for _, event in entry_events.iterrows():
        obj_id = event["object_id"]
        if obj_id not in objects:
            objects[obj_id] = {
                "object_id": obj_id,
                "object_type": event["object_type"],
                "case_id": event["caseID"],
                "parent_object": None,
                "created_time": event["timestamp"],
                "resource_id": "source",
            }

    return pd.DataFrame(list(objects.values()))


def get_target_components(structure: Dict[str, Dict]) -> Dict[str, int]:
    """
    Extract all leaf components (not groups) from a product structure.

    Args:
        structure: Product structure from JSON

    Returns:
        Dict mapping component name to total quantity
    """
    target_components = {}

    def extract_components(struct, prefix=""):
        for key, value in struct.items():
            if "structure" in value:
                # Group - recurse into it
                extract_components(value["structure"], f"{prefix}{key}_")
            else:
                # Leaf component
                component_name = f"{prefix}{key}"
                quantity = value.get("quantity", 1)
                if component_name in target_components:
                    target_components[component_name] += quantity
                else:
                    target_components[component_name] = quantity

    extract_components(structure)
    return target_components

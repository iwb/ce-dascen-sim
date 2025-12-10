"""
File: vehicle.py
Location: /src/vehicle.py
Description: Transport vehicle resource for material handling
Author: Patrick Jordan
Version: 2025-10

Implements transport vehicles as SimPy PreemptiveResources:
- Load/unload operations with configurable times
- Travel between locations using distance matrix
- Load capacity management in transport units
- Location tracking and usage logging

Vehicles can be requested as resources and handle the physical
movement of products, groups, and components between stations.
"""

from contextlib import ExitStack

import simpy

import functions
import helper_functions
from src.g import *


class Vehicle(simpy.PreemptiveResource):
    """This class represents a transport vehicle and extends simpy's PreemptiveResource class.
    It can be used to load, unload and drive to a specific location.
    For this, the vehicle can be requested like a resource.

    Attributes:
        env (simpy.Environment): The simulation environment.
        name (str): The name of the vehicle.
        speed (float): The speed of the vehicle in m/min
        load (simpy.FilterStore): A storage for the items loaded on the vehicle.
        transport_units_used (int): The amount of transport units currently used by the load on the vehicle.
        load_capacity (int): The maximum load capacity of the vehicle in terms of transport units.
        location (str): The current location of the vehicle.
        load_time (float): The time it takes to load or undload one item.
        busy_time (float): The time the vehicle has been busy.

    Methods:
        create_return(*args, **kwargs): A method to return the vehicle if it is requested.
        release(request): A method to release the vehicle.
        load_item(item): A method to load an item onto the vehicle.
        unload_item(): A method to unload an item from the vehicle.
        drive(end_location): A method to drive the vehicle to a specific location.
    """

    def __init__(
        self: object,
        env: simpy.Environment,
        name: str,
        location: str,
        speed: float,
        load_capacity: int,
        loading_time: float,
    ) -> None:
        # capacity 1 (each vehicle can only serve one request at a time)
        super().__init__(env, capacity=1)
        self.env = env
        self.name = name
        self.speed = speed
        # capacity is infinite (capacity is limited in terms of transport units, not count of items)
        self.load = simpy.FilterStore(env, capacity=float("inf"))
        self.transport_units_used = 0
        self.load_capacity = load_capacity
        self.location = location
        self.load_time = loading_time
        self.busy_time = 0

    def create_request(self: object, *args, **kwargs) -> None:
        """Submits a request for the vehicle and attaches a reference to the vehicle in the request.

        Args:
            self (object): A reference to the vehicle instance.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            simpy.Request: The request for the vehicle resource.
        """
        req = self.request(*args, **kwargs)
        # Store a reference to the vehicle in the request
        req.vehicle = self
        return req

    def release(self: object, request: object) -> None:
        """release the vehicle

        Args:
            self (object): A reference to the vehicle instance.
            request (object): The request for the vehicle resource.
        """
        super().release(request)

    def load_item(self: object, item: object) -> None:
        """Loads an item onto the vehicle and updates the transport_units_used attribute
        according the transport_units used by the item.

        Args:
            self (object): A reference to the vehicle instance.
            item (object): The item to be loaded onto the vehicle.

        Returns:
            simpy.Event: An event representing the action of loading the item onto the vehicle.
        """
        self.transport_units_used += item.transport_units
        # Load an item onto the vehicle
        return self.load.put(item)

    def unload_item(self: object) -> None:
        """Unloads the first item from the vehicle and updates the transport_units_used attribute
        according the transport_units used by the item.
        Return None if there is no item in the vehicle.

        Args:
            self (object): A reference to the vehicle instance.
            item (object): The item to be unloaded from the vehicle.

        Returns:
            simpy.Event: An event representing the action of unloading the first item from the vehicle.
        """
        if len(self.load.items) > 0:
            item = self.load.items[0]
            self.transport_units_used -= item.transport_units
            # Return simpy.Event
            return self.load.get()
        # Return None if there is no product to unload
        else:
            return None

    def drive(self: object, end_location: str) -> None:
        """Drives the vehicle to a specified location."""
        # Check, if vehicle is not already at end location
        if self.location != end_location:
            # calculate driving time
            base_driving_time = helper_functions.get_driving_time(
                self.location,
                end_location,
                self.speed,
                SimulationConfig.distance_matrix,
            )

            # Apply variation based on behavior mode
            if SimulationConfig.behavior_mode == SimulationBehavior.DETERMINISTIC:
                # Use exact calculated time for deterministic behavior
                driving_time = base_driving_time
            else:
                # Add some randomness (±10%) for seeded behavior
                # variation = SimulationConfig.rng_process_times.triangular(0.9, 1.1, 1.0)
                variation = SimulationConfig.rng_transport.triangular(0.9, 1.1, 1.0)
                driving_time = base_driving_time * variation

            yield self.env.timeout(driving_time)
            # update vehicle location
            self.location = end_location

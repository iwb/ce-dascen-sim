"""
File: source.py
Location: /src/source.py
Description: Product source/generator for incoming products
Author: Patrick Jordan
Version: 2025-10

Manages product generation and delivery to the system:
- Random product generation based on variant configurations
- Scheduled delivery processing from JSON schedules
- Mixed mode (scheduled + random) support
- Product initialization with IDs, conditions, and timestamps

The Source class creates products and delivers them to the incoming storage.
Supports three delivery modes:
1. random: Stochastic arrivals based on weekly volumes
2. scheduled: Deterministic from delivery schedule file
3. mixed: Combination of scheduled and random deliveries
"""

from src.g import *
from src.product import *


class Source:
    """This class represents the source of products in the simulation environment.

    The source is responsible for both scheduled and random product generation based on configuration.
    It can process a delivery schedule for deterministic product creation, while also generating
    random products based on specified variant files.

    Attributes:
        env (simpy.Environment): The simulation environment in which the source is operating.
        productcount (int): A counter for the total number of products generated.
        successor (simpy.Store): The next entity in the process flow, where generated products will be put.
        delivery_schedule (dict): Schedule defining deterministic product deliveries.
        use_schedule (bool): Flag indicating if a delivery schedule is being used.
        schedule_complete (bool): Flag indicating if all scheduled deliveries have been processed.
        product_generators (list): Active simulation processes for product generation.
    """

    def __init__(
        self, env: simpy.Environment, successor: simpy.Store, simulation=None
    ) -> None:
        """Initialize the product source.

        Args:
            env: The simulation environment.
            successor: The next entity in the process flow to receive generated products.
            simulation: The simulation instance (for routing plan generation).
        """
        self.env = env
        self.productcount = 0
        self.successor = successor
        self.simulation = simulation
        self.delivery_schedule = None
        self.use_schedule = False
        self.schedule_complete = False
        self.product_generators = []

    def load_delivery_schedule(self, schedule_path: str) -> bool:
        """Load and validate a delivery schedule from a JSON file.

        Args:
            schedule_path: Path to the delivery schedule JSON file.

        Returns:
            bool: True if schedule was successfully loaded, False otherwise.
        """
        try:
            # Load schedule file
            with open(schedule_path, "r") as f:
                schedule_data = json.load(f)

            # Validate basic structure
            if "delivery_schedule" not in schedule_data:
                print(f"Error: Invalid delivery schedule format in {schedule_path}")
                return False

            # Store schedule
            self.delivery_schedule = schedule_data["delivery_schedule"]

            # Check for required fields
            required_fields = ["entries"]
            for field in required_fields:
                if field not in self.delivery_schedule:
                    print(f"Error: Missing '{field}' in delivery schedule")
                    return False

            # Validate entries
            for i, entry in enumerate(self.delivery_schedule["entries"]):
                required_entry_fields = ["delivery_time", "product_file"]
                for field in required_entry_fields:
                    if field not in entry:
                        print(
                            f"Error: Missing '{field}' in delivery schedule entry {i + 1}"
                        )
                        return False

            # Sort entries by delivery time
            self.delivery_schedule["entries"].sort(key=lambda x: x["delivery_time"])

            self.use_schedule = True
            print(
                f"Loaded delivery schedule with {len(self.delivery_schedule['entries'])} entries"
            )
            return True

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading delivery schedule: {e}")
            return False

    def scheduled_product_generator(self) -> None:
        """Generate products according to the delivery schedule.

        This generator processes the entries in the delivery schedule and creates
        products at the specified times with the specified properties.

        Yields:
            SimPy timeout events for waiting between deliveries.
        """
        # ==========================================
        # PHASE 1: Validate schedule
        # ==========================================
        log_disassembly_list = []

        if not self.use_schedule or not self.delivery_schedule:
            print("Warning: No delivery schedule loaded. Using only random generators.")
            return

        current_time = 0

        # ==========================================
        # PHASE 2: Process each scheduled delivery
        # ==========================================
        for entry in self.delivery_schedule["entries"]:
            # Calculate wait time until next delivery
            wait_time = entry["delivery_time"] - current_time

            if wait_time > 0:
                yield self.env.timeout(wait_time)

            current_time = entry["delivery_time"]

            # ==========================================
            # PHASE 3: Create product
            # ==========================================
            # Construct path to product variant file
            variant_path = os.path.join(
                SimulationConfig.file_path,
                SimulationConfig.product_range_path,
                entry["product_file"],
            )

            # Check if file exists
            if not os.path.exists(variant_path):
                print(
                    f"Warning: Product file {entry['product_file']} not found at {variant_path}"
                )
                continue

            # Create the product with specified condition if provided
            condition = entry.get("condition", None)
            p = self.create_product(variant_path, condition)

            # ==========================================
            # PHASE 4: Update tracking logs
            # ==========================================
            log_disassembly_list.append(
                {
                    "ID": p.ID,
                    "product_type": p.type,
                    "entry_time": p.delivery_time,
                    "done_time": None,
                    "lead_time": 0.0,  # Numeric fields float (datatyp warning)
                    "level_of_disassembly": 0.0,
                    "handling_time": 0.0,
                    "done": False,
                }
            )

        # ==========================================
        # PHASE 5: Finalize schedule
        # ==========================================
        # Update log_disassembly with all new entries
        if log_disassembly_list:
            SimulationConfig.log_disassembly = pd.concat(
                [SimulationConfig.log_disassembly, pd.DataFrame(log_disassembly_list)],
                ignore_index=True,
            )

        # Mark schedule completion
        self.schedule_complete = True
        print(
            f"Scheduled delivery complete: {len(self.delivery_schedule['entries'])} products delivered"
        )

    def create_product(self, variant_path: str, condition: float = None) -> object:
        """Create a single product with the specified properties.

        Args:
            variant_path: Path to the product variant JSON file.
            condition: Optional fixed condition value to use instead of random generation.

        Returns:
            product: The created product instance.
        """
        # Increment product count
        self.productcount += 1

        # Create product instance with simulation reference for routing plan
        p = product(
            self.env, self.productcount, variant_path, simulation=self.simulation
        )

        # Debug log product creation
        helper_functions.debug_print(
            f"Created product {p.ID} type={p.type} condition={p.condition:.2f} parts={p.parts_count}"
        )
        # Show routing plan (always print for verification)
        if hasattr(p, "routing_plan") and p.routing_plan:
            helper_functions.debug_print(
                f"Product {p.ID} ({p.type}): Routing = {' -> '.join(p.routing_plan)}"
            )
            print(
                f"  Product {p.ID} ({p.type}): Routing = {' -> '.join(p.routing_plan)}"
            )

        # Set condition if provided, otherwise it uses the default random generation
        if condition is not None:
            p.condition = min(
                max(condition, 0), 1
            )  # Ensure condition is in [0,1] range

        # Get the pre-calculated target components (based on product config)
        target_components = SimulationConfig.target_components_by_variant.get(
            p.type, {}
        )

        # DEBUG
        helper_functions.debug_print(f"\nCreating product {p.ID} type {p.type}")
        helper_functions.debug_print(
            f"  Original target components: {target_components}"
        )

        # Remove missing components and get list of what was removed
        missing_components = helper_functions.remove_components(p.content["structure"])

        # DEBUG
        helper_functions.debug_print(f"  Missing components: {missing_components}")
        helper_functions.debug_print(
            f"  Remaining: {list(helper_functions.list_components(p.content['structure']))}"
        )

        # LOG: OBJECT CREATION - Product is created
        SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
            case_id=p.caseID,
            object_id=p.ID,
            object_type="product",
            activity="object",
            activity_state="created",
            resource_id="source",
            resource_location="generator",
            timestamp=self.env.now,
            related_objects=None,  # No parent - this is a new product
        )

        # Put product into the successor
        self.successor.put(p)

        # LOG 2: SYSTEM ENTRY - Product enters the disassembly system
        SimulationConfig.eventlog = helper_functions.add_to_eventlog_v3(
            case_id=p.caseID,
            object_id=p.ID,
            object_type="product",
            activity="system",
            activity_state="entry",
            resource_id="incoming_storage",
            resource_location="entry",
            timestamp=self.env.now,
            related_objects=None,
        )

        # Add to case table
        SimulationConfig.case_table = helper_functions.add_to_case_table(
            p.caseID,
            p.type,
            p.delivery_time,
            p.condition,
            target_components,
            missing_components,
        )

        return p

    def random_product_generator(
        self, variant_information: dict, variant_path: str
    ) -> None:
        """Generate products randomly according to the variant configuration.

        This method maintains the original random generation behavior but now respects the
        delivery mode configuration.

        Args:
            variant_information: Configuration for the product variant.
            variant_path: Path to the product variant JSON file.

        Yields:
            SimPy timeout events for waiting between product generations.
        """
        # Get delivery mode
        delivery_mode = SimulationConfig.delivery_mode

        # In scheduled-only mode, exit immediately
        if delivery_mode == "scheduled":
            return

        log_disassembly_list = []

        # If scheduled deliveries are enabled and random deliveries are disabled, exit
        if (
            self.use_schedule
            and self.delivery_schedule.get("random_deliveries", {}).get("enabled", True)
            == False
        ):
            print("Random deliveries disabled in schedule configuration")
            return

        while True:
            # Generate lot_size products without waiting in between
            for i in range(variant_information["lot_size"]):
                # Create product
                p = self.create_product(
                    os.path.join(SimulationConfig.file_path, variant_path)
                )

                # Add to log_disassembly list
                log_disassembly_list.append(
                    {
                        "ID": p.ID,
                        "product_type": p.type,
                        "entry_time": p.delivery_time,
                        "done_time": None,
                        "lead_time": 0.0,
                        "level_of_disassembly": 0.0,
                        "handling_time": 0.0,
                        "done": False,
                    }
                )

            # Batch update the log
            if log_disassembly_list:
                SimulationConfig.log_disassembly = pd.concat(
                    [
                        SimulationConfig.log_disassembly,
                        pd.DataFrame(log_disassembly_list),
                    ],
                    ignore_index=True,
                )
                log_disassembly_list = []  # Reset for next iteration

            # Get appropriate delivery cycle time based on behavior mode
            delivery_cycle_time_min = (7 * 24 * 60) / variant_information[
                "volume_per_week_min"
            ]
            delivery_cycle_time_mu = (7 * 24 * 60) / variant_information[
                "volume_per_week_mu"
            ]
            delivery_cycle_time_max = (7 * 24 * 60) / variant_information[
                "volume_per_week_max"
            ]

            if SimulationConfig.behavior_mode == SimulationBehavior.DETERMINISTIC:
                # Use mode value
                random_delivery_cycle_time = delivery_cycle_time_mu
            else:
                # SEEDED -> Use random number generator with triangular distribution
                random_delivery_cycle_time = -1
                while random_delivery_cycle_time < 0:
                    random_delivery_cycle_time = SimulationConfig.rng_supply.triangular(
                        delivery_cycle_time_min,
                        delivery_cycle_time_max,
                        delivery_cycle_time_mu,
                    )

            # Wait until next product is generated
            yield self.env.timeout(
                random_delivery_cycle_time * variant_information["lot_size"]
            )

    def initialize_generators(self):
        """Initialize product generation processes based on delivery mode.

        This method starts either scheduled deliveries, random generators,
        or both depending on the configured delivery mode.
        """
        # Get delivery mode from SimulationConfig
        delivery_mode = SimulationConfig.delivery_mode

        # Start generators based on delivery mode
        if delivery_mode in ["scheduled", "mixed"]:
            # Initialize scheduled deliveries
            if self.use_schedule:
                print(
                    f"Initializing scheduled product delivery with {len(self.delivery_schedule['entries'])} entries"
                )
                self.product_generators.append(
                    self.env.process(self.scheduled_product_generator())
                )
            else:
                print(
                    "Warning: Scheduled delivery requested but no valid schedule loaded"
                )

        # Start random generators if mode is 'random' or 'mixed'
        if delivery_mode in ["random", "mixed"]:
            product_dir = os.path.join(
                SimulationConfig.file_path, SimulationConfig.product_range_path
            )

            # Determine which product files to use
            if (
                hasattr(SimulationConfig, "enabled_product_files")
                and SimulationConfig.enabled_product_files
            ):
                # Use the configuration's enabled product files
                product_files = [
                    os.path.join(product_dir, pf)
                    for pf in SimulationConfig.enabled_product_files
                ]
            elif (
                self.use_schedule
                and "random_deliveries" in self.delivery_schedule
                and delivery_mode == "mixed"
            ):
                # Use the schedule's random_deliveries products if in mixed mode
                random_config = self.delivery_schedule["random_deliveries"]
                if "products" in random_config and random_config.get("enabled", True):
                    product_files = [
                        os.path.join(product_dir, product["product_file"])
                        for product in random_config["products"]
                    ]
                    print(
                        f"Using {len(product_files)} product variants from delivery schedule for random generation"
                    )
                else:
                    # If random deliveries are disabled in the schedule but mixed mode is requested
                    if not random_config.get("enabled", True):
                        print(
                            "Warning: Random deliveries disabled in schedule but 'mixed' mode requested"
                        )
                        product_files = []
                    else:
                        # Default: use all products in directory
                        product_files = [
                            os.path.join(product_dir, f)
                            for f in os.listdir(product_dir)
                            if f.endswith(".json")
                        ]
                        print(
                            f"Using all {len(product_files)} available product variants for random generation"
                        )
            else:
                # Default: use all products in directory
                product_files = [
                    os.path.join(product_dir, f)
                    for f in os.listdir(product_dir)
                    if f.endswith(".json")
                ]
                print(
                    f"Using all {len(product_files)} available product variants for random generation"
                )

            # Get variant overrides from config if present
            variant_overrides = SimulationConfig.full_configuration.get("variant_overrides", {})

            # Start random generators for each product file
            for product_path in product_files:
                if not os.path.exists(product_path):
                    print(f"Warning: Product file not found: {product_path}")
                    continue

                # Load variant information
                with open(product_path) as json_file:
                    variant_info = json.load(json_file)["variant"]

                # Get variant type/name from the loaded info
                variant_type = variant_info.get("type", "")

                # Apply variant-specific overrides if present
                # Check both capitalized and lowercase variant names
                for variant_key in [variant_type, variant_type.lower()]:
                    if variant_key in variant_overrides:
                        overrides = variant_overrides[variant_key]

                        # Apply volume overrides if specified
                        if "volume_per_week_min" in overrides:
                            variant_info["volume_per_week_min"] = overrides["volume_per_week_min"]
                        if "volume_per_week_mu" in overrides:
                            variant_info["volume_per_week_mu"] = overrides["volume_per_week_mu"]
                        if "volume_per_week_max" in overrides:
                            variant_info["volume_per_week_max"] = overrides["volume_per_week_max"]

                        break  # Only apply once

                # Start generator process for random deliveries
                self.product_generators.append(
                    self.env.process(
                        self.random_product_generator(variant_info, product_path)
                    )
                )

            if not product_files:
                print("Warning: No product files found for random generation")

        # If no generators were started, print a warning
        if not self.product_generators:
            print(
                "ERROR: No product generators started! Check delivery mode and configuration."
            )

# Configuration Guide

> **🔬 Research Software Notice**: This document is part of a research prototype (2025-09) and serves as implementation guidance. Scientific references are included for contextual understanding and further reading only. The peer-reviewed scientific contribution can only be found in the published article.

This guide explains how to configure experiments in the disassembly simulation framework. The framework utilizes a hierarchical, JSON-based configuration system that allows for the flexible customization of simulation parameters.

For parameter definitions and implementation details, please refer to the [parameter_reference.md](parameter_reference.md) document. For information on implementation limitations and future extensions, please refer to the [limitations.md](limitations.md) document.


## Table of Contents

- [1. Configuration Hierarchy](#1-configuration-hierarchy)
  - [1.1 Loading Order](#11-loading-order)
  - [1.2 File Locations](#12-file-locations)
- [2. Configuration Types](#2-configuration-types)
  - [2.1 Experiment Configuration](#21-experiment-configuration)
  - [2.2 Factory and Product Configuration](#22-factory-and-product-configuration)
  - [2.3 Runtime Configuration](#23-runtime-configuration)
- [3. Material Flow Modes](#3-material-flow-modes)
  - [3.1 Pull Mode](#31-pull-mode)
  - [3.2 Push Mode](#32-push-mode)
- [4. Stochastic Behavior Control](#4-stochastic-behavior-control)
  - [4.1 Seeded Mode](#41-seeded-mode)
  - [4.2 Deterministic Mode](#42-deterministic-mode)
  - [4.3 Random Mode](#43-random-mode)
- [5. Running Experiments](#5-running-experiments)
  - [5.1 Basic Commands](#51-basic-commands)
  - [5.2 Creating New Experiments](#52-creating-new-experiments)

<br>

---

<br>

<!-- ================================================== -->
<!-- CONFIGURATION HIERARCHY -->
<!-- ================================================== -->
## 1. Configuration Hierarchy

The simulation uses a layered configuration system where the later configurations override the earlier ones. This approach allows the users to define default values that apply across all experiments while still enabling experiment-specific customization.

### 1.1 Loading Order

The simulation loads the configuration files in the following order, with each subsequent level overriding the values from the previous levels. Table 1.1 shows the loading priority and the purpose of each configuration level.

**Table 1.1.** Configuration loading order and override hierarchy

<table>
  <thead>
    <tr>
      <th>Priority</th>
      <th>Configuration type</th>
      <th>Location</th>
      <th>Purpose</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>Default configuration</td>
      <td><code>config/default_config.json</code></td>
      <td>Technical defaults including MTBF, MTTR, handling times, behavior mode, and random seeds</td>
    </tr>
    <tr>
      <td>2</td>
      <td>Runtime configuration</td>
      <td><code>config/runtime_config.json</code></td>
      <td>Output settings, visualization settings, and global overrides</td>
    </tr>
    <tr>
      <td>3</td>
      <td>Experiment configuration</td>
      <td><code>config/experiments/expXX.json</code></td>
      <td>Simulation duration, links to system and product files, and experiment-specific settings</td>
    </tr>
    <tr>
      <td>4</td>
      <td>Experiment overrides</td>
      <td>Within experiment config</td>
      <td>Parameter-specific overrides and variant-specific settings</td>
    </tr>
  </tbody>
</table>

<br>

The following example illustrates how the override mechanism works:

```
default_config.json: handling_time = 2
runtime_config.json: [no override]
experiment.json overrides: handling_time = 1
→ Final value: handling_time = 1
```

### 1.2 File Locations

Table 1.2 shows the location and the purpose of each configuration file type in the framework. These files are organized into specific directories to separate the concerns between default settings, runtime behavior, experiments, and factory structures.

**Table 1.2.** Configuration file locations and purposes

<table>
  <thead>
    <tr>
      <th>Configuration Type</th>
      <th>Location</th>
      <th>Purpose</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Default config</td>
      <td><code>config/default_config.json</code></td>
      <td>Process parameters (MTBF, MTTR, times)</td>
    </tr>
    <tr>
      <td>Runtime config</td>
      <td><code>config/runtime_config.json</code></td>
      <td>Output and visualization settings</td>
    </tr>
    <tr>
      <td>Experiments</td>
      <td><code>config/experiments/exp*.json</code></td>
      <td>Individual experiment definitions</td>
    </tr>
    <tr>
      <td>System resources</td>
      <td><code>config/system_config/system_*.json</code></td>
      <td>Factory structures (stations, storage, vehicles)</td>
    </tr>
    <tr>
      <td>Distance matrices</td>
      <td><code>config/system_config/distance_matrix_*.csv</code></td>
      <td>Station-to-station distances</td>
    </tr>
    <tr>
      <td>Products</td>
      <td><code>config/product_config/variant*.json</code></td>
      <td>Product structures and components</td>
    </tr>
    <tr>
      <td>Schedules</td>
      <td><code>config/delivery_schedules/schedule_*.json</code></td>
      <td>Delivery schedules (for scheduled mode)</td>
    </tr>
  </tbody>
</table>

<br>

---

<br>

<!-- ================================================== -->
<!-- CONFIGURATION TYPES -->
<!-- ================================================== -->
## 2. Configuration Types

This section describes the structure and the key fields for each configuration file type.

### 2.1 Experiment Configuration

The experiment configuration files are located in the `config/experiments/` directory and follow the naming convention `expXX_name.json`. Each experiment file defines the complete setup for a simulation run. Table 2.1 shows the key fields that must be configured in each experiment file. Example experiment files can be found in the `config/experiments/exp01_baseline_workshop_pull.json` file and other experiment files in the same directory.

**Table 2.1.** Experiment configuration key fields

<table>
  <thead>
    <tr>
      <th>Field</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>experiment_id</code></td>
      <td>Unique identifier for the experiment</td>
    </tr>
    <tr>
      <td><code>description</code></td>
      <td>Purpose and description of the experiment</td>
    </tr>
    <tr>
      <td><code>simulation.weeks</code></td>
      <td>Duration in weeks (decimal values accepted, e.g., 0.714 = 5 days). Minimum value: 0.1 weeks</td>
    </tr>
    <tr>
      <td><code>simulation.start_date</code></td>
      <td>Reference timestamp in ISO format</td>
    </tr>
    <tr>
      <td><code>factory_structure.file</code></td>
      <td>System JSON filename (from <code>system_config/</code>)</td>
    </tr>
    <tr>
      <td><code>factory_structure.distance_matrix</code></td>
      <td>Distance CSV filename</td>
    </tr>
    <tr>
      <td><code>products</code></td>
      <td>Array of product configurations with <code>enabled</code> flags</td>
    </tr>
    <tr>
      <td><code>product_delivery.mode</code></td>
      <td>Delivery mode: "random" or "scheduled"</td>
    </tr>
    <tr>
      <td><code>product_delivery.schedule_file</code></td>
      <td>Schedule file (required if mode is "scheduled")</td>
    </tr>
    <tr>
      <td><code>overrides</code></td>
      <td>Parameter overrides for this experiment</td>
    </tr>
  </tbody>
</table>

<br>

### 2.2 Factory and Product Configuration

This section describes the configuration files that define the physical factory structure, the product variants, and the delivery patterns. These three configuration types work together to create a complete simulation scenario. Table 2.2 shows the components and the attributes for each configuration type. Each system layout requires an accompanying distance matrix that includes all the resources (stations, storages) defined in the system configuration. Example files can be found in the `config/system_config/workshop_1.json` and `line_parallel_4.json` files (system layouts), the `config/product_config/` directory (product variants), and the `config/delivery_schedules/schedule_deterministic.json` file (delivery schedules).

**Table 2.2.** Factory and product configuration components

<table>
  <thead>
    <tr>
      <th>Component</th>
      <th>Attribute</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td colspan="3"><strong>System layouts</strong> (<code>config/system_config/</code>)</td>
    </tr>
    <tr>
      <td rowspan="5">Stations</td>
      <td>ID</td>
      <td>Station identifier</td>
    </tr>
    <tr>
      <td>Predecessors</td>
      <td>Upstream stations or storages</td>
    </tr>
    <tr>
      <td>Shift hours</td>
      <td>Start and end of day times</td>
    </tr>
    <tr>
      <td>Steps</td>
      <td>Disassembly operations with resource requirements</td>
    </tr>
    <tr>
      <td>Local resources</td>
      <td>Equipment and employees assigned to this station</td>
    </tr>
    <tr>
      <td rowspan="3">Storages</td>
      <td>ID</td>
      <td>Storage identifier</td>
    </tr>
    <tr>
      <td>Predecessors</td>
      <td>Upstream stations or storages</td>
    </tr>
    <tr>
      <td>Capacity limits</td>
      <td>Entry, storage, and exit buffer capacities</td>
    </tr>
    <tr>
      <td rowspan="3">Vehicles</td>
      <td>ID</td>
      <td>Vehicle identifier</td>
    </tr>
    <tr>
      <td>Speed</td>
      <td>Transport speed (units per minute)</td>
    </tr>
    <tr>
      <td>Load capacity</td>
      <td>Maximum products per trip</td>
    </tr>
    <tr>
      <td rowspan="2">Global resources</td>
      <td>Equipment</td>
      <td>Factory-wide shared equipment</td>
    </tr>
    <tr>
      <td>Employees</td>
      <td>Factory-wide shared employees</td>
    </tr>
    <tr>
      <td colspan="3"><strong>Products</strong> (<code>config/product_config/</code>)</td>
    </tr>
    <tr>
      <td rowspan="5">Product variant</td>
      <td>Variant name</td>
      <td>Product type identifier</td>
    </tr>
    <tr>
      <td>Volume parameters (min, mu, max)</td>
      <td>Weekly production volume distribution</td>
    </tr>
    <tr>
      <td>Lot size</td>
      <td>Number of products per batch</td>
    </tr>
    <tr>
      <td>Product condition (min, mu, max)</td>
      <td>Product condition distribution</td>
    </tr>
    <tr>
      <td>Component structure</td>
      <td>Hierarchical definition including component names, disassembly times, blocking relationships (precedence constraints), mandatory flags, condition deviations, and missing component probabilities</td>
    </tr>
    <tr>
      <td colspan="3"><strong>Delivery schedules</strong> (<code>config/delivery_schedules/</code>)</td>
    </tr>
    <tr>
      <td rowspan="3">Schedule entry</td>
      <td><code>delivery_time</code></td>
      <td>Time in simulation minutes when the product arrives in the system</td>
    </tr>
    <tr>
      <td><code>product_file</code></td>
      <td>Path to the product configuration file (relative to <code>product_config/</code>)</td>
    </tr>
    <tr>
      <td><code>condition</code></td>
      <td>Product condition value (0.0 to 1.0, where 1.0 represents perfect condition)</td>
    </tr>
  </tbody>
</table>

<br>

### 2.3 Runtime Configuration

The runtime configuration file (`config/runtime_config.json`) controls the simulation output and the visualization settings. The settings are organized into eight main categories covering data export, visualization, and performance options. Table 2.3 provides a complete overview of all the available runtime configuration settings. All settings are boolean (true/false) except `monitoring_frequency_factor` and `element_entry_monitoring_frequency`, which are numeric values.

**Table 2.3.** Runtime configuration settings

<table>
  <thead>
    <tr>
      <th>Category</th>
      <th>Setting</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td colspan="3"><strong>Core outputs</strong> (raw simulation data files)</td>
    </tr>
    <tr>
      <td rowspan="3">Core outputs</td>
      <td><code>export_eventlog</code></td>
      <td>Master event log with all activities (required for object_lookup)</td>
    </tr>
    <tr>
      <td><code>export_case_table</code></td>
      <td>Summary table of all products entering the system</td>
    </tr>
    <tr>
      <td><code>export_output_table</code></td>
      <td>Details of all components/products leaving the system</td>
    </tr>
    <tr>
      <td colspan="3"><strong>Derived outputs</strong> (computed metrics from eventlog)</td>
    </tr>
    <tr>
      <td rowspan="4">Derived outputs</td>
      <td><code>export_object_lookup</code></td>
      <td>Object reference table derived from eventlog</td>
    </tr>
    <tr>
      <td><code>export_product_time_analysis</code></td>
      <td>Resource time consumption analysis (PT/HT/LT breakdown)</td>
    </tr>
    <tr>
      <td><code>export_quality_analysis</code></td>
      <td>Quality-based analysis and routing statistics</td>
    </tr>
    <tr>
      <td><code>export_station_stats_absolute</code></td>
      <td>Station time metrics in minutes (busy, blocked, idle, failed, closed)</td>
    </tr>
    <tr>
      <td colspan="3"><strong>Parameter extraction</strong> (configuration analysis)</td>
    </tr>
    <tr>
      <td rowspan="2">Parameter extraction</td>
      <td><code>export_product_parameters</code></td>
      <td>Extract product structure metrics and portfolio parameters</td>
    </tr>
    <tr>
      <td><code>export_system_parameters</code></td>
      <td>Extract system configuration and capacity parameters</td>
    </tr>
    <tr>
      <td colspan="3"><strong>Debug outputs</strong> (diagnostic files)</td>
    </tr>
    <tr>
      <td rowspan="5">Debug outputs</td>
      <td><code>export_merged_config</code></td>
      <td>Complete configuration used for the run</td>
    </tr>
    <tr>
      <td><code>create_debug_log</code></td>
      <td>Detailed text log of simulation decisions</td>
    </tr>
    <tr>
      <td><code>time_consistency_checks</code></td>
      <td>Validates station time accounting (requires station_state_tracking)</td>
    </tr>
    <tr>
      <td><code>station_state_tracking</code></td>
      <td>Tracks all station state transitions</td>
    </tr>
    <tr>
      <td><code>export_monitoring_data</code></td>
      <td>Time series data (inventory, station counts)</td>
    </tr>
    <tr>
      <td colspan="3"><strong>Visualization</strong> (visual outputs)</td>
    </tr>
    <tr>
      <td rowspan="3">Visualization</td>
      <td><code>show_progress_bar</code></td>
      <td>Real-time simulation progress in console</td>
    </tr>
    <tr>
      <td><code>show_structure</code></td>
      <td>Factory network graph after simulation (requires matplotlib)</td>
    </tr>
    <tr>
      <td><code>show_timeseries_graphs</code></td>
      <td>Inventory and throughput graphs after simulation (requires matplotlib)</td>
    </tr>
    <tr>
      <td colspan="3"><strong>Display</strong> (console output after simulation)</td>
    </tr>
    <tr>
      <td rowspan="5">Display</td>
      <td><code>show_system_overview</code></td>
      <td>Basic run statistics (time, products processed)</td>
    </tr>
    <tr>
      <td><code>show_production_metrics</code></td>
      <td>Throughput rates and disassembly levels</td>
    </tr>
    <tr>
      <td><code>show_resource_utilization</code></td>
      <td>Station utilization percentages</td>
    </tr>
    <tr>
      <td><code>show_logistics_performance</code></td>
      <td>Vehicle utilization and transport statistics</td>
    </tr>
    <tr>
      <td><code>show_technical_performance</code></td>
      <td>Simulation runtime and event generation stats</td>
    </tr>
    <tr>
      <td colspan="3"><strong>Monitoring</strong> (data collection frequency)</td>
    </tr>
    <tr>
      <td rowspan="2">Monitoring</td>
      <td><code>monitoring_frequency_factor</code></td>
      <td>Divides simulation time for monitoring interval (higher = less frequent)</td>
    </tr>
    <tr>
      <td><code>element_entry_monitoring_frequency</code></td>
      <td>Minutes between station order checks</td>
    </tr>
    <tr>
      <td colspan="3"><strong>Performance</strong> (optimization settings)</td>
    </tr>
    <tr>
      <td>Performance</td>
      <td><code>optimize_state_machine</code></td>
      <td>Uses faster state tracking without history (disables detailed state logs)</td>
    </tr>
  </tbody>
</table>

<br>

---

<br>

<!-- ================================================== -->
<!-- MATERIAL FLOW MODES -->
<!-- ================================================== -->
## 3. Material Flow Modes

The simulation supports two material flow strategies that determine how products move through the disassembly system.

### 3.1 Pull Mode

In the default setup, the system operates in pull mode. In this mode, the workstations monitor their own entry buffers. When the entry buffer level drops below the threshold defined by `entry_order_threshold`, the workstation requests material from its predecessors. The vehicles then fetch products from the predecessor stations and deliver them to the requesting station. This threshold-based control mechanism prevents buffer starvation.

### 3.2 Push Mode

In push mode, the workstations monitor their own exit buffers instead of entry buffers. When the exit buffer level reaches the threshold defined by `entry_order_threshold` of the successor workstation, the workstation pushes material to its successors. The vehicles transport products to the entry buffer of the next station. This threshold-based control mechanism prevents a buffer overflow.

The material flow mode is configured in the `config/runtime_config.json` file under the `material_flow.flow_mode` parameter. This setting applies globally to all experiments, but individual experiments can override this setting using the experiment configuration file:

**Global configuration** (`config/runtime_config.json`):
```json
"material_flow": {
  "flow_mode": "pull"
}
```

**Experiment-specific override** (`config/experiments/expXX.json`):
```json
"overrides": {
  "material_flow": {
    "flow_mode": "push"
  }
}
```

Replace `"pull"` with `"push"` to enable push mode.

<br>

---

<br>

<!-- ================================================== -->
<!-- STOCHASTIC BEHAVIOR CONTROL -->
<!-- ================================================== -->
## 4. Stochastic Behavior Control

The simulation supports three behavior modes for controlling the randomness in the simulation. These modes affect all stochastic aspects including product arrivals and quantities, processing times, component conditions, equipment breakdowns (MTBF/MTTR), and transport times.

### 4.1 Seeded Mode

The seeded mode is the default behavior mode and produces reproducible results across various simulation runs. This mode uses the fixed random seeds defined in `default_config.json`, ensuring that the same configuration always produces the same output. The random number generators (RNG) are initialized with these fixed seeds. This mode is recommended for validation and comparison studies.

### 4.2 Deterministic Mode

The deterministic mode eliminates all randomness from the simulation. This mode always uses the mean or mode values instead of sampling from distributions. This mode is useful for debugging and understanding the baseline system behavior. It was also used for the initial validation of the simulation framework.

### 4.3 Random Mode

The random mode produces non-reproducible results where each simulation run generates different outputs. This mode uses system time-based random seeds, making it suitable for sensitivity analysis and exploring the range of possible outcomes.

The behavior mode is configured in the `default_config.json` file:

```json
"behavior_mode": "seeded"
```

Valid values are `"seeded"`, `"deterministic"`, or `"random"`.

<br>

---

<br>

<!-- ================================================== -->
<!-- RUNNING EXPERIMENTS -->
<!-- ================================================== -->
## 5. Running Experiments

This section describes how to run the experiments and how to create new experiment configurations.

### 5.1 Basic Commands

The following commands are available for running the experiments:

**List available experiments:**
```bash
python run_simulation.py list
```

**Run a single experiment:**
```bash
python run_simulation.py run --experiment exp01_baseline_workshop_pull
```

**Run multiple experiments:**
```bash
python run_simulation.py batch --experiments exp01 exp02 exp03
```

For additional command options, see the main [README.md](../README.md) file.

### 5.2 Creating New Experiments

To create a new experiment, follow these steps:

1. Create a new experiment JSON file in the `config/experiments/` directory.

2. Add the experiment entry to the `config/experiments/exp_index.json` file. This step is required for the experiment to be discovered by the `python run_simulation.py list` command.

3. Reference an existing system configuration or create a new one in the `config/system_config/` directory.

4. Reference the existing product configurations or create new ones in the `config/product_config/` directory.

5. Optionally, create a delivery schedule in the `config/delivery_schedules/` directory if the scheduled delivery mode is used.

6. Run the experiment using the following command: `python run_simulation.py run --experiment your_experiment_name`

**Modifying outputs:** Edit the `config/runtime_config.json` file to control which output files are generated.

**Changing default parameters:** Edit the `config/default_config.json` file to change the defaults that apply to all experiments, or use the `overrides` section in the experiment configuration to apply changes to a specific experiment only.

For detailed examples, refer to the existing configuration files in the `config/experiments/` directory (17 complete experiment examples), the `config/system_config/` directory (various factory layout examples), and the `config/product_config/` directory (product variant examples).

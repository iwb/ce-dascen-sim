# Parameter Reference

> **🔬 Research Software Notice**: This document is part of a research prototype (v2025-09) and serves as implementation guidance. Scientific references are included for contextual understanding and further reading only. The peer-reviewed scientific contribution can only be found in the published article.

This document provides a comprehensive reference for all 48 simulation parameters identified through a structured literature review.

For experiment configuration and system setup, see the [configuration_guide.md](configuration_guide.md) document. For implementation limitations and future extensions, see the [limitations.md](limitations.md) document.

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. Implementation Summary](#2-implementation-summary)
- [3. Product Parameters (PRD)](#3-product-parameters-prd)
- [4. Process Parameters (PRO)](#4-process-parameters-pro)
- [5. Resource and Control Parameters (RES)](#5-resource-and-control-parameters-res)

---

## 1. Introduction

The parameter set comprises **48 parameters** organized into three main categories. Table 1.1 provides an overview of the parameter categories and their respective table references.

**Table 1.1.** Parameter category overview

<table>
  <thead>
    <tr>
      <th>Category</th>
      <th>Abbreviation</th>
      <th>Count</th>
      <th>Description</th>
      <th>Reference</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Product parameters</td>
      <td>PRD</td>
      <td>13</td>
      <td>Define the products, variants, and components</td>
      <td>Table 2.1</td>
    </tr>
    <tr>
      <td>Process parameters</td>
      <td>PRO</td>
      <td>13</td>
      <td>Describe the disassembly processes and steps</td>
      <td>Table 3.1</td>
    </tr>
    <tr>
      <td>Resource and control parameters</td>
      <td>RES</td>
      <td>22</td>
      <td>Specify the factory structure, resources, and control logic</td>
      <td>Table 4.1</td>
    </tr>
  </tbody>
</table>

<br>

Each parameter is documented with the implementation status, the configuration file location, and the implementation details. The following legend describes the implementation status indicators used throughout this document:

- ✅ **Fully**: Complete functionality available
- 🔶 **Partial**: Basic functionality available, missing advanced features
- ⚠️ **Not**: Not currently supported

The parameter types are classified as follows:

- **Det.** = Deterministic parameter
- **Stoch.** = Stochastic parameter

---

## 2. Implementation Summary

The implementation status of the 48 parameters is summarized across the three main categories. Table 1.2 provides an overview of the implementation rates for each parameter category.

**Table 1.2.** Implementation status overview by parameter category

<table>
  <thead>
    <tr>
      <th>Category</th>
      <th>Total</th>
      <th>Fully</th>
      <th>Partial</th>
      <th>Not</th>
      <th>Rate</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Product parameters (PRD)</td>
      <td>13</td>
      <td>11</td>
      <td>1</td>
      <td>1</td>
      <td>85%</td>
    </tr>
    <tr>
      <td>Process parameters (PRO)</td>
      <td>13</td>
      <td>6</td>
      <td>4</td>
      <td>3</td>
      <td>46%</td>
    </tr>
    <tr>
      <td>Resource and control parameters (RES)</td>
      <td>22</td>
      <td>12</td>
      <td>6</td>
      <td>4</td>
      <td>55%</td>
    </tr>
    <tr>
      <td><strong>TOTAL</strong></td>
      <td><strong>48</strong></td>
      <td><strong>29</strong></td>
      <td><strong>11</strong></td>
      <td><strong>8</strong></td>
      <td><strong>60%</strong></td>
    </tr>
  </tbody>
</table>

<br>

---

## 3. Product Parameters (PRD)

Product parameters define the products to be disassembled, their structure, and the variability. This includes the product variants (types and characteristics), individual product instances (condition, missing components), and component-level attributes (names, damage, precedence). The framework models the products hierarchically with stochastic variation in quantities, conditions, and missing parts. Table 2.1 presents the complete list of all 13 product parameters along with their implementation status and configuration details.

**Table 2.1.** Product parameters (PRD) with implementation details

<table>
  <thead>
    <tr>
      <th>#</th>
      <th>Parameter</th>
      <th>Type</th>
      <th>Status</th>
      <th>Config Location</th>
      <th>Implementation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>Product variant name</td>
      <td>Det.</td>
      <td>✅</td>
      <td><code>product_config/*.json</code> → <code>type</code></td>
      <td>The variant name is read from the JSON file and assigned as a product attribute during instantiation.</td>
    </tr>
    <tr>
      <td>2</td>
      <td>Product quantity</td>
      <td>Stoch.</td>
      <td>✅</td>
      <td><code>product_config/*.json</code> → <code>volume_per_week_min/mu/max</code><br><code>experiments/*.json</code> → <code>overrides</code> (optional)<br><code>delivery_schedules/*.json</code> (scheduled mode)</td>
      <td>In random delivery mode, the generator uses a triangular distribution to stochastically determine the number of products created per week. In scheduled mode, arrivals are defined by a delivery schedule file, bypassing this parameter. Experiment-level overrides can replace the default values.</td>
    </tr>
    <tr>
      <td>3</td>
      <td>Lot size</td>
      <td>Stoch.</td>
      <td>✅</td>
      <td><code>product_config/*.json</code> → <code>lot_size</code></td>
      <td>The lot size is read from the JSON file and used by the generator to create product batches. In scheduled delivery mode, each delivery is defined individually, bypassing the lot size parameter.</td>
    </tr>
    <tr>
      <td>4</td>
      <td>Contained components</td>
      <td>Det.</td>
      <td>✅</td>
      <td><code>product_config/*.json</code> → <code>structure</code> hierarchy</td>
      <td>The hierarchical JSON structure is parsed and stored as a product attribute, including properties such as time, quantity, and <code>blocked_by</code>.</td>
    </tr>
    <tr>
      <td>5</td>
      <td>Component structure</td>
      <td>Det.</td>
      <td>✅</td>
      <td><code>product_config/*.json</code> → Nested tree</td>
      <td>Components are organized in groups. The <code>blocked_by</code> field specifies precedence constraints that are enforced by stations.</td>
    </tr>
    <tr>
      <td>6</td>
      <td>Components to disassemble</td>
      <td>Det.</td>
      <td>✅</td>
      <td><code>product_config/*.json</code> → <code>mandatory</code> field (mandatory disassembly)<br><code>product_config/*.json</code> → <code>condition_dev_*</code> + <code>system_config/*.json</code> → <code>min_condition</code> (target disassembly)</td>
      <td>Defines the disassembly scope per variant. Mandatory components (<code>mandatory=true</code>) are disassembled regardless of their condition. Target components are selected when the component condition ≥ the <code>min_condition</code> threshold. The processing priority is: Mandatory → Blocking → Eligible.</td>
    </tr>
    <tr>
      <td>7</td>
      <td>Product variant designation</td>
      <td>Stoch.</td>
      <td>✅</td>
      <td>Mapped via <code>variant.type</code></td>
      <td>Each product instance stores its variant type, which is used for routing and process selection.</td>
    </tr>
    <tr>
      <td>8</td>
      <td>Sensor data</td>
      <td>Stoch.</td>
      <td>⚠️</td>
      <td>Not implemented</td>
      <td>The product condition is currently modeled as a single scalar value (0–1). Sensor data is not explicitly modeled.</td>
    </tr>
    <tr>
      <td>9</td>
      <td>Known missing components</td>
      <td>Stoch.</td>
      <td>🔶</td>
      <td><code>product_config/*.json</code> → <code>prob_missing</code></td>
      <td>Components are stochastically removed from the product structure during creation, before the product enters the system, based on the <code>prob_missing</code> probability. The removed components are recorded in the case table alongside each product entry. Alternatively, known missing components can be modeled by omitting them from the product configuration. Removed components cannot be disassembled, which affects routing.</td>
    </tr>
    <tr>
      <td>10</td>
      <td>External product condition</td>
      <td>Stoch.</td>
      <td>✅</td>
      <td><code>product_config/*.json</code> → <code>condition_min/mu/max</code></td>
      <td>The product condition is sampled from a triangular distribution at creation. In scheduled delivery mode, the condition can be set explicitly per delivery entry. It influences the disassembly time via the <code>scale_disassembly_time</code> factor.</td>
    </tr>
    <tr>
      <td>11</td>
      <td>Component name</td>
      <td>Det.</td>
      <td>✅</td>
      <td><code>product_config/*.json</code> → Dictionary keys</td>
      <td>The component key in the JSON file serves as both the unique component name and the step name for disassembly.</td>
    </tr>
    <tr>
      <td>12</td>
      <td>Component damage degree</td>
      <td>Stoch.</td>
      <td>✅</td>
      <td><code>product_config/*.json</code> → <code>condition_dev_min/mu/max</code></td>
      <td>The component condition is calculated as the product condition plus a random deviation (triangular distribution), clamped to [0, 1]. It influences both the processing time and the execution decision.</td>
    </tr>
    <tr>
      <td>13</td>
      <td>Missing components</td>
      <td>Stoch.</td>
      <td>✅</td>
      <td><code>product_config/*.json</code> → <code>prob_missing</code></td>
      <td>Same mechanism as parameter 9. The <code>blocked_by</code> references are automatically cleaned when components are removed.</td>
    </tr>
  </tbody>
</table>

<br>

---

## 4. Process Parameters (PRO)

Process parameters describe how the disassembly is performed, including the overall process structure (number of steps, sequence) and the individual step characteristics (execution criteria, resource requirements, processing times). The framework derives the step count from the product structure and uses condition-based execution criteria with resource allocation. The processing times are influenced by the component condition through a linear scaling factor. Table 3.1 presents the complete list of all 13 process parameters along with their implementation status and configuration details.

**Table 3.1.** Process parameters (PRO) with implementation details

<table>
  <thead>
    <tr>
      <th>#</th>
      <th>Parameter</th>
      <th>Type</th>
      <th>Status</th>
      <th>Config Location</th>
      <th>Implementation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>14</td>
      <td>Name of the assigned variant to process</td>
      <td>Det.</td>
      <td>🔶</td>
      <td><code>system_config/*.json</code> → <code>stations.variants</code></td>
      <td>The <code>variant_routing</code> function in functions.py filters products by variant. Each station only processes products whose variant matches its configured variants list.</td>
    </tr>
    <tr>
      <td>15</td>
      <td>Number of disassembly steps</td>
      <td>Det.</td>
      <td>✅</td>
      <td>Derived from structure</td>
      <td>The number of steps equals the number of components and groups in the product structure. The total step count is determined at runtime.</td>
    </tr>
    <tr>
      <td>16</td>
      <td>Sequence of steps</td>
      <td>Det.</td>
      <td>✅</td>
      <td><code>system_config/*.json</code> → <code>stations.steps</code></td>
      <td>Stations process components in priority order: (1) mandatory, (2) blocking, and (3) eligible (condition ≥ threshold). The <code>blocked_by</code> field enforces precedence constraints between steps.</td>
    </tr>
    <tr>
      <td>17</td>
      <td>Further processing paths</td>
      <td>Det.</td>
      <td>⚠️</td>
      <td>Not implemented</td>
      <td>Currently, all components are routed to a single outgoing storage. There is no distinction between recycling, reuse, and disposal pathways.</td>
    </tr>
    <tr>
      <td>18</td>
      <td>Step type name</td>
      <td>Det.</td>
      <td>✅</td>
      <td>Implicit (step = component name)</td>
      <td>Each step is implicitly named after the component it removes.</td>
    </tr>
    <tr>
      <td>19</td>
      <td>Input component</td>
      <td>Det.</td>
      <td>✅</td>
      <td>Implied via <code>blocked_by</code></td>
      <td>The parent-child relationships in the product structure define which components serve as inputs to each step.</td>
    </tr>
    <tr>
      <td>20</td>
      <td>Output components</td>
      <td>Det.</td>
      <td>✅</td>
      <td>Generated after execution</td>
      <td>The station creates each extracted component as a separate entity. Components are logged and routed to the outgoing storage or the next station.</td>
    </tr>
    <tr>
      <td>21</td>
      <td>Required resources</td>
      <td>Det.</td>
      <td>✅</td>
      <td><code>system_config/*.json</code> → <code>equipment</code>/<code>employees</code></td>
      <td>Resources are requested before each step begins and held until completion. The system fully supports local and global resource pools with proper preemption handling.</td>
    </tr>
    <tr>
      <td>22</td>
      <td>Preparation time</td>
      <td>Stoch.</td>
      <td>🔶</td>
      <td><code>system_config/*.json</code> → <code>preparation_time</code></td>
      <td>Currently a fixed value per station. The preparation time is applied once when a product enters the station.</td>
    </tr>
    <tr>
      <td>23</td>
      <td>Processing time</td>
      <td>Stoch.</td>
      <td>🔶</td>
      <td><code>product_config/*.json</code> → <code>time</code></td>
      <td>The processing time is calculated as <code>time_ideal + (1 - condition) × (scale - 1) × time_ideal</code>. The product condition linearly influences the processing time.</td>
    </tr>
    <tr>
      <td>24</td>
      <td>Learning effects</td>
      <td>Stoch.</td>
      <td>⚠️</td>
      <td>Not implemented</td>
      <td>Not modeled</td>
    </tr>
    <tr>
      <td>25</td>
      <td>Damage probability</td>
      <td>Stoch.</td>
      <td>⚠️</td>
      <td>Not implemented</td>
      <td>Not modeled</td>
    </tr>
    <tr>
      <td>26</td>
      <td>Step execution criteria</td>
      <td>Det.</td>
      <td>🔶</td>
      <td><code>system_config/*.json</code> → <code>min_condition</code></td>
      <td>The only criterion is that the component condition must meet or exceed the <code>min_condition</code> threshold. Components below this threshold are skipped, unless they are mandatory or blocking.</td>
    </tr>
  </tbody>
</table>

<br>

---

## 5. Resource and Control Parameters (RES)

Resource and control parameters specify the physical disassembly system structure, including the spatial layout (transport matrix), the structural elements (stations, storage, vehicles with assigned resources and capabilities), the resource pools (employees and equipment with quantities, qualifications, and reliability characteristics), and the control logic (transport and processing order execution). The framework models the local and global resource pools, shift-based operation, equipment failures (MTBF/MTTR), and distance-based transportation. Table 4.1 presents the complete list of all 22 resource and control parameters along with their implementation status and configuration details.

**Table 4.1.** Resource and control parameters (RES) with implementation details

<table>
  <thead>
    <tr>
      <th>#</th>
      <th>Parameter</th>
      <th>Type</th>
      <th>Status</th>
      <th>Config Location</th>
      <th>Implementation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>27</td>
      <td>Product allocation to workstations</td>
      <td>Det.</td>
      <td>🔶</td>
      <td><code>system_config/*.json</code> → <code>stations.variants</code></td>
      <td>The <code>variant_routing</code> function provides the allocation logic. Products are routed to stations based on the configured variant lists.</td>
    </tr>
    <tr>
      <td>28</td>
      <td>Transport matrix</td>
      <td>Det.</td>
      <td>✅</td>
      <td><code>distance_matrix_system_XX.csv</code></td>
      <td>A CSV file defines a symmetric distance matrix in meters. Vehicles calculate their travel time as <code>distance / speed</code>.</td>
    </tr>
    <tr>
      <td>29</td>
      <td>Element name</td>
      <td>Det.</td>
      <td>✅</td>
      <td><code>system_config/*.json</code> → <code>id</code></td>
      <td>Each element has a unique identifier used for routing and logging.</td>
    </tr>
    <tr>
      <td>30</td>
      <td>Assigned employees</td>
      <td>Det.</td>
      <td>✅</td>
      <td><code>system_config/*.json</code> → <code>resources.employees</code></td>
      <td>Both local (station-specific) and global (factory-wide) employees are defined by type and quantity.</td>
    </tr>
    <tr>
      <td>31</td>
      <td>Assigned equipment</td>
      <td>Det.</td>
      <td>✅</td>
      <td><code>system_config/*.json</code> → <code>resources.equipment</code></td>
      <td>Both local and global equipment pools are defined by type and quantity. Equipment is subject to breakdowns modeled via MTBF/MTTR.</td>
    </tr>
    <tr>
      <td>32</td>
      <td>Assigned steps <sup>[1]</sup></td>
      <td>Det.</td>
      <td>✅</td>
      <td><code>system_config/*.json</code> → <code>stations.steps</code></td>
      <td>Each station defines the steps it can perform, along with the required resources and criteria.</td>
    </tr>
    <tr>
      <td>33</td>
      <td>Storage strategy <sup>[2]</sup></td>
      <td>Det.</td>
      <td>⚠️</td>
      <td>Not implemented</td>
      <td>The storage strategy is hard-coded: input buffer → main storage → output buffer. Vehicles pick up the first compatible product (FIFO).</td>
    </tr>
    <tr>
      <td>34</td>
      <td>Transport time <sup>[3]</sup></td>
      <td>Stoch.</td>
      <td>✅</td>
      <td><code>distance_matrix.csv</code> + <code>vehicles.speed</code></td>
      <td>The travel time is calculated as <code>distance / speed</code>. Each vehicle tracks its current location, and loading/unloading times are included.</td>
    </tr>
    <tr>
      <td>35</td>
      <td>Linked elements <sup>[3]</sup></td>
      <td>Det.</td>
      <td>✅</td>
      <td><code>system_config/*.json</code> → <code>predecessors</code></td>
      <td>Connections between elements are derived from the predecessor lists. Stations pull products from their predecessors, and vehicles handle the delivery.</td>
    </tr>
    <tr>
      <td>36</td>
      <td>Number of elements</td>
      <td>Det.</td>
      <td>✅</td>
      <td><code>system_config/*.json</code> → Arrays</td>
      <td>Each element is defined as a separate JSON object. The simulation creates an instance for each element and automatically adds incoming and outgoing storage.</td>
    </tr>
    <tr>
      <td>37</td>
      <td>Employee type name</td>
      <td>Det.</td>
      <td>✅</td>
      <td><code>system_config/*.json</code> → <code>employees[].type</code></td>
      <td>The employee type name is specified in the <code>stations.resources.employees[].type</code> field.</td>
    </tr>
    <tr>
      <td>38</td>
      <td>Number of employees per type</td>
      <td>Det.</td>
      <td>✅</td>
      <td><code>system_config/*.json</code> → <code>employees[].quantity</code></td>
      <td>The number of employees per type is specified in the <code>stations.resources.employees[].quantity</code> field.</td>
    </tr>
    <tr>
      <td>39</td>
      <td>Shift models</td>
      <td>Det.</td>
      <td>🔶</td>
      <td><code>system_config/*.json</code> → <code>start/end_of_day</code></td>
      <td>A single daily shift is defined with start and end times. Employees are unavailable outside working hours, and all stations close simultaneously.</td>
    </tr>
    <tr>
      <td>40</td>
      <td>Break time regulation</td>
      <td>Det.</td>
      <td>⚠️</td>
      <td>Only end-of-shift</td>
      <td>The system pauses between shifts but does not model breaks during shifts.</td>
    </tr>
    <tr>
      <td>41</td>
      <td>Employee qualification</td>
      <td>Det.</td>
      <td>🔶</td>
      <td>Implicit via employee types</td>
      <td>Qualification is modeled through different employee types. Each step requires a specific type, so only qualified employees can perform it.</td>
    </tr>
    <tr>
      <td>42</td>
      <td>Performance factor</td>
      <td>Det.</td>
      <td>⚠️</td>
      <td>Not implemented</td>
      <td>All employees of the same type perform identically. Individual performance factors are not modeled.</td>
    </tr>
    <tr>
      <td>43</td>
      <td>Equipment type name</td>
      <td>Det.</td>
      <td>✅</td>
      <td><code>system_config/*.json</code> → <code>equipment[].type</code></td>
      <td>The equipment type name is specified in the <code>stations.resources.equipment[].type</code> field.</td>
    </tr>
    <tr>
      <td>44</td>
      <td>Number of equipment per type</td>
      <td>Det.</td>
      <td>✅</td>
      <td><code>system_config/*.json</code> → <code>equipment[].quantity</code></td>
      <td>The number of equipment units per type is specified in the <code>stations.resources.equipment[].quantity</code> field.</td>
    </tr>
    <tr>
      <td>45</td>
      <td>Equipment capacity</td>
      <td>Det.</td>
      <td>⚠️</td>
      <td>Not implemented</td>
      <td>All equipment currently has a fixed capacity of 1.</td>
    </tr>
    <tr>
      <td>46</td>
      <td>Failure duration (MTTR)</td>
      <td>Stoch.</td>
      <td>🔶</td>
      <td><code>default_config.json</code> → <code>MTTR_mu/sigma</code></td>
      <td>The same MTTR parameters are applied to all equipment types. The repair time is sampled from a normal distribution (mu, sigma).</td>
    </tr>
    <tr>
      <td>47</td>
      <td>Failure interval (MTBF)</td>
      <td>Stoch.</td>
      <td>🔶</td>
      <td><code>default_config.json</code> → <code>MTBF_mu/sigma</code></td>
      <td>The same MTBF parameters are applied to all equipment types, following the same approach as parameter 46. Equipment blocks the station during repair.</td>
    </tr>
    <tr>
      <td>48</td>
      <td>Order execution logic <sup>[4]</sup></td>
      <td>Det.</td>
      <td>🔶</td>
      <td>Hard-coded FIFO / priority</td>
      <td>Transport orders follow a FIFO queue, and vehicles work sequentially. Processing orders use the priority: mandatory → blocking → eligible. There are no configurable scheduling rules.</td>
    </tr>
  </tbody>
</table>

<details>
<summary>Table notes</summary>

- [1] Only for workstations
- [2] Only for storages
- [3] Only for logistics
- [4] Includes transport order and processing order execution logic

</details>

<br>

For detailed limitations and extension opportunities, see the [limitations.md](limitations.md) document. For configuration examples, see the existing experiment files in the `config/experiments/` directory.

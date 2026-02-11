# Known Limitations and Future Work

> **🔬 Research Software Notice**: This document is part of a research prototype (v2025-09) and serves as implementation guidance. Scientific references are included for contextual understanding and further reading only. The peer-reviewed scientific contribution can only be found in the published article.

This document outlines the current implementation limitations, primarily from a code structure and maintainability perspective. For a detailed overview of the modeling assumptions and the scope boundaries relevant to the scientific contribution, please refer to the published article.

For more information about the parameter definitions and the implementation status, see the [parameter_reference.md](parameter_reference.md) document. For configuration details, see the [configuration_guide.md](configuration_guide.md) document.

## Table of Contents

- [1. Verified Functionality](#1-verified-functionality)
- [2. Code Implementation Limitations](#2-code-implementation-limitations)
- [3. Potential Extensions](#3-potential-extensions)

<br>

---

<br>

## 1. Verified Functionality

The key features of the simulation framework have been tested and verified through 17 experiments (11 verification + 6 validation). Table 1 presents an overview of the verified features organized by functional category. For additional information, please refer to the [experiments_overview.md](experiments_overview.md) document.

**Table 1.** Verified features and their functionality

<table>
  <thead>
    <tr>
      <th>#</th>
      <th>Feature</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td colspan="3"><strong>Material flow and routing</strong></td>
    </tr>
    <tr>
      <td>1</td>
      <td>Material flow control modes</td>
      <td>Supports both pull and push control strategies</td>
    </tr>
    <tr>
      <td>2</td>
      <td>Product variant routing</td>
      <td>Determines the dynamic paths based on the variant type</td>
    </tr>
    <tr>
      <td colspan="3"><strong>Quality control</strong></td>
    </tr>
    <tr>
      <td>3</td>
      <td>Quality-based component routing</td>
      <td>Routes the components using the configurable condition thresholds</td>
    </tr>
    <tr>
      <td>4</td>
      <td>Quality-based disassembly decisions</td>
      <td>Uses the configurable condition thresholds per component</td>
    </tr>
    <tr>
      <td>5</td>
      <td>Component condition sampling</td>
      <td>Samples the quality using the triangular distributions with component-specific deviations</td>
    </tr>
    <tr>
      <td>6</td>
      <td>Missing component probability</td>
      <td>Enables the stochastic removal based on the configurable probabilities</td>
    </tr>
    <tr>
      <td colspan="3"><strong>Product structure</strong></td>
    </tr>
    <tr>
      <td>7</td>
      <td>Hierarchical product structures</td>
      <td>Enforces the component blocking relationships</td>
    </tr>
    <tr>
      <td>8</td>
      <td>Component scanning mechanism</td>
      <td>Matches the workstation capabilities during the inspection</td>
    </tr>
    <tr>
      <td>9</td>
      <td>Mandatory component flags</td>
      <td>Enables the required disassembly regardless of the quality condition</td>
    </tr>
    <tr>
      <td>10</td>
      <td>Component blocking relationships</td>
      <td>Enforces the hierarchical disassembly dependencies</td>
    </tr>
    <tr>
      <td>11</td>
      <td>Missing component detection</td>
      <td>Detects the missing components during the inspection with automatic removal from the processing queue and event logging</td>
    </tr>
    <tr>
      <td>12</td>
      <td>Component quantity handling</td>
      <td>Handles the multiple instances with unique identification</td>
    </tr>
    <tr>
      <td colspan="3"><strong>Stochastic modeling</strong></td>
    </tr>
    <tr>
      <td>13</td>
      <td>Stochastic processing times</td>
      <td>Incorporates the condition-influenced variations and mode-specific behavior (deterministic vs seeded)</td>
    </tr>
    <tr>
      <td>14</td>
      <td>Equipment breakdowns</td>
      <td>Models the failures using MTBF/MTTR distributions with maintenance resource allocation and interruption handling</td>
    </tr>
    <tr>
      <td colspan="3"><strong>Resource and schedule management</strong></td>
    </tr>
    <tr>
      <td>15</td>
      <td>Workstation opening and closing hours</td>
      <td>Manages the workstation availability with automated shift scheduling</td>
    </tr>
    <tr>
      <td>16</td>
      <td>Hybrid resource allocation</td>
      <td>Combines the local workstation resources and the global shared pools for employees and equipment</td>
    </tr>
    <tr>
      <td colspan="3"><strong>System architecture</strong></td>
    </tr>
    <tr>
      <td>17</td>
      <td>Three-zone storage architecture</td>
      <td>Consists of an entry buffer, a main storage area, and dual exit buffers</td>
    </tr>
    <tr>
      <td>18</td>
      <td>Workstation state machine</td>
      <td>Tracks the five operational states (IDLE, BUSY, BLOCKED, FAILED, CLOSED) with time accounting</td>
    </tr>
    <tr>
      <td>19</td>
      <td>Distance-based vehicle transportation</td>
      <td>Models the vehicle movement with speed variations and capacity constraints</td>
    </tr>
    <tr>
      <td colspan="3"><strong>Output and validation</strong></td>
    </tr>
    <tr>
      <td>20</td>
      <td>Process mining compatible event logs</td>
      <td>Captures the detailed state transitions and component tracking</td>
    </tr>
    <tr>
      <td>21</td>
      <td>Real-world validation</td>
      <td>Validated against the Smart Production Lab data achieving a 100% completion rate across 6 scenarios</td>
    </tr>
  </tbody>
</table>

<br>

---

<br>

## 2. Code Implementation Limitations

This section outlines the current implementation limitations from a code structure and maintainability perspective. Table 2 presents an overview of the identified limitations along with potential recommendations for future enhancements.

**Table 2.** Code implementation limitations and recommendations
<table>
  <thead>
    <tr>
      <th>#</th>
      <th>Limitation</th>
      <th>Recommendation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td colspan="3"><strong><em>File Organization</em></strong></td>
    </tr>
    <tr>
      <td>1</td>
      <td>The core utility files (functions.py, helper_functions.py, config_manager.py) are located in the project root instead of the src/ folder</td>
      <td>Move these files to the src/ directory or a dedicated modules folder to improve the project structure and package organization</td>
    </tr>
    <tr>
      <td>2</td>
      <td>The main execution script (run_simulation.py) is in the root directory</td>
      <td>Move to a scripts/ folder to clearly separate the user-executable code from the library code</td>
    </tr>
    <tr>
      <td>3</td>
      <td>The output folder is at the top level</td>
      <td>Consider making it a subfolder of the scripts/ directory to indicate it contains user-generated data</td>
    </tr>
    <tr>
      <td colspan="3"><strong><em>Module Size and Function Organization</em></strong></td>
    </tr>
    <tr>
      <td>4</td>
      <td>The helper_functions.py file contains 33 functions across 1,285 lines</td>
      <td>Split into multiple focused modules (e.g., structure_helpers.py, time_helpers.py, logging_helpers.py) for improved maintainability</td>
    </tr>
    <tr>
      <td>5</td>
      <td>Large module files exist throughout the codebase (station.py: 1,679 lines, logging.py: 1,663 lines, functions.py: 1,034 lines)</td>
      <td>Refactor the large modules into smaller components.</td>
    </tr>
    <tr>
      <td>6</td>
      <td>The helper functions in the utility modules are not prefixed with an underscore to indicate internal use</td>
      <td>Prepend the private/internal functions with <code>_</code> to clarify the intended internal use</td>
    </tr>
    <tr>
      <td colspan="3"><strong><em>Class Naming Conventions</em></strong></td>
    </tr>
    <tr>
      <td>7</td>
      <td>The core entity classes in src/product.py (product, component, group) use lowercase names instead of PascalCase</td>
      <td>Rename to Product, Component, and Group for consistency with naming standards</td>
    </tr>
    <tr>
      <td colspan="3"><strong><em>Global State Management</em></strong></td>
    </tr>
    <tr>
      <td>8</td>
      <td>The SimulationConfig class in src/g.py acts as a global configuration object creating implicit dependencies</td>
      <td>Refactor to use dependency injection or context managers to reduce the global state coupling</td>
    </tr>
    <tr>
      <td>9</td>
      <td>Global variables exist in helper_functions.py (_debug_file, _object_registry) for debug logging and object tracking</td>
      <td>Encapsulate in the configuration or context objects for better state management</td>
    </tr>
    <tr>
      <td colspan="3"><strong><em>Error Handling</em></strong></td>
    </tr>
    <tr>
      <td>10</td>
      <td>Limited exception handling throughout the codebase</td>
      <td>Add comprehensive exception handling to improve error visibility and debugging capabilities</td>
    </tr>
    <tr>
      <td>11</td>
      <td>Many functions may fail silently or return the original inputs when errors occur</td>
      <td>Implement explicit exception raising to make the errors visible rather than silent failures</td>
    </tr>
    <tr>
      <td>12</td>
      <td>No consistent error handling strategy or custom exception hierarchy exists for simulation-specific errors</td>
      <td>Create a custom exception hierarchy for better error categorization</td>
    </tr>
    <tr>
      <td colspan="3"><strong><em>Logging and Output</em></strong></td>
    </tr>
    <tr>
      <td>13</td>
      <td>Extensive use of print() statements for the output rather than the standard logging module</td>
      <td>Replace the print() statements with a logging module for better control</td>
    </tr>
    <tr>
      <td>14</td>
      <td>A custom debug_print() function exists in helper_functions.py, but the usage is mixed with standard print() calls</td>
      <td>Standardize on a single logging approach</td>
    </tr>
    <tr>
      <td colspan="3"><strong><em>Documentation</em></strong></td>
    </tr>
    <tr>
      <td>15</td>
      <td>Function docstrings are present, but consistency across all modules has not been verified</td>
      <td>Conduct a comprehensive review to ensure all functions have consistent, complete docstrings</td>
    </tr>
  </tbody>
</table>

<br>

---

<br>

## 3. Potential Extensions

This section presents various extensions that could enhance the simulation capabilities in future iterations. Table 3 outlines the potential enhancements along with their intended benefits for the framework.

**Table 3.** Potential extensions and their intended benefits

<table>
  <thead>
    <tr>
      <th>#</th>
      <th>Extension</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>1</td>
      <td>Enhanced routing</td>
      <td>Enable the dynamic re-routing of products to alternative workstations based on real-time machine availability and quality test results to reduce the blocking times and improve the system throughput</td>
    </tr>
    <tr>
      <td>2</td>
      <td>Advanced scheduling</td>
      <td>Implement configurable dispatch rules (e.g., EDD, SPT, CR) and sequencing logic to optimize the workstation utilization and prioritize products based on due dates or processing times</td>
    </tr>
    <tr>
      <td>3</td>
      <td>Complex quality</td>
      <td>Support multi-dimensional quality attributes (e.g., structural integrity, functional tests, visual inspection) integrated with real-time sensor data for more accurate disassembly decisions</td>
    </tr>
    <tr>
      <td>4</td>
      <td>Learning curves</td>
      <td>Model the worker learning curves where the processing times decrease as workers gain experience with specific tasks or product variants over time</td>
    </tr>
    <tr>
      <td>5</td>
      <td>Cost optimization</td>
      <td>Implement the non-linear cost models (e.g., economies of scale, setup costs) and economic dispatch logic to optimize the resource allocation based on profitability</td>
    </tr>
    <tr>
      <td>6</td>
      <td>Multiple pathways</td>
      <td>Support multiple end-of-life pathways where the components can be routed to reuse, recycling, refurbishment, or disposal facilities based on the condition and market value</td>
    </tr>
    <tr>
      <td>7</td>
      <td>Batch processing</td>
      <td>Model the batch processing workstations where multiple components can be processed simultaneously with batch-dependent setup times and capacity constraints</td>
    </tr>
    <tr>
      <td>8</td>
      <td>Inspection stations</td>
      <td>Add dedicated inspection workstations that perform pre-disassembly diagnostics to detect the missing components and assess the condition before routing to the appropriate disassembly paths</td>
    </tr>
  </tbody>
</table>

<br>
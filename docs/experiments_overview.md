# Experiments Overview

> **🔬 Research Software Notice**: This document is part of a research prototype (2025-09) and serves as implementation guidance. Scientific references are included for contextual understanding and further reading only. The peer-reviewed scientific contribution can only be found in the published article.

This document provides an overview of the 17 experiments included in the disassembly simulation framework. The experiments were divided into two categories: verification experiments, which tested framework features; and validation experiments, which compared simulation results against real-world data.


## Table of Contents

- [1. Verification Experiments (exp01-11)](#1-verification-experiments-exp01-11)
- [2. Validation Experiments (exp12-17)](#2-validation-experiments-exp12-17)
- [3. Detailed Results - Lead Times](#3-detailed-results---lead-times)
- [4. Detailed Results - Station Statistics](#4-detailed-results---station-statistics)
- [5. Detailed Results - Component Counts](#5-detailed-results---component-counts)

<br>

---

<br>

<!-- ================================================== -->
<!-- VERIFICATION EXPERIMENTS -->
<!-- ================================================== -->
## 1. Verification Experiments (exp01-11)

To assess the individual capabilities of the framework, multiple verification experiments were conducted. The correct implementation was verified through a thorough review of the output files, with a focus on the detailed event logs that record all system state transitions and decisions. Table 1.1 provides a summary overview of the evaluated features and the scope of their implementation across the verification experiments.

<br>

**Table 1.1.** Feature coverage in verification experiments

<table>
  <thead>
    <tr>
      <th>Feature</th>
      <th>Description</th>
      <th>Exp ID</th>
      <th>Coverage</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Material flow control</td>
      <td>Push and pull strategies</td>
      <td>exp01-11</td>
      <td>Pull mode was tested in exp01 and exp03-11, while push mode was tested in exp02.</td>
    </tr>
    <tr>
      <td>System layouts</td>
      <td>Workshop, linear, parallel, and split-flow configurations</td>
      <td>exp01-11</td>
      <td>The experiments covered workshop layouts (exp01, exp02, exp05, exp06, exp10, exp11), linear layouts (exp03, exp04, exp08), parallel stations (exp03, exp04, exp05), and split-flow configurations (exp09).</td>
    </tr>
    <tr>
      <td>Stochastic modeling</td>
      <td>Equipment failures and variable processing times</td>
      <td>exp07</td>
      <td>Equipment breakdowns using MTBF/MTTR modeling were tested in exp07.</td>
    </tr>
    <tr>
      <td>Quality-based routing</td>
      <td>Quality-based routing logic and condition-based decisions</td>
      <td>exp01, exp06, exp09, exp10, exp11</td>
      <td>No quality restrictions (exp10), mixed quality (exp01), strict thresholds (exp11), quality-varied scenarios (exp06), and quality-based routing paths (exp09) were all tested.</td>
    </tr>
    <tr>
      <td>Delivery patterns</td>
      <td>Random and scheduled delivery</td>
      <td>exp05, exp06</td>
      <td>Random delivery was used in most experiments, while scheduled delivery was tested in exp05 and exp06.</td>
    </tr>
    <tr>
      <td>Workload levels</td>
      <td>Baseline and high volume scenarios</td>
      <td>exp04, exp07</td>
      <td>Baseline workload and high volume scenarios were tested in exp04 and exp07.</td>
    </tr>
  </tbody>
</table>

<br>

These features were evaluated across 11 verification experiments (exp01-11), the details of which can be found in Table 1.2. All verification tests confirmed the correct implementation of the functionalities.

<br>

**Table 1.2.** Verification experiments (exp01-11)

<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>Name</th>
      <th>System Layout</th>
      <th>Material Flow</th>
      <th>Duration</th>
      <th>Features Tested</th>
      <th>Config File</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>exp01</strong></td>
      <td>Baseline pull mixed</td>
      <td>Workshop (1 station)</td>
      <td>Pull</td>
      <td>2 weeks</td>
      <td>Baseline pull mode, quality-based routing, 3 variants</td>
      <td><code>exp01_baseline_workshop_pull.json</code></td>
    </tr>
    <tr>
      <td><strong>exp02</strong></td>
      <td>Workshop push</td>
      <td>Workshop (1 station)</td>
      <td>Push</td>
      <td>2 weeks</td>
      <td>Push mode vs pull mode comparison, single variant</td>
      <td><code>exp02_workshop_push_comparison.json</code></td>
    </tr>
    <tr>
      <td><strong>exp03</strong></td>
      <td>Linear storage</td>
      <td>Linear (4 stations)</td>
      <td>Pull</td>
      <td>2 weeks</td>
      <td>Linear layout, parallel stations, storage buffers</td>
      <td><code>exp03_linear_flow_storage.json</code></td>
    </tr>
    <tr>
      <td><strong>exp04</strong></td>
      <td>Parallel balance</td>
      <td>Linear (4 stations)</td>
      <td>Pull</td>
      <td>2 weeks</td>
      <td>High volume, load balancing, parallel processing</td>
      <td><code>exp04_parallel_stations_balancing.json</code></td>
    </tr>
    <tr>
      <td><strong>exp05</strong></td>
      <td>Scheduled baseline</td>
      <td>Workshop (2 parallel)</td>
      <td>Pull</td>
      <td>2 weeks</td>
      <td>Deterministic delivery schedule, predictable arrivals</td>
      <td><code>exp05_scheduled_delivery_deterministic.json</code></td>
    </tr>
    <tr>
      <td><strong>exp06</strong></td>
      <td>Scheduled quality</td>
      <td>Workshop (1 station)</td>
      <td>Pull</td>
      <td>2 weeks</td>
      <td>Quality-varied schedule, missing components</td>
      <td><code>exp06_quality_and_missing.json</code></td>
    </tr>
    <tr>
      <td><strong>exp07</strong></td>
      <td>Breakdown stress</td>
      <td>Linear (4 stations)</td>
      <td>Pull</td>
      <td>2 weeks</td>
      <td>Equipment failures (MTBF/MTTR), high volume</td>
      <td><code>exp07_stress_test_breakdowns.json</code></td>
    </tr>
    <tr>
      <td><strong>exp08</strong></td>
      <td>Linear simple</td>
      <td>Linear (3 stations)</td>
      <td>Pull</td>
      <td>2 weeks</td>
      <td>Single-station capacity comparison vs exp03</td>
      <td><code>exp08_linear_simple.json</code></td>
    </tr>
    <tr>
      <td><strong>exp09</strong></td>
      <td>Split flow</td>
      <td>Split-flow (5 stations)</td>
      <td>Pull</td>
      <td>2 weeks</td>
      <td>Split-flow layout, quality-based routing paths</td>
      <td><code>exp09_split_flow.json</code></td>
    </tr>
    <tr>
      <td><strong>exp10</strong></td>
      <td>Baseline pull no qual</td>
      <td>Workshop (1 station)</td>
      <td>Pull</td>
      <td>2 weeks</td>
      <td>Complete disassembly, no quality thresholds</td>
      <td><code>exp10_baseline_workshop_pull_no_quality.json</code></td>
    </tr>
    <tr>
      <td><strong>exp11</strong></td>
      <td>Baseline pull strict</td>
      <td>Workshop (1 station)</td>
      <td>Pull</td>
      <td>2 weeks</td>
      <td>Highly selective disassembly, strict thresholds</td>
      <td><code>exp11_baseline_workshop_pull_strict_quality.json</code></td>
    </tr>
  </tbody>
</table>

<br>

The verification experiments confirmed the successful implementation of the core functionalities. For a detailed discussion of the identified limitations and constraints, please refer to [limitations.md](limitations.md).

<br>

---

<br>

<!-- ================================================== -->
<!-- VALIDATION EXPERIMENTS -->
<!-- ================================================== -->
## 2. Validation Experiments (exp12-17)

To validate the framework against real-world data, six validation experiments were conducted using experimental data collected in the Smart Production Lab (SPL) at the Institute for Machine Tools and Industrial Management (*iwb*) at the Technical University of Munich (https://iwb-spl.de/). The configurations are based on remotely controlled (RC) cars with measured disassembly times and various real system layouts, as well as actual delivery schedules. The RC cars are classified into four quality types: Hail Damage (HD), Rear Damage (RD), Shock Absorber Damage (SA), and Total Loss (TL) represent varying degrees of required disassembly. The experiments tested two automation levels: manual disassembly and automated disassembly, with operators receiving assistance from tools. Each validation scenario was executed for 40 simulated hours (0.238 weeks ≈ 2400 minutes) with a continuous operation to match the 40-minute real experiments. A 60x time scaling factor was applied, representing real-world seconds as simulation minutes, enabling the direct comparison between the simulated and collected datasets. All scenarios were executed in deterministic mode with push material flow to reflect the conducted experiment setup in the SPL. The actual experiments did not experience any machine downtime, although various process variations (e.g., difficulty removing components) did occur. These variations are reflected in the measured fluctuations in process time.

For detailed information about the validation data, system layouts, process times, and real-world results, please refer to the associated repository, available at: [ce-dascen-lf-dataset](https://github.com/iwb/ce-dascen-lf-data)

<br>

**Table 2.1.** Validation experiments overview (exp12-17)

<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>Name</th>
      <th>System Layout</th>
      <th>Products</th>
      <th>Automation</th>
      <th>Config File</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>exp12</strong></td>
      <td>Scenario 01 validation</td>
      <td>3 stations (line)</td>
      <td>10 RC cars (mixed: 6RD/2TL/2SA)</td>
      <td>Manual</td>
      <td><code>exp12_scenario_01.json</code></td>
    </tr>
    <tr>
      <td><strong>exp13</strong></td>
      <td>Scenario 02 validation</td>
      <td>4 stations (parallel)</td>
      <td>10 RC cars (HD only)</td>
      <td>Automated</td>
      <td><code>exp13_scenario_02.json</code></td>
    </tr>
    <tr>
      <td><strong>exp14</strong></td>
      <td>Scenario 03 validation</td>
      <td>5 stations (line)</td>
      <td>10 RC cars (HD only)</td>
      <td>Automated</td>
      <td><code>exp14_scenario_03.json</code></td>
    </tr>
    <tr>
      <td><strong>exp14s</strong></td>
      <td>Scenario 03 sensitivity</td>
      <td>5 stations (line)</td>
      <td>10 RC cars (HD only)</td>
      <td>Automated</td>
      <td><code>exp14_scenario_03_sensitivity.json</code></td>
    </tr>
    <tr>
      <td><strong>exp15</strong></td>
      <td>Scenario 04 validation</td>
      <td>5 stations (workshop + buffer)</td>
      <td>10 RC cars (HD only)</td>
      <td>Manual</td>
      <td><code>exp15_scenario_04.json</code></td>
    </tr>
    <tr>
      <td><strong>exp16</strong></td>
      <td>Scenario 05 validation</td>
      <td>5 stations (workshop)</td>
      <td>10 RC cars (mixed: 6HD/1TL/1SA/2RD)</td>
      <td>Automated</td>
      <td><code>exp16_scenario_05.json</code></td>
    </tr>
    <tr>
      <td><strong>exp17</strong></td>
      <td>Scenario 06 validation</td>
      <td>5 stations (line)</td>
      <td>10 RC cars (mixed: 3HD/3SA/3RD/1TL)</td>
      <td>Manual</td>
      <td><code>exp17_scenario_06.json</code></td>
    </tr>
    <tr>
      <td><strong>exp17s</strong></td>
      <td>Scenario 06 sensitivity</td>
      <td>5 stations (line)</td>
      <td>10 RC cars (mixed: 3HD/3SA/3RD/1TL)</td>
      <td>Manual</td>
      <td><code>exp17_scenario_06_sensitivity.json</code></td>
    </tr>
  </tbody>
</table>

<br>

---

<br>

The validation results across these eight experiments are summarized in Table 2.2. All scenarios except Scenario 03 (baseline) passed the ±20% validation threshold.

**Table 2.2.** Summary of validation deviations across all scenarios

<table>
  <thead>
    <tr>
      <th>Metric</th>
      <th>Sc.01</th>
      <th>Sc.02</th>
      <th>Sc.03</th>
      <th>Sc.03 [s]</th>
      <th>Sc.04</th>
      <th>Sc.05</th>
      <th>Sc.06</th>
      <th>Sc.06 [s]</th>
      <th>Details</th>
    </tr>
  </thead>
  <tbody>
  <tr>
      <td>Experiment ID</td>
      <td>exp12</td>
      <td>exp13</td>
      <td>exp14</td>
      <td>exp14s</td>
      <td>exp15</td>
      <td>exp16</td>
      <td>exp17</td>
      <td>exp17s</td>
      <td></td>
    </tr>
    <tr>
      <td>Lead time deviation<sup>[1]</sup></td>
      <td>-0.3%</td>
      <td>+3.1%</td>
      <td>-28.0%</td>
      <td>-6.6%</td>
      <td>+4.6%</td>
      <td>+11.2%</td>
      <td>+11.5%</td>
      <td>+1.5%</td>
      <td>Tables 3.1–3.6</td>
    </tr>
    <tr>
      <td>Utilization deviation<sup>[2]</sup></td>
      <td>+2.2 pp</td>
      <td>+3.5 pp</td>
      <td>+4.2 pp</td>
      <td>+1.8 pp</td>
      <td>+7.6 pp</td>
      <td>-3.7 pp</td>
      <td>-5.7 pp</td>
      <td>-2.1 pp</td>
      <td>Tables 4.1–4.6</td>
    </tr>
    <tr>
      <td>Component count deviation<sup>[3]</sup></td>
      <td>-4.2%</td>
      <td>-3.6%</td>
      <td>0.0%</td>
      <td>-17.8%</td>
      <td>-2.9%</td>
      <td>0.0%</td>
      <td>-12.6%</td>
      <td>-2.3%</td>
      <td>Tables 5.1a–5.6a</td>
    </tr>
    <tr>
      <td>Assessment<sup>[4]</sup></td>
      <td>Pass</td>
      <td>Pass</td>
      <td>Fail</td>
      <td>Pass</td>
      <td>Pass</td>
      <td>Pass</td>
      <td>Pass</td>
      <td>Pass</td>
      <td>-</td>
    </tr>
  </tbody>
</table>

<details>
<summary>Table notes</summary>

- All deviations compare system-level averages or totals, not the mean of the individual per-PO or per-station deviations.
- [1] Lead time deviation: (Simulated avg - Real avg) / Real avg × 100%. The averages include only POs that were completed in both the simulation and the real experiment.
- [2] Utilization deviation: Simulated avg - Real avg, in percentage points (pp). The averages include all workstations.
- [3] Component count deviation: (Simulated - Real) / Real × 100%, based on the total number of target components.
- [4] Assessment: Pass = lead time and component count deviations within ±20% and utilization deviation within ±20 pp.

</details>

<br>

**Conclusion**

The six validation scenarios demonstrated the validity of the framework, with five of the six scenarios passing a ±20% validation threshold. Two scenarios required sensitivity adjustments: Scenario 03 was calibrated using a queue delay adjustment to account for the high process variability (CV = 79.4%), improving the deviation from -28.0% to -6.6%. Scenario 06 was recalibrated with reduced processing times to investigate a bottleneck behavior.

For more insights into the validation results, please refer to the associated scientific article.

<br>

---

<br>

<!-- ================================================== -->
<!-- DETAILED RESULTS - LEAD TIMES -->
<!-- ================================================== -->
## 3. Detailed Results - Lead Times

This section presents the detailed product-level lead time data from each validation scenario. Simulated times are given in **simulation minutes**, factory times in **seconds** (1 sim minute = 1 real second due to 60x scaling).

The following tables show the data for each production order (PO, identified by caseID), including the product quality type (RD = Rear Damage, HD = Hail Damage, SA = Shock Absorber, TL = Total Loss), the delivery time when the product entered the system, and the exit time when the disassembly was completed. The lead time represents the total time in the system (Exit - Delivery). The lead time deviation indicates the percentage difference between the simulated and actual measurements, calculated as (Simulated - Real) / Real &middot; 100%.

Only POs that were completed in both the simulation and the real experiment are included in the averages. POs that were not finished are marked as DNF (did not finish): DNF (sim) if the PO was not completed in the simulation, DNF (factory) if it was not completed in the real experiment, and DNF (sim + factory) if it was completed in neither. The average deviation is calculated from the average lead times, (Simulated avg - Real avg) / Real avg &middot; 100%, and not as the mean of the per-PO deviations.

> **⚠️ Note**
> The value-creating time (VT) represents the deterministic disassembly processing time and remains consistent for completed products of the same type and scenario. The non-value creating time (NCT) captures blocking and waiting times due to downstream congestion and varies based on the system state. Products arriving later in the experiment typically experience a higher NCT as workstations become congested.

<br>

---

<br>

Scenario 01 (exp12) achieved an average lead time deviation of -0.3%, demonstrating an alignment with the real-world data for the 3-workstation line layout processing mixed product types (6RD/2TL/2SA). The individual PO deviations ranged from -17.0% to +14.9%. The NCT ranged from 90 to 745 minutes, reflecting the system congestion of later products. The average NCT of 387 minutes indicates a moderate congestion in the system. PO 10 was not completed in the simulation and is therefore excluded from the average (see Table 3.1).

<details>
<summary><strong>Table 3.1.</strong> Lead times (scenario 01, exp12)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">PO</th>
      <th rowspan="2">Type</th>
      <th rowspan="2">Delivery (min)</th>
      <th colspan="4">Simulated data</th>
      <th colspan="2">Factory data</th>
      <th rowspan="2">Lead time Dev.</th>
    </tr>
    <tr>
      <th>Exit</th>
      <th>VT</th>
      <th>NCT</th>
      <th>Lead time</th>
      <th>Handling time</th>
      <th>Lead time</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>1</td><td>RD</td><td>0.0</td><td>571.5</td><td>445.1</td><td>90.2</td><td>571.5</td><td>629</td><td>586</td><td>-2.5%</td></tr>
    <tr><td>2</td><td>RD</td><td>120.0</td><td>753.1</td><td>445.1</td><td>145.1</td><td>633.1</td><td>482</td><td>721</td><td>-12.2%</td></tr>
    <tr><td>3</td><td>RD</td><td>240.0</td><td>901.5</td><td>445.1</td><td>178.3</td><td>661.5</td><td>360</td><td>721</td><td>-8.2%</td></tr>
    <tr><td>4</td><td>TL</td><td>360.0</td><td>961.5</td><td>374.1</td><td>189.5</td><td>601.5</td><td>402</td><td>530</td><td>+13.5%</td></tr>
    <tr><td>5</td><td>SA</td><td>540.0</td><td>1444.9</td><td>444.1</td><td>418.8</td><td>904.9</td><td>555</td><td>976</td><td>-7.3%</td></tr>
    <tr><td>6</td><td>RD</td><td>600.0</td><td>1621.5</td><td>445.1</td><td>533.9</td><td>1021.5</td><td>480</td><td>1231</td><td>-17.0%</td></tr>
    <tr><td>7</td><td>RD</td><td>720.0</td><td>1801.5</td><td>445.1</td><td>595.4</td><td>1081.5</td><td>383</td><td>941</td><td>+14.9%</td></tr>
    <tr><td>8</td><td>TL</td><td>870.0</td><td>1860.9</td><td>374.1</td><td>581.4</td><td>990.9</td><td>403</td><td>931</td><td>+6.4%</td></tr>
    <tr><td>9</td><td>RD</td><td>1110.0</td><td>2341.5</td><td>445.1</td><td>745.4</td><td>1231.5</td><td>285</td><td>1082</td><td>+13.8%</td></tr>
    <tr><td>10</td><td>SA</td><td>1800.0</td><td>2371.5</td><td>236.0</td><td>296.9</td><td>571.5</td><td>330</td><td>616</td><td>DNF (sim)</td></tr>
    <tr><td><strong>Avg (1-9)</strong></td><td>-</td><td>-</td><td>-</td><td><strong>429.2</strong></td><td><strong>386.5</strong></td><td><strong>855.3</strong></td><td><strong>442.1</strong></td><td><strong>857.7</strong></td><td><strong>-0.3%</strong></td></tr>
  </tbody>
</table>

**Note:** PO 10 was not finished in the simulation (DNF (sim)). Only POs completed in both the simulation and the real experiment are included in the average.

</details>

<br>

Scenario 02 (exp13) achieved an average lead time deviation of +3.1% in the 4-workstation workshop layout. The NCT increased significantly for POs 5-7 (855-885 min vs 43-49 min for POs 1-4) due to severe blocking, demonstrating the ability of the model to capture congestion dynamics in high-utilization scenarios. <br>
**Note:** POs 9 and 10 were completed neither in the simulation nor in the real experiment, and PO 8 was not completed in the simulation. The lead time comparison in Table 3.2 is therefore based on POs 1-7.

<details>
<summary><strong>Table 3.2.</strong> Lead times (scenario 02, exp13)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">PO</th>
      <th rowspan="2">Type</th>
      <th rowspan="2">Delivery (min)</th>
      <th colspan="4">Simulated data</th>
      <th colspan="2">Factory data</th>
      <th rowspan="2">Lead time Dev.</th>
    </tr>
    <tr>
      <th>Exit</th>
      <th>VT</th>
      <th>NCT</th>
      <th>Lead time</th>
      <th>Handling time</th>
      <th>Lead time</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>1</td><td>HD</td><td>0.0</td><td>1171.5</td><td>1089.3</td><td>49.4</td><td>1171.5</td><td>1155</td><td>1231</td><td>-4.8%</td></tr>
    <tr><td>2</td><td>HD</td><td>60.0</td><td>1233.1</td><td>1089.3</td><td>46.1</td><td>1173.1</td><td>1325</td><td>1051</td><td>+11.6%</td></tr>
    <tr><td>3</td><td>HD</td><td>120.0</td><td>1293.1</td><td>1089.3</td><td>44.5</td><td>1173.1</td><td>1140</td><td>1171</td><td>+0.2%</td></tr>
    <tr><td>4</td><td>HD</td><td>180.0</td><td>1353.1</td><td>1089.3</td><td>43.0</td><td>1173.1</td><td>959</td><td>1006</td><td>+16.6%</td></tr>
    <tr><td>5</td><td>HD</td><td>240.0</td><td>2251.5</td><td>1089.3</td><td>884.6</td><td>2011.5</td><td>943</td><td>1877</td><td>+7.2%</td></tr>
    <tr><td>6</td><td>HD</td><td>300.0</td><td>2311.5</td><td>1089.3</td><td>883.9</td><td>2011.5</td><td>1125</td><td>2041</td><td>-1.4%</td></tr>
    <tr><td>7</td><td>HD</td><td>390.0</td><td>2371.5</td><td>1089.3</td><td>854.6</td><td>1981.5</td><td>1200</td><td>1997</td><td>-0.8%</td></tr>
    <tr><td>8</td><td>HD</td><td>435.0</td><td>2346.1</td><td>1008.7</td><td>872.3</td><td>1911.1</td><td>930</td><td>1786</td><td>DNF (sim)</td></tr>
    <tr><td>9</td><td>HD</td><td>480.0</td><td>2341.5</td><td>97.0</td><td>1725.4</td><td>1861.5</td><td>149</td><td>-</td><td>DNF (sim + factory)</td></tr>
    <tr><td>10</td><td>HD</td><td>540.0</td><td>2343.1</td><td>97.0</td><td>1699.3</td><td>1803.1</td><td>165</td><td>-</td><td>DNF (sim + factory)</td></tr>
    <tr><td><strong>Avg (1-7)</strong></td><td>-</td><td>-</td><td>-</td><td><strong>1089.3</strong></td><td><strong>400.9</strong></td><td><strong>1527.9</strong></td><td><strong>1121.0</strong></td><td><strong>1482.0</strong></td><td><strong>+3.1%</strong></td></tr>
  </tbody>
</table>

**Note:** PO 8 was not finished in the simulation (DNF (sim)); POs 9-10 were not finished in the simulation and in the real experiment (DNF (sim + factory)). Only POs completed in both the simulation and the real experiment are included in the average.

</details>

<br>

Scenario 03 (exp14) demonstrated a deviation of -28.0%, attributable to a substantial process variability, e.g. as observed at station S5/FAXS (CV = 79.4%). A high process variability can lead to queuing delays that were not incorporated into the deterministic simulation run. To account for these queuing effects, a queue delay adjustment was applied using Kingman’s approximation (Hopp & Spearman, 2011). 

The coefficients of variation c<sub>e</sub> (ratio of standard deviation to mean) were derived from the real process data, and the utilization μ from the baseline simulation. The mean processing time t<sub>e</sub> was taken from the baseline product configuration. For each workstation, the adjusted processing times were calculated as: <br>
t<sub>adjusted</sub> = t<sub>e</sub> · [1 + (c²<sub>e</sub> / 2) · μ / (1 – μ)] <br>

<details>
<summary><strong>see details of the formula derivation</strong></summary>

Kingman’s approximation: <br>
CT<sub>q</sub> = ((c²<sub>a</sub> + c²<sub>e</sub>) / 2) · (μ / (1 – μ)) · t<sub>e</sub> <br>

Kingman’s approximation with c<sub>a</sub> set to 0, due to scheduled (deterministic) arrivals: <br>
CT<sub>q</sub> = (c²<sub>e</sub> / 2) · (μ / (1 – μ)) · t<sub>e</sub> <br>

Total cycle time: <br>
CT = t<sub>e</sub> + CT<sub>q</sub> <br>

Kingman’s approximation substituted into total cycle time: <br>
CT = t<sub>e</sub> + (c²<sub>e</sub> / 2) · (μ / (1 – μ)) · t<sub>e</sub> <br>

t<sub>e</sub> factored out, results in: <br>
t<sub>adjusted</sub> = t<sub>e</sub> · [1 + (c²<sub>e</sub> / 2) · μ / (1 – μ)] <br>

Example calculation (FAXS on ws-03): <br>
t<sub>e</sub> = 170s (baseline), c<sub>e</sub> = 135/170 = 0.794 (StdDev/Mean), μ = 0.710 (baseline simulation) <br>
t<sub>adjusted</sub> = 170 · [1 + (0.794² / 2) · 0.710 / (1 – 0.710)] = 170 · [1 + 0.315 · 2.448] = 170 · 1.771 = 301s <br>

</details>
<br>

In the sensitivity run, the NCT ranged from 156.3 to 961.3 minutes for POs 1–5, reflecting the progressive system congestion. The VUT adjustment reduced the lead time deviation from -28.0% to -6.6%, bringing the model within the acceptable validation threshold. <br>
For more details on queuing delays, please refer to Hopp & Spearman (2011). <br>
**Note:** In the real experiment, only POs 1-5 were completed. In the baseline run (Table 3.3), POs 6 and 7 were completed in the simulation but not in the real experiment. In the sensitivity run (Table 3.3 [s]), POs 6-10 were completed neither in the simulation nor in the real experiment. The deviations in both tables are therefore based on POs 1-5.

<details>
<summary><strong>Table 3.3.</strong> Lead times (scenario 03, exp14)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">PO</th>
      <th rowspan="2">Type</th>
      <th rowspan="2">Delivery (min)</th>
      <th colspan="4">Simulated data</th>
      <th colspan="2">Factory data</th>
      <th rowspan="2">Lead time Dev.</th>
    </tr>
    <tr>
      <th>Exit</th>
      <th>VT</th>
      <th>NCT</th>
      <th>Lead time</th>
      <th>Handling time</th>
      <th>Lead time</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>1</td><td>HD</td><td>0.0</td><td>843.9</td><td>700.3</td><td>109.9</td><td>843.9</td><td>910</td><td>1066</td><td>-20.8%</td></tr>
    <tr><td>2</td><td>HD</td><td>90.0</td><td>1084.6</td><td>823.3</td><td>258.1</td><td>994.6</td><td>752</td><td>1636</td><td>-39.2%</td></tr>
    <tr><td>3</td><td>HD</td><td>180.0</td><td>1321.5</td><td>823.3</td><td>278.3</td><td>1141.5</td><td>720</td><td>1186</td><td>-3.7%</td></tr>
    <tr><td>4</td><td>HD</td><td>270.0</td><td>1563.1</td><td>823.3</td><td>410.4</td><td>1293.1</td><td>848</td><td>2027</td><td>-36.2%</td></tr>
    <tr><td>5</td><td>HD</td><td>360.0</td><td>1803.1</td><td>823.3</td><td>561.9</td><td>1443.1</td><td>600</td><td>2027</td><td>-28.8%</td></tr>
    <tr><td>6</td><td>HD</td><td>450.0</td><td>2016.5</td><td>823.3</td><td>688.4</td><td>1566.5</td><td>707</td><td>-</td><td>DNF (factory)</td></tr>
    <tr><td>7</td><td>HD</td><td>600.0</td><td>2251.5</td><td>823.3</td><td>773.2</td><td>1651.5</td><td>909</td><td>-</td><td>DNF (factory)</td></tr>
    <tr><td>8</td><td>HD</td><td>630.0</td><td>2374.9</td><td>768.7</td><td>937.7</td><td>1744.9</td><td>858</td><td>-</td><td>DNF (sim + factory)</td></tr>
    <tr><td>9</td><td>HD</td><td>780.0</td><td>2193.4</td><td>590.1</td><td>767.7</td><td>1413.4</td><td>645</td><td>-</td><td>DNF (sim + factory)</td></tr>
    <tr><td>10</td><td>HD</td><td>840.0</td><td>2373.4</td><td>590.1</td><td>891.1</td><td>1533.4</td><td>605</td><td>-</td><td>DNF (sim + factory)</td></tr>
    <tr><td><strong>Avg (1-5)</strong></td><td>-</td><td>-</td><td>-</td><td><strong>798.7</strong></td><td><strong>323.7</strong></td><td><strong>1143.2</strong></td><td><strong>766.0</strong></td><td><strong>1588.4</strong></td><td><strong>-28.0%</strong></td></tr>
  </tbody>
</table>

**Note:** POs 6-7 were not finished in the real experiment (DNF (factory)); POs 8-10 were not finished in the simulation and in the real experiment (DNF (sim + factory)). Only POs completed in both the simulation and the real experiment are included in the average.

</details>


<br>

<details>
<summary><strong>Table 3.3 [s].</strong> Lead times (scenario 03 sensitivity, exp14s)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">PO</th>
      <th rowspan="2">Type</th>
      <th rowspan="2">Delivery (min)</th>
      <th colspan="4">Simulated data</th>
      <th colspan="2">Factory data</th>
      <th rowspan="2">Lead time Dev.</th>
    </tr>
    <tr>
      <th>Exit</th>
      <th>VT</th>
      <th>NCT</th>
      <th>Lead time</th>
      <th>Handling time</th>
      <th>Lead time</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>1</td><td>HD</td><td>0.0</td><td>1083.1</td><td>1027.3</td><td>156.3</td><td>1083.1</td><td>910</td><td>1066</td><td>+1.6%</td></tr>
    <tr><td>2</td><td>HD</td><td>90.0</td><td>1358.5</td><td>1027.3</td><td>327.1</td><td>1268.5</td><td>752</td><td>1636</td><td>-22.5%</td></tr>
    <tr><td>3</td><td>HD</td><td>180.0</td><td>1656.9</td><td>1027.3</td><td>542.3</td><td>1476.9</td><td>720</td><td>1186</td><td>+24.5%</td></tr>
    <tr><td>4</td><td>HD</td><td>270.0</td><td>1958.5</td><td>1027.3</td><td>756.3</td><td>1688.5</td><td>848</td><td>2027</td><td>-16.7%</td></tr>
    <tr><td>5</td><td>HD</td><td>360.0</td><td>2256.9</td><td>1027.3</td><td>961.3</td><td>1896.9</td><td>600</td><td>2027</td><td>-6.4%</td></tr>
    <tr><td>6</td><td>HD</td><td>450.0</td><td>2341.5</td><td>911.2</td><td>1103.4</td><td>1891.5</td><td>707</td><td>-</td><td>DNF (sim + factory)</td></tr>
    <tr><td>7</td><td>HD</td><td>600.0</td><td>1894.9</td><td>355.0</td><td>1239.5</td><td>1294.9</td><td>909</td><td>-</td><td>DNF (sim + factory)</td></tr>
    <tr><td>8</td><td>HD</td><td>630.0</td><td>2134.9</td><td>355.0</td><td>1104.6</td><td>1504.9</td><td>858</td><td>-</td><td>DNF (sim + factory)</td></tr>
    <tr><td>9</td><td>HD</td><td>780.0</td><td>2374.9</td><td>355.0</td><td>1198.8</td><td>1594.9</td><td>645</td><td>-</td><td>DNF (sim + factory)</td></tr>
    <tr><td>10</td><td>HD</td><td>840.0</td><td>1173.4</td><td>111.0</td><td>1366.3</td><td>333.4</td><td>605</td><td>-</td><td>DNF (sim + factory)</td></tr>
    <tr><td><strong>Avg (1-5)</strong></td><td>-</td><td>-</td><td>-</td><td><strong>1027.3</strong></td><td><strong>548.7</strong></td><td><strong>1482.8</strong></td><td><strong>766.0</strong></td><td><strong>1588.4</strong></td><td><strong>-6.6%</strong></td></tr>
  </tbody>
</table>

**Note:** POs 6-10 were not finished in the simulation and in the real experiment (DNF (sim + factory)). Only POs completed in both the simulation and the real experiment are included in the average.

</details>

<br>

Scenario 04 (exp15) demonstrated an average lead time deviation of +4.6% for a workshop layout with a centralized FIFO buffer, processing HD products manually. The NCT variation was significant (72-1002 min) due to the FIFO routing constraint and buffer blocking, indicating bottleneck behavior at stations S1 to S4 that constrained throughput, irrespective of the available downstream capacity. <br>
**Note:** POs 7-10 were not completed in the real experiment within the 40-minute observation period, and PO 6 was not completed in the simulation. The lead time comparison in Table 3.4 is therefore based on POs 1-5.

<details>
<summary><strong>Table 3.4.</strong> Lead times (scenario 04, exp15)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">PO</th>
      <th rowspan="2">Type</th>
      <th rowspan="2">Delivery (min)</th>
      <th colspan="4">Simulated data</th>
      <th colspan="2">Factory data</th>
      <th rowspan="2">Lead time Dev.</th>
    </tr>
    <tr>
      <th>Exit</th>
      <th>VT</th>
      <th>NCT</th>
      <th>Lead time</th>
      <th>Handling time</th>
      <th>Lead time</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>1</td><td>HD</td><td>0.0</td><td>1353.1</td><td>1211.3</td><td>76.6</td><td>1353.1</td><td>1333</td><td>1396</td><td>-3.1%</td></tr>
    <tr><td>2</td><td>HD</td><td>90.0</td><td>1443.1</td><td>1211.3</td><td>72.4</td><td>1353.1</td><td>1471</td><td>1501</td><td>-9.9%</td></tr>
    <tr><td>3</td><td>HD</td><td>180.0</td><td>1833.1</td><td>1211.3</td><td>371.8</td><td>1653.1</td><td>1341</td><td>1546</td><td>+6.9%</td></tr>
    <tr><td>4</td><td>HD</td><td>270.0</td><td>2074.6</td><td>1211.3</td><td>521.0</td><td>1804.6</td><td>1200</td><td>1411</td><td>+27.9%</td></tr>
    <tr><td>5</td><td>HD</td><td>360.0</td><td>2313.1</td><td>1211.3</td><td>674.8</td><td>1953.1</td><td>1169</td><td>1906</td><td>+2.5%</td></tr>
    <tr><td>6</td><td>HD</td><td>450.0</td><td>2371.5</td><td>1053.2</td><td>797.6</td><td>1921.5</td><td>946</td><td>1832</td><td>DNF (sim)</td></tr>
    <tr><td>7</td><td>HD</td><td>600.0</td><td>2343.1</td><td>784.6</td><td>886.9</td><td>1743.1</td><td>763</td><td>-</td><td>DNF (sim + factory)</td></tr>
    <tr><td>8</td><td>HD</td><td>810.0</td><td>2073.1</td><td>483.0</td><td>898.1</td><td>1263.1</td><td>390</td><td>-</td><td>DNF (sim + factory)</td></tr>
    <tr><td>9</td><td>HD</td><td>930.0</td><td>2311.5</td><td>404.5</td><td>1002.0</td><td>1381.5</td><td>345</td><td>-</td><td>DNF (sim + factory)</td></tr>
    <tr><td>10</td><td>HD</td><td>1200.0</td><td>2341.5</td><td>326.0</td><td>823.0</td><td>1141.5</td><td>165</td><td>-</td><td>DNF (sim + factory)</td></tr>
    <tr><td><strong>Avg (1-5)</strong></td><td>-</td><td>-</td><td>-</td><td><strong>1211.3</strong></td><td><strong>343.3</strong></td><td><strong>1623.4</strong></td><td><strong>1302.8</strong></td><td><strong>1552.0</strong></td><td><strong>+4.6%</strong></td></tr>
  </tbody>
</table>

**Note:** PO 6 was not finished in the simulation (DNF (sim)); POs 7-10 were not finished in the simulation and in the real experiment (DNF (sim + factory)). Only POs completed in both the simulation and the real experiment are included in the average.

</details>

<br>

Scenario 05 (exp16) demonstrated an average lead time deviation of +11.2% for a mixed product scenario (6HD/1TL/1SA/2RD) in a workshop layout. All POs were completed in both the simulation and the real experiment. The NCT ranged from 49 to 738 minutes across the mixed-product scenario, with RD products experiencing the highest blocking (avg. 721 min NCT at POs 6 and 8) due to congestion. As shown in Table 3.5, individual PO deviations vary significantly by product type (ranging from -28.9% to +59.1%), due to different queuing patterns between the simulation and reality. <br>
**Note:** In the actual experiment, each PO was processed at a freely available workstation. In the simulation, FIFO routing was used, which resulted in different queuing delays for later arrivals.

<details>
<summary><strong>Table 3.5.</strong> Lead times (scenario 05, exp16)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">PO</th>
      <th rowspan="2">Type</th>
      <th rowspan="2">Delivery (min)</th>
      <th colspan="4">Simulated data</th>
      <th colspan="2">Factory data</th>
      <th rowspan="2">Lead time Dev.</th>
    </tr>
    <tr>
      <th>Exit</th>
      <th>VT</th>
      <th>NCT</th>
      <th>Lead time</th>
      <th>Handling time</th>
      <th>Lead time</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>1</td><td>HD</td><td>0.0</td><td>1081.5</td><td>997.3</td><td>51.4</td><td>1081.5</td><td>864</td><td>812</td><td>+33.2%</td></tr>
    <tr><td>2</td><td>TL</td><td>60.0</td><td>571.5</td><td>424.1</td><td>52.8</td><td>511.5</td><td>421</td><td>497</td><td>+2.9%</td></tr>
    <tr><td>3</td><td>HD</td><td>120.0</td><td>1203.1</td><td>997.3</td><td>49.7</td><td>1083.1</td><td>856</td><td>797</td><td>+35.9%</td></tr>
    <tr><td>4</td><td>HD</td><td>180.0</td><td>1264.6</td><td>997.3</td><td>49.0</td><td>1084.6</td><td>1164</td><td>1171</td><td>-7.4%</td></tr>
    <tr><td>5</td><td>SA</td><td>240.0</td><td>784.6</td><td>449.1</td><td>56.4</td><td>544.6</td><td>958</td><td>766</td><td>-28.9%</td></tr>
    <tr><td>6</td><td>RD</td><td>300.0</td><td>1591.5</td><td>516.1</td><td>737.8</td><td>1291.5</td><td>524</td><td>812</td><td>+59.1%</td></tr>
    <tr><td>7</td><td>HD</td><td>420.0</td><td>1563.1</td><td>997.3</td><td>105.9</td><td>1143.1</td><td>762</td><td>1097</td><td>+4.2%</td></tr>
    <tr><td>8</td><td>RD</td><td>420.0</td><td>1711.5</td><td>516.1</td><td>704.6</td><td>1291.5</td><td>405</td><td>947</td><td>+36.4%</td></tr>
    <tr><td>9</td><td>HD</td><td>540.0</td><td>2251.5</td><td>997.3</td><td>675.9</td><td>1711.5</td><td>1137</td><td>1456</td><td>+17.6%</td></tr>
    <tr><td>10</td><td>HD</td><td>600.0</td><td>1771.5</td><td>997.3</td><td>136.6</td><td>1171.5</td><td>915</td><td>1456</td><td>-19.5%</td></tr>
    <tr><td><strong>Avg (1-10)</strong></td><td>-</td><td>-</td><td>-</td><td><strong>788.9</strong></td><td><strong>262.0</strong></td><td><strong>1091.5</strong></td><td><strong>800.6</strong></td><td><strong>981.1</strong></td><td><strong>+11.2%</strong></td></tr>
  </tbody>
</table>

</details>

<br>

Scenario 06 (exp17) demonstrated a baseline deviation of +11.5% for a mixed product scenario (3HD/3SA/3RD/1TL) in a 5-workstation line layout. The NCT demonstrated significant variation (43-1535 min), primarily attributable to the critical bottleneck at S3S4, which exhibited 98.5% utilization. Products requiring this station encountered severe blocking, regardless of their specific routing. <br>
**Note:** In the baseline run, POs 6 and 8-10 were not completed within the simulation time due to the bottleneck, and POs 8 and 10 were not completed in the real experiment. The average in Table 3.6 is therefore based on POs 1-5 and 7. Table 3.6 [s] shows the sensitivity analysis (exp17s), in which the RT and FT processing times were reduced by 20% (RT: 81.5→65 min, FT: 62→50 min) to match the observed WS-02 throughput. This empirical calibration improved the average lead time deviation from +11.5% to +1.5%. In the sensitivity run, PO 9 was not completed in the simulation, PO 10 not in the real experiment, and PO 8 in neither, so the average in Table 3.6 [s] is based on POs 1-7.

<details>
<summary><strong>Table 3.6.</strong> Lead times (scenario 06, exp17)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">PO</th>
      <th rowspan="2">Type</th>
      <th rowspan="2">Delivery (min)</th>
      <th colspan="4">Simulated data</th>
      <th colspan="2">Factory data</th>
      <th rowspan="2">Lead time Dev.</th>
    </tr>
    <tr>
      <th>Exit</th>
      <th>VT</th>
      <th>NCT</th>
      <th>Lead time</th>
      <th>Handling time</th>
      <th>Lead time</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>1</td><td>SA</td><td>0.0</td><td>666.5</td><td>582.1</td><td>43.3</td><td>666.5</td><td>435</td><td>691</td><td>-3.6%</td></tr>
    <tr><td>2</td><td>RD</td><td>90.0</td><td>843.1</td><td>510.1</td><td>198.7</td><td>753.1</td><td>708</td><td>737</td><td>+2.2%</td></tr>
    <tr><td>3</td><td>HD</td><td>180.0</td><td>1593.1</td><td>1053.3</td><td>480.6</td><td>1413.1</td><td>1102</td><td>1397</td><td>+1.2%</td></tr>
    <tr><td>4</td><td>TL</td><td>270.0</td><td>1381.5</td><td>436.1</td><td>637.7</td><td>1111.5</td><td>426</td><td>669</td><td>+66.1%</td></tr>
    <tr><td>5</td><td>SA</td><td>360.0</td><td>1471.5</td><td>582.1</td><td>488.3</td><td>1111.5</td><td>516</td><td>1036</td><td>+7.3%</td></tr>
    <tr><td>6</td><td>HD</td><td>450.0</td><td>2108.3</td><td>784.2</td><td>884.6</td><td>1658.3</td><td>889</td><td>1396</td><td>DNF (sim)</td></tr>
    <tr><td>7</td><td>RD</td><td>540.0</td><td>2161.5</td><td>510.1</td><td>1066.7</td><td>1621.5</td><td>495</td><td>1456</td><td>+11.4%</td></tr>
    <tr><td>8</td><td>HD</td><td>630.0</td><td>2341.5</td><td>436.0</td><td>1265.8</td><td>1711.5</td><td>1011</td><td>-</td><td>DNF (sim + factory)</td></tr>
    <tr><td>9</td><td>RD</td><td>720.0</td><td>994.3</td><td>78.0</td><td>1534.7</td><td>274.3</td><td>660</td><td>1546</td><td>DNF (sim)</td></tr>
    <tr><td>10</td><td>SA</td><td>810.0</td><td>2371.5</td><td>521.0</td><td>999.8</td><td>1561.5</td><td>463</td><td>-</td><td>DNF (sim + factory)</td></tr>
    <tr><td><strong>Avg (1-5, 7)</strong></td><td>-</td><td>-</td><td>-</td><td><strong>612.3</strong></td><td><strong>485.9</strong></td><td><strong>1112.9</strong></td><td><strong>613.7</strong></td><td><strong>997.7</strong></td><td><strong>+11.5%</strong></td></tr>
  </tbody>
</table>

**Note:** POs 6 and 9 were not finished in the simulation (DNF (sim)); POs 8 and 10 were not finished in the simulation and in the real experiment (DNF (sim + factory)). Only POs completed in both the simulation and the real experiment are included in the average.

</details>


<br>

<details>
<summary><strong>Table 3.6 [s].</strong> Lead times (scenario 06 sensitivity, exp17s)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">PO</th>
      <th rowspan="2">Type</th>
      <th rowspan="2">Delivery (min)</th>
      <th colspan="4">Simulated data</th>
      <th colspan="2">Factory data</th>
      <th rowspan="2">Lead time Dev.</th>
    </tr>
    <tr>
      <th>Exit</th>
      <th>VT</th>
      <th>NCT</th>
      <th>Lead time</th>
      <th>Handling time</th>
      <th>Lead time</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>1</td><td>SA</td><td>0.0</td><td>607.3</td><td>525.1</td><td>38.9</td><td>607.3</td><td>435</td><td>691</td><td>-12.1%</td></tr>
    <tr><td>2</td><td>RD</td><td>90.0</td><td>783.2</td><td>477.1</td><td>169.3</td><td>693.2</td><td>708</td><td>737</td><td>-5.9%</td></tr>
    <tr><td>3</td><td>HD</td><td>180.0</td><td>1441.5</td><td>996.3</td><td>389.3</td><td>1261.5</td><td>1102</td><td>1397</td><td>-9.7%</td></tr>
    <tr><td>4</td><td>TL</td><td>270.0</td><td>1141.5</td><td>379.1</td><td>454.7</td><td>871.5</td><td>426</td><td>669</td><td>+30.3%</td></tr>
    <tr><td>5</td><td>SA</td><td>360.0</td><td>1326.4</td><td>525.1</td><td>394.5</td><td>966.4</td><td>516</td><td>1036</td><td>-6.7%</td></tr>
    <tr><td>6</td><td>HD</td><td>450.0</td><td>2251.5</td><td>849.3</td><td>964.7</td><td>1801.5</td><td>889</td><td>1396</td><td>+29.0%</td></tr>
    <tr><td>7</td><td>RD</td><td>540.0</td><td>1833.1</td><td>477.1</td><td>771.2</td><td>1293.1</td><td>495</td><td>1456</td><td>-11.2%</td></tr>
    <tr><td>8</td><td>HD</td><td>630.0</td><td>2343.4</td><td>640.7</td><td>1136.4</td><td>1713.4</td><td>1011</td><td>-</td><td>DNF (sim + factory)</td></tr>
    <tr><td>9</td><td>RD</td><td>720.0</td><td>2193.4</td><td>355.0</td><td>1272.4</td><td>1473.4</td><td>660</td><td>1546</td><td>DNF (sim)</td></tr>
    <tr><td>10</td><td>SA</td><td>810.0</td><td>2131.5</td><td>525.1</td><td>756.3</td><td>1321.5</td><td>463</td><td>-</td><td>DNF (factory)</td></tr>
    <tr><td><strong>Avg (1-7)</strong></td><td>-</td><td>-</td><td>-</td><td><strong>604.2</strong></td><td><strong>454.7</strong></td><td><strong>1070.7</strong></td><td><strong>653.0</strong></td><td><strong>1054.6</strong></td><td><strong>+1.5%</strong></td></tr>
  </tbody>
</table>

**Note:** PO 9 was not finished in the simulation (DNF (sim)); PO 10 was not finished in the real experiment (DNF (factory)); PO 8 was not finished in the simulation and in the real experiment (DNF (sim + factory)). Only POs completed in both the simulation and the real experiment are included in the average.

</details>

<br>

---

<br>

<!-- ================================================== -->
<!-- DETAILED RESULTS - STATION STATISTICS -->
<!-- ================================================== -->
## 4. Detailed Results - Station Statistics

This section presents the station-level performance statistics from each validation scenario. Simulated times are given in **simulation minutes**, factory times in **seconds** (1 sim minute = 1 real second due to 60x scaling).

The following tables present the data for each workstation, including the total available time (~2399 min = 40 hours in simulation), the busy time spent actively processing products, the blocked time when waiting for downstream capacity, the waiting time when idle for products. The utilization (Util.) is a measure of the station's efficiency, calculated as Busy / Total &middot; 100%. The factory data columns present the values from the actual experiments as reported in the dataset: the run time of the experiment (Total, from the first entry to the last exit), the measured busy time, and the utilization (Busy / Total). The utilization deviation (Util. Dev.) indicates the difference between the simulated and factory utilization in percentage points (pp). The averages include all workstations of a scenario.

<br>

---

<br>

In Scenario 01 (exp12), the average utilization deviation across the three workstations was +2.2 pp. The deviations range from -0.2 pp to +5.7 pp, demonstrating a consistent station-level performance modeling (see Table 4.1).

<details>
<summary><strong>Table 4.1.</strong> Station statistics (scenario 01, exp12)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">Station</th>
      <th colspan="5">Simulated data</th>
      <th colspan="3">Factory data</th>
      <th rowspan="2">Util. Dev.</th>
    </tr>
    <tr>
      <th>Total</th>
      <th>Busy</th>
      <th>Blocked</th>
      <th>Waiting</th>
      <th>Util.</th>
      <th>Total</th>
      <th>Busy</th>
      <th>Util.</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ws-03_S1toS4</td><td>2399.0</td><td>2110.2</td><td>5.6</td><td>283.2</td><td>88.0%</td><td>2416</td><td>1988</td><td>82.3%</td><td>+5.7 pp</td></tr>
    <tr><td>ws-04_S5S7</td><td>2399.0</td><td>775.2</td><td>1.2</td><td>1622.6</td><td>32.3%</td><td>2416</td><td>756</td><td>31.3%</td><td>+1.0 pp</td></tr>
    <tr><td>ws-05_S6S8</td><td>2399.0</td><td>1275.2</td><td>2.4</td><td>1121.4</td><td>53.2%</td><td>2416</td><td>1290</td><td>53.4%</td><td>-0.2 pp</td></tr>
    <tr><td><strong>Average</strong></td><td>-</td><td>-</td><td>-</td><td>-</td><td><strong>57.8%</strong></td><td>-</td><td>-</td><td><strong>55.7%</strong></td><td><strong>+2.2 pp</strong></td></tr>
  </tbody>
</table>

</details>

<br>

Scenario 02 (exp13) demonstrated an average utilization deviation of +3.5 pp across the system. Individual workstation deviations ranged from -7.3 pp to +19.7 pp. <br>
**Note:** In the real experiment, each PO was disassembled completely at a single workstation. In the simulation, the disassembly steps of a product were distributed across several workstations. The deviations for individual stations therefore reflect different PO-to-workstation assignments, while the average utilization of the system is comparable (see Table 4.2).

<details>
<summary><strong>Table 4.2.</strong> Station statistics (scenario 02, exp13)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">Station</th>
      <th colspan="5">Simulated data</th>
      <th colspan="3">Factory data</th>
      <th rowspan="2">Util. Dev.</th>
    </tr>
    <tr>
      <th>Total</th>
      <th>Busy</th>
      <th>Blocked</th>
      <th>Waiting</th>
      <th>Util.</th>
      <th>Total</th>
      <th>Busy</th>
      <th>Util.</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ws-01_S1toS8</td><td>2399.0</td><td>2364.8</td><td>3.0</td><td>31.3</td><td>98.6%</td><td>2416</td><td>1906</td><td>78.9%</td><td>+19.7 pp</td></tr>
    <tr><td>ws-02_S1toS8</td><td>2399.0</td><td>2301.4</td><td>3.0</td><td>94.6</td><td>95.9%</td><td>2416</td><td>2221</td><td>91.9%</td><td>+4.0 pp</td></tr>
    <tr><td>ws-03_S1toS8</td><td>2399.0</td><td>2179.0</td><td>2.8</td><td>217.2</td><td>90.8%</td><td>2416</td><td>2248</td><td>93.0%</td><td>-2.2 pp</td></tr>
    <tr><td>ws-04_S1toS8</td><td>2399.0</td><td>2178.7</td><td>2.6</td><td>217.7</td><td>90.8%</td><td>2416</td><td>2371</td><td>98.1%</td><td>-7.3 pp</td></tr>
    <tr><td><strong>Average</strong></td><td>-</td><td>-</td><td>-</td><td>-</td><td><strong>94.0%</strong></td><td>-</td><td>-</td><td><strong>90.5%</strong></td><td><strong>+3.5 pp</strong></td></tr>
  </tbody>
</table>

</details>

<br>

In Scenario 03 (exp14), there was an average utilization deviation of +4.2 pp in the baseline run (Table 4.3) and +1.8 pp in the sensitivity run (Table 4.3 [s]). <br>
**Note:** The VUT adjustment increases processing times at stations with high variability, leading to shifts in utilization patterns. In the sensitivity run, ws-02 and ws-03 are utilized more strongly, while ws-04 and ws-05 are utilized less.

<details>
<summary><strong>Table 4.3.</strong> Station statistics (scenario 03, exp14)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">Station</th>
      <th colspan="5">Simulated data</th>
      <th colspan="3">Factory data</th>
      <th rowspan="2">Util. Dev.</th>
    </tr>
    <tr>
      <th>Total</th>
      <th>Busy</th>
      <th>Blocked</th>
      <th>Waiting</th>
      <th>Util.</th>
      <th>Total</th>
      <th>Busy</th>
      <th>Util.</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ws-01_S1S2</td><td>2399.0</td><td>1092.0</td><td>4.0</td><td>1303.0</td><td>45.5%</td><td>2387</td><td>1171</td><td>49.1%</td><td>-3.5 pp</td></tr>
    <tr><td>ws-02_S3S4</td><td>2399.0</td><td>1882.0</td><td>5.0</td><td>512.0</td><td>78.4%</td><td>2387</td><td>1875</td><td>78.6%</td><td>-0.1 pp</td></tr>
    <tr><td>ws-03_S5</td><td>2399.0</td><td>1703.0</td><td>2.0</td><td>694.0</td><td>71.0%</td><td>2387</td><td>1173</td><td>49.1%</td><td>+21.8 pp</td></tr>
    <tr><td>ws-04_S7</td><td>2399.0</td><td>1232.0</td><td>2.0</td><td>1165.0</td><td>51.4%</td><td>2387</td><td>1379</td><td>57.8%</td><td>-6.4 pp</td></tr>
    <tr><td>ws-05_S6S8</td><td>2399.0</td><td>1823.1</td><td>4.6</td><td>571.4</td><td>76.0%</td><td>2387</td><td>1600</td><td>67.0%</td><td>+9.0 pp</td></tr>
    <tr><td><strong>Average</strong></td><td>-</td><td>-</td><td>-</td><td>-</td><td><strong>64.5%</strong></td><td>-</td><td>-</td><td><strong>60.3%</strong></td><td><strong>+4.2 pp</strong></td></tr>
  </tbody>
</table>

</details>


<br>

<details>
<summary><strong>Table 4.3 [s].</strong> Station statistics (scenario 03 sensitivity, exp14s)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">Station</th>
      <th colspan="5">Simulated data</th>
      <th colspan="3">Factory data</th>
      <th rowspan="2">Util. Dev.</th>
    </tr>
    <tr>
      <th>Total</th>
      <th>Busy</th>
      <th>Blocked</th>
      <th>Waiting</th>
      <th>Util.</th>
      <th>Total</th>
      <th>Busy</th>
      <th>Util.</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ws-01_S1S2</td><td>2399.0</td><td>1112.0</td><td>4.0</td><td>1283.0</td><td>46.4%</td><td>2387</td><td>1171</td><td>49.1%</td><td>-2.7 pp</td></tr>
    <tr><td>ws-02_S3S4</td><td>2399.0</td><td>2243.5</td><td>4.5</td><td>151.0</td><td>93.5%</td><td>2387</td><td>1875</td><td>78.6%</td><td>+15.0 pp</td></tr>
    <tr><td>ws-03_S5</td><td>2399.0</td><td>1974.5</td><td>1.2</td><td>423.3</td><td>82.3%</td><td>2387</td><td>1173</td><td>49.1%</td><td>+33.2 pp</td></tr>
    <tr><td>ws-04_S7</td><td>2399.0</td><td>751.2</td><td>1.2</td><td>1646.6</td><td>31.3%</td><td>2387</td><td>1379</td><td>57.8%</td><td>-26.5 pp</td></tr>
    <tr><td>ws-05_S6S8</td><td>2399.0</td><td>1363.3</td><td>3.3</td><td>1032.4</td><td>56.8%</td><td>2387</td><td>1600</td><td>67.0%</td><td>-10.2 pp</td></tr>
    <tr><td><strong>Average</strong></td><td>-</td><td>-</td><td>-</td><td>-</td><td><strong>62.1%</strong></td><td>-</td><td>-</td><td><strong>60.3%</strong></td><td><strong>+1.8 pp</strong></td></tr>
  </tbody>
</table>

</details>

<br>

Scenario 04 (exp15) showed an average utilization deviation of +7.6 pp across the five workstations. <br>
**Note:** WS-03 shows a notably higher utilization in the simulation (+25.5 pp), possibly due to different PO-to-station assignment patterns between the simulation and the real experiment (see Table 4.4).

<details>
<summary><strong>Table 4.4.</strong> Station statistics (scenario 04, exp15)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">Station</th>
      <th colspan="5">Simulated data</th>
      <th colspan="3">Factory data</th>
      <th rowspan="2">Util. Dev.</th>
    </tr>
    <tr>
      <th>Total</th>
      <th>Busy</th>
      <th>Blocked</th>
      <th>Waiting</th>
      <th>Util.</th>
      <th>Total</th>
      <th>Busy</th>
      <th>Util.</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ws-01_S1toS4</td><td>2399.0</td><td>2364.0</td><td>3.8</td><td>31.3</td><td>98.5%</td><td>2461</td><td>2293</td><td>93.2%</td><td>+5.4 pp</td></tr>
    <tr><td>ws-02_S1toS4</td><td>2399.0</td><td>2270.7</td><td>3.7</td><td>124.6</td><td>94.7%</td><td>2461</td><td>2190</td><td>89.0%</td><td>+5.7 pp</td></tr>
    <tr><td>ws-03_S5toS8</td><td>2399.0</td><td>1826.7</td><td>1.5</td><td>570.9</td><td>76.1%</td><td>2461</td><td>1246</td><td>50.6%</td><td>+25.5 pp</td></tr>
    <tr><td>ws-04_S5toS8</td><td>2399.0</td><td>1596.0</td><td>1.4</td><td>801.7</td><td>66.5%</td><td>2461</td><td>1620</td><td>65.8%</td><td>+0.7 pp</td></tr>
    <tr><td>ws-05_S5toS8</td><td>2399.0</td><td>1345.5</td><td>1.1</td><td>1052.4</td><td>56.1%</td><td>2461</td><td>1364</td><td>55.4%</td><td>+0.7 pp</td></tr>
    <tr><td><strong>Average</strong></td><td>-</td><td>-</td><td>-</td><td>-</td><td><strong>78.4%</strong></td><td>-</td><td>-</td><td><strong>70.8%</strong></td><td><strong>+7.6 pp</strong></td></tr>
  </tbody>
</table>

</details>

<br>

Scenario 05 (exp16) showed an average utilization deviation of -3.7 pp. Individual station deviations ranged from -27.8 pp to +29.3 pp. <br>
**Note:** The significant variation reflects different PO-to-station assignment patterns. The simulation was configured to utilize FIFO load balancing, which distributed the workload differently than in the real experiments (see Table 4.5).

<details>
<summary><strong>Table 4.5.</strong> Station statistics (scenario 05, exp16)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">Station</th>
      <th colspan="5">Simulated data</th>
      <th colspan="3">Factory data</th>
      <th rowspan="2">Util. Dev.</th>
    </tr>
    <tr>
      <th>Total</th>
      <th>Busy</th>
      <th>Blocked</th>
      <th>Waiting</th>
      <th>Util.</th>
      <th>Total</th>
      <th>Busy</th>
      <th>Util.</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ws-01_S1toS8</td><td>2399.0</td><td>1513.8</td><td>2.2</td><td>883.0</td><td>63.1%</td><td>2146</td><td>1950</td><td>90.9%</td><td>-27.8 pp</td></tr>
    <tr><td>ws-02_S1toS8</td><td>2399.0</td><td>1421.8</td><td>2.2</td><td>975.0</td><td>59.3%</td><td>2146</td><td>1201</td><td>56.0%</td><td>+3.3 pp</td></tr>
    <tr><td>ws-03_S1toS8</td><td>2399.0</td><td>1513.8</td><td>2.2</td><td>883.0</td><td>63.1%</td><td>2146</td><td>1486</td><td>69.2%</td><td>-6.1 pp</td></tr>
    <tr><td>ws-04_S1toS8</td><td>2399.0</td><td>1995.0</td><td>2.8</td><td>401.2</td><td>83.2%</td><td>2146</td><td>1155</td><td>53.8%</td><td>+29.3 pp</td></tr>
    <tr><td>ws-05_S1toS8</td><td>2399.0</td><td>1446.8</td><td>2.3</td><td>949.9</td><td>60.3%</td><td>2146</td><td>1665</td><td>77.6%</td><td>-17.3 pp</td></tr>
    <tr><td><strong>Average</strong></td><td>-</td><td>-</td><td>-</td><td>-</td><td><strong>65.8%</strong></td><td>-</td><td>-</td><td><strong>69.5%</strong></td><td><strong>-3.7 pp</strong></td></tr>
  </tbody>
</table>

</details>

<br>

Scenario 06 (exp17) demonstrated an average utilization deviation of -5.7 pp in the baseline run (Table 4.6) and -2.1 pp in the calibrated sensitivity run (Table 4.6 [s]). <br>
**Note:** In the sensitivity run, the RT and FT processing times were reduced by 20%. In the baseline, WS-02 was a bottleneck at a 98.5% utilization rate, which was reduced in the calibrated run (83.5%), closely matching the real value (83.7%). WS-04 and WS-05 show higher utilization in the calibrated run because more products reached these stations within the simulation time after the bottleneck at WS-02 was relieved.

<details>
<summary><strong>Table 4.6.</strong> Station statistics (scenario 06, exp17)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">Station</th>
      <th colspan="5">Simulated data</th>
      <th colspan="3">Factory data</th>
      <th rowspan="2">Util. Dev.</th>
    </tr>
    <tr>
      <th>Total</th>
      <th>Busy</th>
      <th>Blocked</th>
      <th>Waiting</th>
      <th>Util.</th>
      <th>Total</th>
      <th>Busy</th>
      <th>Util.</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ws-01_S1S2</td><td>2399.0</td><td>831.4</td><td>2.5</td><td>1565.1</td><td>34.7%</td><td>2401</td><td>990</td><td>41.2%</td><td>-6.6 pp</td></tr>
    <tr><td>ws-02_S3S4</td><td>2399.0</td><td>2362.9</td><td>4.1</td><td>32.0</td><td>98.5%</td><td>2401</td><td>2009</td><td>83.7%</td><td>+14.8 pp</td></tr>
    <tr><td>ws-03_S5</td><td>2399.0</td><td>350.6</td><td>0.4</td><td>2048.0</td><td>14.6%</td><td>2401</td><td>495</td><td>20.6%</td><td>-6.0 pp</td></tr>
    <tr><td>ws-04_S7</td><td>2399.0</td><td>588.8</td><td>0.8</td><td>1809.4</td><td>24.5%</td><td>2401</td><td>1304</td><td>54.3%</td><td>-29.8 pp</td></tr>
    <tr><td>ws-05_S6S8</td><td>2399.0</td><td>1574.1</td><td>2.8</td><td>822.1</td><td>65.6%</td><td>2401</td><td>1604</td><td>66.8%</td><td>-1.2 pp</td></tr>
    <tr><td><strong>Average</strong></td><td>-</td><td>-</td><td>-</td><td>-</td><td><strong>47.6%</strong></td><td>-</td><td>-</td><td><strong>53.3%</strong></td><td><strong>-5.7 pp</strong></td></tr>
  </tbody>
</table>

</details>


<br>

<details>
<summary><strong>Table 4.6 [s].</strong> Station statistics (scenario 06 sensitivity, exp17s)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">Station</th>
      <th colspan="5">Simulated data</th>
      <th colspan="3">Factory data</th>
      <th rowspan="2">Util. Dev.</th>
    </tr>
    <tr>
      <th>Total</th>
      <th>Busy</th>
      <th>Blocked</th>
      <th>Waiting</th>
      <th>Util.</th>
      <th>Total</th>
      <th>Busy</th>
      <th>Util.</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ws-01_S1S2</td><td>2399.0</td><td>831.4</td><td>2.5</td><td>1565.1</td><td>34.7%</td><td>2401</td><td>990</td><td>41.2%</td><td>-6.6 pp</td></tr>
    <tr><td>ws-02_S3S4</td><td>2399.0</td><td>2002.1</td><td>4.4</td><td>392.5</td><td>83.5%</td><td>2401</td><td>2009</td><td>83.7%</td><td>-0.2 pp</td></tr>
    <tr><td>ws-03_S5</td><td>2399.0</td><td>525.9</td><td>0.6</td><td>1872.5</td><td>21.9%</td><td>2401</td><td>495</td><td>20.6%</td><td>+1.3 pp</td></tr>
    <tr><td>ws-04_S7</td><td>2399.0</td><td>883.2</td><td>1.2</td><td>1514.6</td><td>36.8%</td><td>2401</td><td>1304</td><td>54.3%</td><td>-17.5 pp</td></tr>
    <tr><td>ws-05_S6S8</td><td>2399.0</td><td>1903.3</td><td>3.6</td><td>492.1</td><td>79.3%</td><td>2401</td><td>1604</td><td>66.8%</td><td>+12.5 pp</td></tr>
    <tr><td><strong>Average</strong></td><td>-</td><td>-</td><td>-</td><td>-</td><td><strong>51.2%</strong></td><td>-</td><td>-</td><td><strong>53.3%</strong></td><td><strong>-2.1 pp</strong></td></tr>
  </tbody>
</table>

</details>

<br>

---

<br>

<!-- ================================================== -->
<!-- DETAILED RESULTS - COMPONENT COUNTS -->
<!-- ================================================== -->
## 5. Detailed Results - Component Counts

This section presents the component-level output data from each validation scenario, comparing the number of disassembled components between the simulation and the recorded factory data.

The component tables (see Tables 5.Xa) contain the data for each target component, identified by a code (e.g., BOSP, RT, BSA) and a full description. The "# per car" column indicates the quantity per product; a "1+1" notation indicates two separate items. The simulated count displays the number of components in the simulation output within the simulation time, including the components of POs that were not completed. The factory # POs represents the number of production orders from which the component was removed in the real experiment, and the factory count is calculated as # POs &middot; # per car. The remaining parts tables (see Tables 5.Xb) follow the same structure, with # per car always set to "1", indicating one remaining part per production order.

The same list of target components is used for the simulation and the factory data. CORE and CHS denote the same component and are counted as one group. The front axle is counted once per car, regardless of whether it was separated from the shock absorbers (FAX) or not (FAXS). The component count deviation is calculated from the totals, (Simulated - Factory) / Factory &middot; 100%. The remaining parts are shown for completeness and are not part of the validation assessment.

<br>

---

<br>

Scenario 01 (exp12) demonstrated a total component count deviation of -4.2%, indicating a close alignment with the actual factory data (see Table 5.1a). The deviation results from PO 10, which was not completed in the simulation (missing SSA and BSA). The remaining parts count deviation was -10.0% (see Table 5.1b).
<details>
<summary><strong>Table 5.1a.</strong> Component counts (scenario 01, exp12)</summary>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Code</th>
        <th rowspan="2">Description</th>
        <th rowspan="2"># per car</th>
        <th colspan="1">Simulated data</th>
        <th colspan="2">Factory data</th>
        <th rowspan="2">Deviation</th>
      </tr>
      <tr>
        <th>Count</th>
        <th># POs</th>
        <th>Count</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>BOSP</td><td>Body + Spoiler</td><td>1+1</td><td>16</td><td>8</td><td>16</td><td>0.0%</td></tr>
      <tr><td>RT</td><td>Rear Tires</td><td>2</td><td>20</td><td>10</td><td>20</td><td>0.0%</td></tr>
      <tr><td>FT</td><td>Front Tires</td><td>2</td><td>8</td><td>4</td><td>8</td><td>0.0%</td></tr>
      <tr><td>BAT</td><td>Battery</td><td>1</td><td>2</td><td>2</td><td>2</td><td>0.0%</td></tr>
      <tr><td>CORE</td><td>Engine Core</td><td>1</td><td>6</td><td>6</td><td>6</td><td>0.0%</td></tr>
      <tr><td>BSA</td><td>Big Shock Absorbers</td><td>2</td><td>14</td><td>8</td><td>16</td><td>-12.5%</td></tr>
      <tr><td>SSA</td><td>Small Shock Absorbers</td><td>2</td><td>3</td><td>2</td><td>4</td><td>-25.0%</td></tr>
      <tr><td colspan="3"><strong>Total components</strong></td><td><strong>69</strong></td><td><strong>40</strong></td><td><strong>72</strong></td><td><strong>-4.2%</strong></td></tr>
    </tbody>
  </table>
</details>

<details>
<summary><strong>Table 5.1b.</strong> Remaining parts (scenario 01, exp12)</summary>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Code</th>
        <th rowspan="2">Description</th>
        <th rowspan="2"># per car</th>
        <th colspan="1">Simulated data</th>
        <th colspan="2">Factory data</th>
        <th rowspan="2">Deviation</th>
      </tr>
      <tr>
        <th>Count</th>
        <th># POs</th>
        <th>Count</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>RAX (RD)</td><td>Rear axis</td><td>1</td><td>6</td><td>6</td><td>6</td><td>0.0%</td></tr>
      <tr><td>CRE (TL)</td><td>Chassis, remaining systems, engine</td><td>1</td><td>2</td><td>2</td><td>2</td><td>0.0%</td></tr>
      <tr><td>CSEB-NABS (SA)</td><td>Chassis, systems, engine, body</td><td>1</td><td>1</td><td>2</td><td>2</td><td>-50.0%</td></tr>
      <tr><td colspan="3"><strong>Total remaining parts</strong></td><td><strong>9</strong></td><td><strong>10</strong></td><td><strong>10</strong></td><td><strong>-10.0%</strong></td></tr>
    </tbody>
  </table>
</details>
<br>

Scenario 02 (exp13) achieved a total component count deviation of -3.6% (see Table 5.2a). The simulation completed seven of the eight POs that were completed in the real experiment. The lower counts of BOSP, BAT and BSA result from POs 8 to 10, which were not completed within the simulation time. The remaining parts count deviation was -12.5% (see Table 5.2b).
<details>
<summary><strong>Table 5.2a.</strong> Component counts (scenario 02, exp13)</summary>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Code</th>
        <th rowspan="2">Description</th>
        <th rowspan="2"># per car</th>
        <th colspan="1">Simulated data</th>
        <th colspan="2">Factory data</th>
        <th rowspan="2">Deviation</th>
      </tr>
      <tr>
        <th>Count</th>
        <th># POs</th>
        <th>Count</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>BOSP</td><td>Body + Spoiler</td><td>1+1</td><td>19</td><td>10</td><td>20</td><td>-5.0%</td></tr>
      <tr><td>BAT</td><td>Battery</td><td>1</td><td>8</td><td>10</td><td>10</td><td>-20.0%</td></tr>
      <tr><td>RT</td><td>Rear Tires</td><td>2</td><td>16</td><td>8</td><td>16</td><td>0.0%</td></tr>
      <tr><td>FT</td><td>Front Tires</td><td>2</td><td>16</td><td>8</td><td>16</td><td>0.0%</td></tr>
      <tr><td>SSA</td><td>Small Shock Absorbers</td><td>2</td><td>16</td><td>8</td><td>16</td><td>0.0%</td></tr>
      <tr><td>FAX</td><td>Front Axle</td><td>1</td><td>8</td><td>8</td><td>8</td><td>0.0%</td></tr>
      <tr><td>CHS</td><td>Chassis</td><td>1</td><td>8</td><td>8</td><td>8</td><td>0.0%</td></tr>
      <tr><td>BSA</td><td>Big Shock Absorbers</td><td>2</td><td>15</td><td>8</td><td>16</td><td>-6.3%</td></tr>
      <tr><td colspan="3"><strong>Total components</strong></td><td><strong>106</strong></td><td><strong>68</strong></td><td><strong>110</strong></td><td><strong>-3.6%</strong></td></tr>
    </tbody>
  </table>
</details>

<details>
<summary><strong>Table 5.2b.</strong> Remaining parts (scenario 02, exp13)</summary>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Code</th>
        <th rowspan="2">Description</th>
        <th rowspan="2"># per car</th>
        <th colspan="1">Simulated data</th>
        <th colspan="2">Factory data</th>
        <th rowspan="2">Deviation</th>
      </tr>
      <tr>
        <th>Count</th>
        <th># POs</th>
        <th>Count</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>RAX (HD)</td><td>Rear axis</td><td>1</td><td>7</td><td>8</td><td>8</td><td>-12.5%</td></tr>
      <tr><td colspan="3"><strong>Total remaining parts</strong></td><td><strong>7</strong></td><td><strong>8</strong></td><td><strong>8</strong></td><td><strong>-12.5%</strong></td></tr>
    </tbody>
  </table>
</details>
<br>

Scenario 03 (exp14) showed component count deviations of 0.0% in the baseline run (Table 5.3a) and -17.8% in the sensitivity run (Table 5.3a [s]). The baseline run matches the total number of components, although it completed more POs (7) than the real experiment (5). Consequently, more BSA were removed (+40.0%), while fewer SSA and FAX were removed (-11.1% and -20.0%). The sensitivity run using VUT-adjusted processing times matched the real completion rate (5 POs), but fewer POs reached the front axle and chassis disassembly within the simulation time (FAX and CHS: -50.0%). The remaining parts count deviations were +40.0% for the baseline run (Table 5.3b) and 0.0% for the sensitivity run (Table 5.3b [s]).
<details>
<summary><strong>Table 5.3a.</strong> Component counts (scenario 03, exp14)</summary>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Code</th>
        <th rowspan="2">Description</th>
        <th rowspan="2"># per car</th>
        <th colspan="1">Simulated data</th>
        <th colspan="2">Factory data</th>
        <th rowspan="2">Deviation</th>
      </tr>
      <tr>
        <th>Count</th>
        <th># POs</th>
        <th>Count</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>BOSP</td><td>Body + Spoiler</td><td>1+1</td><td>20</td><td>10</td><td>20</td><td>0.0%</td></tr>
      <tr><td>BAT</td><td>Battery</td><td>1</td><td>10</td><td>10</td><td>10</td><td>0.0%</td></tr>
      <tr><td>RT</td><td>Rear Tires</td><td>2</td><td>20</td><td>10</td><td>20</td><td>0.0%</td></tr>
      <tr><td>FT</td><td>Front Tires</td><td>2</td><td>20</td><td>10</td><td>20</td><td>0.0%</td></tr>
      <tr><td>SSA</td><td>Small Shock Absorbers</td><td>2</td><td>16</td><td>9</td><td>18</td><td>-11.1%</td></tr>
      <tr><td>FAX</td><td>Front Axle</td><td>1</td><td>8</td><td>10</td><td>10</td><td>-20.0%</td></tr>
      <tr><td>CHS</td><td>Chassis</td><td>1</td><td>10</td><td>10</td><td>10</td><td>0.0%</td></tr>
      <tr><td>BSA</td><td>Big Shock Absorbers</td><td>2</td><td>14</td><td>5</td><td>10</td><td>+40.0%</td></tr>
      <tr><td colspan="3"><strong>Total components</strong></td><td><strong>118</strong></td><td><strong>74</strong></td><td><strong>118</strong></td><td><strong>0.0%</strong></td></tr>
    </tbody>
  </table>

**Note:** FAX includes 9 front axles separated from FAXS and 1 FAXS that was removed but not separated in the real experiment; each is counted as one front axle.

</details>

<details>
<summary><strong>Table 5.3a [s].</strong> Component counts (scenario 03 sensitivity, exp14s)</summary>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Code</th>
        <th rowspan="2">Description</th>
        <th rowspan="2"># per car</th>
        <th colspan="1">Simulated data</th>
        <th colspan="2">Factory data</th>
        <th rowspan="2">Deviation</th>
      </tr>
      <tr>
        <th>Count</th>
        <th># POs</th>
        <th>Count</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>BOSP</td><td>Body + Spoiler</td><td>1+1</td><td>20</td><td>10</td><td>20</td><td>0.0%</td></tr>
      <tr><td>BAT</td><td>Battery</td><td>1</td><td>10</td><td>10</td><td>10</td><td>0.0%</td></tr>
      <tr><td>RT</td><td>Rear Tires</td><td>2</td><td>18</td><td>10</td><td>20</td><td>-10.0%</td></tr>
      <tr><td>FT</td><td>Front Tires</td><td>2</td><td>18</td><td>10</td><td>20</td><td>-10.0%</td></tr>
      <tr><td>SSA</td><td>Small Shock Absorbers</td><td>2</td><td>11</td><td>9</td><td>18</td><td>-38.9%</td></tr>
      <tr><td>FAX</td><td>Front Axle</td><td>1</td><td>5</td><td>10</td><td>10</td><td>-50.0%</td></tr>
      <tr><td>CHS</td><td>Chassis</td><td>1</td><td>5</td><td>10</td><td>10</td><td>-50.0%</td></tr>
      <tr><td>BSA</td><td>Big Shock Absorbers</td><td>2</td><td>10</td><td>5</td><td>10</td><td>0.0%</td></tr>
      <tr><td colspan="3"><strong>Total components</strong></td><td><strong>97</strong></td><td><strong>74</strong></td><td><strong>118</strong></td><td><strong>-17.8%</strong></td></tr>
    </tbody>
  </table>

**Note:** FAX includes 9 front axles separated from FAXS and 1 FAXS that was removed but not separated in the real experiment; each is counted as one front axle.

</details>

<details>
<summary><strong>Table 5.3b.</strong> Remaining parts (scenario 03, exp14)</summary>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Code</th>
        <th rowspan="2">Description</th>
        <th rowspan="2"># per car</th>
        <th colspan="1">Simulated data</th>
        <th colspan="2">Factory data</th>
        <th rowspan="2">Deviation</th>
      </tr>
      <tr>
        <th>Count</th>
        <th># POs</th>
        <th>Count</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>RAX (HD)</td><td>Rear axis</td><td>1</td><td>7</td><td>5</td><td>5</td><td>+40.0%</td></tr>
      <tr><td colspan="3"><strong>Total remaining parts</strong></td><td><strong>7</strong></td><td><strong>5</strong></td><td><strong>5</strong></td><td><strong>+40.0%</strong></td></tr>
    </tbody>
  </table>
</details>

<details>
<summary><strong>Table 5.3b [s].</strong> Remaining parts (scenario 03 sensitivity, exp14s)</summary>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Code</th>
        <th rowspan="2">Description</th>
        <th rowspan="2"># per car</th>
        <th colspan="1">Simulated data</th>
        <th colspan="2">Factory data</th>
        <th rowspan="2">Deviation</th>
      </tr>
      <tr>
        <th>Count</th>
        <th># POs</th>
        <th>Count</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>RAX (HD)</td><td>Rear axis</td><td>1</td><td>5</td><td>5</td><td>5</td><td>0.0%</td></tr>
      <tr><td colspan="3"><strong>Total remaining parts</strong></td><td><strong>5</strong></td><td><strong>5</strong></td><td><strong>5</strong></td><td><strong>0.0%</strong></td></tr>
    </tbody>
  </table>
</details>
<br>

Scenario 04 (exp15) demonstrated a component count deviation of -2.9% (see Table 5.4a). The simulation completed five POs, whereas the real experiment completed six. The deviation of -16.7% for BSA is attributable to a reduced number of POs progressing to the rear axle disassembly. The remaining parts count deviation was -16.7% (see Table 5.4b).
<details>
<summary><strong>Table 5.4a.</strong> Component counts (scenario 04, exp15)</summary>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Code</th>
        <th rowspan="2">Description</th>
        <th rowspan="2"># per car</th>
        <th colspan="1">Simulated data</th>
        <th colspan="2">Factory data</th>
        <th rowspan="2">Deviation</th>
      </tr>
      <tr>
        <th>Count</th>
        <th># POs</th>
        <th>Count</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>BOSP</td><td>Body + Spoiler</td><td>1+1</td><td>20</td><td>10</td><td>20</td><td>0.0%</td></tr>
      <tr><td>BAT</td><td>Battery</td><td>1</td><td>10</td><td>10</td><td>10</td><td>0.0%</td></tr>
      <tr><td>RT</td><td>Rear Tires</td><td>2</td><td>19</td><td>9</td><td>18</td><td>+5.6%</td></tr>
      <tr><td>FT</td><td>Front Tires</td><td>2</td><td>16</td><td>8</td><td>16</td><td>0.0%</td></tr>
      <tr><td>SSA</td><td>Small Shock Absorbers</td><td>2</td><td>13</td><td>7</td><td>14</td><td>-7.1%</td></tr>
      <tr><td>CHS</td><td>Chassis</td><td>1</td><td>6</td><td>6</td><td>6</td><td>0.0%</td></tr>
      <tr><td>BSA</td><td>Big Shock Absorbers</td><td>2</td><td>10</td><td>6</td><td>12</td><td>-16.7%</td></tr>
      <tr><td>FAX</td><td>Front Axle</td><td>1</td><td>6</td><td>7</td><td>7</td><td>-14.3%</td></tr>
      <tr><td colspan="3"><strong>Total components</strong></td><td><strong>100</strong></td><td><strong>63</strong></td><td><strong>103</strong></td><td><strong>-2.9%</strong></td></tr>
    </tbody>
  </table>

**Note:** FAX is a target component in this scenario and is therefore listed as a component, not as a remaining part.

</details>

<details>
<summary><strong>Table 5.4b.</strong> Remaining parts (scenario 04, exp15)</summary>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Code</th>
        <th rowspan="2">Description</th>
        <th rowspan="2"># per car</th>
        <th colspan="1">Simulated data</th>
        <th colspan="2">Factory data</th>
        <th rowspan="2">Deviation</th>
      </tr>
      <tr>
        <th>Count</th>
        <th># POs</th>
        <th>Count</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>RAX (HD)</td><td>Rear axis</td><td>1</td><td>5</td><td>6</td><td>6</td><td>-16.7%</td></tr>
      <tr><td colspan="3"><strong>Total remaining parts</strong></td><td><strong>5</strong></td><td><strong>6</strong></td><td><strong>6</strong></td><td><strong>-16.7%</strong></td></tr>
    </tbody>
  </table>
</details>
<br>

Scenario 05 (exp16) reached a component count deviation of 0.0%, as all POs were completed in both the simulation and the real experiment (see Table 5.5a). The remaining parts count deviation was also 0.0% (see Table 5.5b).
<details>
<summary><strong>Table 5.5a.</strong> Component counts (scenario 05, exp16)</summary>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Code</th>
        <th rowspan="2">Description</th>
        <th rowspan="2"># per car</th>
        <th colspan="1">Simulated data</th>
        <th colspan="2">Factory data</th>
        <th rowspan="2">Deviation</th>
      </tr>
      <tr>
        <th>Count</th>
        <th># POs</th>
        <th>Count</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>BOSP</td><td>Body + Spoiler</td><td>1+1</td><td>18</td><td>9</td><td>18</td><td>0.0%</td></tr>
      <tr><td>BAT</td><td>Battery</td><td>1</td><td>7</td><td>7</td><td>7</td><td>0.0%</td></tr>
      <tr><td>RT</td><td>Rear Tires</td><td>2</td><td>20</td><td>10</td><td>20</td><td>0.0%</td></tr>
      <tr><td>FT</td><td>Front Tires</td><td>2</td><td>16</td><td>8</td><td>16</td><td>0.0%</td></tr>
      <tr><td>SSA</td><td>Small Shock Absorbers</td><td>2</td><td>14</td><td>7</td><td>14</td><td>0.0%</td></tr>
      <tr><td>CHS/CORE</td><td>Chassis/Core</td><td>1</td><td>8</td><td>8</td><td>8</td><td>0.0%</td></tr>
      <tr><td>BSA</td><td>Big Shock Absorbers</td><td>2</td><td>18</td><td>9</td><td>18</td><td>0.0%</td></tr>
      <tr><td>FAX</td><td>Front Axle</td><td>1</td><td>6</td><td>6</td><td>6</td><td>0.0%</td></tr>
      <tr><td colspan="3"><strong>Total components</strong></td><td><strong>107</strong></td><td><strong>64</strong></td><td><strong>107</strong></td><td><strong>0.0%</strong></td></tr>
    </tbody>
  </table>

**Note:** FAX is a target component in this scenario and is therefore listed as a component, not as a remaining part. CHS/CORE denote the same component. The SA car (PO 05) has no BOSP step; the BOSP events recorded under PO-05 in the raw data belong to another car (RD condition), so BOSP was removed from 9 POs.

</details>

<details>
<summary><strong>Table 5.5b.</strong> Remaining parts (scenario 05, exp16)</summary>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Code</th>
        <th rowspan="2">Description</th>
        <th rowspan="2"># per car</th>
        <th colspan="1">Simulated data</th>
        <th colspan="2">Factory data</th>
        <th rowspan="2">Deviation</th>
      </tr>
      <tr>
        <th>Count</th>
        <th># POs</th>
        <th>Count</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>RAX (HD)</td><td>Rear axis</td><td>1</td><td>6</td><td>6</td><td>6</td><td>0.0%</td></tr>
      <tr><td>RAX (RD)</td><td>Rear axis</td><td>1</td><td>2</td><td>2</td><td>2</td><td>0.0%</td></tr>
      <tr><td>CRE (TL)</td><td>Chassis, remaining systems, engine</td><td>1</td><td>1</td><td>1</td><td>1</td><td>0.0%</td></tr>
      <tr><td>CSEB-NABS (SA)</td><td>Chassis, systems, engine, body</td><td>1</td><td>1</td><td>1</td><td>1</td><td>0.0%</td></tr>
      <tr><td colspan="3"><strong>Total remaining parts</strong></td><td><strong>10</strong></td><td><strong>10</strong></td><td><strong>10</strong></td><td><strong>0.0%</strong></td></tr>
    </tbody>
  </table>
</details>
<br>

Scenario 06 (exp17) showed component count deviations of -12.6% in the baseline run (Table 5.6a) and -2.3% in the calibrated sensitivity run (Table 5.6a [s]). The baseline deviation is attributable to incomplete product processing as a consequence of the WS-02 bottleneck (98.5% utilization): POs 6 and 8 to 10 were not completed within the simulation time. After the throughput calibration, only POs 8 and 9 remained incomplete, which reduced the deviation to -2.3%. The remaining parts count deviations were -40.0% for the baseline run (Table 5.6b) and -20.0% for the sensitivity run (Table 5.6b [s]).
<details>
<summary><strong>Table 5.6a.</strong> Component counts (scenario 06, exp17)</summary>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Code</th>
        <th rowspan="2">Description</th>
        <th rowspan="2"># per car</th>
        <th colspan="1">Simulated data</th>
        <th colspan="2">Factory data</th>
        <th rowspan="2">Deviation</th>
      </tr>
      <tr>
        <th>Count</th>
        <th># POs</th>
        <th>Count</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>BOSP</td><td>Body + Spoiler</td><td>1+1</td><td>14</td><td>7</td><td>14</td><td>0.0%</td></tr>
      <tr><td>BAT</td><td>Battery</td><td>1</td><td>4</td><td>4</td><td>4</td><td>0.0%</td></tr>
      <tr><td>RT</td><td>Rear Tires</td><td>2</td><td>18</td><td>10</td><td>20</td><td>-10.0%</td></tr>
      <tr><td>FT</td><td>Front Tires</td><td>2</td><td>13</td><td>7</td><td>14</td><td>-7.1%</td></tr>
      <tr><td>SSA</td><td>Small Shock Absorbers</td><td>2</td><td>10</td><td>6</td><td>12</td><td>-16.7%</td></tr>
      <tr><td>CHS/CORE</td><td>Chassis/Core</td><td>1</td><td>4</td><td>6</td><td>6</td><td>-33.3%</td></tr>
      <tr><td>BSA</td><td>Big Shock Absorbers</td><td>2</td><td>11</td><td>7</td><td>14</td><td>-21.4%</td></tr>
      <tr><td>FAX</td><td>Front Axle</td><td>1</td><td>2</td><td>3</td><td>3</td><td>-33.3%</td></tr>
      <tr><td colspan="3"><strong>Total components</strong></td><td><strong>76</strong></td><td><strong>50</strong></td><td><strong>87</strong></td><td><strong>-12.6%</strong></td></tr>
    </tbody>
  </table>

**Note:** CHS/CORE denote the same component. In the real experiment, the front axle was recorded as FAXS (not separated) and is counted as one front axle. The removal of BOSP from PO 10 (SA) deviated from the process plan and is not counted, so BOSP was removed from 7 POs.

</details>

<details>
<summary><strong>Table 5.6a [s].</strong> Component counts (scenario 06 sensitivity, exp17s)</summary>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Code</th>
        <th rowspan="2">Description</th>
        <th rowspan="2"># per car</th>
        <th colspan="1">Simulated data</th>
        <th colspan="2">Factory data</th>
        <th rowspan="2">Deviation</th>
      </tr>
      <tr>
        <th>Count</th>
        <th># POs</th>
        <th>Count</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>BOSP</td><td>Body + Spoiler</td><td>1+1</td><td>14</td><td>7</td><td>14</td><td>0.0%</td></tr>
      <tr><td>BAT</td><td>Battery</td><td>1</td><td>4</td><td>4</td><td>4</td><td>0.0%</td></tr>
      <tr><td>RT</td><td>Rear Tires</td><td>2</td><td>20</td><td>10</td><td>20</td><td>0.0%</td></tr>
      <tr><td>FT</td><td>Front Tires</td><td>2</td><td>14</td><td>7</td><td>14</td><td>0.0%</td></tr>
      <tr><td>SSA</td><td>Small Shock Absorbers</td><td>2</td><td>11</td><td>6</td><td>12</td><td>-8.3%</td></tr>
      <tr><td>CHS/CORE</td><td>Chassis/Core</td><td>1</td><td>6</td><td>6</td><td>6</td><td>0.0%</td></tr>
      <tr><td>BSA</td><td>Big Shock Absorbers</td><td>2</td><td>14</td><td>7</td><td>14</td><td>0.0%</td></tr>
      <tr><td>FAX</td><td>Front Axle</td><td>1</td><td>2</td><td>3</td><td>3</td><td>-33.3%</td></tr>
      <tr><td colspan="3"><strong>Total components</strong></td><td><strong>85</strong></td><td><strong>50</strong></td><td><strong>87</strong></td><td><strong>-2.3%</strong></td></tr>
    </tbody>
  </table>

**Note:** CHS/CORE denote the same component. In the real experiment, the front axle was recorded as FAXS (not separated) and is counted as one front axle. The removal of BOSP from PO 10 (SA) deviated from the process plan and is not counted, so BOSP was removed from 7 POs.

</details>

<details>
<summary><strong>Table 5.6b.</strong> Remaining parts (scenario 06, exp17)</summary>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Code</th>
        <th rowspan="2">Description</th>
        <th rowspan="2"># per car</th>
        <th colspan="1">Simulated data</th>
        <th colspan="2">Factory data</th>
        <th rowspan="2">Deviation</th>
      </tr>
      <tr>
        <th>Count</th>
        <th># POs</th>
        <th>Count</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>RAX (HD)</td><td>Rear axis</td><td>1</td><td>1</td><td>3</td><td>3</td><td>-66.7%</td></tr>
      <tr><td>RAX (RD)</td><td>Rear axis</td><td>1</td><td>2</td><td>3</td><td>3</td><td>-33.3%</td></tr>
      <tr><td>CRE (TL)</td><td>Chassis, remaining systems, engine</td><td>1</td><td>1</td><td>1</td><td>1</td><td>0.0%</td></tr>
      <tr><td>CSEB-NABS (SA)</td><td>Chassis, systems, engine, body</td><td>1</td><td>2</td><td>3</td><td>3</td><td>-33.3%</td></tr>
      <tr><td colspan="3"><strong>Total remaining parts</strong></td><td><strong>6</strong></td><td><strong>10</strong></td><td><strong>10</strong></td><td><strong>-40.0%</strong></td></tr>
    </tbody>
  </table>
</details>

<details>
<summary><strong>Table 5.6b [s].</strong> Remaining parts (scenario 06 sensitivity, exp17s)</summary>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Code</th>
        <th rowspan="2">Description</th>
        <th rowspan="2"># per car</th>
        <th colspan="1">Simulated data</th>
        <th colspan="2">Factory data</th>
        <th rowspan="2">Deviation</th>
      </tr>
      <tr>
        <th>Count</th>
        <th># POs</th>
        <th>Count</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>RAX (HD)</td><td>Rear axis</td><td>1</td><td>2</td><td>3</td><td>3</td><td>-33.3%</td></tr>
      <tr><td>RAX (RD)</td><td>Rear axis</td><td>1</td><td>2</td><td>3</td><td>3</td><td>-33.3%</td></tr>
      <tr><td>CRE (TL)</td><td>Chassis, remaining systems, engine</td><td>1</td><td>1</td><td>1</td><td>1</td><td>0.0%</td></tr>
      <tr><td>CSEB-NABS (SA)</td><td>Chassis, systems, engine, body</td><td>1</td><td>3</td><td>3</td><td>3</td><td>0.0%</td></tr>
      <tr><td colspan="3"><strong>Total remaining parts</strong></td><td><strong>8</strong></td><td><strong>10</strong></td><td><strong>10</strong></td><td><strong>-20.0%</strong></td></tr>
    </tbody>
  </table>
</details>





<br>

---

<br>

## References

#### Jordan et al. 2025
Jordan, P., Streibel, L., Lindholm, N., Maroof, W., Vernim, S., Goebel, L. and Zaeh, M.F., 2025. Demonstrator-based implementation of an infrastructure for event data acquisition in disassembly material flows. Procedia CIRP, 134, pp.277-282. https://doi.org/10.1016/j.procir.2025.03.040 <br>
GitHub Repository: https://github.com/iwb/ce-dascen-lf-data

#### Hopp & Spearman 2011
Hopp, W. J. and Spearman, M. L., 2011. Factory physics. 3rd ed., 3rd reissue. Long Grove, Ill.: Waveland Press. ISBN: 978-1-57766-739-1.

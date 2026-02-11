# Experiments Overview

> **🔬 Research Software Notice**: This document is part of a research prototype (2025-09) and serves as implementation guidance. Scientific references are included for contextual understanding and further reading only. The peer-reviewed scientific contribution can only be found in the published article.

This document provides an overview of the 17 experiments included in the disassembly simulation framework. The experiments were divided into two categories: verification experiments, which tested framework features; and validation experiments, which compared simulation results against real-world data.


## Table of Contents

- [1. Verification Experiments (exp01-11)](#1-verification-experiments-exp01-11)
- [2. Validation Experiments (exp12-17)](#2-validation-experiments-exp12-17)
  - [2.1 Validation Methodology](#21-validation-methodology)
  - [2.2 Experiment Configurations](#22-experiment-configurations)
  - [2.3 Validation Results](#23-validation-results)
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

For detailed information about the validation data, system layouts, process times, and real-world results, please refer to the associated repository, available at: [ce-disassembly-lf-dataset](https://github.com/iwb/ce-disassembly-lf-dataset)

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
      <td>-0.8%</td>
      <td>+3.7%</td>
      <td>-28.0%</td>
      <td>-6.7%</td>
      <td>+4.6%</td>
      <td>+11.3%</td>
      <td>+12.9%</td>
      <td>+1.5%</td>
      <td>Tables 3.1–3.6</td>
    </tr>
    <tr>
      <td>Utilization deviation<sup>[2]</sup></td>
      <td>+2.1%</td>
      <td>+3.5%</td>
      <td>+4.2%</td>
      <td>+1.8%</td>
      <td>+7.6%</td>
      <td>-3.7%</td>
      <td>-5.7%</td>
      <td>-2.1%</td>
      <td>Tables 4.1–4.6</td>
    </tr>
    <tr>
      <td>Component count deviation<sup>[3]</sup></td>
      <td>-4.2%</td>
      <td>-0.9%</td>
      <td>+40%</td>
      <td>0%</td>
      <td>-16.7%</td>
      <td>0%</td>
      <td>-37.3%</td>
      <td>0%</td>
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

- [1] Lead time deviation: (Simulated avg - Real avg) / Real avg × 100%
- [2] Utilization deviation: Simulated avg - Real avg (%)
- [3] Component count deviation: (Simulated - Real) / Real × 100%
- [4] Assessment: Pass = within ±20% tolerance

</details>

<br>

**Conclusion**

The six validation scenarios demonstrated the validity of the framework, with five of the six scenarios passing a ±20% validation threshold. Two scenarios required sensitivity adjustments: Scenario 03 was calibrated using a queue delay adjustment to account for the high process variability (CV = 79.4%), improving the deviation from -28.0% to -6.7%. Scenario 06 was recalibrated with reduced processing times to investigate a bottleneck behavior. The recalibration confirmed that the FIFO routing constraint was the limiting factor rather than a modeling error.

For more insights into the validation results, please refer to the associated scientific article.

<br>

---

<br>

<!-- ================================================== -->
<!-- DETAILED RESULTS - LEAD TIMES -->
<!-- ================================================== -->
## 3. Detailed Results - Lead Times

This section presents the detailed product-level lead time data from each validation scenario. All times are in **simulation minutes** (1 sim minute = 1 real second due to 60x scaling).

The following tables show the data for each production order (PO, identified by caseID), including the product quality type (RD = Rear Damage, HD = Hail Damage, SA = Shock Absorber, TL = Total Loss), the delivery time when the product entered the system, and the exit time when the disassembly was completed. The lead time represents the total time in the system (Exit - Delivery). The lead time deviation indicates the percentage difference between the simulated and actual measurements, calculated as  (Simulated - Real) / Real &middot; 100%.

> **⚠️ Note**
> The value-creating time (VT) represents the deterministic disassembly processing time and remains consistent for products of the same type and scenario. The non-value creating time (NCT) captures blocking and waiting times due to downstream congestion and varies based on the system state. Products arriving later in the experiment typically experience higher a NCT as workstations become congested.

<br>

---

<br>

Scenario 01 (exp12) achieved an average lead time deviation of -0.8%, demonstrating an alignment with the real-world data for the 3-workstation line layout processing mixed product types (6RD/2TL/2SA). The individual PO deviations ranged from -17.0% to +14.9%. The NCT ranged from 90 to 745 minutes, reflecting the system congestion of later products. The average NCT of 378 minutes indicates a moderate congestion in the system (see Table 3.1).

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
    <tr><td>10</td><td>SA</td><td>1800.0</td><td>2371.5</td><td>236.0</td><td>296.9</td><td>571.5</td><td>330</td><td>616</td><td>-7.2%</td></tr>
    <tr><td><strong>Avg</strong></td><td>-</td><td>-</td><td>-</td><td><strong>409.9</strong></td><td><strong>377.5</strong></td><td><strong>827.0</strong></td><td><strong>430.9</strong></td><td><strong>833.5</strong></td><td><strong>-0.8%</strong></td></tr>
  </tbody>
</table>

</details>

<br>

Scenario 02 (exp13) achieved an average lead time deviation of +3.7% in the 4-workstation workshop layout. The NCT increased significantly for POs 5-7 (855-885 min vs 43-49 min for POs 1-4) due to severe blocking, demonstrating the ability of the model to capture congestion dynamics in high-utilization scenarios. <br>
**Note:** POs 9 and 10 were not fully completed in both the simulation and the real experiment. The lead time comparison in Table 3.2 is based on completed POs 1-8 only.

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
    <tr><td>8</td><td>HD</td><td>435.0</td><td>2346.1</td><td>1008.7</td><td>872.3</td><td>1911.1</td><td>930</td><td>1786</td><td>+7.0%</td></tr>
    <tr><td>9</td><td>HD</td><td>480.0</td><td>2341.5</td><td>97.0</td><td>1725.4</td><td>1861.5</td><td>149</td><td>-</td><td>-</td></tr>
    <tr><td>10</td><td>HD</td><td>540.0</td><td>2343.1</td><td>97.0</td><td>1699.3</td><td>1803.1</td><td>165</td><td>-</td><td>-</td></tr>
    <tr><td><strong>Avg (1-8)</strong></td><td>-</td><td>-</td><td>-</td><td><strong>1079.2</strong></td><td><strong>459.8</strong></td><td><strong>1575.8</strong></td><td><strong>1097</strong></td><td><strong>1520</strong></td><td><strong>+3.7%</strong></td></tr>
  </tbody>
</table>

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

Example calculation (FAXG on ws-03): <br>
t<sub>e</sub> = 170s (baseline), c<sub>e</sub> = 135/170 = 0.794 (StdDev/Mean), μ = 0.710 (baseline simulation) <br>
t<sub>adjusted</sub> = 170 · [1 + (0.794² / 2) · 0.710 / (1 – 0.710)] = 170 · [1 + 0.315 · 2.448] = 170 · 1.771 = 301s <br>

</details>
<br>

The NCT ranged from 25.6 to 834.3 minutes for POs 1–5, reflecting the progressive system congestion. The VUT adjustment successfully reduced the lead time deviation to -6.7%, aligning the model within the acceptable validation threshold. <br>
For more details on queuing delays, please refer to Hopp & Spearman (2011). <br>
**Note:** Lead times were only available for POs 1-5 in the real data, and the deviation calculations in Table 3.3 are based on these POs only. The column labeled **[s]** indicates the sensitivity run.

<details>
<summary><strong>Table 3.3.</strong> Lead times (scenario 03, exp14, exp14s)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">PO</th>
      <th rowspan="2">Type</th>
      <th rowspan="2">Delivery (min)</th>
      <th colspan="8">Simulated data</th>
      <th colspan="2">Factory data</th>
      <th colspan="2">Lead time Dev.</th>
    </tr>
    <tr>
      <th>Exit</th>
      <th>Exit [s]</th>
      <th>VT</th>
      <th>VT [s]</th>
      <th>NCT</th>
      <th>NCT [s]</th>
      <th>Lead time</th>
      <th>Lead time [s]</th>
      <th>Handling time</th>
      <th>Lead time</th>
      <th>Dev.</th>
      <th>Dev. [s]</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>1</td><td>HD</td><td>0.0</td><td>843.9</td><td>1083.1</td><td>700.3</td><td>1027.3</td><td>109.9</td><td>25.6</td><td>843.9</td><td>1083.1</td><td>910</td><td>1066</td><td>-20.8%</td><td>+1.6%</td></tr>
    <tr><td>2</td><td>HD</td><td>90.0</td><td>1084.5</td><td>1358.5</td><td>823.3</td><td>1027.3</td><td>258.1</td><td>209.2</td><td>994.5</td><td>1268.5</td><td>752</td><td>1636</td><td>-39.2%</td><td>-22.5%</td></tr>
    <tr><td>3</td><td>HD</td><td>180.0</td><td>1321.5</td><td>1656.9</td><td>823.3</td><td>1027.3</td><td>278.3</td><td>416.2</td><td>1141.5</td><td>1476.9</td><td>720</td><td>1186</td><td>-3.7%</td><td>+24.5%</td></tr>
    <tr><td>4</td><td>HD</td><td>270.0</td><td>1563.0</td><td>1958.5</td><td>823.3</td><td>1027.3</td><td>410.4</td><td>627.7</td><td>1293.0</td><td>1688.5</td><td>848</td><td>2027</td><td>-36.2%</td><td>-16.7%</td></tr>
    <tr><td>5</td><td>HD</td><td>360.0</td><td>1803.0</td><td>2256.9</td><td>823.3</td><td>1027.3</td><td>561.9</td><td>834.3</td><td>1443.0</td><td>1896.9</td><td>600</td><td>2027</td><td>-28.8%</td><td>-6.4%</td></tr>
    <tr><td>6</td><td>HD</td><td>450.0</td><td>2016.5</td><td>2341.5</td><td>823.3</td><td>911.2</td><td>688.4</td><td>943.5</td><td>1566.5</td><td>1891.5</td><td>707</td><td>-</td><td>-</td><td>-</td></tr>
    <tr><td>7</td><td>HD</td><td>600.0</td><td>2251.5</td><td>1894.9</td><td>823.3</td><td>355.0</td><td>773.2</td><td>906.4</td><td>1651.5</td><td>1294.9</td><td>909</td><td>-</td><td>-</td><td>-</td></tr>
    <tr><td>8</td><td>HD</td><td>630.0</td><td>2374.9</td><td>2134.9</td><td>768.7</td><td>355.0</td><td>937.7</td><td>1112.2</td><td>1744.9</td><td>1504.9</td><td>858</td><td>-</td><td>-</td><td>-</td></tr>
    <tr><td>9</td><td>HD</td><td>780.0</td><td>2193.4</td><td>2374.9</td><td>590.1</td><td>355.0</td><td>767.7</td><td>1206.4</td><td>1413.4</td><td>1594.9</td><td>645</td><td>-</td><td>-</td><td>-</td></tr>
    <tr><td>10</td><td>HD</td><td>840.0</td><td>2373.4</td><td>1173.4</td><td>590.1</td><td>111.0</td><td>891.1</td><td>188.9</td><td>1533.4</td><td>333.4</td><td>605</td><td>-</td><td>-</td><td>-</td></tr>
    <tr><td><strong>Avg (1-5)</strong></td><td>-</td><td>-</td><td><strong>1323.2</strong></td><td>-</td><td><strong>798.7</strong></td><td>-</td><td><strong>323.7</strong></td><td>-</td><td><strong>1143.2</strong></td><td>-</td><td><strong>766</strong></td><td><strong>1588</strong></td><td><strong>-28.0%</strong></td><td>-</td></tr>
    <tr><td><strong>Avg (1-5) [s]</strong></td><td>-</td><td>-</td><td>-</td><td><strong>1662.8</strong></td><td>-</td><td><strong>1027.3</strong></td><td>-</td><td><strong>422.6</strong></td><td>-</td><td><strong>1482.8</strong></td><td><strong>766</strong></td><td><strong>1588</strong></td><td>-</td><td><strong>-6.7%</strong></td></tr>
  </tbody>
</table>

</details>

<br>

Scenario 04 (exp15) demonstrated an average lead time deviation of +4.6% for a workshop layout with a centralized FIFO buffer, processing HD products manually. The NCT variation was significant (73-1002 min) due to the FIFO routing constraint and buffer blocking, indicating bottleneck behavior at stations S1 to S4 that constrained throughput, irrespective of the available downstream capacity. <br>
**Note:** POs 7-10 were not fully completed in the real experiment due to the 40-hour time constraint. The lead time comparison in Table 3.4 is based on the completed POs 1-6 only.

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
    <tr><td>6</td><td>HD</td><td>450.0</td><td>2371.5</td><td>1053.2</td><td>797.6</td><td>1921.5</td><td>946</td><td>1832</td><td>+4.9%</td></tr>
    <tr><td>7</td><td>HD</td><td>600.0</td><td>2343.1</td><td>784.6</td><td>886.9</td><td>1743.1</td><td>763</td><td>-</td><td>-</td></tr>
    <tr><td>8</td><td>HD</td><td>810.0</td><td>2073.1</td><td>483.0</td><td>898.1</td><td>1263.1</td><td>390</td><td>-</td><td>-</td></tr>
    <tr><td>9</td><td>HD</td><td>930.0</td><td>2311.5</td><td>404.5</td><td>1002.0</td><td>1381.5</td><td>345</td><td>-</td><td>-</td></tr>
    <tr><td>10</td><td>HD</td><td>1200.0</td><td>2341.5</td><td>326.0</td><td>823.0</td><td>1141.5</td><td>165</td><td>-</td><td>-</td></tr>
    <tr><td><strong>Avg (1-6)</strong></td><td>-</td><td>-</td><td>-</td><td><strong>1183.4</strong></td><td><strong>419.0</strong></td><td><strong>1673.1</strong></td><td><strong>1243</strong></td><td><strong>1599</strong></td><td><strong>+4.6%</strong></td></tr>
  </tbody>
</table>

</details>

<br>

Scenario 05 (exp16) demonstrated an average lead time deviation of +11.3% for a mixed product scenario (6HD/1TL/1SA/2RD) in a workshop layout. The NCT ranged from 49 to 738 minutes across the mixed-product scenario, with RD products experiencing the highest blocking (avg. 721 min NCT at POs 6 and 8) due to congestion. As shown in Table 3.5, individual PO deviations vary significantly by product type (ranging from -28.9% to +59.1%), due to different queuing patterns between the simulation and reality. <br>
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
    <tr><td>9</td><td>HD</td><td>540.0</td><td>2251.5</td><td>997.3</td><td>675.9</td><td>1711.5</td><td>1137</td><td>1456</td><td>+17.5%</td></tr>
    <tr><td>10</td><td>HD</td><td>600.0</td><td>1771.5</td><td>997.3</td><td>136.6</td><td>1171.5</td><td>915</td><td>1456</td><td>-19.5%</td></tr>
    <tr><td><strong>Avg</strong></td><td>-</td><td>-</td><td>-</td><td><strong>789.0</strong></td><td><strong>262.0</strong></td><td><strong>1091.4</strong></td><td><strong>801</strong></td><td><strong>981</strong></td><td><strong>+11.3%</strong></td></tr>
  </tbody>
</table>

</details>

<br>

Scenario 06 (exp17) demonstrated a baseline deviation of +12.9% for a mixed product scenario (3HD/3SA/3RD/1TL) in a 5-workstation line layout. The NCT demonstrated significant variation (43-1535 min), primarily attributable to the critical bottleneck at S3S4, which exhibited 98.5% utilization. Products requiring this station encountered severe blocking, regardless of their specific routing. <br>
**Note:** in the baseline run, POs 8-10 did not fully complete within the simulation time due to the bottleneck. Therefore, the average deviation in Table 3.6 has been calculated for completed POs 1-7 only. The column labeled with **[s]** represents the sensitivity analysis (exp17s), where RT and FT processing times were reduced by 20% (RT: 81.5→65 min, FT: 62→50 min) to match the observed WS-02 throughput. This empirical calibration improved the average lead time deviation from +12.9% to +1.5% and enabled all 10 POs to complete successfully.

<details>
<summary><strong>Table 3.6.</strong> Lead times (scenario 06, exp17, exp17s)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">PO</th>
      <th rowspan="2">Type</th>
      <th rowspan="2">Delivery (min)</th>
      <th colspan="6">Simulated data</th>
      <th colspan="2">Factory data</th>
      <th colspan="2">Lead time Dev.</th>
    </tr>
    <tr>
      <th>VT</th>
      <th>NCT</th>
      <th>Lead time</th>
      <th>Lead time [s]</th>
      <th>Handling time</th>
      <th>Handling time [s]</th>
      <th>Handling time</th>
      <th>Lead time</th>
      <th>Dev.</th>
      <th>Dev. [s]</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>1</td><td>SA</td><td>0.0</td><td>582.1</td><td>43.3</td><td>666</td><td>607</td><td>636.3</td><td>577.1</td><td>435</td><td>691</td><td>-3.6%</td><td>-12.2%</td></tr>
    <tr><td>2</td><td>RD</td><td>90.0</td><td>510.1</td><td>198.7</td><td>753</td><td>693</td><td>720.3</td><td>660.4</td><td>708</td><td>737</td><td>+2.2%</td><td>-6.0%</td></tr>
    <tr><td>3</td><td>HD</td><td>180.0</td><td>1053.3</td><td>480.6</td><td>1413</td><td>1262</td><td>1376.2</td><td>1226.2</td><td>1102</td><td>1397</td><td>+1.1%</td><td>-9.7%</td></tr>
    <tr><td>4</td><td>TL</td><td>270.0</td><td>436.1</td><td>637.7</td><td>1112</td><td>872</td><td>1078.1</td><td>838.1</td><td>426</td><td>669</td><td>+66.2%</td><td>+30.3%</td></tr>
    <tr><td>5</td><td>SA</td><td>360.0</td><td>582.1</td><td>488.3</td><td>1112</td><td>966</td><td>1076.2</td><td>929.5</td><td>516</td><td>1036</td><td>+7.3%</td><td>-6.8%</td></tr>
    <tr><td>6</td><td>HD</td><td>450.0</td><td>784.2</td><td>884.6</td><td>1658</td><td>1802</td><td>1626.3</td><td>1768.1</td><td>889</td><td>1396</td><td>+18.8%</td><td>+29.1%</td></tr>
    <tr><td>7</td><td>RD</td><td>540.0</td><td>510.1</td><td>1066.7</td><td>1622</td><td>1293</td><td>1585.0</td><td>1258.1</td><td>495</td><td>1456</td><td>+11.4%</td><td>-11.2%</td></tr>
    <tr><td>8</td><td>HD</td><td>630.0</td><td>436.0</td><td>1265.8</td><td>1712*</td><td>1713</td><td>1673.1*</td><td>1681.5</td><td>1011</td><td>-</td><td>-</td><td>-</td></tr>
    <tr><td>9</td><td>RD</td><td>720.0</td><td>78.0</td><td>1534.7</td><td>274*</td><td>1473</td><td>237.4*</td><td>1436.5</td><td>660</td><td>1546</td><td>incomplete</td><td>-4.7%</td></tr>
    <tr><td>10</td><td>SA</td><td>810.0</td><td>521.0</td><td>999.8</td><td>1562*</td><td>1322</td><td>1526.5*</td><td>1287.2</td><td>463</td><td>-</td><td>-</td><td>-</td></tr>
    <tr><td><strong>Avg (1-7)</strong></td><td>-</td><td>-</td><td><strong>637.0</strong></td><td><strong>542.9</strong></td><td><strong>1191</strong></td><td>-</td><td><strong>1157</strong></td><td>-</td><td><strong>653</strong></td><td><strong>1055</strong></td><td><strong>+12.9%</strong></td><td>-</td></tr>
    <tr><td><strong>Avg (1-7) [s]</strong></td><td>-</td><td>-</td><td><strong>637.0</strong></td><td><strong>542.9</strong></td><td>-</td><td><strong>1071</strong></td><td>-</td><td><strong>1037</strong></td><td><strong>653</strong></td><td><strong>1055</strong></td><td>-</td><td><strong>+1.5%</strong></td></tr>
  </tbody>
</table>

</details>

<br>

---

<br>

<!-- ================================================== -->
<!-- DETAILED RESULTS - STATION STATISTICS -->
<!-- ================================================== -->
## 4. Detailed Results - Station Statistics

This section presents the station-level performance statistics from each validation scenario. All times are in **simulation minutes**.

The following tables present the data for each workstation, including the total available time (~2399 min = 40 hours in simulation), the busy time spent actively processing products, the blocked time when waiting for downstream capacity, the waiting time when idle for products, and the number of components processed (Comp.). The utilization (Util.) is a measure of the station's efficiency, calculated as Busy / Total &middot; 100%. The factory data columns present the measured values from actual experiments, including the total experiment duration (~2400 seconds), the measured busy time, the number of components processed (where available), and the measured utilization. The utilization deviation (Util. Dev.) indicates the discrepancy between the simulated and factory utilization rates in.

<br>

---

<br>

In Scenario 01 (exp12), the average utilization deviation across the three workstations was +2.1%. The deviations range from -0.2% to +5.7%, demonstrating a consistent station-level performance modeling (see Table 4.1).

<details>
<summary><strong>Table 4.1.</strong> Station statistics (scenario 01, exp12)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">Station</th>
      <th colspan="6">Simulated data</th>
      <th colspan="4">Factory data</th>
      <th rowspan="2">Util. Dev.</th>
    </tr>
    <tr>
      <th>Total</th>
      <th>Busy</th>
      <th>Blocked</th>
      <th>Waiting</th>
      <th>Comp.</th>
      <th>Util.</th>
      <th>Total</th>
      <th>Busy</th>
      <th>Comp.</th>
      <th>Util.</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ws-03_S1toS4</td><td>2399.0</td><td>2110.2</td><td>5.6</td><td>283.2</td><td>46</td><td>88.0%</td><td>2400</td><td>1975</td><td>-</td><td>82.3%</td><td>+5.7%</td></tr>
    <tr><td>ws-04_S5S7</td><td>2399.0</td><td>775.2</td><td>1.2</td><td>1622.6</td><td>6</td><td>32.3%</td><td>2400</td><td>751</td><td>-</td><td>31.3%</td><td>+1.0%</td></tr>
    <tr><td>ws-05_S6S8</td><td>2399.0</td><td>1275.2</td><td>2.4</td><td>1121.4</td><td>17</td><td>53.2%</td><td>2400</td><td>1282</td><td>-</td><td>53.4%</td><td>-0.2%</td></tr>
    <tr><td><strong>Average</strong></td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td><strong>57.8%</strong></td><td>-</td><td>-</td><td>-</td><td><strong>55.7%</strong></td><td><strong>+2.1%</strong></td></tr>
  </tbody>
</table>

</details>

<br>

Scenario 02 (exp13) demonstrated an average utilization deviation of +3.5% across the system. Individual workstation deviations ranged from -7.3% to +19.7%. <br>
**Note:** The component counts (Comp.) indicate the number of processed production orders (PO) per station. The deviations for individual stations may vary due to different PO-to-workstation assignments in the actual experiment compared to the simulated data (see Table 4.2).

<details>
<summary><strong>Table 4.2.</strong> Station statistics (scenario 02, exp13)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">Station</th>
      <th colspan="6">Simulated data</th>
      <th colspan="4">Factory data</th>
      <th rowspan="2">Util. Dev.</th>
    </tr>
    <tr>
      <th>Total</th>
      <th>Busy</th>
      <th>Blocked</th>
      <th>Waiting</th>
      <th>Comp.</th>
      <th>Util.</th>
      <th>Total</th>
      <th>Busy</th>
      <th>Comp.</th>
      <th>Util.</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ws-01_S1toS8</td><td>2399.0</td><td>2364.8</td><td>3.0</td><td>31.3</td><td>8</td><td>98.6%</td><td>2400</td><td>1894</td><td>16</td><td>78.9%</td><td>+19.7%</td></tr>
    <tr><td>ws-02_S1toS8</td><td>2399.0</td><td>2301.4</td><td>3.0</td><td>94.6</td><td>8</td><td>95.9%</td><td>2400</td><td>2206</td><td>18</td><td>91.9%</td><td>+4.0%</td></tr>
    <tr><td>ws-03_S1toS8</td><td>2399.0</td><td>2179.0</td><td>2.8</td><td>217.2</td><td>8</td><td>90.8%</td><td>2400</td><td>2232</td><td>18</td><td>93.0%</td><td>-2.2%</td></tr>
    <tr><td>ws-04_S1toS8</td><td>2399.0</td><td>2178.7</td><td>2.6</td><td>217.7</td><td>7</td><td>90.8%</td><td>2400</td><td>2354</td><td>16</td><td>98.1%</td><td>-7.3%</td></tr>
    <tr><td><strong>Average</strong></td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td><strong>94.0%</strong></td><td>-</td><td>-</td><td>-</td><td><strong>90.5%</strong></td><td><strong>+3.5%</strong></td></tr>
  </tbody>
</table>

</details>

<br>

In Scenario 03 (exp14), there was an average utilization deviation of +4.2% (baseline) and +1.8% (sensitivity). <br>
**Note:** The column labeled **[s]** represents the sensitivity run. The VUT adjustment increases processing times at stations with high variability, leading to shifts in utilization patterns (see Table 4.3).

<details>
<summary><strong>Table 4.3.</strong> Station statistics (scenario 03, exp14, exp14s)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">Station</th>
      <th colspan="4">Simulated data</th>
      <th colspan="2">Factory data</th>
      <th colspan="2">Util. Dev.</th>
    </tr>
    <tr>
      <th>Busy</th>
      <th>Busy [s]</th>
      <th>Util.</th>
      <th>Util. [s]</th>
      <th>Busy</th>
      <th>Util.</th>
      <th>Dev.</th>
      <th>Dev. [s]</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ws-01_S1S2</td><td>1092.0</td><td>1112.0</td><td>45.5%</td><td>46.4%</td><td>1178</td><td>49.1%</td><td>-3.6%</td><td>-2.7%</td></tr>
    <tr><td>ws-02_S3S4</td><td>1882.0</td><td>2243.5</td><td>78.4%</td><td>93.5%</td><td>1886</td><td>78.6%</td><td>-0.2%</td><td>+14.9%</td></tr>
    <tr><td>ws-03_S5</td><td>1703.0</td><td>1974.5</td><td>71.0%</td><td>82.3%</td><td>1178</td><td>49.1%</td><td>+21.9%</td><td>+33.2%</td></tr>
    <tr><td>ws-04_S7</td><td>1232.0</td><td>751.2</td><td>51.4%</td><td>31.3%</td><td>1387</td><td>57.8%</td><td>-6.4%</td><td>-26.5%</td></tr>
    <tr><td>ws-05_S6S8</td><td>1823.1</td><td>1363.3</td><td>76.0%</td><td>56.8%</td><td>1608</td><td>67.0%</td><td>+9.0%</td><td>-10.2%</td></tr>
    <tr><td><strong>Average</strong></td><td>-</td><td>-</td><td><strong>64.5%</strong></td><td><strong>62.1%</strong></td><td>-</td><td><strong>60.3%</strong></td><td><strong>+4.2%</strong></td><td><strong>+1.8%</strong></td></tr>
  </tbody>
</table>

</details>

<br>

Scenario 04 (exp15) showed an average utilization deviation of +7.6% across the five workstations. <br> **Note:** WS-03 shows a notably higher utilization in the simulation (+25.5%), possibly due to different PO-to-station assignment patterns between the simulation and the real experiment (see Table 4.4).

<details>
<summary><strong>Table 4.4.</strong> Station statistics (scenario 04, exp15)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">Station</th>
      <th colspan="6">Simulated data</th>
      <th colspan="4">Factory data</th>
      <th rowspan="2">Util. Dev.</th>
    </tr>
    <tr>
      <th>Total</th>
      <th>Busy</th>
      <th>Blocked</th>
      <th>Waiting</th>
      <th>Comp.</th>
      <th>Util.</th>
      <th>Total</th>
      <th>Busy</th>
      <th>Comp.</th>
      <th>Util.</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ws-01_S1toS4</td><td>2399.0</td><td>2364.0</td><td>3.8</td><td>31.3</td><td>4</td><td>98.5%</td><td>2400</td><td>2293</td><td>19</td><td>93.2%</td><td>+5.3%</td></tr>
    <tr><td>ws-02_S1toS4</td><td>2399.0</td><td>2270.7</td><td>3.7</td><td>124.6</td><td>4</td><td>94.7%</td><td>2400</td><td>2190</td><td>18</td><td>89.0%</td><td>+5.7%</td></tr>
    <tr><td>ws-03_S5toS8</td><td>2399.0</td><td>1826.7</td><td>1.5</td><td>570.9</td><td>7</td><td>76.1%</td><td>2400</td><td>1246</td><td>8</td><td>50.6%</td><td>+25.5%</td></tr>
    <tr><td>ws-04_S5toS8</td><td>2399.0</td><td>1596.0</td><td>1.4</td><td>801.7</td><td>6</td><td>66.5%</td><td>2400</td><td>1620</td><td>8</td><td>65.8%</td><td>+0.7%</td></tr>
    <tr><td>ws-05_S5toS8</td><td>2399.0</td><td>1345.5</td><td>1.1</td><td>1052.4</td><td>5</td><td>56.1%</td><td>2400</td><td>1364</td><td>10</td><td>55.4%</td><td>+0.7%</td></tr>
    <tr><td><strong>Average</strong></td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td><strong>78.4%</strong></td><td>-</td><td>-</td><td>-</td><td><strong>70.8%</strong></td><td><strong>+7.6%</strong></td></tr>
  </tbody>
</table>

</details>

<br>

Scenario 05 (exp16) showed an average utilization deviation of -3.7%. Individual station deviations ranged from -27.8% to +29.4%. <br>
**Note:** The significant variation reflects different PO-to-station assignment patterns. The simulation was configured to utilize FIFO load balancing, which distributed the workload differently than in the real experiments (see Table 4.5).

<details>
<summary><strong>Table 4.5.</strong> Station statistics (scenario 05, exp16)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">Station</th>
      <th colspan="6">Simulated data</th>
      <th colspan="4">Factory data</th>
      <th rowspan="2">Util. Dev.</th>
    </tr>
    <tr>
      <th>Total</th>
      <th>Busy</th>
      <th>Blocked</th>
      <th>Waiting</th>
      <th>Comp.</th>
      <th>Util.</th>
      <th>Total</th>
      <th>Busy</th>
      <th>Comp.</th>
      <th>Util.</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ws-01_S1toS8</td><td>2399.0</td><td>1513.8</td><td>2.2</td><td>883.0</td><td>5</td><td>63.1%</td><td>2400</td><td>1950</td><td>16</td><td>90.9%</td><td>-27.8%</td></tr>
    <tr><td>ws-02_S1toS8</td><td>2399.0</td><td>1421.8</td><td>2.2</td><td>975.0</td><td>5</td><td>59.3%</td><td>2400</td><td>1201</td><td>12</td><td>56.0%</td><td>+3.3%</td></tr>
    <tr><td>ws-03_S1toS8</td><td>2399.0</td><td>1513.8</td><td>2.2</td><td>883.0</td><td>5</td><td>63.1%</td><td>2400</td><td>1486</td><td>16</td><td>69.2%</td><td>-6.1%</td></tr>
    <tr><td>ws-04_S1toS8</td><td>2399.0</td><td>1995.0</td><td>2.8</td><td>401.2</td><td>8</td><td>83.2%</td><td>2400</td><td>1155</td><td>8</td><td>53.8%</td><td>+29.4%</td></tr>
    <tr><td>ws-05_S1toS8</td><td>2399.0</td><td>1446.8</td><td>2.3</td><td>949.9</td><td>5</td><td>60.3%</td><td>2400</td><td>1665</td><td>13</td><td>77.6%</td><td>-17.3%</td></tr>
    <tr><td><strong>Average</strong></td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td><strong>65.8%</strong></td><td>-</td><td>-</td><td>-</td><td><strong>69.5%</strong></td><td><strong>-3.7%</strong></td></tr>
  </tbody>
</table>

</details>

<br>

Scenario 06 (exp17) demonstrated an average utilization deviations of -5.7% (baseline) and -2.1% (calibrated). <br>
**Note:** The column labeled **[s]** represents the throughput-calibrated sensitivity run with RT/FT processing times reduced by 20%. In the baseline, WS-02 was a bottleneck at a 98.5% utilization rate, which was adjusted in the calibrated run (83.5%), closely matching the real value (83.7%). WS-04 and WS-05 show higher utilization in the calibrated run because all 10 POs completed successfully, compared to only seven in the baseline (see Table 4.6).

<details>
<summary><strong>Table 4.6.</strong> Station statistics (scenario 06, exp17, exp17s)</summary>

<table>
  <thead>
    <tr>
      <th rowspan="2">Station</th>
      <th colspan="4">Simulated data</th>
      <th colspan="2">Factory data</th>
      <th colspan="2">Util. Dev.</th>
    </tr>
    <tr>
      <th>Busy</th>
      <th>Busy [s]</th>
      <th>Util.</th>
      <th>Util. [s]</th>
      <th>Busy</th>
      <th>Util.</th>
      <th>Dev.</th>
      <th>Dev. [s]</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>ws-01_S1S2</td><td>831.4</td><td>831.4</td><td>34.7%</td><td>34.7%</td><td>990</td><td>41.2%</td><td>-6.5%</td><td>-6.5%</td></tr>
    <tr><td>ws-02_S3S4</td><td>2362.9</td><td>2002.1</td><td>98.5%</td><td>83.5%</td><td>2009</td><td>83.7%</td><td>+14.8%</td><td>-0.2%</td></tr>
    <tr><td>ws-03_S5</td><td>350.6</td><td>525.9</td><td>14.6%</td><td>21.9%</td><td>495</td><td>20.6%</td><td>-6.0%</td><td>+1.3%</td></tr>
    <tr><td>ws-04_S7</td><td>588.8</td><td>883.2</td><td>24.5%</td><td>36.8%</td><td>1304</td><td>54.3%</td><td>-29.8%</td><td>-17.5%</td></tr>
    <tr><td>ws-05_S6S8</td><td>1574.1</td><td>1903.3</td><td>65.6%</td><td>79.3%</td><td>1604</td><td>66.8%</td><td>-1.2%</td><td>+12.5%</td></tr>
    <tr><td><strong>Average</strong></td><td>-</td><td>-</td><td><strong>47.6%</strong></td><td><strong>51.2%</strong></td><td>-</td><td><strong>53.3%</strong></td><td><strong>-5.7%</strong></td><td><strong>-2.1%</strong></td></tr>
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

This section presents the component-level output data from each validation scenario, comparing the number of disassembled components between the simulation and recorded factory data.

The component tables (see Tables 5.Xa) contain the data for each component type, identified by a code (e.g., BOSP, RT, BSA) and a full description. The "# per car" column indicates the quantity per product. A "1+1" notation indicates two separate items. The Count (Simulated) displays the number of components in the simulation output, while # POs (Factory) represents the number of production orders recorded in the factory data. The expected count is calculated as Count (# POs &middot; # per car). The remaining parts tables (see Tables 5.Xb) follow the same structure, with # per car always set to "1" for remaining parts, indicating one remaining part per production order.

<br>

---

<br>

Scenario 01 (exp12) demonstrated a total component count deviation of -4.2%, indicating a close alignment with the actual factory data (see Table 5.1a). The remaining parts count deviation was -10% (see Table 5.1b).

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
      <tr><td>BOSP</td><td>Body + Spoiler</td><td>1+1</td><td>16</td><td>8</td><td>16</td><td>0%</td></tr>
      <tr><td>RT</td><td>Rear Tires</td><td>2</td><td>20</td><td>10</td><td>20</td><td>0%</td></tr>
      <tr><td>FT</td><td>Front Tires</td><td>2</td><td>8</td><td>4</td><td>8</td><td>0%</td></tr>
      <tr><td>BAT</td><td>Battery</td><td>1</td><td>2</td><td>2</td><td>2</td><td>0%</td></tr>
      <tr><td>CORE</td><td>Engine Core</td><td>1</td><td>6</td><td>6</td><td>6</td><td>0%</td></tr>
      <tr><td>BSA</td><td>Big Shock Absorbers</td><td>2</td><td>14</td><td>8</td><td>16</td><td>-12.5%</td></tr>
      <tr><td>SSA</td><td>Small Shock Absorbers</td><td>2</td><td>3</td><td>2</td><td>4</td><td>-25%</td></tr>
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
      <tr><td>RAX (RD)</td><td>Rear axis</td><td>1</td><td>6</td><td>6</td><td>6</td><td>0%</td></tr>
      <tr><td>CRE (TL)</td><td>Chassis, remaining systems, engine</td><td>1</td><td>2</td><td>2</td><td>2</td><td>0%</td></tr>
      <tr><td>CSEB-NABS (SA)</td><td>Chassis, systems, engine, body</td><td>1</td><td>1</td><td>2</td><td>2</td><td>-50%</td></tr>
      <tr><td colspan="3"><strong>Total remaining parts</strong></td><td><strong>9</strong></td><td><strong>10</strong></td><td><strong>10</strong></td><td><strong>-10%</strong></td></tr>
    </tbody>
  </table>
</details>


<br>

Scenario 02 (exp13) achieved a total component count deviation of -0.9%, demonstrating an excellent alignment with the factory data (see Table 5.2a). The remaining parts count deviation was -12.5% (see Table 5.2b). The simulation successfully completed seven out of eight HD products.

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
      <tr><td>BOSP</td><td>Body + Spoiler</td><td>2</td><td>20</td><td>10</td><td>20</td><td>0%</td></tr>
      <tr><td>BAT</td><td>Battery</td><td>1</td><td>10</td><td>10</td><td>10</td><td>0%</td></tr>
      <tr><td>RT</td><td>Rear Tires</td><td>2</td><td>16</td><td>8</td><td>16</td><td>0%</td></tr>
      <tr><td>FT</td><td>Front Tires</td><td>2</td><td>16</td><td>8</td><td>16</td><td>0%</td></tr>
      <tr><td>SSA</td><td>Small Shock Absorbers</td><td>2</td><td>16</td><td>8</td><td>16</td><td>0%</td></tr>
      <tr><td>FAX</td><td>Front Axle</td><td>1</td><td>8</td><td>8</td><td>8</td><td>0%</td></tr>
      <tr><td>CHS</td><td>Chassis</td><td>1</td><td>8</td><td>8</td><td>8</td><td>0%</td></tr>
      <tr><td>BSA</td><td>Big Shock Absorbers</td><td>2</td><td>15</td><td>8</td><td>16</td><td>-6.3%</td></tr>
      <tr><td colspan="3"><strong>Total components</strong></td><td><strong>109</strong></td><td><strong>68</strong></td><td><strong>110</strong></td><td><strong>-0.9%</strong></td></tr>
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

Scenario 03 (exp14) showed baseline and sensitivity component count deviations of +40% and 0% respectively (see Table 5.3a). The **[s]** column signifies the sensitivity run using VUT-adjusted processing times. The baseline run completed a higher number of POs (7) due to faster processing times, while the sensitivity run matched the real completion rate (5 POs). As illustrated in Table 5.3b, the remaining parts count deviations were 40% and 0% for the baseline and sensitivity runs, respectively.

<details>
<summary><strong>Table 5.3a.</strong> Component counts (scenario 03, exp14, exp14s)</summary>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Code</th>
        <th rowspan="2">Description</th>
        <th rowspan="2"># per car</th>
        <th colspan="2">Simulated data</th>
        <th colspan="2">Factory data</th>
        <th colspan="2">Deviation</th>
      </tr>
      <tr>
        <th>Count</th>
        <th>Count [s]</th>
        <th># POs</th>
        <th>Count</th>
        <th>Dev.</th>
        <th>Dev. [s]</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>BOSP</td><td>Body + Spoiler</td><td>2</td><td>20</td><td>20</td><td>10</td><td>20</td><td>0%</td><td>0%</td></tr>
      <tr><td>BAT</td><td>Battery</td><td>1</td><td>10</td><td>10</td><td>10</td><td>10</td><td>0%</td><td>0%</td></tr>
      <tr><td>RT</td><td>Rear Tires</td><td>2</td><td>20</td><td>18</td><td>10</td><td>20</td><td>0%</td><td>-10%</td></tr>
      <tr><td>FT</td><td>Front Tires</td><td>2</td><td>20</td><td>18</td><td>10</td><td>20</td><td>0%</td><td>-10%</td></tr>
      <tr><td>SSA</td><td>Small Shock Absorbers</td><td>2</td><td>16</td><td>11</td><td>9</td><td>18</td><td>-11%</td><td>-39%</td></tr>
      <tr><td>CHS</td><td>Chassis</td><td>1</td><td>10</td><td>5</td><td>10</td><td>10</td><td>0%</td><td>-50%</td></tr>
      <tr><td>BSA</td><td>Big Shock Absorbers</td><td>2</td><td>14</td><td>10</td><td>5</td><td>10</td><td>+40%</td><td>0%</td></tr>
      <tr><td colspan="3"><strong>Total components</strong></td><td><strong>110</strong></td><td><strong>92</strong></td><td><strong>64</strong></td><td><strong>108</strong></td><td><strong>+1.9%</strong></td><td><strong>-14.8%</strong></td></tr>
    </tbody>
  </table>
</details>

<details>
<summary><strong>Table 5.3b.</strong> Remaining parts (scenario 03, exp14, exp14s)</summary>
  <table>
    <thead>
      <tr>
        <th rowspan="2">Code</th>
        <th rowspan="2">Description</th>
        <th rowspan="2"># per car</th>
        <th colspan="2">Simulated data</th>
        <th colspan="2">Factory data</th>
        <th colspan="2">Deviation</th>
      </tr>
      <tr>
        <th>Count</th>
        <th>Count [s]</th>
        <th># POs</th>
        <th>Count</th>
        <th>Dev.</th>
        <th>Dev. [s]</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>RAX (HD)</td><td>Rear axis</td><td>1</td><td>7</td><td>5</td><td>5</td><td>5</td><td>+40%</td><td>0%</td></tr>
      <tr><td colspan="3"><strong>Total remaining parts</strong></td><td><strong>7</strong></td><td><strong>5</strong></td><td><strong>5</strong></td><td><strong>5</strong></td><td><strong>+40%</strong></td><td><strong>0%</strong></td></tr>
    </tbody>
  </table>
</details>

<br>

Scenario 04 (exp15) demonstrated a component count deviation of -16.7% (see Table 5.4a). The simulation completed five POs, whereas the real data set completed six. The analysis of the data revealed a deviation of -16.7% in the BSA, attributable to a reduced number of POs progressing to the stage of the rear axis disassembly. The remaining parts count deviation was -15.4% (see Table 5.4b).

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
      <tr><td>BOSP</td><td>Body + Spoiler</td><td>2</td><td>20</td><td>10</td><td>20</td><td>0%</td></tr>
      <tr><td>BAT</td><td>Battery</td><td>1</td><td>10</td><td>10</td><td>10</td><td>0%</td></tr>
      <tr><td>RT</td><td>Rear Tires</td><td>2</td><td>18</td><td>9</td><td>18</td><td>0%</td></tr>
      <tr><td>FT</td><td>Front Tires</td><td>2</td><td>16</td><td>8</td><td>16</td><td>0%</td></tr>
      <tr><td>SSA</td><td>Small Shock Absorbers</td><td>2</td><td>14</td><td>7</td><td>14</td><td>0%</td></tr>
      <tr><td>CHS</td><td>Chassis</td><td>1</td><td>6</td><td>6</td><td>6</td><td>0%</td></tr>
      <tr><td>BSA</td><td>Big Shock Absorbers</td><td>2</td><td>10</td><td>6</td><td>12</td><td>-16.7%</td></tr>
      <tr><td colspan="3"><strong>Total components</strong></td><td><strong>94</strong></td><td><strong>56</strong></td><td><strong>96</strong></td><td><strong>-2.1%</strong></td></tr>
    </tbody>
  </table>
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
      <tr><td>FAX</td><td>Front Axle</td><td>1</td><td>6</td><td>7</td><td>7</td><td>-14.3%</td></tr>
      <tr><td>RAX (HD)</td><td>Rear axis</td><td>1</td><td>5</td><td>6</td><td>6</td><td>-16.7%</td></tr>
      <tr><td colspan="3"><strong>Total remaining parts</strong></td><td><strong>11</strong></td><td><strong>13</strong></td><td><strong>13</strong></td><td><strong>-15.4%</strong></td></tr>
    </tbody>
  </table>
</details>

<br>

Scenario 05 (exp16) reached a component count deviation of 0%, indicating a precise alignment with the factory data (see Table 5.5a). The remaining parts count deviation was found to be 0% (see Table 5.5b).

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
      <tr><td>BOSP</td><td>Body + Spoiler</td><td>2</td><td>18</td><td>10</td><td>18</td><td>0%</td></tr>
      <tr><td>BAT</td><td>Battery</td><td>1</td><td>7</td><td>7</td><td>7</td><td>0%</td></tr>
      <tr><td>RT</td><td>Rear Tires</td><td>2</td><td>20</td><td>10</td><td>20</td><td>0%</td></tr>
      <tr><td>FT</td><td>Front Tires</td><td>2</td><td>16</td><td>8</td><td>16</td><td>0%</td></tr>
      <tr><td>SSA</td><td>Small Shock Absorbers</td><td>2</td><td>14</td><td>7</td><td>14</td><td>0%</td></tr>
      <tr><td>CHS/CORE</td><td>Chassis/Core</td><td>1</td><td>8</td><td>8</td><td>8</td><td>0%</td></tr>
      <tr><td>BSA</td><td>Big Shock Absorbers</td><td>2</td><td>18</td><td>9</td><td>18</td><td>0%</td></tr>
      <tr><td colspan="3"><strong>Total components</strong></td><td><strong>101</strong></td><td><strong>59</strong></td><td><strong>101</strong></td><td><strong>0%</strong></td></tr>
    </tbody>
  </table>
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
      <tr><td>FAX</td><td>Front Axle</td><td>1</td><td>6</td><td>6</td><td>6</td><td>0%</td></tr>
      <tr><td>RAX (HD)</td><td>Rear axis</td><td>1</td><td>6</td><td>6</td><td>6</td><td>0%</td></tr>
      <tr><td>RAX (RD)</td><td>Rear axis</td><td>1</td><td>2</td><td>2</td><td>2</td><td>0%</td></tr>
      <tr><td>CRE (TL)</td><td>Chassis, remaining systems, engine</td><td>1</td><td>1</td><td>1</td><td>1</td><td>0%</td></tr>
      <tr><td>CSEB-NABS (SA)</td><td>Chassis, systems, engine, body</td><td>1</td><td>1</td><td>1</td><td>1</td><td>0%</td></tr>
      <tr><td colspan="3"><strong>Total remaining parts</strong></td><td><strong>16</strong></td><td><strong>16</strong></td><td><strong>16</strong></td><td><strong>0%</strong></td></tr>
    </tbody>
  </table>
</details>


<br>

Scenario 06 (exp17) showed baseline and calibrated component count deviations of -37.3% and 0% respectively (see Table 5.6a). The baseline deviation is attributed to incomplete product processing, a consequence of the WS-02 bottleneck. However, the calibrated run attained perfect alignment following the throughput adjustment. Component counts were lower than expected due to incomplete processing of POs 8 to 10. The WS-02 bottleneck (98.5% utilization) prevented downstream stations from completing all products within the simulation time. The remaining parts count deviation was -40.0% (see Table 5.6b).

<details>
  <summary><strong>Table 5.6a.</strong> Component counts (scenario 06, exp17, exp17s)</summary>
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
      <tr><td>BOSP</td><td>Body + Spoiler</td><td>1+1</td><td>14</td><td>8</td><td>16</td><td>-12.5%</td></tr>
      <tr><td>BAT</td><td>Battery</td><td>1</td><td>4</td><td>4</td><td>4</td><td>0%</td></tr>
      <tr><td>RT</td><td>Rear Tires</td><td>1+1</td><td>18</td><td>10</td><td>20</td><td>-10.0%</td></tr>
      <tr><td>FT</td><td>Front Tires</td><td>1+1</td><td>11</td><td>7</td><td>14</td><td>-21.4%</td></tr>
      <tr><td>SSA</td><td>Shock Absorbers</td><td>1+1</td><td>10</td><td>6</td><td>12</td><td>-16.7%</td></tr>
      <tr><td>CHS/CORE</td><td>Chassis/Core</td><td>1</td><td>4</td><td>6</td><td>6</td><td>-33.3%</td></tr>
      <tr><td>BSA</td><td>Brake System</td><td>1+1</td><td>11</td><td>7</td><td>14</td><td>-21.4%</td></tr>
      <tr><td>FAX</td><td>Front Axle</td><td>1</td><td>2</td><td>3</td><td>3</td><td>-33.3%</td></tr>
      <tr><td colspan="3"><strong>Total components</strong></td><td><strong>74</strong></td><td><strong>51</strong></td><td><strong>89</strong></td><td><strong>-16.9%</strong></td></tr>
    </tbody>
  </table>
</details>

<details>
<summary><strong>Table 5.6b.</strong> Remaining parts (scenario 06, exp17, exp17s)</summary>
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
      <tr><td>CRE (TL)</td><td>Chassis, remaining systems, engine</td><td>1</td><td>1</td><td>1</td><td>1</td><td>0%</td></tr>
      <tr><td>CSEB-NABS (SA)</td><td>Chassis, systems, engine, body</td><td>1</td><td>2</td><td>3</td><td>3</td><td>-33.3%</td></tr>
      <tr><td colspan="3"><strong>Total remaining parts</strong></td><td><strong>6</strong></td><td><strong>10</strong></td><td><strong>10</strong></td><td><strong>-40.0%</strong></td></tr>
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

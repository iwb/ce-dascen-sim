# Validation

This folder contains the simulation outputs and the workbook used to calculate the validation results in [`docs/experiments_overview.md`](../docs/experiments_overview.md) (Sections 2–5).

- `outputs/`: Simulation outputs of the eight validation runs (exp12–exp17, including the sensitivity runs exp14s and exp17s).
- `validation_results.xlsx`: Workbook that combines the simulation outputs with the factory data from [ce-dascen-lf-data](https://github.com/iwb/ce-dascen-lf-data) and calculates all deviations.

## Workbook

| Tab color | Sheets | Content |
|---|---|---|
| Red | `Summary`, `Final_Values` | Final deviations per run and their calculation |
| Blue | `Runs`, `raw_*` | Simulation outputs (raw output) |
| Purple | `Scenarios`, `Factory_*` | Factory reference data from the dataset |
| Green | `Calc_*` | Calculations per PO, workstation, and component |

Run IDs: `S1`–`S6` = scenarios 01–06, `S3s`/`S6s` = sensitivity runs. Simulated times are given in simulation minutes and factory times in seconds (1 sim minute = 1 real second).

## Calculation rules

- **Lead time:** Averaged over the POs completed in both the simulation and the real experiment. Unfinished POs are marked as DNF in `Calc_LeadTime`.
- **Utilization:** Busy time / total time per workstation, averaged over all workstations. Factory values are taken 1:1 from the dataset. Deviation in percentage points.
- **Deviations** are calculated from averages and totals, not as the mean of individual deviations.
- **Assessment:** Pass if the lead time and component deviations are within ±20 % and the utilization deviation within ±20 pp.
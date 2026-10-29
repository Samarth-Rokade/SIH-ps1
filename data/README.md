# projects.csv — training dataset for infrastructure delay / cost-overrun prediction

3,600 rows: 1,800 real records extracted from the MoSPI **PAIMANA Flash Report, July 2026**
(central sector projects costing ₹150 crore and above) plus 1,800 synthetic records generated
from the real ones. Reference month for every derived field is **July 2026**.

## Extraction validation

The parser was checked against the figures printed in the report itself:

| Check | Parsed | Report |
|---|---|---|
| Ongoing projects | 1,775 | 1,775 |
| Completed during month | 25 | 25 |
| Line ministries | 17 | 17 |
| Total original cost (₹ cr) | 33,70,138 | 33,70,138 |
| Total revised cost (₹ cr) | 37,10,642 | 37,10,642 |
| Cumulative expenditure (₹ cr) | 19,26,100 | 19,26,100 |

## Columns

| Column | Type | Notes |
|---|---|---|
| `project_id` | str | P00001 … P03600 |
| `project_name` | str | |
| `ministry` | str | 17 categories |
| `state` | str | 37 categories; multi-state projects collapsed to `Multi-States`, plus `PAN India`, `Offshore` |
| `sector` | str | 22 categories (Roads & Highways, Railways, Coal, Oil & Gas, Transmission & Distribution, Urban Public Transport, Waste & Water …) |
| `original_cost` | float | ₹ crore, sanctioned cost |
| `revised_cost` | float | ₹ crore; equals original where no revision was reported |
| `expenditure` | float | ₹ crore, cumulative to date |
| `approval_date` | date | YYYY-MM-01 |
| `start_date` | date | falls back to approval date where the report leaves it blank |
| `planned_completion` | date | original / target date of completion |
| `revised_completion` | date | null where no revision has been notified |
| `actual_completion` | date | populated only for `status = Completed` |
| `physical_progress` | float | percent, 0–100 |
| `status` | str | Ongoing / Completed |
| `planned_duration_months` | int | planned_completion − start_date |
| `elapsed_months` | int | July 2026 − start_date |
| `time_elapsed_pct` | float | elapsed ÷ planned duration × 100 |
| `progress_gap_pct` | float | physical_progress − time_elapsed_pct (negative = behind schedule) |
| `expenditure_pct_of_revised_cost` | float | |
| `project_age_months` | int | since approval |
| `delay_months` | int | see below |
| **`delay_label`** | 0/1 | 1 if `delay_months > 3` |
| `cost_escalation_pct` | float | (revised − original) ÷ original × 100 |
| **`cost_overrun_label`** | 0/1 | 1 if `cost_escalation_pct > 20` |
| `data_source` | str | `flash_report_jul2026` or `synthetic` |
| `data_quality_flag` | 0/1 | 1 = implausible source values (44 rows) |

### How `delay_months` is computed

```
Completed : actual_completion       − planned_completion
Ongoing   : max(revised_completion or planned_completion, Jul-2026) − planned_completion
```

The `max(…, Jul-2026)` term is what makes the label meaningful for ongoing work: a project
whose own revised date has already passed while it is still running keeps accumulating delay
instead of freezing at its last notified date. Values are floored at 0.

Label balance: **63.1% delayed**, **14.9% cost overrun**, 398 rows both.

## Synthetic generation

Donor resampling rather than parametric simulation, so joint structure survives:

1. Draw a real ongoing project as donor (donors with corrupt source values excluded).
2. Keep its ministry and sector; resample the state from that sector's state distribution 40% of the time.
3. `original_cost` = donor cost × lognormal(0, 0.40); escalation drawn from the real escalation pool, with the spike at exactly 0% preserved (55.6% real vs 53.8% synthetic).
4. Planned duration = donor duration × U(0.85, 1.20); start date = donor start ± 12 months.
5. Delay inherits the donor's slippage 85% of the time, otherwise is redrawn from the sector's delay pool.
6. `physical_progress` sampled from real projects with the same lateness; spend ratio from real projects at a similar completion stage.
7. Every schedule is then forced to be internally consistent with the label rule (an on-time ongoing project cannot already be past its target; a completed project cannot finish after July 2026).
8. Labels are recomputed for real and synthetic rows with the same function, so no definitional drift.

Resulting match on real vs synthetic: delay rate 64.4% vs 61.7%, overrun rate 14.8% vs 15.1%,
median cost ₹792 cr vs ₹751 cr, median delay 12 vs 12 months.

Synthetic project names come from sector templates and are placeholders — do not treat them as
geographically meaningful. 18% of synthetic rows are `Completed`, deliberately more than the real
file, which only shows the 25 projects commissioned in that single month.

## Using it

**Leakage warning.** `revised_completion`, `delay_months`, `cost_escalation_pct` and
`revised_cost` are all derived from the same revision event as the labels. Drop them from the
feature matrix:

```python
import pandas as pd
df = pd.read_csv("projects.csv")
df = df[df.data_quality_flag == 0]

LEAKS = ["delay_months", "revised_completion", "cost_escalation_pct",
         "revised_cost", "actual_completion", "expenditure_pct_of_revised_cost"]
X = df.drop(columns=LEAKS + ["delay_label", "cost_overrun_label",
                             "project_id", "project_name", "data_source"])
y = df.delay_label
```

For the cost-overrun target, `revised_cost` and `cost_escalation_pct` are the leaks;
`revised_completion` and `delay_months` are legitimate features.

Split by `start_date` (train on projects started before ~2023, test on later ones) rather than
randomly — a random split lets the model see the same era it is predicting, and the early-warning
use case is inherently forward-looking. Keeping real and synthetic rows separable via
`data_source` also lets you train on both and evaluate on real rows only, which is the honest
number to report.

## Files

- `projects.csv` — the dataset
- `parse_flashreport.py` — extracts Table 6 (ongoing) from the PDF
- `parse_completed.py` — extracts Table 3 (completed during month)
- `build_dataset.py` — cleaning, synthetic generation, labelling

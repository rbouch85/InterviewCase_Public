---
name: kaplan-meier-survival
description: Use Python lifelines.KaplanMeierFitter for survival and time-to-event analysis with right-censored data
---

# Kaplan-Meier survival skill

Use this skill before defining, fitting, or reporting a Kaplan-Meier curve or any time-to-event summary using the Python `lifelines.KaplanMeierFitter` API. The goal is to estimate event-free survival with the correct treatment of censoring and to communicate the limits of the evidence clearly.

Reference: https://lifelines.readthedocs.io/en/latest/fitters/univariate/KaplanMeierFitter.html

---

## What a Kaplan-Meier estimate is

A Kaplan-Meier (KM) estimator is a non-parametric estimate of the survival function, `S(t)`, the probability that an individual remains event-free beyond time `t`.

At each observed event time, the curve drops by the proportion of subjects still at risk who experience the event. Subjects who are censored are still counted in the risk set before their final observed follow-up time, but they do not contribute an event at that point.

In plain terms: the curve shows how the share of the population still remaining event-free changes over time, while correctly accounting for the fact that some people are observed for shorter periods and are not followed long enough to see the event.

For reporting, a concise non-technical explanation is:

> The Kaplan-Meier curve estimates the probability of staying event-free over time, accounting for the fact that some people are observed for different lengths of time and are censored before the event is seen. It is a survival estimate, not a simple retention rate, and it should be interpreted in the context of the follow-up window.

---

## Data setup for lifelines

The minimum setup is a duration variable and a binary event indicator.

- `duration`: numeric follow-up time from a defined origin to either the event or the last known censoring time.
- `event_observed`: `1` if the event occurred during observation, `0` if the observation ended without the event (right-censoring).
- `time_origin`: conceptual anchor date or timestamp when follow-up is defined relative to a calendar date; use it to compute elapsed durations before fitting. It is not an argument accepted by `KaplanMeierFitter.fit()`.

Recommended structure:

```python
import pandas as pd
from lifelines import KaplanMeierFitter

df = df[["duration_days", "event_observed"]].dropna().copy()

kmf = KaplanMeierFitter()
kmf.fit(
    durations=df["duration_days"],
    event_observed=df["event_observed"],
    label="all accounts"
)
```

If the analysis is defined relative to an origin date (`time_origin`), keep that origin consistent and document it explicitly. Compute durations from the origin and the event or censoring date before calling `fit()`:

```python
df["cohort_start"] = pd.to_datetime(df["cohort_start"])
df["observed_end"] = pd.to_datetime(df["observed_end"])
df["duration_days"] = (
    df["observed_end"] - df["cohort_start"]
).dt.days

kmf.fit(
    durations=df["duration_days"],
    event_observed=df["event_observed"],
    label="accounts since cohort start"
)
```

### Right-censoring workflow

Use this sequence whenever the outcome is time-to-event:

1. Define the event precisely: what counts as a failure/event and what does not.
2. Define the time origin: when follow-up starts for each unit.
3. Convert to a consistent duration measure (days, weeks, months).
4. Mark `event_observed = 1` for events and `event_observed = 0` for right-censoring.
5. Fit the KM estimator.
6. Inspect `survival_function_`, `confidence_interval_`, and `event_table` before interpreting.
7. Compare curves only when the same event definition and follow-up window apply.

In a right-censored design, the observation is incomplete for units without the event by the last follow-up date. This is not the same as saying the event never occurred; it means the event could have occurred later than the last observed time.

---

## Essential lifelines examples

### Survival function and confidence intervals

```python
kmf = KaplanMeierFitter()
kmf.fit(df["duration_days"], df["event_observed"])

survival = kmf.survival_function_
ci = kmf.confidence_interval_

print(survival.head())
print(ci.head())
```

`kmf.survival_function_` is a DataFrame with the estimated survival probability by time. `kmf.confidence_interval_` provides the confidence interval around that estimate (typically 95% by default).

### Median survival time

```python
median_survival = kmf.median_survival_time_
print(f"Median survival time: {median_survival}")
```

The median survival time is the time at which the estimated survival probability first falls to 0.5. If the curve never reaches 50% event probability, the median may be infinite (`inf`), which should be reported as "median survival not reached within the observed follow-up window." Do not interpret this as zero risk.

### Event table

```python
event_table = kmf.event_table
print(event_table.head())
```

`event_table` reports, at each unique observed time, the number at risk, number of events, number censored, and the cumulative observed counts. This is essential for checking whether the data and censoring pattern are plausible.

### Grouped curves

```python
ax = None
for cohort, group in df.groupby("cohort"):
    kmf = KaplanMeierFitter()
    kmf.fit(group["duration_days"], group["event_observed"], label=cohort)
    ax = kmf.plot(ax=ax, ci_show=False)
```

Grouped KM plots are useful for comparing survival across cohorts, segments, or treatment groups. Keep the same time origin, event definition, and min/max follow-up window across groups before comparing or reporting them.

---

## How to interpret the output

- A curve that sits higher implies a longer time to event / better survival.
- A step down indicates an observed event at that time.
- A wider confidence interval at later times usually reflects fewer people still at risk.
- The median survival time is a useful summary, but it is only interpretable within the observed window and the chosen definition of the event.
- The shape of the curve is informative; compare it to the number at risk and not only to the final value.

For a simple report sentence:

> The estimated probability of remaining event-free at 90 days was 67% (95% CI 61% to 72%). The median time to event was 120 days; however, estimates beyond the observed follow-up window are uncertain because fewer subjects remained under observation.

For formal group comparisons, KM plots are descriptive. A formal significance comparison typically requires a stratified or unstratified log-rank test and a clear statement of the target estimand.

---

## Assumptions and limitations

Kaplan-Meier estimates are most defensible when these conditions are met:

- A clear event definition exists and is applied consistently across the dataset.
- Time origin is defined and consistent for each observation.
- Right-censoring is non-informative enough that censoring is not strongly related to the unobserved event risk after accounting for observed information.
- Follow-up is not obviously biased by unequal observation windows across groups.

Known limitations:

- KM estimates do not account for covariates; they are descriptive unless paired with a model or stratified comparison.
- The estimate depends on the chosen follow-up window and event definition.
- Unequal follow-up can distort apparent differences between cohorts if earlier and later cohorts are not compared on a common observation window.
- A curve can appear flat or stable simply because too few people remain under observation, not because the risk is truly low.

---

## Project-specific caution for this repository

The supplied usage data does not support retention claims without a defined follow-up window and a consistent event definition. The usage extract covers account-day activity through a fixed date, and later cohorts have less possible follow-up than earlier cohorts. That means the data can support descriptive activity and coverage summaries, but not causal or inferential retention statements unless the observation window and censoring process are explicitly defined and aligned across cohorts.

In practical terms:

- Do not describe account-day activity as a retention outcome unless the analysis defines a follow-up horizon and a retention/event rule.
- Do not compare cohorts with materially different possible follow-up without aligning them to a common time window or clearly noting the limitation.
- If the event is "no usage for X days after creation," define the exact day count and the censoring rule at the start of the analysis.

This is especially important in a project where later cohorts were observed over fewer days than earlier cohorts; the data are not equivalent to a balanced, fixed-duration retention study.

---

## Reporting checklist

Before writing up any KM analysis, confirm:

- The event definition is explicit and reproducible.
- The time origin and follow-up window are stated.
- The duration unit is stated (days, weeks, months).
- Right-censoring is described, including how censored observations are treated.
- The number at risk and the number censored are available or visible in the plot.
- The survival estimate is reported with confidence intervals where feasible.
- Median survival, if reached, is reported with context.
- Any unequal follow-up across cohorts is acknowledged and not hidden.

---

## Reusable report paragraph template

> In this analysis, time-to-event was defined as [event definition], with follow-up measured from [time origin] in [units]. Kaplan-Meier estimates were used to estimate the probability of remaining event-free over time, accounting for right-censoring from [censoring description]. The estimated survival probability at [time horizon] was [X%] (95% CI [lower%, upper%]), and the median time to event was [Y units]. These results are limited to the observed follow-up window and should be interpreted as descriptive evidence rather than a retention claim. Because [later cohorts / unequal follow-up / differing observation windows] were not aligned to a common follow-up period, cohort comparisons should be interpreted cautiously.

---

## Recommended use in this repository

Apply this skill when the problem asks for survival curves, time-to-event summaries, event-free analysis, or disposition over follow-up time. Use it before producing a KM chart or writing a retention-style interpretation. If the product question is really about retention, first define the event, the observation window, and the censoring mechanism; only then should a KM analysis be used as evidence.

This skill is a good fit for descriptive product-usage questions that require time-dependent survivorship estimates, but not for causal claims or claim-style retention statements without a valid, defined follow-up design.

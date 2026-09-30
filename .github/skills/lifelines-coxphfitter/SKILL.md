---
name: lifelines-coxphfitter
description: Fit, interpret, and diagnose lifelines 0.30.3 CoxPHFitter models correctly
---

# lifelines CoxPHFitter skill

Use this skill for right-censored survival regression with
`lifelines==0.30.3`. Treat the official
[CoxPHFitter API](https://lifelines.readthedocs.io/en/latest/fitters/regression/CoxPHFitter.html)
as the source of truth. A Cox model describes associations and risk
prediction; its hazard ratios are not causal effects without a separate,
defensible causal design.

## Define the survival outcome first

Create one row per subject (or the documented repeated-observation unit) and
define a common time origin, follow-up end, and event:

- `duration_col` is the non-negative time from the origin to the event or the
  last time the subject was known to be event-free.
- `event_col` is `1` when the target event was observed and `0` when follow-up
  ended before observing it (right-censored). Do not code “still active,”
  “missing,” or “not yet observed” as an event.
- Use one event definition and time unit throughout. Do not silently treat
  calendar dates, elapsed durations, competing events, or interval censoring as
  interchangeable.
- Check that event and censoring dates are ordered, durations are finite and
  valid, and covariates are measured before (or are otherwise valid at) the
  time origin. Never use future information or post-event variables.

If a subject becomes observable only after the time origin, put delayed-entry
(left-truncation) time in `entry_col`; it is not a covariate, and it must be
less than or equal to the observed duration.

## Minimal fit and interpretation

```python
import pandas as pd
from lifelines import CoxPHFitter

# One row per subject. `time_to_event` is elapsed time; `event_observed`
# is 1 for the target event and 0 for right-censoring at last follow-up.
df = pd.DataFrame({
    "time_to_event": [5, 3, 9, 8],
    "event_observed": [1, 1, 0, 0],
    "exposure": [0, 1, 0, 1],
    "baseline_age": [42, 58, 37, 61],
})

cph = CoxPHFitter()  # default baseline_estimation_method="breslow"
cph.fit(df, duration_col="time_to_event", event_col="event_observed")
cph.print_summary()

hr = cph.hazard_ratios_
ci_log_hazard = cph.confidence_intervals_
summary = cph.summary  # includes coef, exp(coef), p, and CI columns
```

For a one-unit increase in a numeric covariate, `exp(coef)` is the hazard
ratio, conditional on the other included covariates and under proportional
hazards. For a binary indicator, it compares `1` with the reference `0`; for a
categorical encoding, state the reference category. HR > 1 means a higher
instantaneous event rate, HR < 1 a lower rate, and HR = 1 no multiplicative
difference. It does **not** mean a percentage change in survival time or event
probability. For a meaningful multi-unit contrast, use `exp(coef * delta)`.

`cph.summary` is the convenient report table. `cph.params_` contains log
hazard coefficients, `cph.hazard_ratios_` contains their exponentials, and
`cph.confidence_intervals_` contains confidence limits on the coefficient
(log-hazard) scale. Exponentiate those limits before reporting an HR interval
(or use the `exp(coef) lower/upper` columns in `summary`). A p-value tests a
coefficient equal to zero under the model; report its estimate and interval,
not significance alone. The default CI level is controlled by `alpha` on the
fitter. Inspect `concordance_index_` as in-sample predictive discrimination
only; it is not evidence of causality or external performance.

## Check proportional hazards and model fit

After fitting, pass the original training frame (or a documented unique-index
subsample) to:

```python
axes = cph.check_assumptions(
    df,
    advice=True,
    show_plots=True,
    p_value_threshold=0.01,
)
```

In lifelines 0.30.3, `check_assumptions()` tests scaled Schoenfeld residuals
using rank and Kaplan–Meier time transforms, prints flagged covariates and
advice, and returns axes when plots are requested. The default threshold is
arbitrary: multiple testing can create false flags, and large samples can flag
minor deviations. Combine the tests with the residual plots and subject-matter
reasoning. Keep the training index unique; use
`df.reset_index(drop=True)` if needed. A flagged variable can indicate a
nonlinear functional form as well as non-proportional hazards.

For a plausible violation, consider a justified transformation or interaction,
a time-varying model, or stratification. With `strata=["category"]`, each
stratum gets its own baseline hazard, but no coefficient or HR is estimated for
that stratifying variable. Do not describe a stratified variable's missing
coefficient as “no effect.”

## Options and cautions

- **Delayed entry:** `cph.fit(..., entry_col="entry_time")` accounts for
  left-truncated risk sets. It requires a defensible entry time and
  `entry_time <= duration`.
- **Strata:** pass `strata="column"` or a list to `fit()` (or to
  `CoxPHFitter(strata=...)`) when a categorical variable should define separate
  baselines. High-cardinality or sparse strata can make estimates unstable.
- **Weights:** `weights_col="weight"` supports case weights and sampling
  weights. For sampling weights, use `robust=True` for more appropriate
  standard errors and document how weights were constructed; weights do not
  repair selection bias.
- **Clusters/correlation:** `cluster_col="subject_or_group_id"` uses clustered
  (sandwich) covariance and forces robust variance. Use it when rows are
  correlated; point estimates do not change. `robust=True` uses the Huber/
  Wei–Lin estimator, whose handling of many tied event times can differ
  substantially.
- **Penalization:** `CoxPHFitter(penalizer=value, l1_ratio=value)` can stabilize
  collinear or high-dimensional fits and shrink coefficients; `l1_ratio=0`
  gives L2-style shrinkage and `1` gives L1-style shrinkage. Choose the
  penalty transparently and assess it as a modeling choice: penalized
  coefficients and ordinary p-values/CIs should not be presented as if they
  came from an unpenalized model. Do not use penalization to conceal bad
  coding, separation, leakage, or inadequate events.
- **Baseline modeling:** the default is the semi-parametric Breslow baseline.
  `baseline_estimation_method="spline"` (with `n_baseline_knots` or `knots`) or
  `"piecewise"` (with `breakpoints`) changes baseline assumptions; use only
  when the choice is justified and validated.

## Common failure modes

Before trusting results, check convergence warnings and, if necessary, use
`show_progress=True` rather than suppressing them. Look for constant or
duplicate columns, an accidental intercept column (Cox models have no
intercept), perfect separation, extreme collinearity, sparse categorical
levels, too few observed events, missing/non-finite values, invalid durations,
and covariates recorded after the origin. Encode categorical predictors
explicitly or use the documented `formula` argument; do not pass identifier
columns as numeric predictors. Handle ties, competing risks, recurrent events,
time-varying covariates, and interval/left censoring with a method appropriate
to that design rather than forcing them into the basic right-censored fit.

# Kaplan-Meier example with lifelines

This self-contained notebook demonstrates Kaplan-Meier estimation using
`load_waltons()` from `lifelines.datasets`. It is an educational example and
does not analyze the repository's customer CSV files.

The dataset contains 163 Drosophila observations. `T` is days survived, `E` is
1 when death was observed and 0 when follow-up was right-censored, and `group`
identifies genotype (`control` or `miR-137`). The dataset documentation notes
that censoring can occur when a fly is accidentally killed or escapes before
its natural death is observed.

## Run

From the repository root, create and activate a Python 3.10+ environment, then
install the notebook dependencies:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r projects/20260929_rbouch85_kaplan_meier_example/requirements.txt
python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=120 projects/20260929_rbouch85_kaplan_meier_example/kaplan_meier_waltons.ipynb
```

The notebook saves the KM figure to
`projects/20260929_rbouch85_kaplan_meier_example/outputs/figures/waltons_kaplan_meier.png`
and displays it inline. Its plot uses Matplotlib because lifelines' plotting
and at-risk-count helpers return Matplotlib axes; the repository's
`save_and_show_mpl` helper saves the reusable figure and displays it inline.

## Interpretation

The curves estimate the probability of remaining alive beyond each day while
accounting for right-censoring. Confidence intervals communicate uncertainty,
and the risk table shows the number of flies still under observation at
selected times. The median is reported only when the estimated curve reaches
50%. These are descriptive group curves: they do not establish that genotype
caused a difference, and estimates late in follow-up can be unstable when few
flies remain at risk.

## Data source

- `lifelines.datasets.load_waltons()`
- [lifelines datasets documentation](https://lifelines.readthedocs.io/en/latest/lifelines.datasets.html)
- [KaplanMeierFitter documentation](https://lifelines.readthedocs.io/en/latest/fitters/univariate/KaplanMeierFitter.html)

# Dataset Documentation and Descriptive Coverage

This project documents the three source CSVs used in the Azure App Service
interview case and produces a small, reproducible set of descriptive figures.
It does not modify or rewrite the source CSV files.

## Reproduce

From the repository root, run:

```bash
python projects/20260924_rbouch85_dataset-documentation/profile_and_visualize.py
```

The script uses only the Python standard library and `matplotlib`. It writes
the report to `outputs/reports/dataset-summary.md` and figures to
`outputs/figures/`.

## Outputs

- `outputs/reports/dataset-summary.md`: row counts, coverage metrics, and
  interpretation caveats.
- `outputs/figures/account_creation_by_day.png`: accounts created per day.
- `outputs/figures/account_mix.png`: account composition by customer type.
- `outputs/figures/usage_active_accounts.png`: distinct active accounts per
  usage date.

The visuals are descriptive only. They do not establish acquisition quality,
retention, causality, or product-market explanations.

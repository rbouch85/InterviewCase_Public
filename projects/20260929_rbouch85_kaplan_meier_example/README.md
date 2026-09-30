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

## Render the teaching materials

The Quarto sources in `reports/` produce a Word teaching note and a PowerPoint
slide deck in `outputs/reports/`. From the repository root, run:

```bash
quarto render projects/20260929_rbouch85_kaplan_meier_example/reports/kaplan_meier_teaching_note.qmd --output-dir projects/20260929_rbouch85_kaplan_meier_example/outputs/reports
quarto render projects/20260929_rbouch85_kaplan_meier_example/reports/kaplan_meier_teaching_slides.qmd --output-dir projects/20260929_rbouch85_kaplan_meier_example/outputs/reports
```

On Windows, finalize the PowerPoint figure's full-slide placement and
accessibility description after rendering:

```powershell
pwsh -File projects/20260929_rbouch85_kaplan_meier_example/reports/finalize_kaplan_meier_slides.ps1
```

The finalizer changes only the saved PNG's placement and PowerPoint accessibility
metadata; it does not edit or regenerate the image or run analysis.

These report-only commands use the notebook's existing saved outputs and
`outputs/figures/waltons_kaplan_meier.png`. Quarto execution is disabled in
both sources; rendering does not execute the notebook, run Python analysis,
or recreate the figure. Re-run the notebook separately only when intentionally
reproducing the analysis.

On Windows, if a long worktree path causes Quarto's temporary cache path to
exceed the Windows path limit, map the repository root to an unused drive
letter and render through that shorter path from PowerShell:

```powershell
$repoRoot = (Get-Location).Path
subst R: $repoRoot
try {
    quarto render R:\projects\20260929_rbouch85_kaplan_meier_example\reports\kaplan_meier_teaching_note.qmd --output-dir R:\projects\20260929_rbouch85_kaplan_meier_example\outputs\reports
    if ($LASTEXITCODE -ne 0) { throw "Word render failed." }
    quarto render R:\projects\20260929_rbouch85_kaplan_meier_example\reports\kaplan_meier_teaching_slides.qmd --output-dir R:\projects\20260929_rbouch85_kaplan_meier_example\outputs\reports
    if ($LASTEXITCODE -ne 0) { throw "PowerPoint render failed." }
    pwsh -File R:\projects\20260929_rbouch85_kaplan_meier_example\reports\finalize_kaplan_meier_slides.ps1
    if ($LASTEXITCODE -ne 0) { throw "PowerPoint finalization failed." }
} finally {
    subst R: /d
}
```

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

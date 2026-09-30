# Skill: Quarto Reporting Standards

---
name: quarto-reporting-standards
description: Assemble concise Quarto reports from saved analytical and visual artifacts
domain: reporting
confidence: high
---

## Purpose

Use this skill whenever creating, editing, or validating a Quarto report for the project.

## Required Sequence

Data preparation and analysis must be completed first. Visual creation follows the approved analysis, and report assembly follows the saved analytical and visual outputs.

## Artifact Contract

Quarto markdown should consume only approved, saved statistics/tables and saved `.png` and `.svg` figures from approved output locations. Rendering is a presentation step: it must not perform analysis, recomputation, notebook execution, or figure regeneration. Data and method decisions belong upstream with the analysis and visualization owners.

The report/analysis handoff must identify the exact approved inputs, their locations, and the analysis version or run that produced them. Quarto sources should reference those handoff artifacts directly; they should not load raw data to derive new results or silently substitute an unapproved output.

## Report Structure

Keep the report concise and use this order:

1. Executive summary
2. Approach
3. Assumptions
4. Findings
5. Appendix

The executive summary states the decision-relevant answer; the approach explains the analytical method; assumptions identify material limitations; findings present supported results; and the appendix preserves supporting detail without interrupting the main narrative.

## Handoff and Validation

Request approved saved figures from Viz-dude before embedding them. Confirm that paths resolve, figures render, headings follow the required structure, and the report remains concise after rendering.

Word and PowerPoint are deliverables, not source-only artifacts. Inspect the actual rendered `.docx` or `.pptx`, rather than relying on the Quarto source or an HTML/PDF proxy. At final reading or presentation size, review chart readability, labels and units, uncertainty and censor marks, and risk-set/number-at-risk support where relevant. Confirm that tables, captions, notes, and page or slide breaks remain usable.

Check accessibility in the emitted Office package or with the Office Accessibility Checker. Verify that figure alt-text metadata is actually present on the relevant DOCX/PPTX drawing properties, and do not assume Markdown alt text survived conversion. Confirm that image/figure files, package relationships, and media parts are intact and openable.

Use independent specialist reviews where appropriate: the relevant method owner must perform the methodology/statistical review (for survival or time-to-event work, Experiment-dude), and Viz-dude must perform the visual review. These reviews validate the handed-off artifacts; they do not authorize new analysis during rendering.

### Windows path-length or cache workaround

If Quarto cache or path-length failures occur on Windows, map the repository root to a temporary short drive letter (for example, `subst Q: $repoRoot`) and render through `Q:\...`. Verify the letter is unused before mapping, keep the mapping scoped to this render, and remove only that exact mapping in a guaranteed `finally` step (for example, `subst Q: /d` in the same automation). Do not delete broad directories, shared caches, or unrelated temporary files. Leave cache files alone unless their exact generated path and ownership are established; cleanup must never expand beyond the mapping created for this render.

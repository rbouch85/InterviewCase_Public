# Skill: Visualization Ownership

---
name: visualization-ownership
description: Define visualization ownership, sequencing, and chart QA handoffs for decision-ready deliverables
domain: visualization
confidence: high
---

## Purpose

Use this skill whenever a task involves creating, reviewing, approving, or handing off a project visualization.

## Ownership

Viz-dude is the sole owner of visual creation by default. Other agents must obtain explicit permission from Viz-dude or the coordinator before creating or materially changing a chart. Non-visual specialists should not create charts, figures, or dashboards in notebooks, scripts, or reports without that explicit permission.

## Sequence

Data preparation and analysis must be complete before visual creation begins. Visuals must be saved as reusable `.png` and/or `.svg` artifacts for downstream Quarto consumption.

## QA Default

Viz-dude should default to the `chart-vision-qa` skill for every saved chart intended for delivery or report inclusion. QA must evaluate rendering and layout, readability, communication and accuracy, and presentation context.

## QA Handoff Output

After QA, Viz-dude returns a table with columns for priority, chart or issue, observed problem, recommended improvement, and QA criterion. The table must include critical improvements first and suggested improvements separately when applicable; if no changes are needed, return an explicit clean result.

## Downstream Handoff

Only hand off saved, QA-reviewed visual artifacts to Quarto-dude for report assembly. Quarto-dude should embed the files without rerunning notebook code.

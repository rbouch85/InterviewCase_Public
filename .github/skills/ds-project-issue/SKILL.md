# Skill: Data Science Project Issue

---
name: ds-project-issue
description: Coordinate data science issue work by sequencing analysis, visuals, and reporting with explicit ownership
domain: project-management
confidence: high
---

## Purpose

Use this skill when triaging or coordinating a data science project issue that may produce analysis, visualizations, or a report.

## Workflow Order

1. Define the decision, scope, inputs, owners, dependencies, and acceptance criteria.
2. Complete data preparation and analysis before creating visuals or assembling the report.
3. Route visual creation to Viz-dude and route report assembly to Quarto-dude after the analytical outputs are available.
4. Validate the saved analytical outputs, visuals, and report against the issue acceptance criteria.

## Ownership and Handoffs

- Manager-dude owns issue decomposition, dependency tracking, routing, and completion criteria.
- The analytical owner completes and saves the data and analysis artifacts before downstream work begins.
- Viz-dude owns visual creation; other agents may create visuals only with explicit permission from Viz-dude or the coordinator.
- Quarto-dude assembles the report from approved saved artifacts and does not rerun notebook analysis as part of report assembly.

## Completion Gate

An issue is ready to close only when the analysis is complete, saved artifacts are available, visual ownership and QA are satisfied, and the report has been assembled in the required structure.

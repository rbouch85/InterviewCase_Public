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

Quarto markdown should consume saved `.png` and `.svg` files from the approved output locations. It should not rerun notebook code or recreate analysis during report rendering.

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

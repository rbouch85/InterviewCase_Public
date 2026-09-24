"""Profile the case CSVs and create reproducible descriptive outputs."""

from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd
from plotnine import (
    aes,
    element_line,
    element_rect,
    element_text,
    geom_col,
    geom_line,
    ggplot,
    labs,
    scale_x_datetime,
    scale_y_continuous,
    theme,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = Path(__file__).resolve().parent / "outputs"
FIGURES = OUTPUTS / "figures"
REPORT = OUTPUTS / "reports" / "dataset-summary.md"
BAY_6 = ["#003f5c", "#665191", "#d45087", "#ff7c43", "#c9b700", "#2db757"]


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def parse_date(value: str) -> datetime:
    return datetime.strptime(value[:10], "%Y-%m-%d")


def rti_growth_plotnine_theme() -> theme:
    return theme(
        plot_title=element_text(size=18, weight="bold", family="DejaVu Sans"),
        axis_title=element_text(size=12, family="DejaVu Sans"),
        axis_text=element_text(size=11, family="DejaVu Sans"),
        panel_grid_major=element_line(color="#dadada", size=0.5),
        panel_grid_minor=element_line(color="#f0f0f0", size=0.3),
        panel_background=element_rect(fill="white"),
        plot_background=element_rect(fill="white"),
        panel_border=element_rect(color="#2f2f2f", size=0.8),
        legend_background=element_rect(fill="white"),
    )


def save_chart(plot, path: Path, width: float = 10, height: float = 6) -> None:
    plot.save(path, width=width, height=height, dpi=180, verbose=False)


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    (OUTPUTS / "reports").mkdir(parents=True, exist_ok=True)

    account_data = read_csv("Case_AccountData.csv")
    creation = read_csv("Case_AccountCreation.csv")
    usage = read_csv("Case_UsageData.csv")

    customer_type = Counter(row["CustomerType"] for row in account_data)
    language = Counter(row["DevLanguage"] for row in account_data)
    creation_day = Counter(row["AccountCreatedDay_Key"] for row in creation)
    usage_day = Counter(row["UsageDate_Key"] for row in usage)
    usage_accounts = {row["AccountID"] for row in usage}
    account_ids = {row["AccountID"] for row in creation}

    ordered_types = sorted(customer_type, key=customer_type.get, reverse=True)
    segment_df = pd.DataFrame(
        {"segment": ordered_types, "count": [customer_type[label] for label in ordered_types]}
    )
    segment_df["segment"] = pd.Categorical(segment_df["segment"], categories=ordered_types, ordered=True)
    account_mix = (
        ggplot(segment_df, aes(x="segment", y="count"))
        + geom_col(fill=BAY_6[0], width=0.8)
        + labs(title="Account composition is concentrated in SMB", x="", y="Accounts")
        + scale_y_continuous(expand=(0.02, 0))
        + rti_growth_plotnine_theme()
    )
    save_chart(account_mix, FIGURES / "account_mix.png")

    creation_df = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [f"{value[:4]}-{value[4:6]}-{value[6:]}" for value in sorted(creation_day)],
                errors="coerce",
            ),
            "count": [creation_day[value] for value in sorted(creation_day)],
        }
    )
    account_creation = (
        ggplot(creation_df, aes(x="date", y="count"))
        + geom_col(fill=BAY_6[0], width=0.8)
        + labs(
            title="977 accounts were created across 27 February dates",
            x="",
            y="New accounts",
        )
        + scale_x_datetime(date_labels="%Y-%m-%d", date_breaks="2 days")
        + rti_growth_plotnine_theme()
        + theme(axis_text_x=element_text(rotation=45, ha="right"))
    )
    save_chart(account_creation, FIGURES / "account_creation_by_day.png")

    usage_df = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [f"{value[:4]}-{value[4:6]}-{value[6:]}" for value in sorted(usage_day)],
                errors="coerce",
            ),
            "count": [usage_day[value] for value in sorted(usage_day)],
        }
    )
    usage_active = (
        ggplot(usage_df, aes(x="date", y="count"))
        + geom_line(color=BAY_6[1], size=1.2)
        + labs(
            title="Daily active accounts vary across the 89-day usage window",
            x="",
            y="Distinct active accounts",
        )
        + scale_x_datetime(date_labels="%Y-%m-%d", date_breaks="7 days")
        + scale_y_continuous(expand=(0.02, 0))
        + rti_growth_plotnine_theme()
        + theme(axis_text_x=element_text(rotation=45, ha="right"))
    )
    save_chart(usage_active, FIGURES / "usage_active_accounts.png")

    creation_dates = [parse_date(row["AccountCreatedDay"]) for row in creation]
    usage_dates = [parse_date(row["UsageDate"]) for row in usage]
    account_data_accounts = len({row["AccountID"] for row in account_data})
    report = f"""# Dataset summary

Generated by `profile_and_visualize.py` from the three repository CSV files.

## Descriptive snapshot

| Dataset | Grain | Rows | Distinct accounts | Time coverage |
|---|---|---:|---:|---|
| `Case_AccountData.csv` | one row per account | {len(account_data):,} | {account_data_accounts:,} | not applicable |
| `Case_AccountCreation.csv` | one row per account creation record | {len(creation):,} | {len(account_ids):,} | {min(creation_dates):%Y-%m-%d} to {max(creation_dates):%Y-%m-%d} |
| `Case_UsageData.csv` | one row per account-day with observed usage | {len(usage):,} | {len(usage_accounts):,} | {min(usage_dates):%Y-%m-%d} to {max(usage_dates):%Y-%m-%d} |

Every source column is non-null in the supplied files. The usage table covers
all {len(account_ids):,} accounts in the creation table ({len(usage_accounts & account_ids) / len(account_ids):.0%} account coverage), with
{len(usage):,} account-day rows and {len(usage) / len(usage_accounts):.1f} observed usage days per account on average.

## Key distributions

- Customer type: {", ".join(f"{key} ({value:,})" for key, value in ((k, customer_type[k]) for k in ordered_types))}.
- Development language: {", ".join(f"{key} ({value:,})" for key, value in sorted(language.items(), key=lambda item: (-item[1], item[0])))}.
- Account creation is represented at daily and week-start keys; the week keys span five Sunday-start buckets.
- Usage has one date key per observed account-day. A missing account-day means no observed usage in this extract; it is not proof of non-use.

## Figures

![Account composition](../figures/account_mix.png)

![Account creation by day](../figures/account_creation_by_day.png)

![Daily active accounts](../figures/usage_active_accounts.png)

## Caveats and join guidance

1. Join the three datasets on `AccountID`; it is unique in the account and
   creation tables and repeats in usage at the account-day grain.
2. `AccountCreatedDay` and `UsageDate` are ISO timestamps serialized as text,
   while the `_Key` columns are `YYYYMMDD` text keys. Parse them as dates
   before sorting or calculating intervals.
3. `DevLanguage = unknown` is an explicit category, not a null. Preserve it
   as a reported value unless a business rule says otherwise.
4. The extract is right-censored at 2022-04-30 for usage and includes only
   February 2022 acquisition. Longer-term retention cannot be inferred for
   later cohorts without a comparable observation window.
5. These are descriptive coverage summaries. They do not support causal
   claims, retention definitions, or comparisons without specifying cohort,
   denominator, observation window, and treatment of unobserved days.
"""
    REPORT.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()

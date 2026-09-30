"""Build the issue #10 decision-ready figures from finalized summary tables."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from plotnine import (
    aes,
    element_blank,
    element_line,
    element_rect,
    element_text,
    facet_wrap,
    geom_col,
    geom_line,
    geom_point,
    geom_text,
    geom_vline,
    ggplot,
    labs,
    coord_flip,
    scale_x_continuous,
    scale_x_datetime,
    scale_y_continuous,
    theme,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TABLES = PROJECT_ROOT / "outputs" / "tables"
FIGURES = Path(__file__).resolve().parent

BAY_6 = ["#003f5c", "#665191", "#d45087", "#ff7c43", "#c9b700", "#2db757"]
FONT = "DejaVu Sans"
PNG_DPI = 180


def rti_growth_plotnine_theme() -> theme:
    """Use the repository's light RTI-style theme with restrained grid lines."""
    return theme(
        plot_title=element_text(
            size=16, weight="bold", family=FONT, color="#202124"
        ),
        plot_subtitle=element_text(size=10, family=FONT, color="#45484b"),
        plot_caption=element_text(size=9, family=FONT, color="#45484b", ha="left"),
        axis_title=element_text(size=10, family=FONT, color="#303336"),
        axis_text=element_text(size=9, family=FONT, color="#303336"),
        strip_text=element_text(size=10, weight="bold", family=FONT, color="#303336"),
        panel_grid_major=element_line(color="#e2e6e9", size=0.35),
        panel_grid_minor=element_blank(),
        panel_background=element_rect(fill="white", color="white"),
        plot_background=element_rect(fill="white", color="white"),
        panel_border=element_blank(),
        axis_ticks=element_blank(),
        legend_position="none",
        figure_size=(10, 5.2),
    )


def read_table(filename: str) -> pd.DataFrame:
    return pd.read_csv(TABLES / filename)


def save_png(plot, filename: str, width: float, height: float) -> Path:
    """Save one plot directly through plotnine at presentation-ready resolution."""
    output_path = FIGURES / filename
    plot.save(
        filename=str(output_path),
        format="png",
        dpi=PNG_DPI,
        width=width,
        height=height,
        units="in",
        verbose=True,
    )
    return output_path


def acquisition_weekly_plot() -> ggplot:
    data = read_table("acquisition_weekly_sunday_start.csv")
    data["account_count"] = pd.to_numeric(data["account_count"])
    data["week_start"] = pd.to_datetime(data["sunday_start_week"])
    data["week_label"] = [
        f"{start:%b} {start.day}–{end:%b} {end.day} (partial)" if partial
        else f"{start:%b} {start.day}–{end:%b} {end.day}"
        for start, end, partial in zip(
            data["week_start"],
            pd.to_datetime(data["calendar_week_end"]),
            data["partial_week"].astype(str).str.lower().eq("true"),
        )
    ]
    data["week_label"] = pd.Categorical(
        data["week_label"], categories=data["week_label"].tolist(), ordered=True
    )

    return (
        ggplot(data, aes(x="week_label", y="account_count"))
        + geom_col(fill=BAY_6[0], width=0.72)
        + geom_text(
            aes(label="account_count"),
            nudge_y=7,
            ha="left",
            color="#303336",
            size=9,
            family=FONT,
        )
        + coord_flip()
        + labs(
            title="The Feb 6-start week had the most recorded acquisitions",
            subtitle=(
                "Sunday-start calendar weeks • 977-account February cohort • "
                "counts shown at bar ends"
            ),
            x="",
            y="New accounts (count)",
            caption=(
                "Partial edge weeks: Jan 30–Feb 5 includes cohort dates Feb 1–5; "
                "Feb 27–Mar 5 includes Feb 27 only.\n"
                "Source: finalized acquisition_weekly_sunday_start.csv"
            ),
        )
        + scale_y_continuous(
            limits=(0, 350), breaks=(0, 100, 200, 300), expand=(0, 0)
        )
        + rti_growth_plotnine_theme()
        + theme(panel_grid_major_y=element_blank())
    )


def acquisition_customer_type_plot() -> ggplot:
    data = read_table("acquisition_composition_customer_type.csv")
    data["account_count"] = pd.to_numeric(data["account_count"])
    data["share_pct"] = pd.to_numeric(data["share_of_cohort"]) * 100
    ordered_categories = data.sort_values("account_count")["category"].tolist()
    data["category"] = pd.Categorical(
        data["category"], categories=ordered_categories, ordered=True
    )
    data["count_share_label"] = data.apply(
        lambda row: f"{int(row['account_count'])} ({row['share_pct']:.1f}%)",
        axis=1,
    )

    return (
        ggplot(data, aes(x="category", y="account_count"))
        + geom_col(fill=BAY_6[0], width=0.72)
        + geom_text(
            aes(label="count_share_label"),
            nudge_y=14,
            ha="left",
            color="#303336",
            size=9,
            family=FONT,
        )
        + coord_flip()
        + scale_y_continuous(
            limits=(0, 760), breaks=(0, 200, 400, 600), expand=(0, 0)
        )
        + labs(
            title="SMB accounts make up nearly two-thirds of the cohort",
            subtitle="Customer type • cohort n = 977 • bars show account counts",
            x="",
            y="Accounts (count)",
            caption="Labels show count and share of the cohort.",
        )
        + rti_growth_plotnine_theme()
        + theme(
            figure_size=(9, 4.6),
            panel_grid_major_y=element_blank(),
        )
    )


def acquisition_dev_language_plot() -> ggplot:
    data = read_table("acquisition_composition_dev_language.csv")
    data["account_count"] = pd.to_numeric(data["account_count"])
    data["share_pct"] = pd.to_numeric(data["share_of_cohort"]) * 100
    ordered_categories = data.sort_values("account_count")["category"].tolist()
    data["category"] = pd.Categorical(
        data["category"], categories=ordered_categories, ordered=True
    )
    data["count_share_label"] = data.apply(
        lambda row: f"{int(row['account_count'])} ({row['share_pct']:.1f}%)",
        axis=1,
    )

    return (
        ggplot(data, aes(x="category", y="account_count"))
        + geom_col(fill=BAY_6[0], width=0.72)
        + geom_text(
            aes(label="count_share_label"),
            nudge_y=15,
            ha="left",
            color="#303336",
            size=9,
            family=FONT,
        )
        + coord_flip()
        + scale_y_continuous(
            limits=(0, 450), breaks=(0, 100, 200, 300, 400), expand=(0, 0)
        )
        + labs(
            title="Unknown is the largest reported development-language category",
            subtitle="Development language • cohort n = 977 • bars show account counts",
            x="",
            y="Accounts (count)",
            caption=(
                "Labels show count and cohort share. `unknown` is an explicit "
                "reported category, not a missing value."
            ),
        )
        + rti_growth_plotnine_theme()
        + theme(figure_size=(9, 5.2), panel_grid_major_y=element_blank())
    )


def observed_coverage_plot() -> ggplot:
    calendar = read_table("daily_observed_coverage.csv")
    calendar["date"] = pd.to_datetime(calendar["date"])
    calendar["eligible_account_count"] = pd.to_numeric(
        calendar["eligible_account_count"]
    )
    calendar["coverage_pct"] = (
        pd.to_numeric(calendar["observed_coverage_rate"]) * 100
    )
    calendar["panel"] = "Calendar date"
    calendar["x_position"] = (
        1000 + (calendar["date"] - pd.Timestamp("2022-02-01")).dt.days
    )

    age = read_table("age_day_observed_coverage.csv")
    age["age_day"] = pd.to_numeric(age["age_day"])
    age["eligible_account_count"] = pd.to_numeric(age["eligible_account_count"])
    age["coverage_pct"] = (
        pd.to_numeric(age["observed_usage_account_fraction"]) * 100
    )
    age["panel"] = "Elapsed account age (days)"
    age["x_position"] = age["age_day"]

    data = pd.concat(
        [
            calendar[["panel", "x_position", "coverage_pct"]],
            age[["panel", "x_position", "coverage_pct"]],
        ],
        ignore_index=True,
    )
    data["panel"] = pd.Categorical(
        data["panel"],
        categories=["Calendar date", "Elapsed account age (days)"],
        ordered=True,
    )

    extract_end = pd.Timestamp("2022-02-27")
    extract_end_position = 1000 + (extract_end - pd.Timestamp("2022-02-01")).days
    marker = pd.DataFrame(
        {"panel": ["Calendar date"], "xintercept": [extract_end_position]}
    )
    marker_label = pd.DataFrame(
        {
            "panel": ["Calendar date"],
            "x_position": [extract_end_position + 2],
            "coverage_pct": [97],
            "label": ["Cohort extract ends: Feb 27"],
        }
    )
    date_labels = {
        1000: "Feb 01",
        1014: "Feb 15",
        1042: "Mar 15",
        1073: "Apr 15",
        1088: "Apr 30",
        0: "0",
        15: "15",
        30: "30",
        45: "45",
        62: "62",
    }

    return (
        ggplot(data, aes(x="x_position", y="coverage_pct", group="panel"))
        + geom_line(color=BAY_6[1], size=1.05)
        + geom_vline(
            data=marker,
            mapping=aes(xintercept="xintercept"),
            inherit_aes=False,
            color=BAY_6[3],
            linetype="dashed",
            size=0.65,
        )
        + geom_text(
            data=marker_label,
            mapping=aes(x="x_position", y="coverage_pct", label="label"),
            inherit_aes=False,
            color=BAY_6[3],
            size=8,
            family=FONT,
            ha="left",
            va="bottom",
        )
        + facet_wrap("~panel", nrow=1, scales="free_x")
        + scale_x_continuous(
            breaks=list(date_labels),
            labels=lambda values: [date_labels.get(int(value), "") for value in values],
            expand=(0.02, 0),
        )
        + scale_y_continuous(
            limits=(0, 100),
            breaks=(0, 25, 50, 75, 100),
            labels=lambda values: [f"{value:.0f}%" for value in values],
            expand=(0, 0),
        )
        + labs(
            title="Observed account-day coverage is lower at later dates and ages",
            subtitle=(
                "Calendar dates: Feb 1–Apr 30 • account age: days 0–62 "
                "(day 0 = creation day)"
            ),
            x="Calendar date / age since account creation (days)",
            y="Observed account-day coverage (%)",
            caption=(
                "Calendar-date eligible denominator grows through Feb 27, then stays "
                "at n = 977; age-day denominator is n = 977 throughout.\n"
                "Missing usage rows do not prove inactivity. Lines are unsmoothed. "
                "Sources: daily_observed_coverage.csv and age_day_observed_coverage.csv."
            ),
        )
        + rti_growth_plotnine_theme()
        + theme(
            figure_size=(12, 5.6),
            panel_grid_major_x=element_blank(),
            panel_spacing_x=0.05,
        )
    )


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    save_png(acquisition_weekly_plot(), "weekly_acquisition.png", width=10, height=5.2)
    save_png(
        acquisition_customer_type_plot(),
        "acquisition_customer_type.png",
        width=9,
        height=4.6,
    )
    save_png(
        acquisition_dev_language_plot(),
        "acquisition_dev_language.png",
        width=9,
        height=5.2,
    )
    save_png(
        observed_coverage_plot(),
        "observed_account_day_coverage.png",
        width=12,
        height=5.6,
    )


if __name__ == "__main__":
    main()

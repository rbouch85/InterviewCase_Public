"""Build descriptive acquisition tables from the February 2022 case CSVs."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUTPUTS = Path(__file__).resolve().parent
COHORT_START = date(2022, 2, 1)
COHORT_END = date(2022, 2, 27)


def read_csv(filename: str) -> list[dict[str, str]]:
    with (ROOT / filename).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def parse_day(value: str) -> date:
    return datetime.strptime(value[:10], "%Y-%m-%d").date()


def write_csv(filename: str, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with (OUTPUTS / filename).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    creation_rows = read_csv("Case_AccountCreation.csv")
    account_data = read_csv("Case_AccountData.csv")
    creation = [
        row
        for row in creation_rows
        if COHORT_START <= parse_day(row["AccountCreatedDay"]) <= COHORT_END
    ]
    cohort_ids = {row["AccountID"] for row in creation}
    denominator = len(cohort_ids)

    daily: Counter[date] = Counter()
    weekly_days: dict[date, list[date]] = defaultdict(list)
    for row in creation:
        created = parse_day(row["AccountCreatedDay"])
        week_start = created - timedelta(days=(created.weekday() + 1) % 7)
        daily[created] += 1
        weekly_days[week_start].append(created)

    daily_rows = [
        {
            "account_created_day": day.isoformat(),
            "account_count": daily[day],
            "cohort_account_denominator": denominator,
            "share_of_cohort": f"{daily[day] / denominator:.6f}",
        }
        for day in sorted(daily)
    ]
    write_csv(
        "acquisition_daily.csv",
        ["account_created_day", "account_count", "cohort_account_denominator", "share_of_cohort"],
        daily_rows,
    )

    weekly_rows = []
    for week_start in sorted(weekly_days):
        days = weekly_days[week_start]
        week_end = week_start + timedelta(days=6)
        observed_start = min(days)
        observed_end = max(days)
        count = len(days)
        weekly_rows.append(
            {
                "sunday_start_week": week_start.isoformat(),
                "calendar_week_end": week_end.isoformat(),
                "observed_cohort_start": observed_start.isoformat(),
                "observed_cohort_end": observed_end.isoformat(),
                "partial_week": str(observed_start != week_start or observed_end != week_end).lower(),
                "account_count": count,
                "cohort_account_denominator": denominator,
                "share_of_cohort": f"{count / denominator:.6f}",
            }
        )
    write_csv(
        "acquisition_weekly_sunday_start.csv",
        [
            "sunday_start_week",
            "calendar_week_end",
            "observed_cohort_start",
            "observed_cohort_end",
            "partial_week",
            "account_count",
            "cohort_account_denominator",
            "share_of_cohort",
        ],
        weekly_rows,
    )

    for field, output, categories in (
        ("CustomerType", "acquisition_composition_customer_type.csv", ["Credit_Program", "Enterprise", "SMB"]),
        ("DevLanguage", "acquisition_composition_dev_language.csv", ["dotnet", "java", "node", "php", "python", "unknown"]),
    ):
        counts = Counter(row[field] for row in account_data if row["AccountID"] in cohort_ids)
        rows = [
            {
                "category": category,
                "account_count": counts[category],
                "cohort_account_denominator": denominator,
                "share_of_cohort": f"{counts[category] / denominator:.6f}",
            }
            for category in categories
        ]
        write_csv(
            output,
            ["category", "account_count", "cohort_account_denominator", "share_of_cohort"],
            rows,
        )


if __name__ == "__main__":
    main()

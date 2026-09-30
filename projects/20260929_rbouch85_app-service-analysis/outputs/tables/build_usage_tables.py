"""Build descriptive account-day coverage tables from the case CSVs."""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUTPUTS = Path(__file__).resolve().parent
COHORT_START = date(2022, 2, 1)
COHORT_END = date(2022, 2, 27)
USAGE_END = date(2022, 4, 30)
MAX_AGE_DAY = 62


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
    accounts = read_csv("Case_AccountData.csv")
    creation_rows = read_csv("Case_AccountCreation.csv")
    usage_rows = read_csv("Case_UsageData.csv")

    account_ids = [row["AccountID"] for row in accounts]
    creation_ids = [row["AccountID"] for row in creation_rows]
    assert len(accounts) == len(creation_rows) == 977
    assert len(set(account_ids)) == len(account_ids)
    assert len(set(creation_ids)) == len(creation_ids)
    assert set(account_ids) == set(creation_ids)
    assert all(value.strip() for rows in (accounts, creation_rows, usage_rows) for row in rows for value in row.values())

    created = {row["AccountID"]: parse_day(row["AccountCreatedDay"]) for row in creation_rows}
    assert min(created.values()) == COHORT_START
    assert max(created.values()) == COHORT_END
    assert all(
        row["AccountCreatedDay_Key"] == created[row["AccountID"]].strftime("%Y%m%d")
        for row in creation_rows
    )

    usage_dates: set[date] = set()
    usage_pairs: set[tuple[str, date]] = set()
    usage_by_date: Counter[date] = Counter()
    usage_by_account_age: Counter[tuple[str, int]] = Counter()
    for row in usage_rows:
        account_id = row["AccountID"]
        usage_date = parse_day(row["UsageDate"])
        assert account_id in created
        assert row["UsageDate_Key"] == usage_date.strftime("%Y%m%d")
        assert created[account_id] <= usage_date <= USAGE_END
        pair = (account_id, usage_date)
        assert pair not in usage_pairs
        usage_pairs.add(pair)
        usage_dates.add(usage_date)
        usage_by_date[usage_date] += 1
        usage_by_account_age[(account_id, (usage_date - created[account_id]).days)] += 1

    expected_dates = {COHORT_START + timedelta(days=offset) for offset in range(89)}
    assert len(usage_rows) == 44_352
    assert len(usage_pairs) == 44_352
    assert usage_dates == expected_dates
    assert {account_id for account_id, _ in usage_pairs} == set(created)

    calendar_rows = []
    for offset in range(89):
        current_date = COHORT_START + timedelta(days=offset)
        eligible = sum(creation_date <= current_date for creation_date in created.values())
        observed = usage_by_date[current_date]
        assert 0 <= observed <= eligible
        calendar_rows.append(
            {
                "date": current_date.isoformat(),
                "eligible_account_count": eligible,
                "observed_account_count": observed,
                "observed_coverage_rate": f"{observed / eligible:.9f}",
            }
        )
    write_csv(
        "daily_observed_coverage.csv",
        ["date", "eligible_account_count", "observed_account_count", "observed_coverage_rate"],
        calendar_rows,
    )

    cohort_size = len(created)
    age_rows = []
    for age_day in range(MAX_AGE_DAY + 1):
        observed = sum(
            usage_by_account_age[(account_id, age_day)] > 0 for account_id in created
        )
        age_rows.append(
            {
                "age_day": age_day,
                "eligible_account_count": cohort_size,
                "accounts_with_observed_usage": observed,
                "observed_usage_account_fraction": f"{observed / cohort_size:.9f}",
            }
        )
    write_csv(
        "age_day_observed_coverage.csv",
        [
            "age_day",
            "eligible_account_count",
            "accounts_with_observed_usage",
            "observed_usage_account_fraction",
        ],
        age_rows,
    )

    account_rows = []
    for account_id in sorted(created):
        observed_days = sum(
            usage_by_account_age[(account_id, age_day)] > 0
            for age_day in range(MAX_AGE_DAY + 1)
        )
        account_rows.append(
            {
                "AccountID": account_id,
                "AccountCreatedDay": created[account_id].isoformat(),
                "eligible_window_days": MAX_AGE_DAY + 1,
                "distinct_observed_days_age_0_62": observed_days,
                "observed_day_rate_age_0_62": f"{observed_days / (MAX_AGE_DAY + 1):.9f}",
            }
        )
    write_csv(
        "per_account_age_0_62_observed_days.csv",
        [
            "AccountID",
            "AccountCreatedDay",
            "eligible_window_days",
            "distinct_observed_days_age_0_62",
            "observed_day_rate_age_0_62",
        ],
        account_rows,
    )


if __name__ == "__main__":
    main()

---
name: dataset-profiling
description: Use the InterviewCase CSV schemas, joins, and descriptive coverage safely
---

# Dataset profiling skill

Use this skill before querying or visualizing the interview-case data. The
source files are repository inputs; do not rewrite them. Reproduce the
descriptive outputs with
`projects/20260924_rbouch85_dataset-documentation/profile_and_visualize.py`.

## Dataset catalog

### `Case_AccountData.csv`

- **Grain:** one row per account; 977 rows and 977 distinct `AccountID`s.
- **Columns:** `AccountID` (string UUID, unique identifier); `CustomerType`
  (categorical; `Credit_Program`, `Enterprise`, `SMB`); `DevLanguage`
  (categorical; `dotnet`, `java`, `node`, `php`, `python`, `unknown`).
- **Nulls:** no blank values in the supplied extract. `unknown` is an explicit
  `DevLanguage` value.
- **Coverage:** no date column.
- **Observed distribution:** `SMB` 625, `Enterprise` 242,
  `Credit_Program` 110; language values are `unknown` 362, `dotnet` 266,
  `node` 119, `python` 105, `php` 84, `java` 41.

### `Case_AccountCreation.csv`

- **Grain:** one row per account creation record; 977 rows and 977 distinct
  `AccountID`s.
- **Columns:** `AccountID` (string UUID, unique identifier);
  `AccountCreatedDay` (ISO timestamp text, `2022-02-01` through `2022-02-27`);
  `AccountCreatedDay_Key` (eight-character `YYYYMMDD` text key, 27 values);
  `AccountCreatedWeek` (ISO timestamp text for Sunday-start weeks,
  `2022-01-30` through `2022-02-27`); `AccountCreatedWeek_Key`
  (five `YYYYMMDD` text week keys: `20220130`, `20220206`, `20220213`,
  `20220220`, `20220227`).
- **Nulls:** no blank values in the supplied extract.
- **Observed day counts:** all 27 February day values occur; counts range
  from 6 to 87 accounts per day.
- **Observed week counts:** `20220130` 174, `20220206` 324, `20220213` 239,
  `20220220` 234, `20220227` 6.

### `Case_UsageData.csv`

- **Grain:** one row per observed account-day; 44,352 rows and 977 distinct
  accounts.
- **Columns:** `AccountID` (repeating string UUID join key);
  `UsageDate` (ISO timestamp text, `2022-02-01` through `2022-04-30`);
  `UsageDate_Key` (89 `YYYYMMDD` text date keys).
- **Nulls:** no blank values in the supplied extract.
- **Coverage:** all 977 creation-table accounts appear at least once.
  Account-day rows per account range from 1 to 89, averaging 45.4.
- **Date values:** 89 consecutive calendar dates from `20220201` through
  `20220430`; daily active-account counts are available in the generated
  summary report.

## Join and question guide

Join on `AccountID`. Use `Case_AccountData` for account composition,
`Case_AccountCreation` for acquisition timing and cohort definitions, and
`Case_UsageData` for observed account-day activity. For descriptive questions,
always state the denominator, cohort, date window, and whether an absent
account-day is treated as unobserved rather than inactive.

Do not call account-day presence a retention outcome without defining a
follow-up window. The usage extract ends on 2022-04-30, so later cohorts have
less possible follow-up. The data supports descriptive activity and coverage
summaries, not causal or inferential claims.

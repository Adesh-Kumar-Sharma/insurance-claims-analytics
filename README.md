# Insurance Claims Analytics Dashboard

A small portfolio project built to demonstrate data preparation, SQL aggregation, exploratory analysis, dashboarding, and data-quality checks in an insurance-style context. **All records are synthetic; this is not real data and is not an actuarial pricing or claims-decision model.**

## What it demonstrates

- Load and validate a 1,000-row CSV dataset with Python and Pandas.
- Derive incurred amount as paid amount plus current reserve, and group claims by reporting month and type.
- Run SQL aggregation through SQLite.
- Explore claim counts, amount and open claims in a Streamlit dashboard.
- Run basic data-quality checks and export filtered records to CSV.
- Verify core calculations using pytest.

## Run locally

Python 3.10+ recommended. From this folder, create and activate a virtual environment, then run:

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
streamlit run app.py
```

## Suggested analysis questions

1. Which claim types contribute most to paid amounts plus reserves?
2. How do monthly claim volumes vary over the two-year synthetic period?
3. How do open claim counts change after selecting a region or claim type?
4. Which data-quality checks should be added before a real reporting pipeline goes into production?

## Important limitations

The data is randomly generated to illustrate the workflow. It has no real policyholders, product rules or actual loss history. Amounts and status patterns are not calibrated to an insurer. The dashboard must not be used for pricing, reserving, fraud detection, coverage decisions or customer decisions. A production version would require governed data, agreed metric definitions, access controls, privacy review, and validation with actuarial/claims experts.

## Summary

> Built a Python/Pandas and SQLite analytics workflow over synthetic insurance claims, deriving incurred amounts, aggregating claims by type and month, surfacing results in Streamlit, and adding automated checks for core calculations and data quality.

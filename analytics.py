"""Small, auditable analytics helpers for the synthetic insurance claims demo."""
from __future__ import annotations
import sqlite3
from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = {
    "claim_id", "reported_date", "claim_type", "region", "channel",
    "customer_tenure_months", "claim_amount_eur", "paid_amount_eur",
    "reserve_amount_eur", "claim_status",
}

def load_claims(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["reported_date"])
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    numeric = ["customer_tenure_months", "claim_amount_eur", "paid_amount_eur", "reserve_amount_eur"]
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def prepare_claims(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["reported_date"] = pd.to_datetime(out["reported_date"], errors="coerce")
    out["incurred_amount_eur"] = out["paid_amount_eur"].fillna(0) + out["reserve_amount_eur"].fillna(0)
    out["report_month"] = out["reported_date"].dt.to_period("M").dt.to_timestamp()
    return out

def summary_metrics(df: pd.DataFrame) -> dict[str, float | int]:
    df = prepare_claims(df)
    if df.empty:
        return {"claim_count": 0, "total_claim_amount": 0.0, "total_incurred": 0.0, "open_claims": 0, "avg_claim_amount": 0.0}
    return {
        "claim_count": int(df["claim_id"].nunique()),
        "total_claim_amount": round(float(df["claim_amount_eur"].fillna(0).sum()), 2),
        "total_incurred": round(float(df["incurred_amount_eur"].sum()), 2),
        "open_claims": int((df["claim_status"] == "Open").sum()),
        "avg_claim_amount": round(float(df["claim_amount_eur"].dropna().mean()) if df["claim_amount_eur"].notna().any() else 0.0, 2),
    }

def sql_claim_type_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Use SQLite SQL aggregation to model a small ETL-to-analytics workflow."""
    working = prepare_claims(df)
    with sqlite3.connect(":memory:") as con:
        working.to_sql("claims", con, index=False, if_exists="replace")
        return pd.read_sql_query(
            """SELECT claim_type, COUNT(*) AS claim_count,
                      ROUND(AVG(claim_amount_eur), 2) AS avg_claim_eur,
                      ROUND(SUM(paid_amount_eur + reserve_amount_eur), 2) AS incurred_eur
               FROM claims GROUP BY claim_type ORDER BY incurred_eur DESC""", con)

def data_quality_checks(df: pd.DataFrame) -> pd.DataFrame:
    checks = [
        ("Duplicate claim IDs", int(df["claim_id"].duplicated().sum())),
        ("Missing reported date", int(pd.to_datetime(df["reported_date"], errors="coerce").isna().sum())),
        ("Non-positive claim amount", int((pd.to_numeric(df["claim_amount_eur"], errors="coerce") <= 0).sum())),
        ("Negative payment or reserve", int(((pd.to_numeric(df["paid_amount_eur"], errors="coerce") < 0) | (pd.to_numeric(df["reserve_amount_eur"], errors="coerce") < 0)).sum())),
    ]
    return pd.DataFrame(checks, columns=["Check", "Issues found"])

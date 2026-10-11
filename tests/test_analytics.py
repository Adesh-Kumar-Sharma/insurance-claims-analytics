from pathlib import Path
import pandas as pd
from analytics import load_claims, prepare_claims, summary_metrics, sql_claim_type_summary, data_quality_checks

DATA = Path(__file__).resolve().parents[1] / "data" / "synthetic_claims.csv"

def test_dataset_loads_and_has_unique_ids():
    df=load_claims(DATA)
    assert len(df) == 1000
    assert df["claim_id"].is_unique

def test_summary_metrics_match_rows():
    df=load_claims(DATA)
    metrics=summary_metrics(df)
    assert metrics["claim_count"] == df["claim_id"].nunique()
    assert metrics["open_claims"] == int((df["claim_status"] == "Open").sum())
    assert metrics["total_claim_amount"] > 0

def test_sql_summary_covers_each_claim_type():
    df=prepare_claims(load_claims(DATA))
    result=sql_claim_type_summary(df)
    assert set(result["claim_type"]) == set(df["claim_type"])
    assert (result["claim_count"] > 0).all()

def test_quality_checks_report_no_duplicate_ids():
    df=load_claims(DATA)
    checks=data_quality_checks(df).set_index("Check")
    assert checks.loc["Duplicate claim IDs", "Issues found"] == 0

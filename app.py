from pathlib import Path
import streamlit as st
import pandas as pd
from analytics import load_claims, prepare_claims, summary_metrics, sql_claim_type_summary, data_quality_checks

DATA_PATH = Path(__file__).parent / "data" / "synthetic_claims.csv"
st.set_page_config(page_title="Insurance Claims Analytics", layout="wide")
st.title("Insurance Claims Analytics Dashboard")
st.caption("Portfolio prototype using synthetic data only - not actual customer data.")

df = prepare_claims(load_claims(DATA_PATH))
with st.sidebar:
    st.header("Filters")
    claim_types = st.multiselect("Claim type", sorted(df["claim_type"].dropna().unique()), default=sorted(df["claim_type"].dropna().unique()))
    regions = st.multiselect("Region", sorted(df["region"].dropna().unique()), default=sorted(df["region"].dropna().unique()))
    statuses = st.multiselect("Status", sorted(df["claim_status"].dropna().unique()), default=sorted(df["claim_status"].dropna().unique()))
    st.caption("Data is generated for demonstration and has no real policyholder information.")
filtered = df[df["claim_type"].isin(claim_types) & df["region"].isin(regions) & df["claim_status"].isin(statuses)].copy()
metrics = summary_metrics(filtered)
col1,col2,col3,col4 = st.columns(4)
col1.metric("Claims", f'{metrics["claim_count"]:,}')
col2.metric("Claim amount", f'€{metrics["total_claim_amount"]:,.0f}')
col3.metric("Paid + reserve", f'€{metrics["total_incurred"]:,.0f}')
col4.metric("Open claims", f'{metrics["open_claims"]:,}')

left,right=st.columns(2)
with left:
    st.subheader("Claim counts by type")
    counts=filtered.groupby("claim_type").size().sort_values(ascending=False).rename("Claims")
    st.bar_chart(counts)
with right:
    st.subheader("Monthly reported claims")
    monthly=filtered.groupby("report_month").size().rename("Claims").sort_index()
    st.line_chart(monthly)

st.subheader("SQL summary by claim type")
st.dataframe(sql_claim_type_summary(filtered), use_container_width=True, hide_index=True)
st.subheader("Data-quality checks")
st.dataframe(data_quality_checks(filtered), use_container_width=True, hide_index=True)
st.subheader("Filtered claims")
show_cols=["claim_id","reported_date","claim_type","region","channel","claim_status","claim_amount_eur","paid_amount_eur","reserve_amount_eur","incurred_amount_eur"]
st.dataframe(filtered[show_cols].sort_values("reported_date",ascending=False), use_container_width=True, hide_index=True)
st.download_button("Download filtered data as CSV", data=filtered[show_cols].to_csv(index=False).encode("utf-8"), file_name="filtered_claims.csv", mime="text/csv")
st.info("Interpretation note: incurred amount is defined here as paid amount + current reserve. These synthetic records do not represent actuarial pricing, reserving, fraud scoring or insurance decisions.")

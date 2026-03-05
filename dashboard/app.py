import streamlit as st
import pandas as pd
import snowflake.connector
import plotly.express as px

# -----------------------------
# Snowflake Connection
# -----------------------------
conn = snowflake.connector.connect(
    user="RAGAWORKSPACE",
    password="S@snowflake@1020",
    account="IQXOOAU-OL07219",
    warehouse="COMPUTE_WH",
    database="PE_PLATFORM",
    schema="ANALYTICS"
)

# -----------------------------
# Load LBO Results
# -----------------------------
query = """
SELECT *
FROM LBO_RETURNS
ORDER BY IRR DESC
"""

df = pd.read_sql(query, conn)

# Convert IRR to percentage
df["IRR (%)"] = df["IRR"] * 100

# -----------------------------
# Page Title
# -----------------------------
st.title("Private Equity Deal Intelligence Platform")

st.markdown(
"""
Identify potential **buyout acquisition targets** using financial metrics,
deal scoring, and LBO return simulations.
"""
)

st.divider()

# -----------------------------
# Key Metrics
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Companies Analyzed", len(df))
col2.metric("Highest IRR", f"{df['IRR (%)'].max():.1f}%")
col3.metric("Average IRR", f"{df['IRR (%)'].mean():.1f}%")

st.divider()

# -----------------------------
# Sector Filter
# -----------------------------
sector = st.selectbox(
    "Filter by Sector",
    ["All"] + sorted(df["SECTOR"].unique())
)

if sector != "All":
    df = df[df["SECTOR"] == sector]

# -----------------------------
# Top Buyout Opportunities
# -----------------------------
st.subheader("Top Buyout Opportunities")

st.dataframe(
    df.sort_values("IRR (%)", ascending=False)[
        [
            "COMPANY_NAME",
            "SECTOR",
            "CURRENT_EBITDA",
            "EQUITY_MULTIPLE",
            "IRR (%)"
        ]
    ],
    use_container_width=True
)

# -----------------------------
# Top Deals Chart
# -----------------------------
st.subheader("Top Deals by IRR")

top_deals = df.sort_values("IRR (%)", ascending=False).head(10)

fig = px.bar(
    top_deals,
    x="COMPANY_NAME",
    y="IRR (%)",
    color="SECTOR",
    title="Top 10 Buyout Opportunities"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Profitability vs Leverage
# -----------------------------
st.subheader("Profitability vs Leverage")

metrics_query = """
SELECT *
FROM COMPANY_FINANCIAL_METRICS
"""

metrics_df = pd.read_sql(metrics_query, conn)

scatter = px.scatter(
    metrics_df,
    x="DEBT_TO_EBITDA",
    y="EBITDA_MARGIN",
    color="SECTOR",
    size="REVENUE",
    title="EBITDA Margin vs Leverage"
)

st.plotly_chart(scatter, use_container_width=True)

# -----------------------------
# Deal Recommendations
# -----------------------------
st.subheader("Recommended Targets")

top_targets = df.sort_values("IRR (%)", ascending=False).head(3)

for i, row in top_targets.iterrows():
    st.markdown(f"""
**{row['COMPANY_NAME']}**

Sector: {row['SECTOR']}  
Equity Multiple: {row['EQUITY_MULTIPLE']:.2f}x  
Expected IRR: **{row['IRR (%)']:.1f}%**

Reason: High return potential based on revenue growth and strong profitability.
""")

st.divider()

# -----------------------------
# Footer
# -----------------------------
st.markdown(
"""
**Pipeline**

Synthetic Financial Data → Snowflake Warehouse → Financial Metrics → Deal Scoring → LBO Simulation → IRR Ranking
"""
)
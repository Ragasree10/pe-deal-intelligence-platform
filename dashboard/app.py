import streamlit as st
import pandas as pd
import snowflake.connector
import plotly.express as px

# -----------------------------
# Snowflake Connection
# -----------------------------
conn = snowflake.connector.connect(
    user=st.secrets["snowflake"]["user"],
    password=st.secrets["snowflake"]["password"],
    account=st.secrets["snowflake"]["account"],
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"]
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

st.markdown("""
This platform screens potential **Private Equity acquisition targets**
using financial metrics, deal scoring, and LBO return simulations.
""")

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
# Investment Criteria
# -----------------------------
st.subheader("Investment Screening Criteria")

irr_threshold = st.slider(
    "Minimum IRR (%)",
    min_value=0,
    max_value=100,
    value=25
)

sector = st.selectbox(
    "Filter by Sector",
    ["All"] + sorted(df["SECTOR"].unique())
)

if sector != "All":
    df = df[df["SECTOR"] == sector]

# -----------------------------
# Filter Deals
# -----------------------------
qualified_deals = df[df["IRR (%)"] >= irr_threshold]

# -----------------------------
# Top Deals Chart
# -----------------------------
st.subheader("Top Buyout Opportunities")

top_deals = df.sort_values("IRR (%)", ascending=False).head(10)

fig = px.bar(
    top_deals,
    x="COMPANY_NAME",
    y="IRR (%)",
    color="SECTOR",
    title="Top 10 Deals by IRR"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Qualified Deals Table
# -----------------------------
st.subheader("Qualified Investment Opportunities")

st.dataframe(
    qualified_deals[
        [
            "COMPANY_NAME",
            "SECTOR",
            "CURRENT_EBITDA",
            "EQUITY_MULTIPLE",
            "IRR (%)"
        ]
    ].sort_values("IRR (%)", ascending=False),
    use_container_width=True
)

# -----------------------------
# Recommended Targets
# -----------------------------
st.subheader("Recommended Targets")

top_targets = df.sort_values("IRR (%)", ascending=False).head(3)

for _, row in top_targets.iterrows():
    st.markdown(f"""
**{row['COMPANY_NAME']}**

Sector: {row['SECTOR']}  
Equity Multiple: {row['EQUITY_MULTIPLE']:.2f}x  
Expected IRR: **{row['IRR (%)']:.1f}%**

Reason: High projected return potential based on strong growth and profitability.
""")

st.divider()

# -----------------------------
# Footer
# -----------------------------
st.markdown("""
**Data Pipeline**

Python Synthetic Data → Snowflake Warehouse → SQL Financial Models →  
Deal Scoring Engine → LBO Simulation → IRR Analysis → Streamlit Dashboard
""")
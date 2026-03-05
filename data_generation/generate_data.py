import pandas as pd
import numpy as np
from faker import Faker
import random

fake = Faker()

NUM_COMPANIES = 300
YEARS = [2019, 2020, 2021, 2022, 2023]

sectors = [
    "Software",
    "Healthcare",
    "Fintech",
    "Industrial",
    "Consumer"
]

countries = [
    "UK",
    "Germany",
    "France",
    "Netherlands",
    "USA"
]

# -------------------------
# Generate Companies Table
# -------------------------

companies = []

for i in range(NUM_COMPANIES):

    companies.append({
        "company_id": i + 1,
        "company_name": fake.company(),
        "sector": random.choice(sectors),
        "country": random.choice(countries),
        "founded_year": random.randint(1985, 2018)
    })

companies_df = pd.DataFrame(companies)

# -------------------------
# Generate Financials Table
# -------------------------

financials = []

for company in companies:

    base_revenue = np.random.uniform(20, 300) * 1e6
    growth_rate = np.random.normal(0.12, 0.05)

    revenue = base_revenue

    for year in YEARS:

        revenue = revenue * (1 + growth_rate)

        ebitda_margin = np.random.uniform(0.15, 0.35)
        ebitda = revenue * ebitda_margin

        debt = np.random.uniform(1.0, 4.0) * ebitda
        cash = np.random.uniform(0.05, 0.3) * revenue
        capex = np.random.uniform(0.03, 0.08) * revenue

        financials.append({
            "company_id": company["company_id"],
            "year": year,
            "revenue": revenue,
            "ebitda": ebitda,
            "debt": debt,
            "cash": cash,
            "capex": capex
        })

financials_df = pd.DataFrame(financials)

# -------------------------
# Save Data
# -------------------------

companies_df.to_csv("data/companies.csv", index=False)
financials_df.to_csv("data/financials.csv", index=False)

print("Synthetic PE dataset generated successfully.")
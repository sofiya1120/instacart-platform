# 🛒 Instacart Customer Intelligence Platform

End-to-end data platform built on Instacart's public dataset.
3.4 million orders · 206,000 customers · 50,000 products.

## 🔗 Live Links
- **Streamlit Dashboard**: https://instacart-platform-gyawczu6x7462utm2mtprf.streamlit.app/
- **Tableau Public**: https://public.tableau.com/app/profile/sofiya.mohammed6217/viz/InstacartCustomerIntelligencePlatform/InstacartIntelligence
- **GitHub**: https://github.com/sofiya1120/instacart-platform

---

## 🏗️ Architecture

Kaggle Dataset
↓
Python Ingestion (pandas)
↓
Neon PostgreSQL
├── raw.*        (exact source copy)
├── staging.*    (cleaned + typed)
├── marts.*      (fact + dimension tables)
└── analytics.*  (cohort, RFM, funnel, A/B results)
↓
dbt Core (transformations + tests + lineage)
↓
Python Analytics Layer
├── Cohort Retention Analysis
├── RFM Segmentation
├── Funnel Analysis
└── A/B Testing (statsmodels)
↓
scikit-learn Churn Prediction Model
↓
Apache Airflow (orchestration)
↓
Streamlit Dashboard + Tableau Public + Groq NL Query

---

## 🛠️ Stack

| Layer | Tools |
|---|---|
| Language | Python 3.11 |
| Database | Neon PostgreSQL (cloud) |
| Transformation | dbt Core 1.7.4 |
| Analytics | pandas, scipy, statsmodels |
| Machine Learning | scikit-learn (Gradient Boosting) |
| Orchestration | Apache Airflow (Astro CLI) |
| CI/CD | GitHub Actions |
| Dashboard | Streamlit, Tableau Public |
| AI Layer | Groq API (Llama 3) |

---

## 📊 What I Built

### Data Engineering
- Designed a 3-layer warehouse (raw → staging → marts) in Neon PostgreSQL
- Built 5 dbt models with full test coverage (unique, not_null, accepted_values)
- Implemented data quality checks before every pipeline run
- Orchestrated the full pipeline with an Airflow DAG on a daily schedule
- Set up GitHub Actions CI to run dbt tests on every push to main

### Analytics
- **Cohort Retention** — tracked 13 periods, 97.5% retention at period 1
- **RFM Segmentation** — classified 30,148 customers into 6 segments
- **Funnel Analysis** — identified drop-off patterns across engagement stages
- **A/B Testing** — weekday vs weekend reorder rates, p=0.030641 (significant at 95%)

### Machine Learning
- Built a churn prediction model using Gradient Boosting
- Features: order frequency, basket size, reorder rate, RFM scores
- **AUC: 0.7425** | Churn rate: 13.4%
- Avoided data leakage by carefully separating churn definition from features

### AI Layer
- Built a natural language query interface using Groq (Llama 3)
- Ask questions in plain English, get SQL results instantly

---

## 🔍 Key Findings

1. **97.5%** of customers return within 30 days of their first order
2. **Loyal Customers** is the largest RFM segment (7,485 customers)
3. **22%** of customers are At Risk or Lost — biggest retention opportunity
4. Weekday orders have **statistically significantly higher** reorder rates than weekend (p=0.03)
5. **Bananas** are the most ordered product — organic produce dominates all categories
6. Champions segment (5,397 customers) drives disproportionate order volume

---

## 🚀 How to Run

```bash
# Clone the repo
git clone https://github.com/sofiya1120/instacart-platform.git
cd instacart-platform

# Set up environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Add your credentials
cp .env.example .env
# Fill in your Neon PostgreSQL and Groq API key

# Load data
python scripts/ingest.py

# Run dbt transformations
cd instacart_dbt
dbt run
dbt test
cd ..

# Run analytics
python scripts/cohort_analysis.py
python scripts/rfm_analysis.py
python scripts/funnel_analysis.py
python scripts/ab_testing.py

# Train churn model
python scripts/churn_model.py

# Launch dashboard
streamlit run app.py
```

---

## 📁 Project Structure

```
instacart-platform/
├── data/
│   ├── raw/                    # Kaggle CSV files (gitignored)
│   └── processed/              # Exported CSVs for Tableau
├── notebooks/
│   └── 01_dataset_exploration.ipynb
├── scripts/
│   ├── __init__.py
│   ├── ingest.py               # Load CSVs into PostgreSQL
│   ├── data_quality.py         # Pre-pipeline quality checks
│   ├── cohort_analysis.py      # Cohort retention
│   ├── rfm_analysis.py         # RFM segmentation
│   ├── funnel_analysis.py      # Funnel analysis
│   ├── ab_testing.py           # A/B testing
│   ├── churn_model.py          # Churn prediction ML
│   ├── nl_query.py             # Groq NL query layer
│   └── export_for_tableau.py   # Export CSVs for Tableau
├── instacart_dbt/
│   ├── models/
│   │   ├── staging/            # stg_orders, stg_products, stg_order_products
│   │   └── marts/              # fct_orders, dim_customers, fct_product_performance
│   └── macros/                 # generate_schema_name.sql
├── airflow/
│   └── dags/
│       └── instacart_pipeline.py
├── models/
│   └── churn_model.pkl         # Saved model (gitignored)
├── app.py                      # Streamlit dashboard
├── requirements.txt
├── .env.example
└── .github/
    └── workflows/
        └── ci.yml              # GitHub Actions dbt CI
```
---

*Built by Sofiya Mohammed*
*Stack: Python · Neon PostgreSQL · dbt Core · Apache Airflow · scikit-learn · Groq · Streamlit · Tableau Public · GitHub Actions*
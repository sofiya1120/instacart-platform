from groq import Groq
from sqlalchemy import create_engine
from dotenv import load_dotenv
import pandas as pd
import os
import re

load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))
engine = create_engine(os.getenv('DB_URL'))

SCHEMA_CONTEXT = """
You are a PostgreSQL expert. The database has these tables:

staging.stg_orders
  columns: order_id, user_id, dataset_split, order_number,
           order_day_of_week, order_day_name, order_hour,
           days_since_prior_order

marts.fct_orders
  columns: order_id, user_id, dataset_split, order_number,
           order_day_of_week, order_day_name, order_hour,
           days_since_prior_order, basket_size,
           reordered_item_count, avg_cart_position, reorder_rate

marts.dim_customers
  columns: user_id, total_orders, avg_basket_size,
           avg_days_between_orders, avg_reorder_rate,
           lifetime_items, is_churned, customer_tier

marts.fct_product_performance
  columns: product_id, product_name, department_name, aisle_name,
           total_orders, reorder_count, avg_cart_position, reorder_rate

analytics.rfm_segments
  columns: user_id, "R", "F", "M", rfm_score, rfm_total, rfm_segment

analytics.cohort_retention
  columns: cohort, period_number, active_users, cohort_size, retention_rate

analytics.funnel_analysis
  columns: stage, users, pct_of_total, pct_of_prev, drop_off_pct

analytics.ab_test_results
  columns: test_name, control_label, treatment_label,
           control_n, treatment_n, control_mean, treatment_mean,
           lift_pct, t_statistic, p_value, cohens_d,
           significant_at_95, significant_at_99
"""

def natural_language_to_sql(question: str) -> str:
    prompt = f"""{SCHEMA_CONTEXT}

Convert this question to a valid PostgreSQL query.
Return ONLY the SQL — no explanation, no markdown, no backticks.

Question: {question}
"""
    response = client.chat.completions.create(
        model='llama-3.1-8b-instant',
        messages=[{'role': 'user', 'content': prompt}],
        max_tokens=400,
    )
    sql = response.choices[0].message.content.strip()
    sql = re.sub(r'```sql|```', '', sql).strip()
    return sql


def ask(question: str):
    print(f'\nQuestion: {question}')
    sql = natural_language_to_sql(question)
    print(f'Generated SQL:\n{sql}')
    try:
        df = pd.read_sql(sql, engine)
        print(f'\nResult:')
        print(df.to_string())
    except Exception as e:
        print(f'Query failed: {e}')


if __name__ == '__main__':
    ask('What are the top 5 departments by total orders?')
    ask('Which RFM segment has the most customers?')
    ask('What percentage of customers have is_churned equal to 1 in marts.dim_customers?')
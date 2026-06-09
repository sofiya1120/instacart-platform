import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DB_URL'))

print('Loading data...')

df = pd.read_sql("""
    SELECT
        user_id,
        order_number,
        days_since_prior_order
    FROM staging.stg_orders
    ORDER BY user_id, order_number
""", engine)

# Build cumulative days per user
df['days_since_prior_order'] = df['days_since_prior_order'].fillna(0)
df['cumulative_days'] = df.groupby('user_id')['days_since_prior_order'].cumsum()

# Cohort = 30 day bucket of first order
first_orders = (
    df[df['order_number'] == 1][['user_id', 'cumulative_days']]
    .rename(columns={'cumulative_days': 'first_order_day'})
)
first_orders['cohort'] = (first_orders['first_order_day'] // 30).astype(int)

df = df.merge(first_orders[['user_id', 'cohort']], on='user_id', how='left')

df['order_period']  = (df['cumulative_days'] // 30).astype(int)
df['period_number'] = df['order_period'] - df['cohort']

# Keep only periods 0-12 and cohorts 0-9
df = df[(df['period_number'] >= 0) & (df['period_number'] <= 12)]
df = df[df['cohort'].between(0, 9)]

cohort_data = (
    df.groupby(['cohort', 'period_number'])['user_id']
    .nunique()
    .reset_index(name='active_users')
)

cohort_sizes = (
    cohort_data[cohort_data['period_number'] == 0]
    [['cohort', 'active_users']]
    .rename(columns={'active_users': 'cohort_size'})
)

cohort_data = cohort_data.merge(cohort_sizes, on='cohort')
cohort_data['retention_rate'] = (
    cohort_data['active_users'] / cohort_data['cohort_size']
).round(4)

# Write to analytics schema
with engine.connect() as conn:
    conn.execute(text('CREATE SCHEMA IF NOT EXISTS analytics'))
    conn.commit()

cohort_data.to_sql(
    'cohort_retention', engine, schema='analytics',
    if_exists='replace', index=False
)

print(f'Done. Written {len(cohort_data)} rows to analytics.cohort_retention')
print('\nSample — retention at period 1:')
print(cohort_data[cohort_data['period_number']==1][['cohort','retention_rate']].to_string(index=False))
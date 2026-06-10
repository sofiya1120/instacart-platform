import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DB_URL'))

print('Loading data...')

df = pd.read_sql("""
    SELECT user_id, total_orders, avg_reorder_rate
    FROM marts.dim_customers
""", engine)

total = len(df)

stages = [
    ('All customers',                       len(df)),
    ('Placed 2+ orders',                    (df['total_orders'] >= 2).sum()),
    ('Placed 5+ orders',                    (df['total_orders'] >= 5).sum()),
    ('Placed 10+ orders',                   (df['total_orders'] >= 10).sum()),
    ('Champions (10+ orders, 60%+ reorder)',
     ((df['total_orders'] >= 10) & (df['avg_reorder_rate'] >= 0.6)).sum()),
]

funnel = pd.DataFrame(stages, columns=['stage', 'users'])
funnel['pct_of_total'] = (funnel['users'] / total * 100).round(2)
funnel['pct_of_prev']  = (funnel['users'] / funnel['users'].shift(1) * 100).round(2)
funnel['drop_off_pct'] = (100 - funnel['pct_of_prev']).round(2)

funnel.to_sql(
    'funnel_analysis', engine, schema='analytics',
    if_exists='replace', index=False
)

print(f'Done. Written to analytics.funnel_analysis')
print()
print(funnel[['stage', 'users', 'pct_of_total', 'drop_off_pct']].to_string(index=False))
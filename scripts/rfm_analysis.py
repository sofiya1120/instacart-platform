import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DB_URL'))

print('Loading data...')

df = pd.read_sql("""
    SELECT
        user_id,
        total_orders,
        avg_days_between_orders,
        avg_reorder_rate,
        lifetime_items,
        avg_basket_size
    FROM marts.dim_customers
""", engine)

print(f'Loaded {len(df):,} customers')

# R: lower avg_days = more recent = higher score
# F: more total_orders = higher score
# M: more lifetime_items = higher score
df['R'] = pd.qcut(
    df['avg_days_between_orders'].rank(method='first'),
    q=5, labels=[5, 4, 3, 2, 1]
).astype(int)

df['F'] = pd.qcut(
    df['total_orders'].rank(method='first'),
    q=5, labels=[1, 2, 3, 4, 5]
).astype(int)

df['M'] = pd.qcut(
    df['lifetime_items'].rank(method='first'),
    q=5, labels=[1, 2, 3, 4, 5]
).astype(int)

df['rfm_score'] = (
    df['R'].astype(str) + df['F'].astype(str) + df['M'].astype(str)
)
df['rfm_total'] = df['R'] + df['F'] + df['M']

def assign_segment(row):
    r, f, m = row['R'], row['F'], row['M']
    if r >= 4 and f >= 4 and m >= 4:
        return 'Champions'
    elif r >= 3 and f >= 3:
        return 'Loyal Customers'
    elif r >= 4 and f <= 2:
        return 'New Customers'
    elif r <= 2 and f >= 3:
        return 'At Risk'
    elif r <= 2 and f <= 2:
        return 'Lost'
    else:
        return 'Potential Loyalists'

df['rfm_segment'] = df.apply(assign_segment, axis=1)

output = df[['user_id', 'R', 'F', 'M', 'rfm_score', 'rfm_total', 'rfm_segment']]
output.to_sql(
    'rfm_segments', engine, schema='analytics',
    if_exists='replace', index=False
)

print(f'Done. Written {len(output)} rows to analytics.rfm_segments')
print('\nSegment distribution:')
print(df['rfm_segment'].value_counts().to_string())
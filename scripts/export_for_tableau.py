import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DB_URL'))

os.makedirs('data/processed', exist_ok=True)

tables = {
    'dim_customers':         'SELECT * FROM marts.dim_customers',
    'fct_orders':            'SELECT * FROM marts.fct_orders LIMIT 100000',
    'fct_product_performance': 'SELECT * FROM marts.fct_product_performance',
    'cohort_retention':      'SELECT * FROM analytics.cohort_retention',
    'rfm_segments':          'SELECT * FROM analytics.rfm_segments',
    'funnel_analysis':       'SELECT * FROM analytics.funnel_analysis',
    'ab_test_results':       'SELECT * FROM analytics.ab_test_results',
}

for name, query in tables.items():
    df = pd.read_sql(query, engine)
    path = f'data/processed/{name}.csv'
    df.to_csv(path, index=False)
    print(f'Exported {len(df):,} rows to {path}')

print('\nAll files exported.')
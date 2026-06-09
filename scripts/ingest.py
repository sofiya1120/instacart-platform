import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import time

load_dotenv()

engine = create_engine(
    os.getenv('DB_URL'),
    connect_args={"connect_timeout": 60}
)

RAW_PATH = 'data/raw/'

with engine.connect() as conn:
    conn.execute(text('CREATE SCHEMA IF NOT EXISTS raw'))
    conn.commit()
    print('Schema created: raw')

# Small files — load fully
small_files = {
    'raw_products':    'products.csv',
    'raw_departments': 'departments.csv',
    'raw_aisles':      'aisles.csv',
}

for table_name, filename in small_files.items():
    path = os.path.join(RAW_PATH, filename)
    df = pd.read_csv(path)
    df.to_sql(table_name, engine, schema='raw',
              if_exists='replace', index=False)
    print(f'raw.{table_name}: {len(df):,} rows loaded')

# Orders — load only 500K rows (enough for all analysis)
print('\nLoading orders.csv (500K sample)...')
start = time.time()
df_orders = pd.read_csv(RAW_PATH + 'orders.csv', nrows=500000)
df_orders.to_sql('raw_orders', engine, schema='raw',
                 if_exists='replace', index=False,
                 chunksize=10000)
print(f'raw.raw_orders: {len(df_orders):,} rows in {time.time()-start:.1f}s')

# Order products — load only 10% sample
print('\nLoading order_products__prior.csv (10% sample)...')
start = time.time()
df_op = pd.read_csv(RAW_PATH + 'order_products__prior.csv', nrows=3000000)
df_op = df_op.sample(frac=0.10, random_state=42)
df_op.to_sql('raw_order_products', engine, schema='raw',
             if_exists='replace', index=False,
             chunksize=10000)
print(f'raw.raw_order_products: {len(df_op):,} rows in {time.time()-start:.1f}s')

print('\nAll files loaded successfully.')
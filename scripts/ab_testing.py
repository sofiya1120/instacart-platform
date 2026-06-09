import pandas as pd
import numpy as np
from scipy import stats
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DB_URL'))

print('Loading data...')

df = pd.read_sql("""
    SELECT
        order_id,
        order_day_of_week,
        reorder_rate,
        basket_size
    FROM marts.fct_orders
    WHERE basket_size > 0
""", engine)

df['group'] = df['order_day_of_week'].apply(
    lambda d: 'weekend' if d in (0, 6) else 'weekday'
)

control   = df[df['group'] == 'weekday']['reorder_rate']
treatment = df[df['group'] == 'weekend']['reorder_rate']

t_stat, p_value = stats.ttest_ind(control, treatment, equal_var=False)

pooled_std = np.sqrt((control.std()**2 + treatment.std()**2) / 2)
cohens_d   = (treatment.mean() - control.mean()) / pooled_std
lift_pct   = (treatment.mean() - control.mean()) / control.mean() * 100

results = pd.DataFrame([{
    'test_name':         'Weekend vs Weekday Reorder Rate',
    'control_label':     'weekday',
    'treatment_label':   'weekend',
    'control_n':         len(control),
    'treatment_n':       len(treatment),
    'control_mean':      round(float(control.mean()), 4),
    'treatment_mean':    round(float(treatment.mean()), 4),
    'lift_pct':          round(float(lift_pct), 2),
    't_statistic':       round(float(t_stat), 4),
    'p_value':           round(float(p_value), 6),
    'cohens_d':          round(float(cohens_d), 4),
    'significant_at_95': bool(p_value < 0.05),
    'significant_at_99': bool(p_value < 0.01),
}])

results.to_sql(
    'ab_test_results', engine, schema='analytics',
    if_exists='replace', index=False
)

print('Done. Written to analytics.ab_test_results')
print()
print(results.T.to_string())
sig = 'SIGNIFICANT' if p_value < 0.05 else 'NOT significant'
print(f'\nResult is {sig} at 95% confidence (p={p_value:.6f})')

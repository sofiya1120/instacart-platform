import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import pickle
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv('DB_URL'))

print('Loading features...')

df = pd.read_sql("""
    SELECT
        c.user_id,
        c.total_orders,
        c.avg_basket_size,
        c.avg_days_between_orders,
        c.avg_reorder_rate,
        c.lifetime_items,
        c.is_churned,
        r."R"             AS recency_score,
        r."F"             AS frequency_score,
        r."M"             AS monetary_score,
        r.rfm_total
    FROM marts.dim_customers c
    INNER JOIN analytics.rfm_segments r ON c.user_id = r.user_id
""", engine)

df = df.dropna()

churn_rate = df['is_churned'].mean()
print(f'Dataset: {len(df):,} customers | Churn rate: {churn_rate*100:.1f}%')

FEATURES = [
    'total_orders',
    'avg_basket_size',
    'avg_reorder_rate',
    'lifetime_items',
    'recency_score',
    'frequency_score',
    'monetary_score',
    'rfm_total',
]

X = df[FEATURES]
y = df['is_churned']

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

candidates = {
    'Logistic Regression': Pipeline([
        ('scaler', StandardScaler()),
        ('clf',    LogisticRegression(max_iter=500, random_state=42))
    ]),
    'Random Forest': Pipeline([
        ('scaler', StandardScaler()),
        ('clf',    RandomForestClassifier(
            n_estimators=100, random_state=42, n_jobs=-1
        ))
    ]),
    'Gradient Boosting': Pipeline([
        ('scaler', StandardScaler()),
        ('clf',    GradientBoostingClassifier(
            n_estimators=100, random_state=42
        ))
    ]),
}

best_auc   = 0
best_name  = ''
best_model = None

for name, pipeline in candidates.items():
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]
    auc    = roc_auc_score(y_test, y_prob)
    print(f'\n{name} — AUC: {auc:.4f}')
    print(classification_report(y_test, y_pred, digits=3))
    if auc > best_auc:
        best_auc   = auc
        best_name  = name
        best_model = pipeline

print(f'\nBest model: {best_name}')
print(f'AUC: {best_auc:.4f}')
print('Write this number down — you will say it in every interview.')

# Feature importances
clf = best_model.named_steps['clf']
if hasattr(clf, 'feature_importances_'):
    importance = pd.DataFrame({
        'feature':    FEATURES,
        'importance': clf.feature_importances_
    }).sort_values('importance', ascending=False)
    print('\nFeature importances:')
    print(importance.to_string(index=False))

# Save model
os.makedirs('models', exist_ok=True)
with open('models/churn_model.pkl', 'wb') as f:
    pickle.dump({
        'model':    best_model,
        'features': FEATURES,
        'auc':      best_auc,
        'name':     best_name,
    }, f)

print('\nModel saved to models/churn_model.pkl')
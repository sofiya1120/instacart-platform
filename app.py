import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pickle
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

st.set_page_config(
    page_title='Instacart Customer Intelligence',
    page_icon='🛒',
    layout='wide',
)

load_dotenv()

@st.cache_resource
def get_engine():
    return create_engine(os.getenv('DB_URL'))

@st.cache_data(ttl=3600)
def load_customers(_engine):
    return pd.read_sql('SELECT * FROM marts.dim_customers', _engine)

@st.cache_data(ttl=3600)
def load_rfm(_engine):
    return pd.read_sql('SELECT * FROM analytics.rfm_segments', _engine)

@st.cache_data(ttl=3600)
def load_cohort(_engine):
    return pd.read_sql('SELECT * FROM analytics.cohort_retention', _engine)

@st.cache_data(ttl=3600)
def load_funnel(_engine):
    return pd.read_sql('SELECT * FROM analytics.funnel_analysis', _engine)

@st.cache_data(ttl=3600)
def load_products(_engine):
    return pd.read_sql(
        'SELECT * FROM marts.fct_product_performance ORDER BY total_orders DESC LIMIT 3000',
        _engine
    )

@st.cache_data(ttl=3600)
def load_ab(_engine):
    return pd.read_sql('SELECT * FROM analytics.ab_test_results', _engine)

engine    = get_engine()
customers = load_customers(engine)
rfm       = load_rfm(engine)
cohort    = load_cohort(engine)
funnel    = load_funnel(engine)
products  = load_products(engine)
ab        = load_ab(engine)

# Header
st.title('🛒 Instacart Customer Intelligence Platform')
st.caption('Python · Neon PostgreSQL · dbt Core · Airflow · scikit-learn · Groq')
st.divider()

# KPIs
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric('Total Customers',   f"{customers['user_id'].nunique():,}")
k2.metric('Avg Basket Size',   f"{customers['avg_basket_size'].mean():.1f}")
k3.metric('Avg Reorder Rate',  f"{customers['avg_reorder_rate'].mean()*100:.1f}%")
k4.metric('Churned Customers', f"{customers['is_churned'].sum():,}")
k5.metric('Champions',         f"{(customers['customer_tier']=='champion').sum():,}")
st.divider()

# Tabs
tab_cohort, tab_rfm, tab_funnel, tab_ab, tab_products, tab_churn, tab_nlq = st.tabs([
    'Cohort Retention',
    'RFM Segments',
    'Funnel',
    'A/B Test',
    'Products',
    'Churn Predictor',
    'Ask the Data',
])

# Cohort
with tab_cohort:
    st.subheader('Customer cohort retention')
    pivot = cohort.pivot(
        index='cohort', columns='period_number', values='retention_rate'
    )
    fig = px.imshow(
        pivot,
        text_auto='.0%',
        color_continuous_scale='Blues',
        title='Retention rate by cohort and period',
        aspect='auto',
    )
    st.plotly_chart(fig, use_container_width=True)

# RFM
with tab_rfm:
    st.subheader('RFM customer segmentation')
    col1, col2 = st.columns(2)
    with col1:
        seg = rfm['rfm_segment'].value_counts().reset_index()
        seg.columns = ['segment', 'customers']
        fig = px.pie(
            seg, values='customers', names='segment',
            title='Customers by RFM segment',
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.scatter(
            rfm.sample(min(3000, len(rfm))),
            x='F', y='R',
            color='rfm_segment',
            size='M',
            title='Frequency vs Recency',
            opacity=0.5,
        )
        st.plotly_chart(fig, use_container_width=True)

# Funnel
with tab_funnel:
    st.subheader('Customer engagement funnel')
    fig = go.Figure(go.Funnel(
        y=funnel['stage'],
        x=funnel['users'],
        textinfo='value+percent initial',
        marker_color=['#1a5276','#1f618d','#2980b9','#5dade2','#aed6f1'],
    ))
    fig.update_layout(title='Customer engagement stages')
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(
        funnel[['stage','users','pct_of_total','drop_off_pct']],
        use_container_width=True
    )

# A/B Test
with tab_ab:
    st.subheader('A/B test: Weekend vs weekday reorder rate')
    row = ab.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Control (weekday)',   f"{row['control_mean']:.4f}")
    c2.metric('Treatment (weekend)', f"{row['treatment_mean']:.4f}")
    c3.metric('Lift',                f"{row['lift_pct']:+.2f}%")
    c4.metric('p-value',             f"{row['p_value']:.6f}")
    if row['significant_at_95']:
        st.success('Statistically significant at 95% confidence.')
    else:
        st.warning('Not statistically significant at 95% confidence.')

# Products
with tab_products:
    st.subheader('Product performance')
    top_n = st.slider('Show top N products', 10, 50, 20)
    top = products.head(top_n)
    fig = px.bar(
        top, x='total_orders', y='product_name',
        orientation='h', color='reorder_rate',
        color_continuous_scale='RdYlGn',
        title=f'Top {top_n} products by order volume',
    )
    fig.update_layout(height=600, yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

# Churn Predictor
with tab_churn:
    st.subheader('Customer churn predictor')
    col1, col2, col3 = st.columns(3)
    with col1:
        total_orders   = st.slider('Total orders',           1,  50,  8)
        avg_basket     = st.slider('Avg basket size',        1,  40, 10)
        avg_reorder    = st.slider('Avg reorder rate',     0.0, 1.0, 0.5, step=0.05)
    with col2:
        lifetime_items = st.slider('Lifetime items',         1, 500, 80)
        r_score = st.selectbox('Recency score (R)',  [1,2,3,4,5], index=2)
        f_score = st.selectbox('Frequency score (F)',[1,2,3,4,5], index=2)
    with col3:
        m_score = st.selectbox('Monetary score (M)', [1,2,3,4,5], index=2)

    if st.button('Predict churn risk', type='primary'):
        model_path = 'models/churn_model.pkl'
        if not os.path.exists(model_path):
            st.error('Model not found. Run scripts/churn_model.py first.')
        else:
            with open(model_path, 'rb') as f:
                artifact = pickle.load(f)
            model    = artifact['model']
            features = artifact['features']
            X = pd.DataFrame([[
                total_orders, avg_basket, avg_reorder,
                lifetime_items, r_score, f_score, m_score,
                r_score + f_score + m_score,
            ]], columns=features)
            prob = float(model.predict_proba(X)[0][1])
            st.metric('Churn probability', f'{prob*100:.1f}%')
            st.progress(prob)
            if prob >= 0.65:
                st.error('High churn risk.')
            elif prob >= 0.35:
                st.warning('Moderate churn risk.')
            else:
                st.success('Low churn risk.')

# NL Query
with tab_nlq:
    st.subheader('Ask the data in plain English')
    st.caption('Powered by Groq — converts your question to SQL and runs it')
    question = st.text_input(
        'Your question:',
        placeholder='Which RFM segment has the most customers?',
    )
    if st.button('Run query') and question.strip():
        from scripts.nl_query import natural_language_to_sql
        with st.spinner('Generating SQL...'):
            try:
                sql = natural_language_to_sql(question)
                st.code(sql, language='sql')
                result = pd.read_sql(sql, engine)
                st.dataframe(result, use_container_width=True)
            except Exception as e:
                st.error(f'Error: {e}')
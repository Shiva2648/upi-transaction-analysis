import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="UPI Transaction Analysis", layout="wide")
st.title("UPI Transaction Analysis Dashboard")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path, parse_dates=['datetime'])
    df['date'] = pd.to_datetime(df['date']).dt.date
    df['month'] = pd.to_datetime(df['datetime']).dt.to_period('M').astype(str)
    return df

df = load_data("upi_transactions_synthetic.csv")

# Filters
st.sidebar.header("Filters")
min_amt, max_amt = int(df['amount'].min()), int(df['amount'].max())
amt_range = st.sidebar.slider("Amount range", min_amt, max_amt, (min_amt, max_amt))
types = st.sidebar.multiselect("Transaction type", options=df['type'].unique(), default=list(df['type'].unique()))
cats = st.sidebar.multiselect("Categories", options=df['category'].unique(), default=list(df['category'].unique()))
months = st.sidebar.multiselect("Months", options=sorted(df['month'].unique()), default=sorted(df['month'].unique()))

filtered = df[
    (df['amount'] >= amt_range[0]) &
    (df['amount'] <= amt_range[1]) &
    (df['type'].isin(types)) &
    (df['category'].isin(cats)) &
    (df['month'].isin(months))
]

st.markdown(f"**Total transactions:** {len(filtered)}  \n**Total amount:** ₹{filtered['amount'].sum():,.2f}")

col1, col2 = st.columns(2)
with col1:
    monthly = filtered.groupby('month')['amount'].sum().reset_index()
    fig1 = px.bar(monthly, x='month', y='amount', title='Monthly Spend (Filtered)', labels={'amount':'Amount (₹)','month':'Month'})
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    top_merchants = filtered.groupby('merchant')['amount'].sum().reset_index().sort_values('amount', ascending=False).head(10)
    fig2 = px.bar(top_merchants, x='merchant', y='amount', title='Top Merchants', labels={'amount':'Amount (₹)','merchant':'Merchant'})
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Category distribution")
cat_s = filtered.groupby('category')['amount'].sum().reset_index()
fig3 = px.pie(cat_s, names='category', values='amount', title='Spend by Category')
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Raw transactions (filtered)")
st.dataframe(filtered.sort_values('datetime', ascending=False).reset_index(drop=True))
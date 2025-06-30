import streamlit as st
import pandas as pd
import plotly.express as px

# Page setup
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("sales_data_clean.csv")
    df['Sale_Date'] = pd.to_datetime(df['Sale_Date'])
    df['Month'] = df['Sale_Date'].dt.to_period('M').astype(str)
    df['Profit'] = (df['Unit_Price'] - df['Unit_Cost']) * df['Quantity_Sold']
    df['Discount_Amount'] = df['Sales_Amount'] * df['Discount']
    df['Net_Sales'] = df['Sales_Amount'] - df['Discount_Amount']
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filter Data")
region = st.sidebar.multiselect("Region", df["Region"].unique(), default=df["Region"].unique())
category = st.sidebar.multiselect("Product Category", df["Product_Category"].unique(), default=df["Product_Category"].unique())

# Filtered dataframe
df_filtered = df[df["Region"].isin(region) & df["Product_Category"].isin(category)]

# KPIs
st.title("Sales Analytics Dashboard")

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${df_filtered['Sales_Amount'].sum():,.0f}")
col2.metric("Total Profit", f"${df_filtered['Profit'].sum():,.0f}")
col3.metric("Avg Discount", f"{df_filtered['Discount'].mean() * 100:.1f}%")

st.markdown("---")

# 1. Revenue by Product Category
fig1 = px.bar(df_filtered.groupby("Product_Category")["Sales_Amount"].sum().reset_index(),
              x="Product_Category", y="Sales_Amount", color="Product_Category",
              title="Revenue by Product Category")
st.plotly_chart(fig1, use_container_width=True)

# 2. Profit by Region
fig2 = px.bar(df_filtered.groupby("Region")["Profit"].sum().reset_index(),
              x="Region", y="Profit", color="Region",
              title="Profit by Region")
st.plotly_chart(fig2, use_container_width=True)

# 3. Revenue by Sales Rep
fig3 = px.bar(df_filtered.groupby("Sales_Rep")["Sales_Amount"].sum().reset_index().sort_values(by="Sales_Amount", ascending=False),
              x="Sales_Rep", y="Sales_Amount", color="Sales_Rep",
              title="Revenue by Sales Representative")
st.plotly_chart(fig3, use_container_width=True)

# 4. Monthly Revenue Trend
fig4 = px.line(df_filtered.groupby("Month")["Sales_Amount"].sum().reset_index(),
               x="Month", y="Sales_Amount", markers=True,
               title="Monthly Revenue Trend")
st.plotly_chart(fig4, use_container_width=True)

# 5. Customer Type Distribution (FIXED)
customer_counts = df_filtered["Customer_Type"].value_counts().reset_index()
customer_counts.columns = ["Customer_Type", "Count"]
fig5 = px.pie(customer_counts,
              names="Customer_Type", values="Count", hole=0.4,
              title="Customer Type Distribution")
fig5.update_traces(textinfo="percent+label")
st.plotly_chart(fig5, use_container_width=True)

# 6. Payment Method Usage
payment_counts = df_filtered["Payment_Method"].value_counts().reset_index()
payment_counts.columns = ["Payment_Method", "Count"]
fig6 = px.bar(payment_counts,
              x="Payment_Method", y="Count", color="Payment_Method",
              title="Payment Method Usage")
fig6.update_layout(xaxis_title="", yaxis_title="Count")
st.plotly_chart(fig6, use_container_width=True)

# 7. Discount vs Net Sales (Bubble Chart)
fig7 = px.scatter(df_filtered, x="Discount", y="Net_Sales", color="Region", size="Quantity_Sold",
                  hover_data=["Product_Category", "Sales_Rep"],
                  title="Discount vs Net Sales (Bubble Chart)")
st.plotly_chart(fig7, use_container_width=True)

import streamlit as st
from utils.data_manager import DataManager
from utils.charts import create_financial_chart
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Financial Management", page_icon="💰")

# Initialize DataManager
dm = DataManager()

st.title("Financial Management")

# Tabs for different financial functions
tab1, tab2, tab3 = st.tabs(["Add Transaction", "Financial Overview", "Reports"])

with tab1:
    st.header("Record Transaction")
    
    with st.form("transaction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_type = st.selectbox(
                "Transaction Type",
                ["income", "expense"]
            )
            amount = st.number_input("Amount ($)", min_value=0.0, format="%.2f")
            
        with col2:
            category = st.selectbox(
                "Category",
                ["Membership Fees", "Personal Training", "Equipment",
                 "Maintenance", "Utilities", "Salary", "Other"]
            )
            description = st.text_area("Description")
        
        if st.form_submit_button("Record Transaction"):
            if amount > 0:
                transaction_data = {
                    'type': transaction_type,
                    'amount': amount,
                    'category': category,
                    'description': description
                }
                dm.add_financial_record(transaction_data)
                st.success("Transaction recorded successfully!")
            else:
                st.error("Please enter a valid amount")

with tab2:
    st.header("Financial Overview")
    
    # Load financial data
    finance_df = dm.get_financial_summary()
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_income = finance_df[finance_df['type'] == 'income']['amount'].sum()
        st.metric("Total Income", f"${total_income:,.2f}")
        
    with col2:
        total_expenses = finance_df[finance_df['type'] == 'expense']['amount'].sum()
        st.metric("Total Expenses", f"${total_expenses:,.2f}")
        
    with col3:
        net_profit = total_income - total_expenses
        st.metric("Net Profit", f"${net_profit:,.2f}")
    
    # Financial chart
    st.plotly_chart(create_financial_chart(finance_df), use_container_width=True)
    
    # Transaction history
    st.subheader("Recent Transactions")
    st.dataframe(
        finance_df.sort_values('date', ascending=False).head(10),
        column_config={
            "date": "Date",
            "type": "Type",
            "category": "Category",
            "amount": "Amount",
            "description": "Description"
        },
        hide_index=True
    )

with tab3:
    st.header("Financial Reports")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            datetime.now() - timedelta(days=30)
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            datetime.now()
        )
    
    # Filter data by date range
    filtered_df = finance_df[
        (finance_df['date'] >= str(start_date)) &
        (finance_df['date'] <= str(end_date))
    ]
    
    # Summary by category
    st.subheader("Category Summary")
    category_summary = filtered_df.groupby(['type', 'category'])['amount'].sum().reset_index()
    st.dataframe(
        category_summary,
        column_config={
            "type": "Type",
            "category": "Category",
            "amount": "Total Amount"
        },
        hide_index=True
    )
    
    # Export functionality
    if not filtered_df.empty:
        st.download_button(
            label="Export Financial Report",
            data=filtered_df.to_csv(index=False),
            file_name=f"financial_report_{start_date}_to_{end_date}.csv",
            mime="text/csv"
        )

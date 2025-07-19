import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime

# Initialize data files
if not os.path.exists('finance_data.csv'):
    pd.DataFrame(columns=['Date', 'Description', 'Category', 'Amount']).to_csv('finance_data.csv', index=False)

if not os.path.exists('categories.json'):
    with open('categories.json', 'w') as f:
        json.dump({
            "Food": ["grocery", "restaurant", "lunch"],
            "Transport": ["uber", "taxi", "gas"],
            "Entertainment": ["movie", "game", "concert"],
            "Bills": ["electric", "water", "internet"],
            "Other": []
        }, f)

def load_data():
    try:
        df = pd.read_csv('finance_data.csv')
        required_columns = ['Date', 'Description', 'Category', 'Amount']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None if col != 'Amount' else 0.0
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(columns=['Date', 'Description', 'Category', 'Amount'])

def load_categories():
    try:
        with open('categories.json', 'r') as f:
            return json.load(f)
    except:
        return {"Other": []}

def save_data(df):
    df.to_csv('finance_data.csv', index=False)

def save_categories(categories):
    with open('categories.json', 'w') as f:
        json.dump(categories, f, indent=4)

def categorize_expense(description, categories):
    description = str(description).lower()
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.lower() in description:
                return category
    return "Other"

def main():
    st.set_page_config(
        page_title="My Finance Tracker",
        page_icon="💰",
        layout="wide"
    )

    # 🔐 Access code check
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 Secure Access")
        access_code = st.text_input("Enter access code to continue", type="password")
        if st.button("Login"):
            if access_code == "ayoub2003":
                st.session_state.authenticated = True
                st.success("Access granted!")
                st.rerun()
            else:
                st.error("Invalid access code")
        return  # Exit until correct code is entered

    # Main app
    expenses_df = load_data()
    categories = load_categories()

    with st.sidebar:
        st.header("Add New Expense")
        date = st.date_input("Date", datetime.now().date())
        description = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")
        suggested_category = categorize_expense(description, categories)
        category = st.selectbox("Category", options=list(categories.keys()),
                                index=list(categories.keys()).index(suggested_category))
        if st.button("Add Expense"):
            if not description:
                st.error("Please enter a description")
            elif amount <= 0:
                st.error("Amount must be positive")
            else:
                new_expense = pd.DataFrame([[pd.to_datetime(date), description, category, amount]],
                                           columns=['Date', 'Description', 'Category', 'Amount'])
                expenses_df = pd.concat([expenses_df, new_expense], ignore_index=True)
                save_data(expenses_df)
                st.success("Expense added successfully!")
                st.rerun()

    tab1, tab2, tab3 = st.tabs(["Dashboard", "Expenses", "Categories"])

    with tab1:
        st.header("Spending Dashboard")
        if not expenses_df.empty:
            total_spent = expenses_df['Amount'].sum()
            st.metric("Total Spent", f"${total_spent:,.2f}")
            by_category = expenses_df.groupby('Category')['Amount'].sum()
            fig, ax = plt.subplots()
            ax.pie(by_category, labels=by_category.index, autopct='%1.1f%%')
            st.pyplot(fig)
        else:
            st.info("No expenses recorded yet. Add some in the sidebar!")

    with tab2:
        st.header("All Expenses")
        if not expenses_df.empty:
            min_date = expenses_df['Date'].min().date()
            max_date = expenses_df['Date'].max().date()

            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", min_date)
            with col2:
                end_date = st.date_input("End Date", max_date)

            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)

            filtered_df = expenses_df[
                (expenses_df['Date'] >= start_date) &
                (expenses_df['Date'] <= end_date)
            ]

            selected_category = st.selectbox("Filter by Category", ["All"] + list(categories.keys()))
            if selected_category != "All":
                filtered_df = filtered_df[filtered_df['Category'] == selected_category]

            st.dataframe(filtered_df)
            filtered_total = filtered_df['Amount'].sum()
            st.metric("Filtered Total", f"${filtered_total:,.2f}")
        else:
            st.info("No expenses to display")

    with tab3:
        st.header("Manage Categories")
        st.subheader("Current Categories")
        st.write(categories)

        st.subheader("Add New Category")
        new_category = st.text_input("Category Name")
        if st.button("Add Category"):
            if new_category and new_category not in categories:
                categories[new_category] = []
                save_categories(categories)
                st.success(f"Category '{new_category}' added!")
                st.rerun()
            else:
                st.warning("Please enter a valid, unique category name")

        st.subheader("Add Keywords to Categories")
        selected_category = st.selectbox("Select Category", list(categories.keys()))
        new_keyword = st.text_input("New Keyword")
        if st.button("Add Keyword"):
            if new_keyword:
                categories[selected_category].append(new_keyword)
                save_categories(categories)
                st.success(f"Keyword '{new_keyword}' added to {selected_category}")
                st.rerun()

    # 🔻 Footer
    st.markdown(
        """
        <div style='position: fixed; bottom: 10px; right: 10px; color: red; font-weight: bold;'>
            powered by ayoub idys, all right reserved, no copyright
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

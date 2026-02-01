import streamlit as st
import sqlite3
import pandas as pd
import os

# ---------------------------
# Connect to SQLite (works on Streamlit Cloud)
# ---------------------------
db_path = os.path.join(os.getcwd(), "CustomDevEstimator.db")
conn = sqlite3.connect(db_path)

# ---------------------------
# Load data from DB
# ---------------------------
scope_df = pd.read_sql_query("SELECT * FROM Scope_Catalog WHERE active=1", conn)
env_df = pd.read_sql_query("SELECT * FROM Environment_Profiles", conn)
rate_df = pd.read_sql_query("SELECT * FROM Rate_Card", conn)

# ---------------------------
# Streamlit App UI
# ---------------------------
st.title("Custom Development Estimator")

# Step 1: Estimate Info
customer = st.text_input("Customer Name")
project = st.text_input("Project Name")
environment_name = st.selectbox("Environment", env_df['name'])

if st.button("Start Estimate"):
    if not customer or not project:
        st.warning("Please enter customer and project")
    else:
        st.session_state['estimate'] = {
            "customer": customer,
            "project": project,
            "environment": environment_name,
            "stories": []
        }
        st.success("Estimate started! Select stories below.")

# Step 2: Select User Stories
if 'estimate' in st.session_state:
    st.subheader("Select User Stories")
    selected_stories = st.multiselect("Stories", scope_df['name'])
    st.session_state['estimate']['stories'] = selected_stories

    if selected_stories:
        # Filter selected stories
        selected_df = scope_df[scope_df['name'].isin(selected_stories)]
        total_ad = selected_df['ad_hours'].sum()
        total_build = selected_df['build_hours'].sum()

        # Get environment multipliers
        env_row = env_df[env_df['name']==environment_name].iloc[0]
        dev_factor = env_row['dev_factor']
        devops_factor = env_row['devops_factor']
        support_factor = env_row['support_factor']
        maint_factor = env_row['maint_factor']

        # Role-based calculation (example from your Excel sheet)
        # Multipliers can be adjusted later
        role_hours = {
            'Dev': total_build * dev_factor,
            'QA': total_build * 0.17,  # example ratio
            'Doc': total_build * 0.085,
            'UAT Support': total_build * 0.14,
            'SA': total_build * 0.19,
            'PM': total_build * 0.03,
            'MGT': total_build * 0.06
        }

        st.subheader("Total Effort (hours by role)")
        for role, hours in role_hours.items():
            st.write(f"{role}: {hours:.2f} h")

        st.subheader("Summary")
        st.write(f"Total A&D Hours: {total_ad}")
        st.write(f"Total Build Hours: {total_build}")

        # Placeholder for Admin-only cost/price
        st.subheader("Cost / Price (Admin only)")
        if st.checkbox("Show Cost/Price (Admin)"):
            # Example calculation: cost = hours * rate
            cost = sum([hours * rate_df.loc[rate_df['role']==role,'cost_rate'].values[0] for role, hours in role_hours.items()])
            price = sum([hours * rate_df.loc[rate_df['role']==role,'sell_rate'].values[0] for role, hours in role_hours.items()])
            st.write(f"Total Cost: ${cost:.2f}")
            st.write(f"Total Price: ${price:.2f}")
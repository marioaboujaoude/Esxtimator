import streamlit as st
import sqlite3
import pandas as pd

# ---------------------------
# Connect to SQLite
# ---------------------------
conn = sqlite3.connect("CustomDevEstimator.db")
cursor = conn.cursor()

# ---------------------------
# Load data from DB
# ---------------------------
scope_df = pd.read_sql_query("SELECT story_id, name, ad_hours, build_hours FROM Scope_Catalog WHERE active=1", conn)
env_df = pd.read_sql_query("SELECT * FROM Environment_Profiles", conn)

# ---------------------------
# Step 1: Create Estimate Info
# ---------------------------
st.title("Custom Development Estimator")

customer = st.text_input("Customer Name")
project = st.text_input("Project Name")
environment = st.selectbox("Environment", env_df['name'])

if st.button("Start Estimate"):
    if not customer or not project:
        st.warning("Please enter customer and project")
    else:
        st.session_state['estimate'] = {
            "customer": customer,
            "project": project,
            "environment": environment,
            "stories": []
        }
        st.success("Estimate started! Select stories below.")

# ---------------------------
# Step 2: Select User Stories
# ---------------------------
if 'estimate' in st.session_state:
    st.subheader("Select User Stories")
    selected_stories = st.multiselect("Stories", scope_df['name'])

    st.session_state['estimate']['stories'] = selected_stories

    # ---------------------------
    # Step 3: Show Total Effort
    # ---------------------------
    if selected_stories:
        total_ad = scope_df[scope_df['name'].isin(selected_stories)]['ad_hours'].sum()
        total_build = scope_df[scope_df['name'].isin(selected_stories)]['build_hours'].sum()

        st.subheader("Total Effort")
        st.write(f"Total A&D Hours: {total_ad}")
        st.write(f"Total Build Hours: {total_build}")

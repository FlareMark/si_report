# app.py (Diagnostic Version)

import streamlit as st
import gspread
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from google.oauth2.credentials import Credentials

st.set_page_config(layout="wide", page_title="Self-Reflection Profile")
st.title("Self-Reflection Profile")

# --- 1. SECRETS DEBUGGING CHECK ---
# This section will help us diagnose the problem.
st.subheader("Secrets Configuration Test")

# Check if the main [web] section exists
if "web" in st.secrets:
    st.success("✅ Found the `[web]` section in your secrets.")
    
    # Check for each required key within the [web] section
    required_keys = ["client_id", "client_secret", "token_uri", "refresh_token"]
    all_keys_found = True
    for key in required_keys:
        if key in st.secrets.web:
            st.success(f"✅ Found key: '{key}'")
        else:
            st.error(f"❌ MISSING KEY: The key '{key}' was not found in your `[web]` secrets!")
            all_keys_found = False

    if all_keys_found:
        st.info("✅ All required keys are present in your secrets. Attempting to connect...")
    else:
        st.warning("Cannot proceed until all required keys are found in your secrets.")
        st.stop() # Stop the script if keys are missing

else:
    st.error("❌ CRITICAL ERROR: The `[web]` section was not found in your secrets.")
    st.info("Please ensure your secrets file starts with `[web]` on the first line.")
    st.stop() # Stop the script if the whole section is missing


# --- 2. AUTHENTICATION AND DATA LOADING ---
@st.cache_data(ttl=600)
def load_data():
    try:
        # Build credentials directly from secrets
        creds = Credentials.from_authorized_user_info({
            "refresh_token": st.secrets.web.refresh_token,
            "token_uri": st.secrets.web.token_uri,
            "client_id": st.secrets.web.client_id,
            "client_secret": st.secrets.web.client_secret,
        })
        
        client = gspread.authorize(creds)
        
        # --- THE FIX IS HERE ---
        # Using the correct spreadsheet name you provided
        spreadsheet = client.open("Strategic Impact Assessment Responses")
        
        worksheet = spreadsheet.worksheet("Form Responses 1")
        
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        if 'Email Address' in df.columns:
            df['Email Address'] = df['Email Address'].str.strip().str.lower()
        else:
            st.error("Sheet must have an 'Email Address' column.")
            st.stop()
            
        return df
        
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None

# The create_profile_chart and Web App Interface sections are unchanged.
# ... (You can paste them here if you want, but they are not needed for this test)

# --- App Execution ---
df = load_data()

if df is not None:
    st.success("🎉 Successfully connected to Google Sheets and loaded data!")
    # The rest of your app logic would go here
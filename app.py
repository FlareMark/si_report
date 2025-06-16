import streamlit as st
import gspread
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Self-Reflection Profile")

# --- Securely Connect to Google Sheets ---
# This uses Streamlit's Secrets Management. You'll need to set up a Google Service Account.
# See tutorial: https://docs.streamlit.io/knowledge-base/tutorials/databases/gsheets
try:
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    spreadsheet = gc.open_by_key("1K2yrZytgnsjEXaSsUU4HODtrT8434S2u39b5uXYeYBY")
    worksheet = spreadsheet.worksheet("Sheet1") # Or whatever your sheet is named
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
except Exception as e:
    st.error("Could not connect to Google Sheets. Please check your configuration.")
    st.stop()


# --- Main Visualization Function ---
# This is our perfected plotting code, wrapped in a function
def create_profile_chart(user_data):
    # Data Extraction
    labels = ['Growth Drive', 'Initiative', 'Courage Under\nUncertainty', 'Strategic\nGenerosity']
    behavior_scores = [user_data['Growth Drive'], user_data['Initiative'], user_data['Courage Under Uncertainty'], user_data['Strategic Generosity']]
    alignment_labels = ['Mission', 'Values', 'Culture', 'Benefits']
    alignment_scores = [user_data['Mission'], user_data['Values'], user_data['Culture'], user_data['Benefits']]

    # Color mapping
    colors = []
    for score in alignment_scores:
        if score <= 4: colors.append('#d62728')
        elif score <= 7: colors.append('#ff7f0e')
        else: colors.append('#2ca02c')

    # Chart Creation
    fig = plt.figure(figsize=(14, 7))
    # ... (The rest of the plotting code from our previous conversation goes here) ...
    # ... It's long, so I'm omitting it here, but you would paste the full working code ...
    # For now, let's just make sure the data is passed correctly
    ax1 = fig.add_subplot(1, 2, 1, polar=True)
    # (Full radar chart code here)
    ax1.set_title("Behavioral Shape")
    
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.barh(alignment_labels, alignment_scores, color=colors)
    ax2.set_xlim(0, 10)
    ax2.set_title("Values Alignment")
    # (Full bar chart code here)
    
    return fig


# --- Web App Interface ---
st.title("Your Personal Self-Reflection Profile")

email = st.text_input("Please enter your email address to load your profile:")

if email:
    # Find the user's data in the DataFrame
    user_row = df[df['Email'] == email] # Assumes you have an 'Email' column

    if not user_row.empty:
        # Get the first matching row as a dictionary
        user_data = user_row.iloc[0].to_dict()
        
        st.header(f"Displaying Profile for: {user_data['Name']}") # Assumes a 'Name' column

        # Generate and display the chart
        fig = create_profile_chart(user_data)
        st.pyplot(fig)

        # Display the explanatory text
        st.subheader("Interpreting Your Profile")
        # You can copy and paste the text from the "Conceptual Framework" document here
        st.write("The 'Behavioral Shape' shows how you see your actions...")
        st.write("The 'Values Alignment' chart explores the 'why' behind them...")
    else:
        st.error("No profile found for that email address. Please check for typos.")
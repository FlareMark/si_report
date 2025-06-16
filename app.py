import streamlit as st
import gspread
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline # Import the new library

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Self-Reflection Profile")

# --- Authentication and Data Loading (Standard Service Account Method) ---
@st.cache_data(ttl=600)
def load_data():
    try:
        # This uses the service account key from your Streamlit secrets
        creds = st.secrets["gcp_service_account"]
        client = gspread.service_account_from_dict(creds)
        
        spreadsheet = client.open("Strategic Impact Assessment Responses")
        worksheet = spreadsheet.worksheet("Form Responses 1")
        
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)

        # Standardize the email column for reliable matching
        column_name = "Work Email Address"
        if column_name in df.columns:
            df[column_name] = df[column_name].astype(str).str.strip().str.lower()
        else:
            st.error(f"CRITICAL: The required column '{column_name}' was not found in your Google Sheet.")
            st.stop()
        return df

    except gspread.exceptions.SpreadsheetNotFound:
        st.error("Spreadsheet not found. Please ensure the name is correct and that you have shared the sheet with your service account's client_email.")
        return None
    except Exception as e:
        st.error(f"An error occurred while loading data: {e}")
        return None

# --- Main Visualization Function ---
def create_profile_chart(user_data):
    try:
        labels = [
            'Growth Drive', 'Initiative', 'Courage', 'Strategic\nGenerosity'
        ]
        behavior_scores = [
            user_data['Growth Drive Score'], 
            user_data['Initiative Score'], 
            user_data['Courage Score'], 
            user_data['Strategic Generosity Score']
        ]
        
        alignment_labels = ['Mission', 'Values', 'Culture', 'Benefits']
        alignment_scores = [
            user_data['Mission Alignment Score'], 
            user_data['Values Alignment Score'], 
            user_data['Culture Alignment Score'], 
            user_data['Benefits Alignment Score']
        ]

        colors = []
        for score in alignment_scores:
            if score <= 4: colors.append('#d62728')
            elif score <= 7: colors.append('#ff7f0e')
            else: colors.append('#2ca02c')

        fig = plt.figure(figsize=(14, 7))
        
        ax1 = fig.add_subplot(1, 2, 1, polar=True)
        num_vars = len(labels)
        
        # Original angles and scores (we still need these for the spline)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        plot_scores = behavior_scores + behavior_scores[:1]
        plot_angles = angles + angles[:1]

        # --- NEW CURVED LINE LOGIC ---
        # 1. Create a spline function. `CubicSpline` creates a smooth curve.
        #    The `periodic=True` argument is perfect for closed shapes like a radar chart.
        spline = CubicSpline(plot_angles, plot_scores, bc_type='periodic')

        # 2. Generate a larger number of smooth points for the new curve
        dense_angles = np.linspace(0, 2 * np.pi, 200)
        dense_scores = spline(dense_angles)
        # --- END NEW LOGIC ---

        # Configure the plot axes
        ax1.set_theta_offset(np.pi / 2)
        ax1.set_theta_direction(-1)
        ax1.set_xticks(angles)
        ax1.set_xticklabels(labels, size=12)
        ax1.set_rlabel_position(0)
        ax1.set_yticks([2, 4, 6, 8, 10])
        ax1.set_yticklabels(["2", "4", "6", "8", "10"], color="grey", size=9)
        ax1.set_ylim(0, 10)
        
        # Plot the NEW curved data instead of the old straight-line data
        ax1.plot(dense_angles, dense_scores, color='#1f77b4', linewidth=2, linestyle='solid')
        ax1.fill(dense_angles, dense_scores, color='#1f77b4', alpha=0.25)
        ax1.set_title("Behavioral Shape", size=14, pad=25)

        # The bar chart code remains exactly the same
        ax2 = fig.add_subplot(1, 2, 2)
        ax2.barh(alignment_labels, alignment_scores, color=colors)
        ax2.set_xlim(0, 10)
        ax2.set_title("Values Alignment", size=14, pad=20)
        # ... (rest of the bar chart code is unchanged) ...
        for index, value in enumerate(alignment_scores):
            ax2.text(value + 0.2, index, str(value), color='black', fontweight='bold', va='center', size=12)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        return fig
    except KeyError as e:
        st.error(f"A required column is missing from the data for this user: {e}. Please check the Google Sheet.")
        return None
    except Exception as e:
        st.error(f"An error occurred while creating the chart: {e}")
        return None

# --- Web App Interface ---
st.title("Your Personal Self-Reflection Profile")
df = load_data()

if df is not None:
    email_column_name = "Work Email Address"
    name_column = "Name" 
    
    email = st.text_input("Please enter your work email address to load your profile:")

    if email:
        user_row = df[df[email_column_name] == email.strip().lower()]

        if not user_row.empty:
            user_data = user_row.iloc[0].to_dict()
            
            if name_column in user_data:
                st.header(f"Displaying Profile for: {user_data[name_column]}")

            fig = create_profile_chart(user_data)
            if fig is not None:
                st.pyplot(fig)

            with st.expander("How to Interpret Your Profile"):
                st.markdown("""
                ### Understanding Your Results
                This dashboard is a **diagnostic mirror**, not a scorecard. It's designed to help you see the relationship between your foundational connection to the organization (Values Alignment) and your self-perceived behaviors (Behavioral Shape).

                * **Behavioral Shape:** Shows your perceived strengths and areas for growth across four key dimensions of impact.
                * **Values Alignment:** Explores the foundational "why" behind your actions, diagnosing your connection to the company's mission, values, culture, and benefits.
                
                Look for connections. Does a low score on **Mission** alignment correlate with a lower **Initiative** score? Does a high score in **Culture** align with your **Strategic Generosity**? Use these insights to prompt deeper self-reflection.
                """)
        elif email: 
             st.error("No profile found for that email address. Please ensure it matches the one used in the assessment and try again.")
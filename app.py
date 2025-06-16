import streamlit as st
import gspread
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Self-Reflection Profile")

# --- Authentication and Data Loading (Service Account Method) ---
@st.cache_data(ttl=600)
def load_data():
    try:
        creds = st.secrets["gcp_service_account"]
        client = gspread.service_account_from_dict(creds)
        spreadsheet = client.open("Strategic Impact Assessment Responses")
        worksheet = spreadsheet.worksheet("Form Responses 1")
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        column_name = "Work Email Address"
        if column_name in df.columns:
            df[column_name] = df[column_name].astype(str).str.strip().str.lower()
        else:
            st.error(f"CRITICAL: The required column '{column_name}' was not found.")
            st.stop()
        return df
    except Exception as e:
        st.error(f"An error occurred loading data: {e}")
        return None

# --- Main Visualization Function (Standard Radar Chart) ---
def create_profile_chart(user_data):
    try:
        labels = ['Growth Drive', 'Initiative', 'Courage', 'Strategic\nGenerosity']
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

        # --- Chart Setup ---
        fig = plt.figure(figsize=(14, 7))
        ax1 = fig.add_subplot(1, 2, 1, polar=True)
        num_vars = len(labels)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

        # "Close the loop" for the plot
        plot_scores = behavior_scores + behavior_scores[:1]
        plot_angles = angles + angles[:1]

        # Configure the plot axes
        ax1.set_theta_offset(np.pi / 2)
        ax1.set_theta_direction(-1)
        ax1.set_xticks(angles)
        ax1.set_xticklabels(labels, size=12)
        ax1.set_rlabel_position(0)
        ax1.set_yticks([2, 4, 6, 8, 10])
        ax1.set_yticklabels(["2", "4", "6", "8", "10"], color="grey", size=9)
        ax1.set_ylim(0, 10)
        
        # --- STANDARD PLOTTING LOGIC ---
        # Draw the straight-line plot and fill the area
        ax1.plot(plot_angles, plot_scores, color='#1f77b4', linewidth=2, linestyle='solid')
        ax1.fill(plot_angles, plot_scores, color='#1f77b4', alpha=0.25)
        ax1.set_title("Behavioral Shape", size=14, pad=25)

        # --- Bar Chart (Unchanged) ---
        ax2 = fig.add_subplot(1, 2, 2)
        colors = []
        for score in alignment_scores:
            if score <= 4: colors.append('#d62728')
            elif score <= 7: colors.append('#ff7f0e')
            else: colors.append('#2ca02c')
        ax2.barh(alignment_labels, alignment_scores, color=colors)
        ax2.set_xlim(0, 10)
        ax2.set_title("Values Alignment", size=14, pad=20)
        ax2.tick_params(axis='y', labelsize=12)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        for index, value in enumerate(alignment_scores):
            ax2.text(value + 0.2, index, str(value), color='black', fontweight='bold', va='center', size=12)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        return fig
    except KeyError as e:
        st.error(f"A required column is missing for this user: {e}.")
        return None
    except Exception as e:
        st.error(f"An error occurred while creating the chart: {e}")
        return None


# --- Web App Interface (Updated to handle URL parameters) ---
st.title("Your Personal Self-Reflection Profile")

df = load_data()

if df is not None:
    email_column_name = "Work Email Address"
    name_column = "Name"
    
    # Check for an email in the URL query parameters
    query_params = st.query_params
    email_from_url = query_params.get("email", "")

    # Pre-fill the text input with the email from the URL
    email = st.text_input(
        "Please enter your work email address to load your profile:",
        value=email_from_url
    )

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
                st.markdown("""...""") # Your explanatory text here
        elif email and not email_from_url: # Only show error if user typed a new, bad email
             st.error("No profile found for that email address.")
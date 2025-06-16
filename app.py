import streamlit as st
import gspread
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from google.oauth2.credentials import Credentials

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Self-Reflection Profile")

# --- Authentication and Data Loading (OAuth 2.0 Method) ---
@st.cache_data(ttl=600)
def load_data():
    try:
        # Build credentials directly from secrets using the [web] section
        creds = Credentials.from_authorized_user_info({
            "refresh_token": st.secrets.web.refresh_token,
            "token_uri": st.secrets.web.token_uri,
            "client_id": st.secrets.web.client_id,
            "client_secret": st.secrets.web.client_secret,
        })
        
        client = gspread.authorize(creds)
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
        
    except Exception as e:
        st.error(f"An error occurred during Google Sheets connection: {e}")
        return None

# --- Main Visualization Function ---
def create_profile_chart(user_data):
    # This function now uses the correct final score column names you provided.
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

    # --- The rest of the plotting code is unchanged ---
    colors = []
    for score in alignment_scores:
        if score <= 4: colors.append('#d62728')
        elif score <= 7: colors.append('#ff7f0e')
        else: colors.append('#2ca02c')

    fig = plt.figure(figsize=(14, 7))
    
    ax1 = fig.add_subplot(1, 2, 1, polar=True)
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    plot_scores = behavior_scores + behavior_scores[:1]
    plot_angles = angles + angles[:1]

    ax1.set_theta_offset(np.pi / 2)
    ax1.set_theta_direction(-1)
    ax1.set_xticks(angles)
    ax1.set_xticklabels(labels, size=12)
    ax1.set_rlabel_position(0)
    ax1.set_yticks([2, 4, 6, 8, 10])
    ax1.set_yticklabels(["2", "4", "6", "8", "10"], color="grey", size=9)
    ax1.set_ylim(0, 10)
    ax1.plot(plot_angles, plot_scores, color='#1f77b4', linewidth=2, linestyle='solid')
    ax1.fill(plot_angles, plot_scores, color='#1f77b4', alpha=0.25)
    ax1.set_title("Behavioral Shape", size=14, pad=25)

    ax2 = fig.add_subplot(1, 2, 2)
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


# --- Web App Interface ---
st.title("Your Personal Self-Reflection Profile")

df = load_data()

if df is not None:
    email_column_name = "Work Email Address"
    
    email = st.text_input("Please enter your work email address to load your profile:")

    if email:
        user_row = df[df[email_column_name] == email.strip().lower()]

        if not user_row.empty:
            user_data = user_row.iloc[0].to_dict()
            
            # Use a generic name column if it exists.
            name_column = "Name" 
            if name_column in user_data:
                st.header(f"Displaying Profile for: {user_data[name_column]}")

            fig = create_profile_chart(user_data)
            st.pyplot(fig)

            with st.expander("How to Interpret Your Profile"):
                st.markdown("""
                ### Understanding Your Results
                This dashboard is a **diagnostic mirror**, not a scorecard... 
                *(The rest of your explanatory text goes here)*
                """)
        elif email: 
             st.error("No profile found for that email address. Please ensure it matches the one used in the assessment and try again.")
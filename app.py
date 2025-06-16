import streamlit as st
import gspread
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Self-Reflection Profile")

# --- Data Loading Function ---
# This function will handle connecting to Google Sheets and fetching the data
@st.cache_data(ttl=600) # Cache the data for 10 minutes
def load_data():
    try:
        # Assumes you have set up secrets management in Streamlit for security
        gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        # Replace with your actual Google Sheet key or name
        spreadsheet = gc.open("Strategic Impact Assessment Responses (5)") 
        worksheet = spreadsheet.worksheet("Form Responses 1")
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        # Make sure the email column header is exactly 'Email Address'
        df['Email Address'] = df['Email Address'].str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None

# --- Main Visualization Function ---
# UPDATED with the correct column headers from your file
def create_profile_chart(user_data):
    # --- Data Extraction from the user's specific row ---
    labels = [
        'Growth Drive', 'Initiative', 'Courage Under\nUncertainty', 'Strategic\nGenerosity'
    ]
    # IMPORTANT: These strings must EXACTLY match your column headers in the CSV/Sheet
    behavior_scores = [
        user_data['I have a passion for learning and believe I can grow my abilities through effort.'], 
        user_data['I proactively identify what needs to be done without waiting to be told.'], 
        user_data['I am willing to take calculated risks and make decisions even when the outcome is uncertain.'], 
        user_data['I actively share my knowledge and resources to help my colleagues succeed.']
    ]
    
    alignment_labels = ['Mission', 'Values', 'Culture', 'Benefits']
    alignment_scores = [
        user_data["I am energized by our company's mission and purpose."], 
        user_data['I see our company values reflected in the decisions and behaviors around me.'], 
        user_data['I feel a strong sense of belonging and psychological safety within my team and the company culture.'], 
        user_data['The compensation and benefits I receive feel fair and motivating for the work I do.']
    ]

    # Color mapping for the alignment bars
    colors = []
    for score in alignment_scores:
        if score <= 4: colors.append('#d62728') # Red
        elif score <= 7: colors.append('#ff7f0e') # Orange/Yellow
        else: colors.append('#2ca02c') # Green

    # --- Chart Creation ---
    fig = plt.figure(figsize=(14, 7))
    
    # PLOT 1: Radar Chart
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

    # PLOT 2: Bar Chart
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
    # Using the exact column header "Email Address" from your file
    email = st.text_input("Please enter your email address to load your profile:")

    if email:
        # Find the user's data, ignoring case and extra whitespace
        user_row = df[df['Email Address'] == email.strip().lower()]

        if not user_row.empty:
            # Get the first matching row as a dictionary
            user_data = user_row.iloc[0].to_dict()
            
            # Assuming you have a "Name" column for the header
            if 'Name' in user_data:
                st.header(f"Displaying Profile for: {user_data['Name']}")

            # Generate and display the chart
            fig = create_profile_chart(user_data)
            st.pyplot(fig)

            # You can add the conceptual framework text here
            with st.expander("How to Interpret Your Profile"):
                st.markdown("""
                ### Understanding Your Results
                This dashboard is a **diagnostic mirror**, not a scorecard. It's designed to help you see the relationship between your foundational connection to the organization (Values Alignment) and your self-perceived behaviors (Behavioral Shape).

                * **Behavioral Shape:** Shows your perceived strengths and areas for growth across four key dimensions of impact.
                * **Values Alignment:** Explores the foundational "why" behind your actions, diagnosing your connection to the company's mission, values, culture, and benefits.
                
                Look for connections. Does a low score on **Mission** alignment correlate with a lower **Initiative** score? Does a high score in **Culture** align with your **Strategic Generosity**? Use these insights to prompt deeper self-reflection.
                """)
        elif email: # This triggers if email is typed but not found
             st.error("No profile found for that email address. Please ensure it matches the one used in the assessment.")

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

# --- Main Visualization Function (NEW ARC METHOD) ---
def create_profile_chart(user_data):
    try:
        # --- You can adjust this value! ---
        # This now controls the "depth" of the inward curve. 
        # 0.0 is a straight line. Higher values create a deeper arc. 0.5 is a good start.
        CURVATURE = 0.5 

        labels = ['Growth Drive', 'Initiative', 'Courage', 'Strategic\nGenerosity']
        behavior_scores = np.array([
            user_data['Growth Drive Score'], 
            user_data['Initiative Score'], 
            user_data['Courage Score'], 
            user_data['Strategic Generosity Score']
        ])
        
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
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

        # Configure the plot axes
        ax1.set_theta_offset(np.pi / 2)
        ax1.set_theta_direction(-1)
        ax1.set_xticks(angles)
        ax1.set_xticklabels(labels, size=12)
        ax1.set_rlabel_position(0)
        ax1.set_yticks([2, 4, 6, 8, 10])
        ax1.set_yticklabels(["2", "4", "6", "8", "10"], color="grey", size=9)
        ax1.set_ylim(0, 10)
        
        # --- ARC DRAWING LOGIC ---
        # Close the loop for scores and angles
        scores_closed = np.concatenate((behavior_scores, [behavior_scores[0]]))
        angles_closed = np.concatenate((angles, [angles[0]]))
        
        # This will store all the small points that make up the curves
        final_angles = np.array([])
        final_scores = np.array([])

        for i in range(num_vars):
            # Define start and end points for this segment
            start_angle, end_angle = angles_closed[i], angles_closed[i+1]
            start_score, end_score = scores_closed[i], scores_closed[i+1]
            
            # Create 50 points between the start and end angles
            segment_angles = np.linspace(start_angle, end_angle, 50)
            
            # Create a linear interpolation for the radius (a straight line)
            segment_scores_straight = np.linspace(start_score, end_score, 50)
            
            # Create a sine wave that is 0 at the start and end, and 1 in the middle
            # This will be our "bow" effect
            curve_effect = CURVATURE * np.sin(np.linspace(0, np.pi, 50))
            
            # Subtract the curve effect from the straight line to make it bow inward
            segment_scores_curved = segment_scores_straight - curve_effect
            
            # Add these new points to our final lists
            final_angles = np.concatenate((final_angles, segment_angles))
            final_scores = np.concatenate((final_scores, segment_scores_curved))

        # Plot the final curved shape
        ax1.plot(final_angles, final_scores, color='#1f77b4', linewidth=2)
        ax1.fill(final_angles, final_scores, color='#1f77b4', alpha=0.25)
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


# --- Web App Interface (Unchanged) ---
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
                st.markdown("""...""") # Explanatory text
        elif email: 
             st.error("No profile found for that email address.")
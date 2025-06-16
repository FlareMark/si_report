import streamlit as st
import gspread
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import matplotlib.patches as mpatches

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

# --- Main Visualization Function (NEW BEZIER CURVE METHOD) ---
def create_profile_chart(user_data):
    try:
        # --- You can adjust this value! ---
        # 0.0 is a straight line, 0.5 is a very deep curve. 0.2 is a good start.
        CURVATURE = 0.2

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
        ax1.set_facecolor('white') # Explicitly set background
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
        ax1.grid(color='lightgray', linestyle='-')
        ax1.spines['polar'].set_visible(False) # Hide outer spine

        # --- BEZIER CURVE DRAWING LOGIC ---
        # Close the loop for scores
        scores_closed = behavior_scores + behavior_scores[:1]
        angles_closed = np.concatenate((angles, [angles[0]]))

        # Convert polar coordinates to Cartesian for path drawing
        verts_cart = [(r * np.cos(theta), r * np.sin(theta)) for r, theta in zip(scores_closed, angles_closed)]
        
        Path = mpath.Path
        path_codes = [Path.MOVETO]
        path_verts = [verts_cart[0]]

        for i in range(len(scores_closed) - 1):
            p_start = np.array(verts_cart[i])
            p_end = np.array(verts_cart[i+1])
            
            # Calculate the control point to bend the curve inwards
            vec = p_end - p_start
            mid_point = p_start + vec / 2
            # The control point is the midpoint shifted towards the center
            control_point = mid_point * (1 - CURVATURE)

            path_codes.extend([Path.CURVE3, Path.CURVE3])
            path_verts.extend([control_point, p_end])

        # Create the patch and add it to the plot
        path = Path(path_verts, path_codes)
        patch_fill = mpatches.PathPatch(path, facecolor='#1f77b4', alpha=0.25)
        patch_line = mpatches.PathPatch(path, facecolor='none', edgecolor='#1f77b4', linewidth=2)
        ax1.add_patch(patch_fill)
        ax1.add_patch(patch_line)

        ax1.set_title("Behavioral Shape", size=14, pad=25)

        # --- Bar Chart (Unchanged) ---
        ax2 = fig.add_subplot(1, 2, 2)
        # ... (rest of bar chart code is unchanged) ...
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
    # ... (rest of web app code is unchanged) ...
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
                st.markdown("...") # Explanatory text
        elif email: 
             st.error("No profile found for that email address.")
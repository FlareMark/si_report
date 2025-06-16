import streamlit as st
import gspread
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- Page Configuration ---
st.set_page_config(
    layout="wide", 
    page_title="Self-Reflection Profile",
    initial_sidebar_state="collapsed"
)

# --- PRIVACY & SECURITY META TAGS ---
# Critical: Prevent search engines and AI from indexing private profile content
st.markdown("""
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex, nocache">
<meta name="googlebot" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
<meta name="bingbot" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
<meta name="slurp" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
<meta name="duckduckbot" content="noindex, nofollow, noarchive, nosnippet, noimageindex">
<meta name="facebookexternalhit" content="noindex, nofollow">
<meta name="twitterbot" content="noindex, nofollow">
<meta name="linkedinbot" content="noindex, nofollow">
<meta name="applebot" content="noindex, nofollow">
<meta name="yandexbot" content="noindex, nofollow">
<meta name="baiduspider" content="noindex, nofollow">
<meta name="ia_archiver" content="noindex, nofollow">
<meta name="archive.org_bot" content="noindex, nofollow">
<meta name="CCBot" content="noindex, nofollow">
<meta name="ChatGPT-User" content="noindex, nofollow">
<meta name="anthropic-ai" content="noindex, nofollow">
<meta name="Claude-Web" content="noindex, nofollow">
<meta name="GPTBot" content="noindex, nofollow">
<meta name="PerplexityBot" content="noindex, nofollow">
<meta name="YouBot" content="noindex, nofollow">
""", unsafe_allow_html=True)

# --- CUSTOM CSS INJECTION ---
# This CSS overrides the default Streamlit theme to remove rounded corners from images.
st.markdown("""
<style>
    /* Target all images within the Streamlit app */
    img {
        border-radius: 0px;
    }
</style>
""", unsafe_allow_html=True)
# --- END CUSTOM CSS ---


# --- Logo Display ---
st.image(
    "https://www.flaremark.com/_next/image/?url=%2Flogo.svg&w=384&q=75",
    width=200, 
)


# --- Authentication and Data Loading (Service Account Method) ---
@st.cache_data(ttl=30)  # Reduced to 30 seconds for fresh data
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

# --- Main Visualization Function ---
def create_profile_chart(user_data):
    # This function is complete and correct from our last version
    # ... (omitted for brevity, no changes needed here) ...
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

# --- Web App Interface ---
st.title("Your Personal Self-Reflection Profile")
df = load_data()

if df is not None:
    # This section is correct and includes the URL parameter logic
    email_column_name = "Work Email Address"
    name_column = "Name"
    
    query_params = st.query_params
    email_from_url = query_params.get("email", "")

    email = st.text_input(
        "Please enter your work email address to load your profile:",
        value=email_from_url
    )

    if email:
        normalized_email = email.strip().lower()
        user_row = df[df[email_column_name] == normalized_email]

        if not user_row.empty:
            user_data = user_row.iloc[0].to_dict()
            
            if name_column in user_data:
                st.header(f"Displaying Profile for: {user_data[name_column]}")

            fig = create_profile_chart(user_data)
            if fig is not None:
                st.pyplot(fig)

            # Add personalized insights based on user's scores
            st.markdown("### Your Personal Insights")
            
            # Behavioral insights
            growth_score = user_data.get('Growth Drive Score', 0)
            initiative_score = user_data.get('Initiative Score', 0)
            courage_score = user_data.get('Courage Score', 0)
            generosity_score = user_data.get('Strategic Generosity Score', 0)
            
            # Values alignment insights
            mission_score = user_data.get('Mission Alignment Score', 0)
            values_score = user_data.get('Values Alignment Score', 0)
            culture_score = user_data.get('Culture Alignment Score', 0)
            benefits_score = user_data.get('Benefits Alignment Score', 0)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Behavioral Strengths:**")
                if growth_score >= 7:
                    st.success("**Growth Drive**: You embrace challenges as development opportunities!")
                if initiative_score >= 7:
                    st.success("**Initiative**: You naturally expand your role to create impact!")
                if courage_score >= 7:
                    st.success("**Courage**: You thrive in uncertain, ambiguous situations!")
                if generosity_score >= 7:
                    st.success("**Strategic Generosity**: You prioritize collective success!")
                    
                # Show development areas if any scores are moderate/low
                if any(score < 7 for score in [growth_score, initiative_score, courage_score, generosity_score]):
                    st.markdown("**Development Focus Areas:**")
                    if growth_score < 7:
                        st.info("**Growth Drive**: Consider seeking more challenging assignments")
                    if initiative_score < 7:
                        st.info("**Initiative**: Look for opportunities to propose solutions proactively")
                    if courage_score < 7:
                        st.info("**Courage**: Practice making decisions with incomplete information")
                    if generosity_score < 7:
                        st.info("**Strategic Generosity**: Explore ways to support team goals")
            
            with col2:
                st.markdown("**Values Alignment:**")
                if mission_score >= 7:
                    st.success("**Mission**: You're deeply connected to organizational purpose!")
                if values_score >= 7:
                    st.success("**Values**: Strong alignment between personal and organizational principles!")
                if culture_score >= 7:
                    st.success("**Culture**: You feel genuine belonging and psychological safety!")
                if benefits_score >= 7:
                    st.success("**Benefits**: Satisfied with compensation and development opportunities!")
                    
                # Show alignment concerns if any scores are low
                if any(score < 7 for score in [mission_score, values_score, culture_score, benefits_score]):
                    st.markdown("**Alignment Opportunities:**")
                    if mission_score < 7:
                        st.warning("**Mission**: Consider discussing organizational purpose with your manager")
                    if values_score < 7:
                        st.warning("**Values**: Explore ways to bring more authenticity to your work")
                    if culture_score < 7:
                        st.warning("**Culture**: Seek opportunities to build stronger connections")
                    if benefits_score < 7:
                        st.warning("**Benefits**: This may be worth discussing in your next review")
            
            # Overall pattern insight
            st.markdown("---")
            behavioral_avg = (growth_score + initiative_score + courage_score + generosity_score) / 4
            alignment_avg = (mission_score + values_score + culture_score + benefits_score) / 4
            
            if behavioral_avg >= 7 and alignment_avg >= 7:
                st.success("**Peak Performance Zone**: You have both high capability and strong organizational connection!")
            elif behavioral_avg >= 7 and alignment_avg < 7:
                st.warning("**High Performer, Lower Alignment**: You're capable but may want to address organizational fit")
            elif behavioral_avg < 7 and alignment_avg >= 7:
                st.info("**High Potential**: Strong alignment suggests focused development could unlock significant growth")
            else:
                st.error("**Multiple Focus Areas**: Consider both skill development and organizational alignment conversations")

            with st.expander("How to Interpret Your Profile"):
                st.markdown("""
                ## Understanding Your Results

                Your Strategic Impact Profile measures two key dimensions that influence workplace performance: **how you work** (Behavioral Shape) and **why you work** (Values Alignment). Together, these reveal patterns that explain your engagement, effectiveness, and potential for strategic contribution.

                ---

                ## Part 1: Your Behavioral Shape

                Your behavioral profile shows your natural approach to strategic role ownership across four research-backed dimensions. Each score represents the degree to which you express that particular capability.

                ### Growth Drive (0-10 scale)
                **What it measures:** Your approach to developing capabilities and learning from challenges.

                **Score Interpretation:**
                - **7-10 (High):** You embrace challenges as development opportunities, actively seek feedback, and view setbacks as learning experiences. You believe your abilities can grow through effort and practice.
                - **4-6 (Moderate):** You're open to growth in some areas but may prefer proven approaches in others. You balance learning opportunities with maintaining your current strengths.
                - **0-3 (Lower):** You tend to favor established methods and may be cautious about taking on unfamiliar challenges. You prefer working within your established expertise areas.

                **Development Insight:** Higher Growth Drive correlates with career advancement and adaptability to organizational change.

                ### Initiative (0-10 scale)
                **What it measures:** Your tendency to proactively identify and act on opportunities without external direction.

                **Score Interpretation:**
                - **7-10 (High):** You anticipate problems, identify opportunities, and take action without being asked. You naturally expand your role to create greater impact.
                - **4-6 (Moderate):** You take initiative in familiar areas but may wait for direction in ambiguous situations. You balance proactive action with appropriate consultation.
                - **0-3 (Lower):** You prefer clear direction and defined responsibilities. You execute assigned tasks well but may not venture beyond explicit expectations.

                **Development Insight:** Higher Initiative predicts leadership emergence and project success rates.

                ### Courage Under Uncertainty (0-10 scale)
                **What it measures:** Your willingness to act and make decisions when outcomes are unclear or information is incomplete.

                **Score Interpretation:**
                - **7-10 (High):** You're comfortable making decisions with incomplete information and experimenting with new approaches. You view uncertainty as opportunity rather than threat.
                - **4-6 (Moderate):** You can handle some ambiguity but prefer gathering additional information when possible. You balance calculated risk-taking with thorough analysis.
                - **0-3 (Lower):** You prefer clear parameters and well-defined outcomes. You gather extensive information before making decisions and favor proven approaches.

                **Development Insight:** Higher Courage Under Uncertainty enables innovation and strategic thinking in complex environments.

                ### Strategic Generosity (0-10 scale)
                **What it measures:** Your inclination to share knowledge, resources, and effort to enhance collective organizational success.

                **Score Interpretation:**
                - **7-10 (High):** You actively share knowledge, support others' development, and prioritize organizational success over individual recognition. You see collective wins as personal wins.
                - **4-6 (Moderate):** You collaborate when asked and share knowledge appropriately. You balance individual productivity with team support.
                - **0-3 (Lower):** You focus primarily on your individual domain and responsibilities. You maintain clear boundaries and prefer working independently.

                **Development Insight:** Higher Strategic Generosity correlates with team performance and cross-functional collaboration effectiveness.

                ---

                ## Part 2: Your Values Alignment

                Values Alignment measures your fundamental connection to your organization across four critical dimensions. These scores directly influence your motivation, engagement, and retention likelihood.

                ### Mission Alignment (0-10 scale)
                **What it measures:** Your belief in and connection to your organization's ultimate purpose and goals.

                - **High Scores (7-10):** You believe strongly in what your organization is trying to achieve and feel proud to be part of that mission.
                - **Moderate Scores (4-6):** You understand and generally support the mission but may not feel deeply connected to the organizational purpose.
                - **Lower Scores (0-3):** You may question the organizational mission or feel disconnected from its stated purpose and goals.

                ### Values Alignment (0-10 scale)
                **What it measures:** How well your personal principles align with your organization's stated values and actual practices.

                - **High Scores (7-10):** You feel comfortable being authentic while following organizational principles and see values consistently applied.
                - **Moderate Scores (4-6):** You generally align with stated values but may notice some inconsistencies in application.
                - **Lower Scores (0-3):** You experience conflict between your personal values and organizational practices or stated values.

                ### Culture Alignment (0-10 scale)
                **What it measures:** Your sense of belonging, psychological safety, and connection with colleagues.

                - **High Scores (7-10):** You feel genuine belonging, can be yourself at work, and find interpersonal dynamics energizing.
                - **Moderate Scores (4-6):** You have good working relationships but may not feel deep connection or complete psychological safety.
                - **Lower Scores (0-3):** You may feel like an outsider, experience interpersonal tension, or find workplace dynamics draining.

                ### Benefits Alignment (0-10 scale)
                **What it measures:** Your satisfaction with total compensation, development opportunities, and work-life integration.

                - **High Scores (7-10):** You feel fairly compensated, see clear development paths, and appreciate the work-life balance offered.
                - **Moderate Scores (4-6):** You're generally satisfied with compensation and benefits but may see room for improvement.
                - **Lower Scores (0-3):** You feel undercompensated, lack development opportunities, or experience poor work-life integration.

                ---

                ## Part 3: Reading the Pattern

                The most powerful insights come from understanding how your Behavioral Shape and Values Alignment interact:

                ### High Behavioral Scores + High Values Alignment
                **Pattern:** Peak Performance Zone  
                **Insight:** You have both the capability and motivation to excel. You're likely a high performer and potential mentor for others.

                ### High Behavioral Scores + Low Values Alignment  
                **Pattern:** Flight Risk  
                **Insight:** You're capable but disconnected. You may be performing well despite misalignment, but you're vulnerable to leaving for better-aligned opportunities.

                ### Low Behavioral Scores + High Values Alignment
                **Pattern:** Development Opportunity  
                **Insight:** You want to contribute but may lack confidence, skills, or role clarity. This is often solvable through targeted development and clearer expectations.

                ### Low Behavioral Scores + Low Values Alignment
                **Pattern:** Fundamental Mismatch  
                **Insight:** Both capability expression and organizational connection are limited. This suggests either a wrong-role fit or systemic organizational issues.

                ### Mixed Patterns
                **Pattern:** Specific Focus Areas  
                **Insight:** Examine which specific dimensions are high vs. low to identify targeted development opportunities.

                ---

                ## Part 4: Using Your Results

                ### For Individual Development
                1. **Leverage Your Strengths:** Focus on areas where you score 7+ to maximize your impact
                2. **Address Alignment Issues:** Low Values Alignment scores often explain behavioral patterns better than skill gaps
                3. **Target Growth Areas:** Identify 1-2 behavioral dimensions for focused development

                ### For Conversations with Your Manager
                1. **Share Your Profile:** Use this as a framework for discussing your role effectiveness and development priorities
                2. **Discuss Alignment:** Low Values Alignment scores indicate systemic issues that may require organizational rather than individual solutions
                3. **Create Development Plans:** High Values Alignment + Lower Behavioral scores suggest clear development opportunities

                ### For Career Planning
                1. **Identify Ideal Role Characteristics:** Look for opportunities that leverage your behavioral strengths and align with your values
                2. **Understand Your Motivation Patterns:** Values Alignment scores predict your long-term satisfaction and performance sustainability
                3. **Plan Skill Development:** Use Behavioral Shape scores to prioritize capability building

                ---

                ## Important Notes

                - **Scores Are Not Judgments:** Lower scores don't indicate personal deficiencies—they reflect current patterns that can change with different circumstances, development, or role fit.

                - **Context Matters:** Your scores reflect your current organizational experience. The same person might score differently in a different role or organization.

                - **Development Is Possible:** All four behavioral dimensions are learnable capabilities. With intention and practice, you can shift your patterns over time.

                - **Alignment Is Negotiable:** Values Alignment issues often reflect organizational factors that can be addressed through dialogue, role changes, or system improvements.

                Your Strategic Impact Profile is a starting point for understanding and improving your workplace effectiveness, not a fixed assessment of your capabilities or worth.
                """)

        elif email:
             st.error("No profile found for that email address.")
             
             # Show refresh button only when no profile is found
             st.markdown("---")
             col1, col2, col3 = st.columns([1, 1, 1])
             with col2:
                 if st.button("🔄 Refresh Data", help="Click if you just submitted the assessment"):
                     st.cache_data.clear()
                     st.rerun()

# --- Footer Section ---
st.divider()
st.caption("© 2025 FlareMark. All Rights Reserved. | [Privacy Policy](https://www.flaremark.com/privacy-policy/)")
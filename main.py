import streamlit as st
import os
from datetime import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="GymFlow - Management System",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')

# Main page header with background image
st.markdown(
    """
    <style>
    .main-header {
        background-image: url('https://images.unsplash.com/photo-1445510861639-5651173bc5d5');
        background-size: cover;
        background-position: center;
        padding: 3rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-header"><h1>Welcome to GymFlow</h1></div>', unsafe_allow_html=True)

# Dashboard Overview
col1, col2, col3 = st.columns(3)

# Read data for dashboard
try:
    members_df = pd.read_csv('data/members.csv')
    finance_df = pd.read_csv('data/finance.csv')
    attendance_df = pd.read_csv('data/attendance.csv')
except FileNotFoundError:
    members_df = pd.DataFrame()
    finance_df = pd.DataFrame()
    attendance_df = pd.DataFrame()

with col1:
    st.metric(
        label="Total Members",
        value=len(members_df) if not members_df.empty else 0
    )

with col2:
    today = datetime.now().date()
    today_attendance = len(attendance_df[attendance_df['date'] == str(today)]) if not attendance_df.empty else 0
    st.metric(
        label="Today's Attendance",
        value=today_attendance
    )

with col3:
    monthly_revenue = finance_df[finance_df['type'] == 'income']['amount'].sum() if not finance_df.empty else 0
    st.metric(
        label="Monthly Revenue",
        value=f"${monthly_revenue:,.2f}"
    )

# Quick Actions
st.subheader("Quick Actions")
quick_action_col1, quick_action_col2 = st.columns(2)

with quick_action_col1:
    st.markdown("""
    ### Member Management
    - [Add New Member](/Members)
    - [View All Members](/Members)
    - [Track Attendance](/Attendance)
    """)

with quick_action_col2:
    st.markdown("""
    ### Business Management
    - [Financial Overview](/Finance)
    - [Fitness Tracking](/Fitness)
    - [Reports](/Finance)
    """)

# Featured Images
st.subheader("Facility Highlights")
img_col1, img_col2 = st.columns(2)

with img_col1:
    st.image("https://images.unsplash.com/photo-1481277542470-605612bd2d61", 
             caption="State-of-the-art Equipment",
             use_column_width=True)

with img_col2:
    st.image("https://images.unsplash.com/photo-1533090161767-e6ffed986c88",
             caption="Spacious Training Areas",
             use_column_width=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>© 2024 GymFlow Management System | Made with ❤️ for fitness enthusiasts</p>
    </div>
    """,
    unsafe_allow_html=True
)

import streamlit as st
from datetime import datetime
import pandas as pd
from utils.tenant_manager import TenantManager
from utils.data_manager import DataManager
from utils.auth_manager import AuthManager

# Initialize managers
tm = TenantManager()
auth = AuthManager()

# Check authentication
if 'user' not in st.session_state:
    st.switch_page("pages/Login.py")

# Initialize page
st.set_page_config(
    page_title="GymFlow - Dashboard",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add logout and tenant management to sidebar
with st.sidebar:
    if 'user' in st.session_state:
        # Show current user and gym info
        st.write(f"**Logged in as:** {st.session_state.user['name']}")
        st.write(f"**Current Gym:** {st.session_state.user.get('tenant_name', 'Unknown')}")

        # Gym switcher
        st.divider()
        st.subheader("Switch Gym")

        # Get available gyms
        tenants = tm.list_tenants()
        tenant_options = {t['name']: t for t in tenants}

        # Find current gym's index
        current_gym_name = st.session_state.user.get('tenant_name', '')
        gym_names = list(tenant_options.keys())
        current_index = gym_names.index(current_gym_name) if current_gym_name in gym_names else 0

        selected_gym = st.selectbox(
            "Select Gym",
            options=gym_names,
            index=current_index
        )

        if st.button("Switch"):
            tenant = tenant_options[selected_gym]
            # Verify user has access to selected gym
            try:
                if auth.validate_session(st.session_state.user['session_id']):
                    # Update user's tenant info
                    st.session_state.user['tenant_id'] = tenant['id']
                    st.session_state.user['tenant_name'] = tenant['name']
                    st.success(f"Switched to {tenant['name']}")
                    st.rerun()
            except ValueError as e:
                st.error(f"Error switching gym: {str(e)}")

        st.divider()
        if st.button("Logout"):
            auth.logout_user(st.session_state.user['session_id'])
            del st.session_state.user
            st.rerun()

# Initialize DataManager with the current tenant
dm = DataManager(st.session_state.user['tenant_id'])

# Read data for dashboard using tenant-aware DataManager
members_df, finance_df, attendance_df = dm.get_data()

# Hero Section
st.markdown(f"""
    <div style="background: linear-gradient(135deg, #FF4B4B 0%, #FF9B9B 100%); padding: 3rem; border-radius: 20px; color: white; text-align: center; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <h1 style='font-size: 3rem; font-weight: 700;'>Welcome to {st.session_state.user.get('tenant_name', 'GymFlow')}</h1>
        <p style='font-size: 1.2rem; opacity: 0.9;'>Your Complete Gym Management Solution</p>
    </div>
""", unsafe_allow_html=True)

# Modern Metrics Dashboard
st.markdown("<h2 style='text-align: center; margin-bottom: 2rem;'>Dashboard Overview</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

metrics_data = [
    {
        "label": "Total Members",
        "value": len(members_df) if not members_df.empty else 0,
        "icon": "👥"
    },
    {
        "label": "Today's Attendance",
        "value": len(attendance_df[attendance_df['date'] == str(datetime.now().date())]) if not attendance_df.empty else 0,
        "icon": "📋"
    },
    {
        "label": "Monthly Revenue",
        "value": f"${finance_df[finance_df['type'] == 'income']['amount'].sum():,.2f}" if not finance_df.empty else "$0.00",
        "icon": "💰"
    }
]

for col, metric in zip([col1, col2, col3], metrics_data):
    with col:
        st.markdown(f"""
            <div style="background: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); transition: transform 0.3s ease;">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">{metric['icon']}</div>
                <h3 style="margin: 0; color: #6c757d;">{metric['label']}</h3>
                <p style="font-size: 1.8rem; font-weight: bold; margin: 0.5rem 0; color: #FF4B4B;">
                    {metric['value']}
                </p>
            </div>
        """, unsafe_allow_html=True)

# Quick Actions Section
st.markdown("<h2 style='text-align: center; margin: 3rem 0 2rem;'>Quick Actions</h2>", unsafe_allow_html=True)

quick_action_col1, quick_action_col2 = st.columns(2)

with quick_action_col1:
    st.markdown("""
        <div style="background: #f8f9fa; padding: 2rem; border-radius: 15px; border: 1px solid #e9ecef; transition: all 0.3s ease;">
            <h3 style="color: #FF4B4B; margin-bottom: 1.5rem;">Member Management</h3>
            <ul style="list-style: none; padding: 0;">
                <li style="margin: 1rem 0;"><a href="/Members" style="color: #FF4B4B; text-decoration: none; padding: 0.5rem 1rem; border-radius: 8px; transition: background-color 0.3s ease;">➕ Add New Member</a></li>
                <li style="margin: 1rem 0;"><a href="/Members" style="color: #FF4B4B; text-decoration: none; padding: 0.5rem 1rem; border-radius: 8px; transition: background-color 0.3s ease;">👥 View All Members</a></li>
                <li style="margin: 1rem 0;"><a href="/Attendance" style="color: #FF4B4B; text-decoration: none; padding: 0.5rem 1rem; border-radius: 8px; transition: background-color 0.3s ease;">📋 Track Attendance</a></li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with quick_action_col2:
    st.markdown("""
        <div style="background: #f8f9fa; padding: 2rem; border-radius: 15px; border: 1px solid #e9ecef; transition: all 0.3s ease;">
            <h3 style="color: #FF4B4B; margin-bottom: 1.5rem;">Business Management</h3>
            <ul style="list-style: none; padding: 0;">
                <li style="margin: 1rem 0;"><a href="/Finance" style="color: #FF4B4B; text-decoration: none; padding: 0.5rem 1rem; border-radius: 8px; transition: background-color 0.3s ease;">💰 Financial Overview</a></li>
                <li style="margin: 1rem 0;"><a href="/Fitness" style="color: #FF4B4B; text-decoration: none; padding: 0.5rem 1rem; border-radius: 8px; transition: background-color 0.3s ease;">📊 Fitness Tracking</a></li>
                <li style="margin: 1rem 0;"><a href="/Finance" style="color: #FF4B4B; text-decoration: none; padding: 0.5rem 1rem; border-radius: 8px; transition: background-color 0.3s ease;">📈 Reports</a></li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# Facility Highlights
st.markdown("<h2 style='text-align: center; margin: 3rem 0 2rem;'>Our Facility</h2>", unsafe_allow_html=True)
img_col1, img_col2 = st.columns(2)

with img_col1:
    st.markdown("""
        <div class="image-gallery">
            <img src="https://images.unsplash.com/photo-1481277542470-605612bd2d61" 
                 style="width: 100%; height: 300px; object-fit: cover;"
                 alt="State-of-the-art Equipment">
        </div>
        <p style="text-align: center; margin-top: 1rem; color: #6c757d;">
            State-of-the-art Equipment
        </p>
    """, unsafe_allow_html=True)

with img_col2:
    st.markdown("""
        <div class="image-gallery">
            <img src="https://images.unsplash.com/photo-1533090161767-e6ffed986c88"
                 style="width: 100%; height: 300px; object-fit: cover;"
                 alt="Spacious Training Areas">
        </div>
        <p style="text-align: center; margin-top: 1rem; color: #6c757d;">
            Spacious Training Areas
        </p>
    """, unsafe_allow_html=True)

# Modern Footer
st.markdown("""
    <div style="text-align: center; margin-top: 4rem; padding: 2rem 0; background: #f8f9fa; border-radius: 15px;">
        <p style="color: #6c757d; margin: 0;">© 2024 GymFlow Management System</p>
        <p style="color: #6c757d; margin: 0.5rem 0;">Made with ❤️ for fitness enthusiasts</p>
    </div>
""", unsafe_allow_html=True)
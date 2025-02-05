import streamlit as st
import os
from datetime import datetime
import pandas as pd
from utils.tenant_manager import TenantManager
from utils.data_manager import DataManager

# Initialize managers
tm = TenantManager()

# Get subdomain from the URL (in production, this would come from the actual subdomain)
# For development, we'll use a session state to simulate different tenants
if 'tenant_id' not in st.session_state:
    st.session_state.tenant_id = None
if 'tenant_name' not in st.session_state:
    st.session_state.tenant_name = None

# Tenant Selection (only for development)
if not st.session_state.tenant_id:
    st.set_page_config(
        page_title="GymFlow - Select Gym",
        page_icon="🏢",
        layout="centered"
    )

    st.title("Welcome to GymFlow")

    # Get list of tenants
    tenants = tm.list_tenants()

    if tenants:
        st.header("Select Your Gym")
        tenant_names = {f"{t['name']} ({t['subdomain']})": t['id'] for t in tenants}
        selected_tenant = st.selectbox("Choose your gym:", list(tenant_names.keys()))

        if st.button("Access Dashboard"):
            st.session_state.tenant_id = tenant_names[selected_tenant]
            st.session_state.tenant_name = selected_tenant.split(" (")[0]
            st.rerun()

    st.markdown("---")
    st.markdown("Don't have a gym account? Contact our sales team to get started!")

else:
    # Initialize DataManager with the selected tenant
    dm = DataManager(st.session_state.tenant_id)

    # Page configuration
    st.set_page_config(
        page_title=f"GymFlow - {st.session_state.tenant_name}",
        page_icon="💪",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Add tenant switcher in sidebar
    with st.sidebar:
        st.write(f"**Current Gym:** {st.session_state.tenant_name}")
        if st.button("Switch Gym"):
            st.session_state.tenant_id = None
            st.session_state.tenant_name = None
            st.rerun()

    # Custom CSS
    st.markdown("""
        <style>
        /* Modern gradient hero section */
        .hero-section {
            background: linear-gradient(135deg, #FF4B4B 0%, #FF9B9B 100%);
            padding: 3rem;
            border-radius: 20px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Modern cards */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }

        /* Quick actions */
        .action-card {
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 15px;
            border: 1px solid #e9ecef;
            transition: all 0.3s ease;
        }
        .action-card:hover {
            background: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Modern links */
        .modern-link {
            color: #FF4B4B;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: background-color 0.3s ease;
        }
        .modern-link:hover {
            background-color: rgba(255, 75, 75, 0.1);
        }

        /* Image gallery */
        .image-gallery {
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown(f"""
        <div class="hero-section">
            <h1 style='font-size: 3rem; font-weight: 700;'>Welcome to {st.session_state.tenant_name}</h1>
            <p style='font-size: 1.2rem; opacity: 0.9;'>Your Complete Gym Management Solution</p>
        </div>
    """, unsafe_allow_html=True)

    # Read data for dashboard using tenant-aware DataManager
    members_df, finance_df, attendance_df = dm.get_data()


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
                <div class="metric-card">
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
            <div class="action-card">
                <h3 style="color: #FF4B4B; margin-bottom: 1.5rem;">Member Management</h3>
                <ul style="list-style: none; padding: 0;">
                    <li style="margin: 1rem 0;"><a href="/Members" class="modern-link">➕ Add New Member</a></li>
                    <li style="margin: 1rem 0;"><a href="/Members" class="modern-link">👥 View All Members</a></li>
                    <li style="margin: 1rem 0;"><a href="/Attendance" class="modern-link">📋 Track Attendance</a></li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

    with quick_action_col2:
        st.markdown("""
            <div class="action-card">
                <h3 style="color: #FF4B4B; margin-bottom: 1.5rem;">Business Management</h3>
                <ul style="list-style: none; padding: 0;">
                    <li style="margin: 1rem 0;"><a href="/Finance" class="modern-link">💰 Financial Overview</a></li>
                    <li style="margin: 1rem 0;"><a href="/Fitness" class="modern-link">📊 Fitness Tracking</a></li>
                    <li style="margin: 1rem 0;"><a href="/Finance" class="modern-link">📈 Reports</a></li>
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
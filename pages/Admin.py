import streamlit as st
from utils.tenant_manager import TenantManager
import re

st.set_page_config(page_title="Tenant Management", page_icon="🏢")

# Initialize TenantManager
tm = TenantManager()

st.title("Tenant Management")

# Add New Tenant
st.header("Add New Gym")

with st.form("add_tenant"):
    gym_name = st.text_input("Gym Name")
    subdomain = st.text_input("Subdomain", help="This will be used to access the gym's dashboard (e.g., mygym)")
    
    if st.form_submit_button("Add Gym"):
        if gym_name and subdomain:
            # Validate subdomain format
            if not re.match("^[a-zA-Z0-9-]+$", subdomain):
                st.error("Subdomain can only contain letters, numbers, and hyphens")
            else:
                try:
                    tenant = tm.create_tenant(gym_name, subdomain.lower())
                    st.success(f"Successfully created gym: {gym_name}")
                    st.info(f"Access URL: {subdomain}.gymflow.com")
                except Exception as e:
                    if "duplicate key value violates unique constraint" in str(e):
                        st.error("This subdomain is already taken. Please choose another one.")
                    else:
                        st.error(f"An error occurred: {str(e)}")
        else:
            st.error("Please fill in all fields")

# List Existing Tenants
st.header("Existing Gyms")
tenants = tm.list_tenants()

if tenants:
    for tenant in tenants:
        with st.expander(f"{tenant['name']} ({tenant['subdomain']})"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Status:** {tenant['status'].title()}")
                st.write(f"**Created:** {tenant['created_at'].strftime('%Y-%m-%d')}")
            with col2:
                st.write(f"**ID:** {tenant['id']}")
                st.write(f"**URL:** {tenant['subdomain']}.gymflow.com")
else:
    st.info("No gyms have been created yet.")

# Add some information about the multi-tenant system
st.markdown("""
---
### About Multi-Tenant System

This system allows multiple gyms to operate independently on the platform:

- Each gym gets its own secure subdomain
- Data is completely isolated between gyms
- Custom settings and configuration per gym
- Centralized management and monitoring
""")

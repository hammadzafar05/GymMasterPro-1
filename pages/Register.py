import streamlit as st
from utils.auth_manager import AuthManager
from utils.tenant_manager import TenantManager

st.set_page_config(page_title="Register - GymFlow", page_icon="📝")

# Initialize managers
auth = AuthManager()
tm = TenantManager()

st.title("Register for GymFlow")

# Get available gyms
tenants = tm.list_tenants()
tenant_options = {f"{t['name']} ({t['subdomain']})": t['id'] for t in tenants}

with st.form("registration_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    selected_gym = st.selectbox(
        "Select Your Gym",
        options=list(tenant_options.keys()),
        help="Choose the gym you work at"
    )
    
    submit = st.form_submit_button("Register")
    
    if submit:
        if password != confirm_password:
            st.error("Passwords do not match")
        elif not name or not email or not password:
            st.error("Please fill in all fields")
        else:
            try:
                tenant_id = tenant_options[selected_gym]
                user = auth.register_user(
                    tenant_id=tenant_id,
                    email=email,
                    password=password,
                    name=name
                )
                st.success("Registration successful! Please log in.")
                st.markdown("[Go to Login](/Login)")
            except ValueError as e:
                st.error(str(e))

# Login link
st.markdown("---")
st.markdown("Already have an account? [Login here](/Login)")

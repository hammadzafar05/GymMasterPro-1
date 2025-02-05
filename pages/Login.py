import streamlit as st
from utils.auth_manager import AuthManager
from utils.tenant_manager import TenantManager

st.set_page_config(page_title="Login - GymFlow", page_icon="🔐")

# Initialize managers
auth = AuthManager()
tm = TenantManager()

# Clear session state if not logged in
if 'user' not in st.session_state:
    if 'tenant_id' in st.session_state:
        del st.session_state.tenant_id
    if 'tenant_name' in st.session_state:
        del st.session_state.tenant_name

# Main login form
st.title("Welcome to GymFlow")

# Get available gyms
tenants = tm.list_tenants()
tenant_options = {f"{t['name']} ({t['subdomain']})": t for t in tenants}

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    selected_gym = st.selectbox(
        "Select Your Gym",
        options=list(tenant_options.keys()),
        help="Choose your gym to login"
    )
    submit = st.form_submit_button("Login")

    if submit:
        try:
            # Get tenant info
            tenant = tenant_options[selected_gym]

            # Attempt login
            user = auth.login_user(email, password)

            # Verify tenant access
            if user['tenant_id'] != tenant['id']:
                st.error("You don't have access to this gym.")
            else:
                # Store user and tenant info in session
                st.session_state.user = user
                st.session_state.user['tenant_name'] = tenant['name']
                st.session_state.tenant_id = tenant['id']
                st.rerun()
        except ValueError as e:
            st.error(str(e))

# Registration link
st.markdown("---")
st.markdown("Don't have an account? [Register here](/Register)")
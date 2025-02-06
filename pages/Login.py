import streamlit as st
from utils.auth_manager import AuthManager

st.set_page_config(page_title="Login - GymFlow", page_icon="🔐")

# Initialize managers
auth = AuthManager()

# Clear session state if not logged in
if 'user' not in st.session_state:
    for key in ['tenant_id', 'tenant_name']:
        if key in st.session_state:
            del st.session_state[key]

st.title("Welcome to GymFlow")

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login")

    if submit:
        try:
            # Attempt login
            user = auth.login_user(email, password)

            # Store user info in session
            st.session_state.user = user

            # Redirect based on role
            if user['role'] == 'owner':
                if not user['tenant_id']:
                    # New owner, redirect to Admin page to create gym
                    st.switch_page("pages/Admin.py")
                else:
                    # Existing owner with gym
                    st.rerun()
            else:
                # Staff member
                if not user['tenant_id']:
                    st.error("Your account hasn't been assigned to a gym yet. Please contact your administrator.")
                else:
                    st.rerun()

        except ValueError as e:
            st.error(str(e))

# Registration link
st.markdown("---")
st.markdown("Want to register your gym? [Register as Gym Owner](/Register)")
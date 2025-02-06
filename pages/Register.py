import streamlit as st
from utils.auth_manager import AuthManager

st.set_page_config(page_title="Register - GymFlow", page_icon="📝")

# Initialize managers
auth = AuthManager()

st.title("Register as Gym Owner")

st.markdown("""
    Welcome to GymFlow! As a gym owner, you'll be able to:
    - Manage multiple facilities
    - Access detailed analytics
    - Track member progress
    - Handle financial operations
""")

with st.form("registration_form"):
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    submit = st.form_submit_button("Register")

    if submit:
        if password != confirm_password:
            st.error("Passwords do not match")
        elif not name or not email or not password:
            st.error("Please fill in all fields")
        else:
            try:
                user = auth.register_user(
                    tenant_id=None,  # Owner registration doesn't require tenant_id
                    email=email,
                    password=password,
                    name=name,
                    role='owner'  # Specify role as owner
                )
                st.success("Registration successful! Please log in to create your gym.")
                st.markdown("[Go to Login](/Login)")
            except ValueError as e:
                st.error(str(e))

# Login link
st.markdown("---")
st.markdown("Already have an account? [Login here](/Login)")
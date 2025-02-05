import streamlit as st

def require_auth():
    """
    Protect a page by requiring authentication.
    Must be called at the start of each protected page.
    """
    if 'user' not in st.session_state:
        st.switch_page("pages/Login.py")

    return st.session_state.user
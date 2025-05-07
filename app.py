# app.py

import streamlit as st
from config import PAGE_TITLE, PAGE_LAYOUT

# — Streamlit page configuration —
st.set_page_config(page_title=PAGE_TITLE, layout=PAGE_LAYOUT)

# — Core imports —
from db import init_db
from auth import verify_token
from components.auth import signup_page, login_page
from components.predict import predict_page
from components.history import history_page  # ← import your new history page

def logout():
    """
    Show a Log Out button in the sidebar and clear session on click.
    """
    if st.sidebar.button("🔓 Log Out"):
        for key in ("token", "user"):
            st.session_state.pop(key, None)
        st.success("You’ve been logged out.")
        st.rerun()

def main():
    # 1) Ensure our tables are created in Neon
    init_db()

    # 2) Default to showing the login screen
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    # 3) Check for an existing token
    token = st.session_state.get("token")
    if token:
        username = verify_token(token)
        if username:
            # Authenticated: show sidebar badge + logout + nav
            st.sidebar.write(f"👤 {username}")
            logout()

            # ← Add a radio to switch between Predict & History
            page = st.sidebar.radio("Navigation", ["Predict", "History"])
            if page == "Predict":
                predict_page()
            else:
                history_page()

            return  # prevent fallback to login/signup below

        else:
            # Token invalid or expired
            st.warning("Session expired, please log in again.")
            st.session_state.pop("token", None)
            st.rerun()

    # 4) No valid token: show Login or Sign-Up
    if st.session_state.auth_mode == "login":
        login_page()
    else:
        signup_page()

if __name__ == "__main__":
    main()
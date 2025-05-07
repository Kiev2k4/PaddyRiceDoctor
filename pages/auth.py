# pages/auth.py

import streamlit as st
from sqlalchemy.exc import IntegrityError

from db import SessionLocal, User
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    get_db,
    get_user_by_username,
    get_user_by_email
)

def signup_page():
    """Render the farmer sign-up form."""
    st.title("🚜 Farmer Sign-Up")

    # Form fields
    username = st.text_input("Username", help="Pick a unique username")
    email    = st.text_input("Email", help="Your email address")
    region   = st.text_input("Region", help="e.g., Mekong Delta")
    password = st.text_input("Password", type="password", help="Create a strong password")

    # Submit button
    if st.button("Create Account"):
        # 1) Validate input
        if not (username and email and region and password):
            st.error("All fields are required.")
            return

        db = next(get_db())

        # 2) Check for existing username/email
        if get_user_by_username(db, username) or get_user_by_email(db, email):
            st.error("Username or email already registered.")
            return

        # 3) Hash password and insert user
        hashed = hash_password(password)
        new_user = User(
            username=username,
            email=email,
            region=region,
            password_hash=hashed
        )
        db.add(new_user)
        try:
            db.commit()
            st.success("Account created! You can now log in.")
        except IntegrityError:
            db.rollback()
            st.error("An error occurred. Please try again.")

    # Link back to Login
    st.markdown("---")
    if st.button("Already have an account? Log In"):
        st.session_state.auth_mode = "login"
        st.rerun()


def login_page():
    """Render the farmer login form."""
    st.title("🔐 Farmer Login")

    # Form fields
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Submit button
    if st.button("Log In"):
        # 1) Validate input
        if not (username and password):
            st.error("Enter both username and password.")
            return

        db = next(get_db())

        # 2) Retrieve user and verify password
        user = get_user_by_username(db, username)
        if not user or not verify_password(password, user.password_hash):
            st.error("Invalid credentials.")
            return

        # 3) Create JWT and store in session
        token = create_access_token(subject=username)
        st.session_state.token = token
        st.session_state.user  = username
        st.success(f"Hello, {username}! You’re now logged in.")
        st.rerun()

    # Link to Sign-Up
    st.markdown("---")
    if st.button("Don’t have an account? Sign Up"):
        st.session_state.auth_mode = "signup"
        st.rerun()
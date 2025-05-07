import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8501"

st.title("Google Sign-In with Streamlit (No Flask)")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_info = {}

query_params = st.query_params
code_in_params = "code" in query_params

if not st.session_state.authenticated and code_in_params:
    code = query_params["code"][0] if isinstance(query_params["code"], list) else query_params["code"]
    # Exchange code for access token
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    token_data = response.json()
    access_token = token_data.get("access_token")

    if access_token:
        # Fetch user info
        user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        user_data = requests.get(user_info_url, headers=headers).json()
        st.session_state.authenticated = True
        st.session_state.user_info = user_data
        # Remove code from URL only after successful authentication
        st.query_params.clear()
        st.rerun()
    else:
        st.error("Failed to authenticate with Google.")

if st.session_state.authenticated:
    user_info = st.session_state.user_info
    st.success(f"Welcome, {user_info.get('name', 'User')}! (Streamlit only)")
    st.image(user_info.get("picture", ""))
    st.write("Email:", user_info.get("email", ""))
    st.write("**Login Successful!** You are now on the main page.")
elif not code_in_params:
    # Only show the sign-in button if not handling a code
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth"
        f"?response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&scope=email profile"
        f"&access_type=offline"
    )
    st.markdown(
        f'<a href="{auth_url}"><button>Sign in with Google</button></a>',
        unsafe_allow_html=True,
    )

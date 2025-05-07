import streamlit as st
from flask import Flask, request, redirect
import requests
import threading
import urllib.parse
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Flask app for handling Google OAuth callbacks
app = Flask(__name__)

# Configuration for Google OAuth
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8502/login/callback"

# Initialize session state for user authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_info = {}

@app.route("/login/callback")
def login_callback():
    """Handles the OAuth 2.0 callback."""
    code = request.args.get("code")
    if not code:
        return "Error: No code provided", 400

    # Exchange the authorization code for an access token
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data).json()
    access_token = response.get("access_token")

    # Fetch user information from Google
    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_data = requests.get(user_info_url, headers=headers).json()

    # Save user info to a file for Streamlit to read
    with open("user_info.json", "w") as f:
        json.dump(user_data, f)

    # Redirect back to Streamlit with a flag
    streamlit_url = "http://localhost:8501/?auth=success"
    return redirect(streamlit_url)


def start_flask():
    """Runs the Flask app in a separate thread."""
    app.run(port=8502, threaded=True)

# Start Flask in a separate thread
flask_thread = threading.Thread(target=start_flask, daemon=True)
flask_thread.start()

# Streamlit UI
st.title("Google Sign-In with Streamlit")

# Check for auth flag in URL and update session state
query_params = st.experimental_get_query_params()
if not st.session_state.authenticated and query_params.get("auth") == ["success"]:
    # Read user info from file
    if os.path.exists("user_info.json"):
        with open("user_info.json", "r") as f:
            user_info = json.load(f)
        st.session_state.authenticated = True
        st.session_state.user_info = user_info
        # Optionally remove the file after reading
        os.remove("user_info.json")
        # Remove the auth flag from URL
        st.experimental_set_query_params()

if st.session_state.authenticated:
    # Show the success page
    user_info = st.session_state.user_info
    st.success(f"Welcome, {user_info['name']}!")
    st.image(user_info["picture"])
    st.write("Email:", user_info["email"])
    st.write("**Login Successful!** You are now on the main page.")
else:
    # Google Sign-In button
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth"
        f"?response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&scope=email profile"
        f"&access_type=offline"
    )
    st.markdown(
        f'<a href="{auth_url}" target="_blank"><button>Sign in with Google</button></a>',
        unsafe_allow_html=True,
    )
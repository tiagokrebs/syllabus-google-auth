## Google Signin API PoC

Environment
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
source venv/bin/activate
```

On GCP Console create a new project, enable Signin API and add a Web Application credential with the following URLs.
- `http://localhost:8502/login/callback`
- `http://localhost:8501`

Set a `.env` with:
```
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

## Streamlit Only
Run
```
streamlit run google_signin_streamlit_only.py
```

1. Streamlit
- Runs the main user interface and handles all logic on port 8501.
- Shows the "Sign in with Google" button.
- Handles the OAuth callback directly by reading the code parameter from the URL.
- Exchanges the authorization code for an access token and fetches user info from Google.
- Updates its own session state with the authenticated user info.
- Displays the user's info after successful login.

2. Communication
- No separate server or process is needed.
- No file-based communication is needed.
- All authentication and user info handling is done within Streamlit’s session state and the current app process.

Summary
- Streamlit = UI, OAuth handler, and session manager (all on port 8501)
- No Flask, no background threads, no file-based communication
- Simpler, more robust, and easier to maintain for most use cases

**Streamlit-only approach is not ideal for scaling to many users or for complex apps. Streamlit is designed for simple, interactive data apps and dashboards, not as a full-featured web framework**

## Streamlit + Flask

Run
```
source venv/bin/activate
```

1. Streamlit
- Runs the main user interface on port 8501.
- Shows the "Sign in with Google" button.
- After login, displays the user's info.

1. Flask
- Runs a lightweight web server on port 8502 (in a background thread).
- Handles the /login/callback route, which is the OAuth redirect URI for Google.
- Exchanges the authorization code for an access token and fetches user info from Google.
- Saves user info to a file and redirects the user back to the Streamlit app with a flag.

3. Communication
- Flask and Streamlit do not share memory or session state.
- They communicate by writing/reading the user info to/from a file (user_info.json).
- After Flask saves the user info and redirects to Streamlit, Streamlit reads the file, updates its session state, and shows the authenticated UI.

Summary:
- Streamlit = UI and main app (port 8501)
- Flask = OAuth callback handler (port 8502)
- File-based communication bridges the two

**A combination of Streamlit and Flask is better than only Streamlit when you need advanced authentication, custom backend logic, or API integrations that go beyond Streamlit’s built-in capabilities.**

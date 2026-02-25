from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For testing; restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- CONFIG ----
GOOGLE_CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Must match Google Cloud Console redirect URI
REDIRECT_URI = "http://127.0.0.1:8001/oauth2callback"

# In-memory storage for tokens (⚠️ replace with DB in production)
user_credentials = None


# ---- AUTH ----
@app.get("/login")
def login():
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    auth_url, _ = flow.authorization_url(prompt="consent")
    return RedirectResponse(auth_url)


@app.get("/oauth2callback")
def oauth2callback(code: str):
    global user_credentials
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    flow.fetch_token(code=code)
    user_credentials = flow.credentials

    # After login, redirect to frontend dashboard
    frontend_url = "http://localhost:5173/dashboard"
    return RedirectResponse(frontend_url)


# ---- EMAILS ----
@app.get("/emails")
def get_emails(limit: int = 10):
    global user_credentials
    if not user_credentials:
        return {"success": False, "error": "Not logged in"}

    creds = Credentials(
        token=user_credentials.token,
        refresh_token=user_credentials.refresh_token,
        token_uri=user_credentials.token_uri,
        client_id=user_credentials.client_id,
        client_secret=user_credentials.client_secret,
        scopes=user_credentials.scopes,
    )

    service = build("gmail", "v1", credentials=creds)
    results = service.users().messages().list(userId="me", maxResults=limit).execute()
    messages = results.get("messages", [])

    email_list = []
    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        headers = msg_data.get("payload", {}).get("headers", [])
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
        email_list.append({"id": msg["id"], "subject": subject, "from": sender})

    return {"success": True, "emails": email_list}


# ---- STATS ----
@app.get("/stats")
def get_stats():
    global user_credentials
    if not user_credentials:
        return {"success": False, "error": "Not logged in"}

    creds = Credentials(
        token=user_credentials.token,
        refresh_token=user_credentials.refresh_token,
        token_uri=user_credentials.token_uri,
        client_id=user_credentials.client_id,
        client_secret=user_credentials.client_secret,
        scopes=user_credentials.scopes,
    )

    service = build("gmail", "v1", credentials=creds)

    # Count total + unread emails
    total = service.users().messages().list(userId="me").execute().get("resultSizeEstimate", 0)
    unread = service.users().messages().list(userId="me", q="is:unread").execute().get("resultSizeEstimate", 0)

    return {"success": True, "total_emails": total, "unread_emails": unread}

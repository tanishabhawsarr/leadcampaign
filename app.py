import streamlit as st
import msal
import requests
import json
from fetchdata import fetch_new_leads
from generatemail import create_mail
from dotenv import load_dotenv
import os

load_dotenv()

# -----------------------------
# 🔧 Azure Config
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["User.Read", "Mail.Send"]

# ✅ Auto-Switch Redirect URI (Local <-> Render)
def get_redirect_uri():
    render_url = os.getenv("RENDER_EXTERNAL_URL")
    if render_url:
        return render_url.rstrip("/") + "/"
    return "http://localhost:8501/"

REDIRECT_URI = get_redirect_uri()

# -----------------------------
# 🌐 Streamlit UI Setup
st.set_page_config(page_title="📧 Addend Analytics Email Campaign", page_icon="📨")
st.title("📧 Addend Analytics Email Campaign (Microsoft Login)")

# -----------------------------
# ✅ MSAL Client (Server-side OAuth)
app = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)

# Session State Initialization
if "access_token" not in st.session_state:
    st.session_state.access_token = None

# -----------------------------
# ✅ Step 1 — Login Handling
st.subheader("Step 1️⃣: Sign in with Microsoft")

query_params = st.query_params
auth_code = query_params.get("code")  # No list indexing needed

if not st.session_state.access_token:
    if auth_code:
        result = app.acquire_token_by_authorization_code(
            auth_code,
            scopes=SCOPE,
            redirect_uri=REDIRECT_URI
        )

        if "access_token" in result:
            st.session_state.access_token = result["access_token"]

            me = requests.get(
                "https://graph.microsoft.com/v1.0/me",
                headers={"Authorization": f"Bearer {result['access_token']}"}
            ).json()

            st.session_state.user_email = me.get("mail") or me.get("userPrincipalName")
            st.success(f"✅ Logged in as: {st.session_state.user_email}")

            # ✅ Remove ?code= parameter to avoid re-login loops
            st.query_params.clear()

        else:
            st.error(f"❌ Login failed:\n\n{result.get('error_description')}")
            st.stop()

    else:
        auth_url = app.get_authorization_request_url(
            SCOPE,
            redirect_uri=REDIRECT_URI,
            prompt="select_account"
        )
        st.markdown(f"[🔐 **Click here to Sign in with Microsoft**]({auth_url})")
        st.stop()
else:
    st.success(f"✅ Logged in as {st.session_state.user_email}")

# -----------------------------
# ✅ Step 2: Fetch Lead
st.subheader("Step 2️⃣: Fetch Lead Data")

target_email = st.text_input("Enter lead email:")

if st.button("Fetch Lead"):
    lead = fetch_new_leads(target_email) if target_email else None

    if lead:
        st.session_state.lead = lead
        st.success("✅ Lead found!")
        st.json(lead)

        subject, body = create_mail(lead["Name"], lead["Company"], lead["OfferDisplayName"])
        st.session_state.mail_body = (subject, body)

        st.markdown("### ✉️ Email Preview")
        st.markdown(body, unsafe_allow_html=True)
    else:
        st.warning("⚠️ No lead found.")

# -----------------------------
# ✅ Step 3: Send Email
st.subheader("Step 3️⃣: Send Email")

if st.session_state.get("lead") and st.session_state.get("mail_body"):
    if st.button("Send Email"):
        lead = st.session_state.lead
        subject, body = st.session_state.mail_body

        body_html = body.replace("\n", "<br>")

        email_msg = {
            "message": {
                "subject": subject,
                "body": {"contentType": "HTML", "content": body_html},
                "toRecipients": [{"emailAddress": {"address": lead["Email"]}}],
            },
            "saveToSentItems": True
        }

        headers = {
            "Authorization": f"Bearer {st.session_state.access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://graph.microsoft.com/v1.0/me/sendMail",
            headers=headers,
            json=email_msg
        )

        if response.status_code == 202:
            st.success("✅ Email sent successfully!")
        else:
            st.error(f"❌ Sending failed:\n\n{response.text}")
else:
    st.info("ℹ️ Fetch a lead first to enable email sending.")

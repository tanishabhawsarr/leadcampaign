import streamlit as st
import msal
import requests
import json
from fetchdata import fetch_new_leads
from generatemail import create_mail
from dotenv import load_dotenv
import os
# ==============================
# 🔧 Azure AD App Registration
# ==============================

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")


AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_URI = "https://leadsemailcampaign-fub8e3fpc7akhyaf.centralindia-01.azurewebsites.net/"
SCOPE = ["User.Read", "Mail.Send"]

st.set_page_config(page_title="📧 AppSource Leads Email Campaign", page_icon="📨")
st.title("📧 Addend Analytics Email Campaign (Microsoft Login)")

print("🔧 Initializing MSAL client...")
app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)

if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "lead" not in st.session_state:
    st.session_state.lead = None
if "mail_body" not in st.session_state:
    st.session_state.mail_body = None

# ==============================
# 🪪 Step 1: Microsoft Login
# ==============================
st.subheader("Step 1️⃣: Sign in with your Microsoft account")

if not st.session_state.access_token:
    flow = app.initiate_device_flow(scopes=SCOPE)
    if "user_code" not in flow:
        st.error("Failed to create device flow. Check Azure AD app settings.")
    else:
        st.markdown("**👉 Go to** [https://microsoft.com/devicelogin](https://microsoft.com/devicelogin)")
        st.code(flow["user_code"], language="bash")
        st.info("After login, return here. The app will wait for authentication...")

        result = app.acquire_token_by_device_flow(flow)
        if "access_token" in result:
            st.session_state.access_token = result["access_token"]
            st.success("✅ Logged in successfully!")

            graph_resp = requests.get(
                "https://graph.microsoft.com/v1.0/me",
                headers={"Authorization": f"Bearer {result['access_token']}"}
            )
            if graph_resp.status_code == 200:
                st.session_state.user_email = graph_resp.json().get("mail")
                print(f"✅ Logged in as {st.session_state.user_email}")
        else:
            st.error(f"❌ Login failed: {result.get('error_description')}")
else:
    st.success(f"✅ Logged in as {st.session_state.user_email or 'user'}")

# ==============================
# 📨 Step 2: Fetch Lead
# ==============================
st.subheader("Step 2️⃣: Fetch Lead Data")

target_email = st.text_input("Enter client email to fetch lead:")

if st.button("Fetch Lead"):
    if not st.session_state.access_token:
        st.warning("Please sign in first.")
    elif target_email:
        print(f"📩 Fetch button clicked for: {target_email}")
        lead = fetch_new_leads(target_email)
        print(f"📊 Lead data returned: {lead}")

        if lead:
            st.session_state.lead = lead
            st.success("✅ Lead found!")
            st.json(lead)

            mail_body = create_mail(
                lead["Name"],
                lead["Company"],
                lead["OfferDisplayName"]
            )

            st.session_state.mail_body = mail_body
            st.markdown("### ✉️ Generated Email Preview")
            st.markdown(mail_body, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No lead found for this email.")
    else:
        st.warning("Please enter a target email.")

# ==============================
# 📤 Step 3: Send Email
# ==============================
st.subheader("Step 3️⃣: Send Email to Client")

if st.session_state.lead and st.session_state.mail_body:
    if st.button("Send Email"):
        lead = st.session_state.lead
        mail_body = st.session_state.mail_body

        if not st.session_state.access_token:
            st.error("No valid authentication found. Please sign in again.")
        else:
            headers = {
                "Authorization": f"Bearer {st.session_state.access_token}",
                "Content-Type": "application/json"
            }

            recipient_email = (
                lead["Email"][0] if isinstance(lead["Email"], list) else lead["Email"]
            )

            # 🧹 Clean up the mail_body
            if isinstance(mail_body, tuple):
                # Some code stores (subject, body) tuples
                subject, body = mail_body
            else:
                subject = f"Regarding your interest in {lead['OfferDisplayName']}"
                body = mail_body

            # 🧠 Convert newlines (\n) into HTML <br> tags
            body_html = str(body).replace("\n", "<br>")

            # 🎨 Wrap everything in a proper HTML structure
            html_body = f"""
            <html>
              <body style="font-family: Arial, sans-serif; color: #222; line-height: 1.6;">
                <p>{body_html}</p>
              </body>
            </html>
            """

            email_msg = {
                "message": {
                    "subject": subject,
                    "body": {
                        "contentType": "HTML",
                        "content": html_body.strip(),
                    },
                    "toRecipients": [
                        {"emailAddress": {"address": recipient_email}}
                    ],
                },
                "saveToSentItems": True,
            }

            print("===========================================")
            print("🧾 Request payload JSON:")
            print(json.dumps(email_msg, indent=2))
            print("===========================================")

            endpoint = "https://graph.microsoft.com/v1.0/me/sendMail"
            resp = requests.post(endpoint, headers=headers, json=email_msg)

            print(f"📨 Graph sendMail status: {resp.status_code}")
            print(f"📬 Response: {resp.text}")
            print("===========================================")

            if resp.status_code == 202:
                st.success("✅ Email sent successfully!")
            else:
                st.error(f"❌ Email failed to send. Check terminal logs for details.")
else:
    st.info("ℹ️ Please fetch a lead first to enable sending.")
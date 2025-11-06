# import streamlit as st
# import msal
# import requests
# import json
# from fetchdata import fetch_new_leads
# from generatemail import create_mail
# from dotenv import load_dotenv
# import os
# # ==============================
# # 🔧 Azure AD App Registration
# # ==============================

# load_dotenv()
# CLIENT_ID = os.getenv("CLIENT_ID")
# TENANT_ID = os.getenv("TENANT_ID")
# CLIENT_SECRET=os.getenv("CLIENT_SECRET")

# AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
# REDIRECT_URI = "https://leadsemailcampaign-fub8e3fpc7akhyaf.centralindia-01.azurewebsites.net/"
# SCOPE = ["User.Read", "Mail.Send"]

# st.set_page_config(page_title="📧 AppSource Leads Email Campaign", page_icon="📨")
# st.title("📧 Addend Analytics Email Campaign (Microsoft Login)")

# print("🔧 Initializing MSAL client...")
# app = msal.ConfidentialClientApplication(
#     CLIENT_ID,
#     authority=AUTHORITY,
#     client_credential=CLIENT_SECRET
# )

# st.subheader("Step 1️⃣: Sign in with Microsoft")

# # ✅ 1. Check if redirected back with ?code=
# query_params = st.query_params
# auth_code = query_params.get("code", [None])[0]

# if not st.session_state.get("access_token"):
#     if auth_code:
#         # ✅ Exchange code for access token
#         result = app.acquire_token_by_authorization_code(
#             auth_code,
#             scopes=SCOPE,
#             redirect_uri=REDIRECT_URI
#         )
#         if "access_token" in result:
#             st.session_state.access_token = result["access_token"]

#             # Fetch user email
#             me = requests.get(
#                 "https://graph.microsoft.com/v1.0/me",
#                 headers={"Authorization": f"Bearer {result['access_token']}"}
#             ).json()
#             st.session_state.user_email = me.get("mail") or me.get("userPrincipalName")
#             st.success(f"✅ Logged in as {st.session_state.user_email}")
#         else:
#             st.error("Login failed. Please try again.")

#     else:
#         # ✅ Create login button
#         auth_url = app.get_authorization_request_url(
#             SCOPE,
#             redirect_uri=REDIRECT_URI
#         )
#         st.markdown(f"[🔐 **Click here to Sign in with Microsoft**]({auth_url})", unsafe_allow_html=True)

# else:
#     st.success(f"✅ Logged in as {st.session_state.user_email}")

# # ==============================
# # 📨 Step 2: Fetch Lead
# # ==============================
# st.subheader("Step 2️⃣: Fetch Lead Data")

# target_email = st.text_input("Enter client email to fetch lead:")

# if st.button("Fetch Lead"):
#     if not st.session_state.access_token:
#         st.warning("Please sign in first.")
#     elif target_email:
#         print(f"📩 Fetch button clicked for: {target_email}")
#         lead = fetch_new_leads(target_email)
#         print(f"📊 Lead data returned: {lead}")

#         if lead:
#             st.session_state.lead = lead
#             st.success("✅ Lead found!")
#             st.json(lead)

#             mail_body = create_mail(
#                 lead["Name"],
#                 lead["Company"],
#                 lead["OfferDisplayName"]
#             )

#             st.session_state.mail_body = mail_body
#             st.markdown("### ✉️ Generated Email Preview")
#             st.markdown(mail_body, unsafe_allow_html=True)
#         else:
#             st.warning("⚠️ No lead found for this email.")
#     else:
#         st.warning("Please enter a target email.")

# # ==============================
# # 📤 Step 3: Send Email
# # ==============================
# st.subheader("Step 3️⃣: Send Email to Client")

# if st.session_state.lead and st.session_state.mail_body:
#     if st.button("Send Email"):
#         lead = st.session_state.lead
#         mail_body = st.session_state.mail_body

#         if not st.session_state.access_token:
#             st.error("No valid authentication found. Please sign in again.")
#         else:
#             headers = {
#                 "Authorization": f"Bearer {st.session_state.access_token}",
#                 "Content-Type": "application/json"
#             }

#             recipient_email = (
#                 lead["Email"][0] if isinstance(lead["Email"], list) else lead["Email"]
#             )

#             # 🧹 Clean up the mail_body
#             if isinstance(mail_body, tuple):
#                 # Some code stores (subject, body) tuples
#                 subject, body = mail_body
#             else:
#                 subject = f"Regarding your interest in {lead['OfferDisplayName']}"
#                 body = mail_body

#             # 🧠 Convert newlines (\n) into HTML <br> tags
#             body_html = str(body).replace("\n", "<br>")

#             # 🎨 Wrap everything in a proper HTML structure
#             html_body = f"""
#             <html>
#               <body style="font-family: Arial, sans-serif; color: #222; line-height: 1.6;">
#                 <p>{body_html}</p>
#               </body>
#             </html>
#             """

#             email_msg = {
#                 "message": {
#                     "subject": subject,
#                     "body": {
#                         "contentType": "HTML",
#                         "content": html_body.strip(),
#                     },
#                     "toRecipients": [
#                         {"emailAddress": {"address": recipient_email}}
#                     ],
#                 },
#                 "saveToSentItems": True,
#             }

#             print("===========================================")
#             print("🧾 Request payload JSON:")
#             print(json.dumps(email_msg, indent=2))
#             print("===========================================")

#             endpoint = "https://graph.microsoft.com/v1.0/me/sendMail"
#             resp = requests.post(endpoint, headers=headers, json=email_msg)

#             print(f"📨 Graph sendMail status: {resp.status_code}")
#             print(f"📬 Response: {resp.text}")
#             print("===========================================")

#             if resp.status_code == 202:
#                 st.success("✅ Email sent successfully!")
#             else:
#                 st.error(f"❌ Email failed to send. Check terminal logs for details.")
# else:
#     st.info("ℹ️ Please fetch a lead first to enable sending.")



import streamlit as st
import msal
import requests
import json
from fetchdata import fetch_new_leads
from generatemail import create_mail
import os
from dotenv import load_dotenv

# -----------------------------
# 🔧 Azure AD App Registration

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_SECRET=os.getenv("CLIENT_SECRET")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["User.Read", "Mail.Send"]

st.set_page_config(page_title="📧 Addend Analytics Campaign", page_icon="📨")
st.title("📧 Addend Analytics Email Campaign")

# -----------------------------
# ✅ Initialize Session State
# -----------------------------
for key, default in {
    "access_token": None,
    "user_email": None,
    "lead": None,
    "mail_body": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# -----------------------------
# ✅ Step 1: Microsoft Login
# -----------------------------
st.subheader("Step 1️⃣: Sign in")

app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)

if not st.session_state.access_token:
    flow = app.initiate_device_flow(scopes=SCOPE)

    if "user_code" not in flow:
        st.error("❌ Login flow could not start. Check Azure App Registration.")
    else:
        st.write("👉 Open: https://microsoft.com/devicelogin")
        st.code(flow["user_code"], language="bash")
        st.info("After logging in, return here.")

        result = app.acquire_token_by_device_flow(flow)

        if "access_token" in result:
            st.session_state.access_token = result["access_token"]

            me = requests.get(
                "https://graph.microsoft.com/v1.0/me",
                headers={"Authorization": f"Bearer {result['access_token']}"}
            )

            if me.status_code == 200:
                st.session_state.user_email = me.json().get("mail")

            st.success(f"✅ Logged in as: {st.session_state.user_email}")

        else:
            st.error(f"❌ Login failed: {result.get('error_description')}")
else:
    st.success(f"✅ Logged in as: {st.session_state.user_email}")

# -----------------------------
# ✅ Step 2: Fetch Lead
# -----------------------------
st.subheader("Step 2️⃣: Fetch Lead")

target_email = st.text_input("Enter lead email:")

if st.button("Fetch Lead"):
    lead = fetch_new_leads(target_email)

    if lead:
        st.session_state.lead = lead
        st.success("✅ Lead found!")
        st.json(lead)

        subject, body = create_mail(lead["Name"], lead["Company"], lead["OfferDisplayName"])
        st.session_state.mail_body = (subject, body)

        st.markdown("### ✉️ Preview Email")
        st.markdown(body, unsafe_allow_html=True)

    else:
        st.warning("⚠️ No lead found for this email.")

# -----------------------------
# ✅ Step 3: Send Email
# -----------------------------
st.subheader("Step 3️⃣: Send Email")

if st.session_state.lead and st.session_state.mail_body:
    if st.button("Send Email"):
        lead = st.session_state.lead
        subject, body = st.session_state.mail_body

        html_body = body if "<html" in body.lower() else f"<html><body>{body}</body></html>"

        email_msg = {
            "message": {
                "subject": subject,
                "body": {"contentType": "HTML", "content": html_body},
                "toRecipients": [{"emailAddress": {"address": lead["Email"]}}]
            },
            "saveToSentItems": True
        }

        headers = {
            "Authorization": f"Bearer {st.session_state.access_token}",
            "Content-Type": "application/json"
        }

        send = requests.post(
            "https://graph.microsoft.com/v1.0/me/sendMail",
            headers=headers,
            json=email_msg
        )

        if send.status_code == 202:
            st.success("✅ Email sent successfully!")
        else:
            st.error(f"❌ Email failed: {send.text}")
else:
    st.info("ℹ️ Please fetch a lead first.")

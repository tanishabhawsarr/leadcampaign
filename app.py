# import streamlit as st
# import msal
# import requests
# import json
# from fetchdata import fetch_new_leads
# from generatemail import create_mail
# from dotenv import load_dotenv
# import os

# load_dotenv()

# # -----------------------------
# # 🔧 Azure Config
# CLIENT_ID = os.getenv("CLIENT_ID")
# TENANT_ID = os.getenv("TENANT_ID")
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
# SCOPE = ["User.Read", "Mail.Send"]

# # ✅ Auto-Switch Redirect URI (Local <-> Render)
# def get_redirect_uri():
#     # 1. Render hosting
#     render_url = os.getenv("RENDER_EXTERNAL_URL")
#     if render_url:
#         return render_url.rstrip("/") + "/"

#     # 2. Azure App Service hosting
#     azure_hostname = os.getenv("WEBSITE_HOSTNAME")
#     if azure_hostname:
#         return f"https://{azure_hostname}/"

#     # 3. Local development
#     return "http://localhost:8501/"
    

# REDIRECT_URI = get_redirect_uri()
# # -----------------------------
# # 🌐 Streamlit UI Setup
# st.set_page_config(page_title="📧 Addend Analytics Email Campaign", page_icon="📨")
# st.title("📧 Addend Analytics Email Campaign (Microsoft Login)")

# # -----------------------------
# # ✅ MSAL Client (Server-side OAuth)
# app = msal.ConfidentialClientApplication(
#     CLIENT_ID,
#     authority=AUTHORITY,
#     client_credential=CLIENT_SECRET
# )

# # Session State Initialization
# if "access_token" not in st.session_state:
#     st.session_state.access_token = None

# # -----------------------------
# # ✅ Step 1 — Login Handling
# st.subheader("Step 1️⃣: Sign in with Microsoft")

# query_params = st.query_params
# auth_code = query_params.get("code")  # No list indexing needed

# if not st.session_state.access_token:
#     if auth_code:
#         result = app.acquire_token_by_authorization_code(
#             auth_code,
#             scopes=SCOPE,
#             redirect_uri=REDIRECT_URI
#         )

#         if "access_token" in result:
#             st.session_state.access_token = result["access_token"]

#             me = requests.get(
#                 "https://graph.microsoft.com/v1.0/me",
#                 headers={"Authorization": f"Bearer {result['access_token']}"}
#             ).json()

#             st.session_state.user_email = me.get("mail") or me.get("userPrincipalName")
#             st.success(f"✅ Logged in as: {st.session_state.user_email}")

#             # ✅ Remove ?code= parameter to avoid re-login loops
#             st.query_params.clear()

#         else:
#             st.error(f"❌ Login failed:\n\n{result.get('error_description')}")
#             st.stop()

#     else:
#         auth_url = app.get_authorization_request_url(
#             SCOPE,
#             redirect_uri=REDIRECT_URI,
#             prompt="select_account"
#         )
#         st.markdown(f"[🔐 **Click here to Sign in with Microsoft**]({auth_url})")
#         st.stop()
# else:
#     st.success(f"✅ Logged in as {st.session_state.user_email}")

# # -----------------------------
# # ✅ Step 2: Fetch Lead
# st.subheader("Step 2️⃣: Fetch Lead Data")

# target_email = st.text_input("Enter lead email:")

# if st.button("Fetch Lead"):
#     lead = fetch_new_leads(target_email) if target_email else None

#     if lead:
#         st.session_state.lead = lead
#         st.success("✅ Lead found!")
#         st.json(lead)

#         subject, body = create_mail(lead["Name"], lead["Company"], lead["OfferDisplayName"])
#         st.session_state.mail_body = (subject, body)

#         st.markdown("### ✉️ Email Preview")
#         st.markdown(body, unsafe_allow_html=True)
#         print("Generated Subject:", subject)
#         print("Generated Body:", body)
#     else:
#         st.warning("⚠️ No lead found.")

# # -----------------------------
# # ✅ Step 3: Send Email
# st.subheader("Step 3️⃣: Send Email")

# if st.session_state.get("lead") and st.session_state.get("mail_body"):
#     if st.button("Send Email"):
#         lead = st.session_state.lead
#         subject, body = st.session_state.mail_body

#         body_html = body.replace("\n", "<br>")

#         email_msg = {
#             "message": {
#                 "subject": subject,
#                 "body": {"contentType": "HTML", "content": body_html},
#                 "toRecipients": [{"emailAddress": {"address": lead["Email"]}}],
#             },
#             "saveToSentItems": True
#         }

#         headers = {
#             "Authorization": f"Bearer {st.session_state.access_token}",
#             "Content-Type": "application/json"
#         }

#         response = requests.post(
#             "https://graph.microsoft.com/v1.0/me/sendMail",
#             headers=headers,
#             json=email_msg
#         )

#         if response.status_code == 202:
#             st.success("✅ Email sent successfully!")
#         else:
#             st.error(f"❌ Sending failed:\n\n{response.text}")
# else:
#     st.info("ℹ️ Fetch a lead first to enable email sending.")



# app.py
# app.py

# import streamlit as st
# import requests
# import os
# import time
# from datetime import datetime
# from dotenv import load_dotenv

# from fetchdata import fetch_new_leads_since
# from generatemail import create_mail
# from state_manager import load_last_processed, save_last_processed


# load_dotenv()

# # ------------ AUTO REFRESH WITHOUT ANY PACKAGE ------------
# # def auto_refresh(seconds=30):
# #     st.markdown(
# #         f"""
# #         <script>
# #         function refresh() {{
# #             setTimeout(function() {{
# #                 window.location.reload();
# #             }}, {seconds * 1000});
# #         }}
# #         refresh();
# #         </script>
# #         """,
# #         unsafe_allow_html=True
# #     )

# # auto_refresh(30)

# # ------------ BACKEND AUTO REFRESH (NO PAGE RELOAD) ------------
# if "last_refresh" not in st.session_state:
#     st.session_state.last_refresh = time.time()

# # If 30 sec passed → rerun code
# if time.time() - st.session_state.last_refresh >= 30:
#     st.session_state.last_refresh = time.time()
#     st.rerun()
# # ---------------------------------------------------------------

# # -----------------------------------------------------------


# st.set_page_config(page_title="Live Leads", page_icon="📧", layout="wide")
# st.title("📧 Addend Analytics — Live Today's Leads")

# # --- SESSION INITIALIZATION ---
# if "leads" not in st.session_state:
#     st.session_state.leads = []

# if "removed_rowkeys" not in st.session_state:
#     st.session_state.removed_rowkeys = set()

# if "access_token" not in st.session_state:
#     st.session_state.access_token = None
#     st.session_state.user_email = None

# # --- MICROSOFT LOGIN (same as before) ---
# try:
#     import msal
#     MSAL_AVAILABLE = True
# except:
#     MSAL_AVAILABLE = False

# CLIENT_ID = os.getenv("CLIENT_ID")
# TENANT_ID = os.getenv("TENANT_ID")
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
# SCOPE = ["User.Read", "Mail.Send"]

# def get_redirect_uri():
#     hostname = os.getenv("WEBSITE_HOSTNAME")
#     if hostname:
#         return f"https://{hostname}/"
#     return "http://localhost:8501/"

# REDIRECT_URI = get_redirect_uri()

# st.sidebar.header("Microsoft Login")

# if MSAL_AVAILABLE and not st.session_state.access_token:

#     app = msal.ConfidentialClientApplication(
#         CLIENT_ID,
#         authority=AUTHORITY,
#         client_credential=CLIENT_SECRET
#     )

#     params = st.query_params
#     code = params.get("code")

#     if code:
#         result = app.acquire_token_by_authorization_code(
#             code, scopes=SCOPE, redirect_uri=REDIRECT_URI
#         )

#         if "access_token" in result:
#             st.session_state.access_token = result["access_token"]
#             st.query_params.clear()

#             me = requests.get(
#                 "https://graph.microsoft.com/v1.0/me",
#                 headers={"Authorization": f"Bearer {result['access_token']}"}
#             ).json()

#             st.session_state.user_email = me.get("mail") or me.get("userPrincipalName")

#             st.success(f"Logged in as {st.session_state.user_email}")

#         else:
#             st.error("Login failed.")
#             st.stop()

#     else:
#         auth_url = app.get_authorization_request_url(
#             scopes=SCOPE, redirect_uri=REDIRECT_URI, prompt="select_account"
#         )
#         st.markdown(f"[🔐 Click to Sign in with Microsoft]({auth_url})")
#         st.stop()

# else:
#     if st.session_state.access_token:
#         st.sidebar.success(f"Logged in as {st.session_state.user_email}")
#     else:
#         st.sidebar.info("Login disabled – emails will not be sent.")


# # --- BACKEND REFRESH LEADS ---
# last_processed_str = load_last_processed()

# if last_processed_str:
#     cutoff_time = datetime.strptime(last_processed_str, "%m/%d/%Y %H:%M:%S")
# else:
#     cutoff_time = None  # means first time → show all leads of today


# all_leads = fetch_new_leads_since(cutoff_time)


# # remove leads that have been "sent" (UI only)
# filtered = [l for l in all_leads if l["RowKey"] not in st.session_state.removed_rowkeys]

# st.session_state.leads = filtered

# # --- DISPLAY LEADS ---
# st.subheader("Today's Unprocessed Leads (Real-time)")

# leads = st.session_state.leads

# if not leads:
#     st.info("No new leads at the moment...")
# else:
#     for lead in leads:

#         pk = lead["PartitionKey"]
#         rk = lead["RowKey"]
#         name = lead["Name"]
#         email = lead["Email"]
#         company = lead["Company"]
#         offer = lead["OfferDisplayName"]
#         created = lead["CreatedTime"]

#         col1, col2, col3, col4 = st.columns([3, 3, 3, 1])

#         with col1:
#             st.markdown(f"### {name}")
#             st.write(f"📧 {email}")
#             st.write(f"🏢 {company}")

#         with col2:
#             st.write(f"🧩 Offer: {offer}")
#             st.write(f"📥 Source: {lead['LeadSource']}")

#         with col3:
#             st.write(f"⏱ Created: {created}")

#         with col4:
#             if st.button("Send", key=f"send_{rk}"):

#     # Generate mail
#                 subject, body_html = create_mail(name, company, offer)

#                 # Confirm button
#                 if st.button("Confirm Send", key=f"confirm_{rk}"):

#                     if st.session_state.access_token:

#                         email_msg = {
#                             "message": {
#                                 "subject": subject,
#                                 "body": {"contentType": "HTML", "content": body_html},
#                                 "toRecipients": [{"emailAddress": {"address": email}}],
#                             },
#                             "saveToSentItems": True,
#                         }

#                         headers = {
#                             "Authorization": f"Bearer {st.session_state.access_token}",
#                             "Content-Type": "application/json"
#                         }

#                         resp = requests.post(
#                             "https://graph.microsoft.com/v1.0/me/sendMail",
#                             headers=headers,
#                             json=email_msg
#                         )

#                         if resp.status_code in (200, 201, 202):
#                             st.success(f"📨 Email sent to {email}")

#                             # Save last processed time locally
#                             save_last_processed(created)

#                             st.rerun()

#                         else:
#                             st.error("❌ Mail failed: " + resp.text)

#                     else:
#                         st.warning("Login required to send email")



# st.markdown("---")
# st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
# app.py (debuggable version)
# import streamlit as st
# import requests
# import os
# import time
# import traceback
# from datetime import datetime
# from dotenv import load_dotenv
# from requests.exceptions import ConnectionError, Timeout

# from fetchdata import fetch_new_leads_since
# from generatemail import create_mail
# from state_manager import load_last_processed, save_last_processed

# load_dotenv()

# # ---------------- Helpers: logging & safe network calls ----------------
# def log(msg):
#     """Append a debug message to session logs and print to console."""
#     ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     entry = f"[{ts}] {msg}"
#     if "debug_logs" not in st.session_state:
#         st.session_state.debug_logs = []
#     st.session_state.debug_logs.append(entry)
#     # keep log length reasonable
#     if len(st.session_state.debug_logs) > 200:
#         st.session_state.debug_logs = st.session_state.debug_logs[-200:]
#     print(entry)

# def safe_create_mail(rk, name, company, offer, timeout_seconds=30):
#     """Call create_mail but catch exceptions and log them. Return (subject, body) or (None, None) on error."""
#     try:
#         log(f"create_mail: starting for rk={rk}, offer={offer!r}")
#         # call the real create_mail (this may raise)
#         subject, body = create_mail(name, company, offer)
#         if not subject or not body:
#             log(f"create_mail: returned empty content for rk={rk}")
#             return None, None
#         log(f"create_mail: success for rk={rk}")
#         return subject, body
#     except Exception as e:
#         tb = traceback.format_exc()
#         log(f"create_mail: EXCEPTION for rk={rk}: {e}\n{tb}")
#         return None, None

# def safe_send_mail(access_token, to_email, subject, body):
#     """Send email via Graph, log errors. Return (ok, status_text)."""
#     try:
#         url = "https://graph.microsoft.com/v1.0/me/sendMail"
#         email_msg = {
#             "message": {
#                 "subject": subject,
#                 "body": {"contentType": "HTML", "content": body},
#                 "toRecipients": [{"emailAddress": {"address": to_email}}],
#             },
#             "saveToSentItems": True,
#         }
#         headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
#         log(f"sendMail: POSTing to Graph for {to_email}")
#         resp = requests.post(url, headers=headers, json=email_msg, timeout=30)
#         log(f"sendMail: response status {resp.status_code}")
#         if resp.status_code in (200, 201, 202):
#             return True, resp.text
#         else:
#             # show body for debugging
#             return False, resp.text
#     except ConnectionError as e:
#         tb = traceback.format_exc()
#         log(f"sendMail: ConnectionError: {e}\n{tb}")
#         return False, f"ConnectionError: {e}"
#     except Timeout as e:
#         tb = traceback.format_exc()
#         log(f"sendMail: Timeout: {e}\n{tb}")
#         return False, f"Timeout: {e}"
#     except Exception as e:
#         tb = traceback.format_exc()
#         log(f"sendMail: EXCEPTION: {e}\n{tb}")
#         return False, f"Exception: {e}"

# # ---------------- Auto backend refresh (no page reload) ---------------
# if "last_refresh" not in st.session_state:
#     st.session_state.last_refresh = time.time()
# if time.time() - st.session_state.last_refresh >= 30:
#     st.session_state.last_refresh = time.time()
#     log("Auto-refresh triggered (30s).")
#     st.rerun()
# # -------------------------------------------------------------------

# # Ensure debug logs exist
# if "debug_logs" not in st.session_state:
#     st.session_state.debug_logs = []

# # Store generated emails cache
# if "generated_emails" not in st.session_state:
#     st.session_state.generated_emails = {}

# # UI setup
# st.set_page_config(page_title="Live Leads (Debug)", page_icon="📧", layout="wide")
# st.title("📧 Addend Analytics — Live Leads (Debug mode)")

# # session init
# if "leads" not in st.session_state:
#     st.session_state.leads = []
# if "send_lead" not in st.session_state:
#     st.session_state.send_lead = None
# if "access_token" not in st.session_state:
#     st.session_state.access_token = None
#     st.session_state.user_email = None

# # MSAL login (wrapped)
# try:
#     import msal
#     MSAL_AVAILABLE = True
# except Exception as e:
#     MSAL_AVAILABLE = False
#     log(f"msal import failed: {e}")

# CLIENT_ID = os.getenv("CLIENT_ID")
# TENANT_ID = os.getenv("TENANT_ID")
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}" if TENANT_ID else None
# SCOPE = ["User.Read", "Mail.Send"]

# def get_redirect_uri():
#     hostname = os.getenv("WEBSITE_HOSTNAME")
#     if hostname:
#         return f"https://{hostname}/"
#     return "http://localhost:8501/"

# REDIRECT_URI = get_redirect_uri()

# st.sidebar.header("Microsoft Login")
# if MSAL_AVAILABLE and not st.session_state.access_token:
#     try:
#         app = msal.ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)
#         params = st.query_params
#         code = params.get("code")
#         if code:
#             log("MSAL: authorization code found in query params, exchanging for token.")
#             try:
#                 result = app.acquire_token_by_authorization_code(code, scopes=SCOPE, redirect_uri=REDIRECT_URI)
#             except Exception as e:
#                 log(f"MSAL.acquire_token_by_authorization_code failed: {e}")
#                 result = {}
#             if "access_token" in result:
#                 st.session_state.access_token = result["access_token"]
#                 st.query_params.clear()
#                 # fetch user info safely
#                 try:
#                     me = requests.get("https://graph.microsoft.com/v1.0/me", headers={"Authorization": f"Bearer {st.session_state.access_token}"}, timeout=15)
#                     if me.status_code == 200:
#                         mej = me.json()
#                         st.session_state.user_email = mej.get("mail") or mej.get("userPrincipalName")
#                         log(f"MSAL: logged in as {st.session_state.user_email}")
#                         st.success(f"Logged in as {st.session_state.user_email}")
#                     else:
#                         log(f"MSAL: /me returned {me.status_code}: {me.text}")
#                         st.warning("Logged in but /me returned non-200. Network or permission issue.")
#                 except Exception as e:
#                     tb = traceback.format_exc()
#                     log(f"MSAL: exception calling /me: {e}\n{tb}")
#                     st.warning("Logged in but failed to call Graph /me (network or DNS).")
#             else:
#                 log(f"MSAL: token exchange failed: {result}")
#                 st.error("Login failed (token not returned).")
#                 st.stop()
#         else:
#             auth_url = app.get_authorization_request_url(scopes=SCOPE, redirect_uri=REDIRECT_URI, prompt="select_account")
#             st.markdown(f"[🔐 Click to sign in]({auth_url})")
#             st.stop()
#     except Exception as e:
#         tb = traceback.format_exc()
#         log(f"MSAL flow error: {e}\n{tb}")
#         st.error("MSAL initialization failed. Check logs.")
# else:
#     if st.session_state.access_token:
#         st.sidebar.success(f"Logged in as {st.session_state.user_email}")
#     else:
#         st.sidebar.info("Not logged in - sending disabled.")

# # If a send_lead is set show the full-screen confirm UI
# if st.session_state.send_lead:
#     lead = st.session_state.send_lead
#     st.markdown("## 📨 Confirm & Send Email")
#     st.write(f"**To:** {lead['email']}")
#     st.write(f"**Subject:** {lead['subject']}")
#     wrapper_start = """<div style="max-width:1000px;margin:12px auto;background:#11151c;color:#e6eef6;border-radius:8px;padding:25px;box-shadow:0 3px 20px rgba(0,0,0,0.5);line-height:1.6;font-family:Arial,sans-serif;">"""
#     wrapper_end = "</div>"
#     body_html = lead["body"].replace("<html>", "").replace("</html>", "").replace("<body>", "").replace("</body>", "")
#     st.markdown(wrapper_start + body_html + wrapper_end, unsafe_allow_html=True)
#     confirm_col, cancel_col = st.columns([1,1])
#     if confirm_col.button("✔ Confirm Send"):
#         if not st.session_state.access_token:
#             st.warning("Login required to send mail.")
#         else:
#             ok, status = safe_send_mail(st.session_state.access_token, lead["email"], lead["subject"], lead["body"])
#             if ok:
#                 st.success("📨 Email sent successfully!")
#                 save_last_processed(lead["created"])
#                 if lead["rk"] in st.session_state.generated_emails:
#                     del st.session_state.generated_emails[lead["rk"]]
#                 st.session_state.send_lead = None
#                 st.rerun()
#             else:
#                 st.error(f"Send failed: {status}")
#     if cancel_col.button("✖ Cancel"):
#         st.session_state.send_lead = None
#         st.rerun()

# # ---------------- Load leads ----------------
# last_processed_str = load_last_processed()
# if last_processed_str:
#     try:
#         cutoff_time = datetime.strptime(last_processed_str, "%m/%d/%Y %H:%M:%S")
#         log(f"Loaded last_processed: {last_processed_str}")
#     except Exception as e:
#         log(f"Invalid last_processed format: {last_processed_str}: {e}")
#         cutoff_time = None
# else:
#     cutoff_time = None
#     log("No last_processed found; showing all leads since no cutoff.")

# try:
#     all_leads = fetch_new_leads_since(cutoff_time)
#     log(f"Fetched {len(all_leads)} leads from Azure (after cutoff).")
# except Exception as e:
#     tb = traceback.format_exc()
#     log(f"fetch_new_leads_since EXCEPTION: {e}\n{tb}")
#     all_leads = []

# # do NOT filter leads by generated_emails here — we must keep the lead visible for preview/send
# st.session_state.leads = all_leads

# # ---------------- Display leads ----------------
# st.subheader("Leads (Auto-refreshing every 30 sec)")

# if not st.session_state.leads:
#     st.info("No new leads at the moment...")
# else:
#     for lead in st.session_state.leads:
#         pk = lead.get("PartitionKey")
#         rk = lead.get("RowKey")
#         name = lead.get("Name")
#         email = lead.get("Email")
#         company = lead.get("Company")
#         offer = lead.get("OfferDisplayName")
#         created = lead.get("CreatedTime")

#         col1, col2, col3, col4 = st.columns([3,3,3,1])
#         with col1:
#             st.markdown(f"### {name}")
#             st.write(f"📧 {email}")
#             st.write(f"🏢 {company}")
#         with col2:
#             st.write(f"🧩 Offer: {offer}")
#             st.write(f"📥 Source: {lead.get('LeadSource')}")
#         with col3:
#             st.write(f"⏱ Created: {created}")
#         with col4:
#             if st.button("Send", key=f"send_{rk}"):
#                 # generate or reuse once
#                 if rk not in st.session_state.generated_emails:
#                     subject, body_html = safe_create_mail(rk, name, company, offer)
#                     if not subject or not body_html:
#                         st.error("Failed to generate email. Check Debug / Status below.")
#                         continue
#                     st.session_state.generated_emails[rk] = {"subject": subject, "body": body_html, "email": email, "created": created}
#                 # open preview/send screen
#                 st.session_state.send_lead = {
#                     "rk": rk,
#                     "email": email,
#                     "subject": st.session_state.generated_emails[rk]["subject"],
#                     "body": st.session_state.generated_emails[rk]["body"],
#                     "created": created
#                 }
#                 log(f"Send requested for rk={rk}; opening confirm screen.")
#                 st.rerun()

# # ---------------- Debug / Status panel ----------------
# st.markdown("---")
# st.subheader("Debug / Status")
# st.write(f"Auto-refresh last run at: {datetime.fromtimestamp(st.session_state.last_refresh).strftime('%Y-%m-%d %H:%M:%S')}")
# st.write(f"Leads fetched: {len(st.session_state.leads)}")
# st.write(f"Cached generated emails: {len(st.session_state.generated_emails)}")
# st.write(f"Send lead open: {bool(st.session_state.send_lead)}")
# st.write(f"Access token present: {bool(st.session_state.access_token)}")
# if st.session_state.user_email:
#     st.write(f"Logged in as: {st.session_state.user_email}")

# st.markdown("#### Recent debug logs")
# for line in st.session_state.debug_logs[-30:]:
#     st.text(line)




## ----- main app.py jo deploy krne k liye use kra tha okay 




# import streamlit as st
# import requests
# import os
# import time
# from datetime import datetime
# from dotenv import load_dotenv

# from fetchdata import fetch_new_leads_since
# from generatemail import create_mail
# from state_manager import load_last_processed, save_last_processed

# load_dotenv()

# # ---------------------------------------------------------
# # SAFE AUTO REFRESH — REQUIRED TO FETCH NEW LEADS
# # ---------------------------------------------------------
#   # Soft rerun (keeps UI & state)
# # ---------------------------------------------------------


# # ---------------------------------------------------------
# # STREAMLIT UI SETUP
# # ---------------------------------------------------------
# st.set_page_config(page_title="Leads Email Campaign", page_icon="📧", layout="wide")
# st.title("📧 Addend Analytics - Leads Email Campaign")


# st.write("### 🔄 Refresh Leads")
# if st.button("Refresh Now"):
#     st.rerun()
# # ---------------------------------------------------------
# # SESSION INITIALIZATION
# # ---------------------------------------------------------
# if "leads" not in st.session_state:
#     st.session_state.leads = []

# if "send_lead" not in st.session_state:
#     st.session_state.send_lead = None  # Stores the lead being previewed

# if "generated_emails" not in st.session_state:
#     st.session_state.generated_emails = {}  # Cache emails

# if "access_token" not in st.session_state:
#     st.session_state.access_token = None
#     st.session_state.user_email = None


# # ---------------------------------------------------------
# # MICROSOFT LOGIN
# # ---------------------------------------------------------
# try:
#     import msal
#     MSAL_AVAILABLE = True
# except:
#     MSAL_AVAILABLE = False

# CLIENT_ID = os.getenv("CLIENT_ID")
# TENANT_ID = os.getenv("TENANT_ID")
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
# SCOPE = ["User.Read", "Mail.Send"]

# def get_redirect_uri():
#     hostname = os.getenv("WEBSITE_HOSTNAME")
#     if hostname:
#         return f"https://{hostname}/"
#     return "http://localhost:8501/"

# REDIRECT_URI = get_redirect_uri()

# st.sidebar.header("Microsoft Login")

# # if MSAL_AVAILABLE and not st.session_state.access_token:

# #     app = msal.ConfidentialClientApplication(
# #         CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
# #     )

# #     params = st.query_params
# #     code = params.get("code")

# #     if code:
# #         result = app.acquire_token_by_authorization_code(
# #             code, scopes=SCOPE, redirect_uri=REDIRECT_URI
# #         )
# #         if "access_token" in result:

# #             st.session_state.access_token = result["access_token"]
# #             st.query_params.clear()

# #             # Force refresh so new leads load immediately after login
# #             st.rerun()

# #         else:
# #             st.error("Login failed.")
# #             st.stop()

# #     else:
# #         auth_url = app.get_authorization_request_url(
# #             scopes=SCOPE,
# #             redirect_uri=REDIRECT_URI,
# #             prompt="select_account"
# #         )
# #         st.markdown(f"[🔐 Click to Sign in with Microsoft]({auth_url})")
# #         st.stop()
# # else:
# #     if st.session_state.access_token:
# #         st.sidebar.success(f"Logged in as {st.session_state.user_email}")
# #     else:
# #         st.sidebar.info("Login disabled — cannot send emails.")



# if MSAL_AVAILABLE and not st.session_state.access_token:

#     app = msal.ConfidentialClientApplication(
#         CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
#     )

#     params = st.query_params
#     code = params.get("code")

#     # -------------------------------
#     # FIXED LOGIN FLOW
#     # -------------------------------
#     if code:
#         result = app.acquire_token_by_authorization_code(
#             code, scopes=SCOPE, redirect_uri=REDIRECT_URI
#         )

#         if "access_token" in result:

#             # Save token
#             st.session_state.access_token = result["access_token"]

#             # REMOVE code from URL
#             st.query_params.clear()

#             # Fetch USER PROFILE BEFORE rerun (THIS WAS MISSING!)
#             me = requests.get(
#                 "https://graph.microsoft.com/v1.0/me",
#                 headers={"Authorization": f"Bearer {result['access_token']}"}
#             ).json()

#             st.session_state.user_email = me.get("mail") or me.get("userPrincipalName")

#             st.rerun()

#         else:
#             st.error("Login failed.")
#             st.stop()

#     else:
#         auth_url = app.get_authorization_request_url(
#             scopes=SCOPE,
#             redirect_uri=REDIRECT_URI,
#             prompt="select_account"
#         )
#         st.markdown(f"[🔐 Click to Sign in with Microsoft]({auth_url})")
#         st.stop()


# # ALREADY LOGGED IN
# else:
#     if st.session_state.access_token:
#         st.sidebar.success(f"Logged in as {st.session_state.user_email}")
#     else:
#         st.sidebar.warning("Login disabled — cannot send emails.")



# # ---------------------------------------------------------
# # FULL-SCREEN CONFIRM SEND UI
# # ---------------------------------------------------------
# if st.session_state.send_lead:

#     lead = st.session_state.send_lead

#     st.markdown("## 📨 Confirm & Send Email")

#     st.write(f"**To:** {lead['email']}")
#     st.write(f"**Subject:** {lead['subject']}")

#     wrapper_start = """
#     <div style="
#         max-width: 1000px;
#         margin: 18px auto;
#         background: #11151c;
#         color: #e6eef6;
#         border-radius: 10px;
#         padding: 28px;
#         box-shadow: 0 4px 25px rgba(0,0,0,0.5);
#         line-height: 1.6;
#         font-family: Arial, sans-serif;
#     ">
#     """
#     wrapper_end = "</div>"

#     body_html = lead["body"]
#     body_html = body_html.replace("<html>", "").replace("</html>", "")
#     body_html = body_html.replace("<body>", "").replace("</body>", "")

#     st.markdown(wrapper_start + body_html + wrapper_end, unsafe_allow_html=True)

#     confirm_col, cancel_col = st.columns([1, 1])

#     if confirm_col.button("✔ Confirm Send"):

#         email_msg = {
#             "message": {
#                 "subject": lead["subject"],
#                 "body": {"contentType": "HTML", "content": lead["body"]},
#                 "toRecipients": [{"emailAddress": {"address": lead["email"]}}],
#             },
#             "saveToSentItems": True,
#         }

#         headers = {
#             "Authorization": f"Bearer {st.session_state.access_token}",
#             "Content-Type": "application/json"
#         }

#         resp = requests.post(
#             "https://graph.microsoft.com/v1.0/me/sendMail",
#             headers=headers,
#             json=email_msg
#         )

#         if resp.status_code in (200, 201, 202):
#             st.success("📨 Email sent successfully!")

#             save_last_processed(lead["created"])

#             if lead["rk"] in st.session_state.generated_emails:
#                 del st.session_state.generated_emails[lead["rk"]]

#             st.session_state.send_lead = None
#             st.rerun()

#         else:
#             st.error("❌ Failed to send email.")

#     if cancel_col.button("✖ Cancel"):
#         st.session_state.send_lead = None
#         st.rerun()


# # ---------------------------------------------------------
# # BACKEND LEAD FETCH (EVERY 30 SEC or FIRST LOAD)
# # ---------------------------------------------------------

# last_processed_str = load_last_processed()

# if last_processed_str:
#     cutoff_time = datetime.strptime(last_processed_str, "%m/%d/%Y %H:%M:%S")
# else:
#     today = datetime.now().strftime("%m/%d/%Y")
#     cutoff_time = datetime.strptime(today + " 00:00:00", "%m/%d/%Y %H:%M:%S")

# st.session_state.leads = fetch_new_leads_since(cutoff_time)


# # ---------------------------------------------------------
# # DISPLAY LEADS
# # ---------------------------------------------------------
# st.subheader("Live Leads")

# if not st.session_state.leads:
#     st.info("No new leads available...")
# else:
#     for lead in st.session_state.leads:

#         rk = lead["RowKey"]
#         name = lead["Name"]
#         email = lead["Email"]
#         company = lead["Company"]
#         offer = lead["OfferDisplayName"]
#         created = lead["CreatedTime"]

#         col1, col2, col3, col4 = st.columns([3,3,3,1])

#         with col1:
#             st.markdown(f"### {name}")
#             st.write(f"📧 {email}")
#             st.write(f"🏢 {company}")

#         with col2:
#             st.write(f"🧩 {offer}")
#             st.write(f"📥 {lead['LeadSource']}")

#         with col3:
#             st.write(f"⏱ {created}")

#         with col4:
#             if st.button("Send", key=f"send_{rk}"):

#                 if rk not in st.session_state.generated_emails:
#                     subject, body_html = create_mail(name, company, offer)
#                     st.session_state.generated_emails[rk] = {
#                         "subject": subject,
#                         "body": body_html,
#                         "email": email,
#                         "created": created
#                     }

#                 st.session_state.send_lead = {
#                     "rk": rk,
#                     "email": email,
#                     "subject": st.session_state.generated_emails[rk]["subject"],
#                     "body": st.session_state.generated_emails[rk]["body"],
#                     "created": created
#                 }

#                 st.rerun()


# # ---------------------------------------------------------
# # FOOTER
# # ---------------------------------------------------------
# st.markdown("---")
# st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")





# import streamlit as st
# import requests
# import os
# import time
# from datetime import datetime
# from dotenv import load_dotenv

# from fetchdata import fetch_new_leads_since
# from generatemail import create_mail
# from state_manager import load_last_processed, save_last_processed

# load_dotenv()

# # ---------------------------------------------------------
# # AUTO FETCH EVERY 30 SECONDS (NO UI FLICKER)
# # ---------------------------------------------------------
# if "last_fetch" not in st.session_state:
#     st.session_state.last_fetch = time.time()

# if time.time() - st.session_state.last_fetch >= 30:
#     st.session_state.last_fetch = time.time()
#     st.rerun()
# # ---------------------------------------------------------


# # STREAMLIT UI SETUP
# st.set_page_config(page_title="Live Leads", page_icon="📧", layout="wide")
# st.title("📧 Addend Analytics — Live Leads")


# # ---------------------------------------------------------
# # SESSION INIT
# # ---------------------------------------------------------
# if "access_token" not in st.session_state:
#     st.session_state.access_token = None
#     st.session_state.user_email = None

# if "send_lead" not in st.session_state:
#     st.session_state.send_lead = None

# if "generated_emails" not in st.session_state:
#     st.session_state.generated_emails = {}

# if "leads" not in st.session_state:
#     st.session_state.leads = []


# # ---------------------------------------------------------
# # MICROSOFT LOGIN
# # ---------------------------------------------------------
# try:
#     import msal
#     MSAL_AVAILABLE = True
# except:
#     MSAL_AVAILABLE = False

# CLIENT_ID = os.getenv("CLIENT_ID")
# TENANT_ID = os.getenv("TENANT_ID")
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
# SCOPE = ["User.Read", "Mail.Send"]

# def get_redirect_uri():
#     hostname = os.getenv("WEBSITE_HOSTNAME")
#     if hostname:
#         return f"https://{hostname}/"
#     return "http://localhost:8501/"

# REDIRECT_URI = get_redirect_uri()

# st.sidebar.header("Microsoft Login")

# if MSAL_AVAILABLE and not st.session_state.access_token:

#     app = msal.ConfidentialClientApplication(
#         CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
#     )

#     params = st.query_params
#     code = params.get("code")

#     if code:
#         result = app.acquire_token_by_authorization_code(
#             code, scopes=SCOPE, redirect_uri=REDIRECT_URI
#         )
#         if "access_token" in result:

#             st.session_state.access_token = result["access_token"]
#             st.query_params.clear()

#             st.rerun()

#         else:
#             st.error("Login failed.")
#             st.stop()

#     else:
#         auth_url = app.get_authorization_request_url(
#             scopes=SCOPE,
#             redirect_uri=REDIRECT_URI,
#             prompt="select_account"
#         )
#         st.markdown(f"[🔐 Click to Sign in with Microsoft]({auth_url})")
#         st.stop()

# else:
#     if st.session_state.access_token:
#         st.sidebar.success(f"Logged in as {st.session_state.user_email}")
#     else:
#         st.sidebar.info("Login disabled — cannot send emails.")


# # ---------------------------------------------------------
# # FULL-SCREEN SEND CONFIRMATION
# # ---------------------------------------------------------
# if st.session_state.send_lead:

#     lead = st.session_state.send_lead

#     st.markdown("## 📨 Confirm & Send Email")
#     st.write(f"**To:** {lead['email']}")
#     st.write(f"**Subject:** {lead['subject']}")

#     # Email body clean
#     body = lead["body"]
#     body = body.replace("<html>", "").replace("</html>", "")
#     body = body.replace("<body>", "").replace("</body>", "")

#     st.markdown(
#         f"""
#         <div style="
#             padding:25px;
#             background:#11151c;
#             color:#e6eef6;
#             border-radius:10px;
#             margin-top:20px;
#             box-shadow:0 4px 20px rgba(0,0,0,0.5);
#         ">
#         {body}
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

#     col1, col2 = st.columns(2)

#     if col1.button("✔ Confirm Send"):

#         email_msg = {
#             "message": {
#                 "subject": lead["subject"],
#                 "body": {"contentType": "HTML", "content": lead["body"]},
#                 "toRecipients": [{"emailAddress": {"address": lead["email"]}}],
#             },
#             "saveToSentItems": True,
#         }

#         headers = {
#             "Authorization": f"Bearer {st.session_state.access_token}",
#             "Content-Type": "application/json"
#         }

#         resp = requests.post(
#             "https://graph.microsoft.com/v1.0/me/sendMail",
#             headers=headers,
#             json=email_msg
#         )

#         if resp.status_code in (200, 201, 202):
#             st.success("📨 Email sent successfully!")

#             # update last processed timestamp
#             save_last_processed(lead["created"])

#             st.session_state.send_lead = None
#             st.rerun()

#         else:
#             st.error("❌ Failed to send email.")

#     if col2.button("✖ Cancel"):
#         st.session_state.send_lead = None
#         st.rerun()


# # ---------------------------------------------------------
# # FETCH LEADS — ALWAYS BASED ON TODAY 00:00
# # (state_manager last_processed only blocks PREVIOUS ones)
# # ---------------------------------------------------------
# today = datetime.now().strftime("%m/%d/%Y")
# cutoff_time = datetime.strptime(today + " 00:00:00", "%m/%d/%Y %H:%M:%S")

# # This calls your updated fetchdata.py
# st.session_state.leads = fetch_new_leads_since(cutoff_time)


# # ---------------------------------------------------------
# # DISPLAY LEADS
# # ---------------------------------------------------------
# st.subheader("Live Leads (Auto-refresh every 30 sec)")

# if not st.session_state.leads:
#     st.info("No new leads available...")
# else:
#     for lead in st.session_state.leads:

#         rk = lead["RowKey"]
#         name = lead["Name"]
#         email = lead["Email"]
#         company = lead["Company"]
#         offer = lead["OfferDisplayName"]
#         created = lead["CreatedTime"]

#         col1, col2, col3, col4 = st.columns([3, 3, 3, 1])

#         with col1:
#             st.markdown(f"### {name}")
#             st.write(f"📧 {email}")
#             st.write(f"🏢 {company}")

#         with col2:
#             st.write(f"🧩 {offer}")
#             st.write(f"📥 {lead['LeadSource']}")

#         with col3:
#             st.write(f"⏱ {created}")

#         with col4:
#             if st.button("Send", key=f"send_{rk}"):

#                 # generate email if not cached
#                 if rk not in st.session_state.generated_emails:
#                     subject, body_html = create_mail(name, company, offer)
#                     st.session_state.generated_emails[rk] = {
#                         "subject": subject,
#                         "body": body_html,
#                         "email": email,
#                         "created": created
#                     }

#                 st.session_state.send_lead = {
#                     "rk": rk,
#                     "email": email,
#                     "subject": st.session_state.generated_emails[rk]["subject"],
#                     "body": st.session_state.generated_emails[rk]["body"],
#                     "created": created
#                 }

#                 st.rerun()


# # ---------------------------------------------------------
# # FOOTER
# # ---------------------------------------------------------
# st.markdown("---")
# st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}"






# import streamlit as st
# import requests
# import os
# import time
# from datetime import datetime
# from dotenv import load_dotenv

# from fetchdata import fetch_new_leads_since
# from generatemail import create_mail
# from state_manager import load_last_processed, save_last_processed

# load_dotenv()


# # ---------------------------------------------------------
# # AUTO FETCH EVERY 30 SECONDS (BACKEND ONLY)
# # ---------------------------------------------------------
# if "last_fetch" not in st.session_state:
#     st.session_state.last_fetch = time.time()

# if time.time() - st.session_state.last_fetch >= 30:
#     st.session_state.last_fetch = time.time()
#     st.rerun()
# # ---------------------------------------------------------


# # UI SETUP
# st.set_page_config(page_title="Leads Email Campaign", page_icon="📧", layout="wide")
# st.title("📧 Addend Analytics - Leads Email Campaign")

# # ----------------- MANUAL REFRESH BUTTON -----------------
# st.write("### 🔄 Refresh New Leads")
# if st.button("Refresh Now"):
#     st.rerun()
# # ---------------------------------------------------------

# # ---------------------------------------------------------
# # SESSION INIT
# # ---------------------------------------------------------
# if "access_token" not in st.session_state:
#     st.session_state.access_token = None
#     st.session_state.user_email = None

# if "send_lead" not in st.session_state:
#     st.session_state.send_lead = None

# if "generated_emails" not in st.session_state:
#     st.session_state.generated_emails = {}

# if "leads" not in st.session_state:
#     st.session_state.leads = []


# # ---------------------------------------------------------
# # MICROSOFT LOGIN
# # ---------------------------------------------------------
# try:
#     import msal
#     MSAL_AVAILABLE = True
# except:
#     MSAL_AVAILABLE = False

# CLIENT_ID = os.getenv("CLIENT_ID")
# TENANT_ID = os.getenv("TENANT_ID")
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
# SCOPE = ["User.Read", "Mail.Send"]

# def get_redirect_uri():
#     hostname = os.getenv("WEBSITE_HOSTNAME")
#     if hostname:
#         return f"https://{hostname}/"
#     return "http://localhost:8501/"

# REDIRECT_URI = get_redirect_uri()

# st.sidebar.header("Microsoft Login")


# if MSAL_AVAILABLE and not st.session_state.access_token:

#     app = msal.ConfidentialClientApplication(
#         CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
#     )

#     params = st.query_params
#     code = params.get("code")

#     # -------------------------------
#     # FIXED LOGIN FLOW
#     # -------------------------------
#     if code:
#         result = app.acquire_token_by_authorization_code(
#             code, scopes=SCOPE, redirect_uri=REDIRECT_URI
#         )

#         if "access_token" in result:

#             # Save token
#             st.session_state.access_token = result["access_token"]

#             # REMOVE code from URL
#             st.query_params.clear()

#             # Fetch USER PROFILE BEFORE rerun (THIS WAS MISSING!)
#             me = requests.get(
#                 "https://graph.microsoft.com/v1.0/me",
#                 headers={"Authorization": f"Bearer {result['access_token']}"}
#             ).json()

#             st.session_state.user_email = me.get("mail") or me.get("userPrincipalName")

#             st.rerun()

#         else:
#             st.error("Login failed.")
#             st.stop()

#     else:
#         auth_url = app.get_authorization_request_url(
#             scopes=SCOPE,
#             redirect_uri=REDIRECT_URI,
#             prompt="select_account"
#         )
#         st.markdown(f"[🔐 Click to Sign in with Microsoft]({auth_url})")
#         st.stop()


# # ALREADY LOGGED IN
# else:
#     if st.session_state.access_token:
#         st.sidebar.success(f"Logged in as {st.session_state.user_email}")
#     else:
#         st.sidebar.warning("Login disabled — cannot send emails.")


# # ---------------------------------------------------------
# # FULL-PAGE SEND CONFIRMATION
# # ---------------------------------------------------------
# if st.session_state.send_lead:

#     lead = st.session_state.send_lead

#     st.markdown("## 📨 Confirm & Send Email")

#     st.write(f"**To:** {lead['email']}")
#     st.write(f"**Subject:** {lead['subject']}")

#     # Clean HTML body
#     clean_body = lead["body"]
#     clean_body = clean_body.replace("<html>", "").replace("</html>", "")
#     clean_body = clean_body.replace("<body>", "").replace("</body>", "")

#     st.markdown(
#         f"""
#         <div style="
#             padding:25px;
#             background:#11151c;
#             color:#e6eef6;
#             border-radius:10px;
#             margin-top:20px;
#             box-shadow:0 4px 20px rgba(0,0,0,0.5);
#         ">
#         {clean_body}
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

#     col1, col2 = st.columns(2)

#     # SEND EMAIL
#     if col1.button("✔ Confirm Send"):

#         email_msg = {
#             "message": {
#                 "subject": lead["subject"],
#                 "body": {"contentType": "HTML", "content": lead["body"]},
#                 "toRecipients": [{"emailAddress": {"address": lead["email"]}}],
#             },
#             "saveToSentItems": True,
#         }

#         headers = {
#             "Authorization": f"Bearer {st.session_state.access_token}",
#             "Content-Type": "application/json"
#         }

#         resp = requests.post(
#             "https://graph.microsoft.com/v1.0/me/sendMail",
#             headers=headers,
#             json=email_msg
#         )

#         if resp.status_code in (200, 201, 202):
#             st.success("📨 Email sent successfully!")

#             # Update last processed timestamp
#             save_last_processed(lead["created"])

#             st.session_state.send_lead = None
#             st.rerun()
#         else:
#             st.error("❌ Failed to send email.")

#     # CANCEL
#     if col2.button("✖ Cancel"):
#         st.session_state.send_lead = None
#         st.rerun()


# # ---------------------------------------------------------
# # FETCH LEADS FOR TODAY
# # ---------------------------------------------------------
# today = datetime.now().strftime("%m/%d/%Y")
# cutoff_time = datetime.strptime(today + " 00:00:00", "%m/%d/%Y %H:%M:%S")

# # THIS IS WHERE AUTO-REFRESH WORKS
# st.session_state.leads = fetch_new_leads_since(cutoff_time)


# # ---------------------------------------------------------
# # DISPLAY LEADS
# # ---------------------------------------------------------
# st.subheader("Live Leads")

# if not st.session_state.leads:
#     st.info("No new leads available...")
# else:
#     for lead in st.session_state.leads:

#         rk = lead["RowKey"]
#         name = lead["Name"]
#         email = lead["Email"]
#         company = lead["Company"]
#         offer = lead["OfferDisplayName"]
#         created = lead["CreatedTime"]

#         col1, col2, col3, col4 = st.columns([3, 3, 3, 1])

#         with col1:
#             st.markdown(f"### {name}")
#             st.write(f"📧 {email}")
#             st.write(f"🏢 {company}")

#         with col2:
#             st.write(f"🧩 {offer}")
#             st.write(f"📥 {lead['LeadSource']}")

#         with col3:
#             st.write(f"⏱ {created}")

#         with col4:
#             if st.button("Send", key=f"send_{rk}"):

#                 if rk not in st.session_state.generated_emails:
#                     subject, body_html = create_mail(name, company, offer)
#                     st.session_state.generated_emails[rk] = {
#                         "subject": subject,
#                         "body": body_html,
#                         "email": email,
#                         "created": created
#                     }

#                 st.session_state.send_lead = {
#                     "rk": rk,
#                     "email": email,
#                     "subject": st.session_state.generated_emails[rk]["subject"],
#                     "body": st.session_state.generated_emails[rk]["body"],
#                     "created": created
#                 }

#                 st.rerun()


# # ---------------------------------------------------------
# # FOOTER
# # ---------------------------------------------------------
# st.markdown("---")
# st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")




import os
import time
from datetime import datetime
from dotenv import load_dotenv
import requests
import msal
import traceback

from fetchdata import fetch_new_leads_since
from generatemail import create_mail
from state_manager import load_last_processed, save_last_processed

load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")  # <-- tu apna email yahan set karega

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

SENDER_EMAIL = os.getenv("SENDER_EMAIL")

CHECK_INTERVAL_SECONDS = 60


def get_graph_token():
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in result:
        raise Exception(f"Token error: {result}")
    return result["access_token"]


def send_graph_email(access_token, to_email, subject, body_html):
    headers = {"Authorization": f"Bearer " + access_token, "Content-Type": "application/json"}
    email_msg = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": body_html},
            "toRecipients": [{"emailAddress": {"address": to_email}}],
        },
        "saveToSentItems": True,
    }

    url = f"https://graph.microsoft.com/v1.0/users/{SENDER_EMAIL}/sendMail"
    resp = requests.post(url, headers=headers, json=email_msg)

    # 👉 ADD THIS ONLY
    print("STATUS:", resp.status_code, "| RESPONSE:", resp.text)

    return resp.status_code in (200, 202)



def send_error_email(error_message):
    token = get_graph_token()
    subject = "🚨 Lead Automation Error Alert"
    body = f"""
    <h2>⚠ Automation Error</h2>
    <p><b>Time:</b> {datetime.now()}</p>
    <p><b>Error:</b></p>
    <pre>{error_message}</pre>
    """

    send_graph_email(token, ADMIN_EMAIL, subject, body)


def main_loop():
    print("🚀 Auto Sender Running...")

    while True:
        try:
            last_time = load_last_processed()
            if last_time:
                cutoff = datetime.strptime(last_time, "%m/%d/%Y %H:%M:%S")
            else:
                cutoff = datetime.now()

            leads = fetch_new_leads_since(cutoff)

            if leads:
                token = get_graph_token()
                leads_sorted = sorted(leads, key=lambda x: x["Created_dt"])

                for lead in leads_sorted:
                    subject, body = create_mail(lead["Name"], lead["Company"], lead["OfferDisplayName"])
                    success = send_graph_email(token, lead["Email"], subject, body)

                    if success:
                        save_last_processed(lead["CreatedTime"])
                        print(f"📧 Sent to: {lead['Email']} | {lead['Name']}")
                    else:
                        raise Exception(f"Mail failed for {lead['Email']}")

            else:
                print("⏳ No new leads...")

        except Exception as e:
            error_text = traceback.format_exc()
            print("💥 ERROR:", error_text)
            send_error_email(error_text)

        print(f"😴 Sleeping {CHECK_INTERVAL_SECONDS}s...\n")
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main_loop()

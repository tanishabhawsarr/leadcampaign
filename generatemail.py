# # generate_mail.py
# import json
# import google.generativeai as genai
# import os
# from dotenv import load_dotenv

# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=GEMINI_API_KEY)
# MODEL = "gemini-2.5-flash"

# def create_mail(customer_name, company, offer):
#     """Generate a professional email and subject using Gemini"""
#     prompt = f"""
#     Write a professional outreach email to {customer_name} from {company} 
#     who showed interest in {offer}.
#     1. Include a short, engaging subject line (max 8 words).
#     2. Write the email body in HTML format.
#     3. End with'Sales Team, Addend Analytics LLP'.
#     4. Do not include markdown formatting and add any blank links.
#     Return ONLY a JSON object with keys 'subject' and 'body'.
#     Example:
#     {{
#       "subject": "Follow up on your interest",
#       "body": "<html> ... </html>"
#     }}
#     """

#     model = genai.GenerativeModel(MODEL)
#     response = model.generate_content(prompt)

#     # Safely extract text content
#     text = getattr(response, "text", None)
#     if not text:
#         return f"Regarding your interest in {offer}", "Hello, thank you for your interest."

#     text = text.strip()
#     if text.startswith("```"):
#         text = text.split("```")[-2]
#     text = text.replace("json", "").strip()

#     try:
#         data = json.loads(text)
#         subject = data.get("subject", f"Regarding your interest in {offer}")
#         body = data.get("body", "Hello, thank you for your interest.")
#     except Exception:
#         subject = f"Regarding your interest in {offer}"
#         body = text or "Hello, thank you for your interest."

#     return subject, body



import json
import pandas as pd
from difflib import get_close_matches
import google.generativeai as genai

# Load the Addend Analytics Apps List once
APPS_FILE_PATH = "Addend_Analytics_Apps_List.xlsx"
apps_df = pd.read_excel(APPS_FILE_PATH)

def get_app_details(offer: str):
    """
    Match the offer name to the closest 'App Name' in the Addend Analytics App List
    and return its Features and Description.
    """
    if not offer or apps_df.empty:
        return None

    app_names = apps_df["App Name"].dropna().tolist()
    matches = get_close_matches(offer.strip(), app_names, n=1, cutoff=0.4)

    if not matches:
        return None

    matched_app = matches[0]
    app_row = apps_df.loc[apps_df["App Name"] == matched_app].iloc[0]

    return {
        "matched_app": matched_app,
        "features": str(app_row["Features"]).strip(),
        "description": str(app_row["Description"]).strip()
    }

def create_mail(customer_name, company, offer, MODEL="gemini-2.5-flash"):
    """Generate a personalized professional email and subject using Gemini"""
    
    # Try to fetch app details for the offer
    app_info = get_app_details(offer)
    app_description = ""
    app_features = ""

    if app_info:
        app_description = app_info["description"]
        app_features = app_info["features"]

    # Build dynamic part of the prompt
    optional_app_details = ""
    if app_description or app_features:
        optional_app_details = f"""
        App Description:
        {app_description}

        Key Features:
        {app_features}
        """

    # Construct the final AI prompt
    prompt = f"""
    Write a professional outreach email to {customer_name} from {company}, 
    who explored or showed interest in the {offer} on Microsoft AppSource.

    {optional_app_details}

    Follow these exact instructions:
    1. Start the email by thanking the customer for exploring or trying the report.
       Example: "Thank you so much for exploring our {offer}. I'd love to hear your experience 
       and if you need any assistance with it."

    2. Write the rest of the email in a friendly, conversational yet professional tone.
       - Briefly restate the value or benefits of the {offer}.
       - If app details are available, use them naturally to describe what the report helps achieve.
       - Mention 3–4 bullet points (if relevant) highlighting what the report or product enables.
       - Optionally, suggest a quick walkthrough or discussion for further assistance.

    3. End the email with this exact signature block:
       Best regards,<br>
       Kirti Sharma<br>
       +1 (470) 686-6644<br>
       <a href="https://addendanalytics.com/" target="_blank" style="color:#0078d4; text-decoration:none;">Addend Analytics</a><br>
       Microsoft Solutions Partner

      4. Include a short, friendly, and professional subject line (maximum 8 words).
       Use **value-driven and benefit-focused** phrasing. 
       The tone should sound informative and helpful, not salesy or like a follow-up.
       Examples of ideal subject lines:
         • "Task Visibility & Team Coordination with Microsoft Planner Reporting"
         • "Unlock the Full Potential of Your Task Management Data"
         • "Enhancing Project and Task Management Insights"
         • "Discover Actionable Insights from Your Planner Reports"
         • "Simplify Task Tracking with Powerful Reporting"

       - Avoid terms like “Follow-up,” “Next Steps,” or anything implying tracking or urgency.

    5. Write the email body in valid HTML format (not Markdown).
       - Use <p> tags for paragraphs (no multiple <br> tags).
       - Maintain consistent spacing between paragraphs with:
         <p style="line-height:1.4; margin-bottom:10px;">...</p>

    6. Do not include any links, placeholders, or markdown formatting.

    7. Return ONLY a JSON object with this structure:
    {{
        "subject": "Your engaging subject here",
        "body": "<html>...HTML formatted email body...</html>"
    }}

    8. Use compact inline CSS for spacing: 
   - paragraph line-height: 1.4
   - paragraph bottom margin: 10px
   - list item margin: 4px

    9. Ensure the email looks clean in Outlook and Microsoft Teams.

    """

    # Generate response from Gemini
    model = genai.GenerativeModel(MODEL)
    response = model.generate_content(prompt)

    # Safely extract text content
    text = getattr(response, "text", None)
    if not text:
        return f"Regarding your interest in {offer}", "Hello, thank you for your interest."

    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[-2]
    text = text.replace("json", "").strip()

    try:
        data = json.loads(text)
        subject = data.get("subject", f"Regarding your interest in {offer}")
        body = data.get("body", "Hello, thank you for your interest.")
    except Exception:
        subject = f"Regarding your interest in {offer}"
        body = text or "Hello, thank you for your interest."

    return subject, body

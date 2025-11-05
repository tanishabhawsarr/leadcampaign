# generate_mail.py
import json
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.5-flash"

def create_mail(customer_name, company, offer):
    """Generate a professional email and subject using Gemini"""
    prompt = f"""
    Write a professional outreach email to {customer_name} from {company} 
    who showed interest in {offer}.
    1. Include a short, engaging subject line (max 8 words).
    2. Write the email body in HTML format.
    3. End with'Sales Team, Addend Analytics LLP'.
    4. Do not include markdown formatting and add any blank links.
    Return ONLY a JSON object with keys 'subject' and 'body'.
    Example:
    {{
      "subject": "Follow up on your interest",
      "body": "<html> ... </html>"
    }}
    """

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
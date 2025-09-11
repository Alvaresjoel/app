import os
import smtplib
from email.message import EmailMessage
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv


load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")  # your Gmail
GMAIL_APP_PASS = os.getenv("GMAIL_APP_PASS")  # app password you generated
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))  # Gmail uses STARTTLS on port 587


# Function to extract supervisor's name from email address
def extract_supervisor_name(email: str) -> str:
    # Extract the part before '@' in the email address and capitalize it.
    supervisor_name = email.split('@')[0]
    supervisor_name = supervisor_name.replace(".", " ").title()
    return supervisor_name


# Function to send email
def send_email(to_email: str):
    # Extract the supervisor's name from the email
    supervisor_name = extract_supervisor_name(to_email)

    # Prepare the email content with the supervisor's name
    html_content = f"""
    <html>
        <body>
            <h2 style="color: #2a9df4;">Weekly Report</h2>
            <p>Hi {supervisor_name},</p>

            <p>Please find the attached <strong>Weekly Report</strong> for this week.</p>

            <footer>
                <p>Best regards, <br>
                   <strong>TimelyAI Creative Capsule</strong><br>
                </p>
            </footer>
        </body>
    </html>
    """

    # Setup the email message
    msg = EmailMessage()
    msg["Subject"] = "Weekly Report"
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    msg.set_content("This is a test email sent from FastAPI using Gmail App Password.")
    msg.add_alternative(html_content, subtype="html")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # upgrade to secure connection
            server.login(GMAIL_USER, GMAIL_APP_PASS)
            server.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")

import os
import logging
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv
load_dotenv()
BREVO_API_KEY = os.getenv("BREVO_API_KEY")

# Brevo API client
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = BREVO_API_KEY
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

# Send Confirmation Email
def send_confirmation_email(recipient_name: str, recipient_email: str) -> bool:
    if not BREVO_API_KEY:
        logging.error("BREVO_API_KEY is not set. Cannot send email.")
        return False

    try:
        with open('email_template.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        html_content = html_content.replace('{{ name }}', recipient_name)
        sender = {"name": "TrendyTracker", "email": "codewithabhishek2026@gmail.com"}
        to = [{"email": recipient_email, "name": recipient_name}]
        subject = "Welcome to TrendyTracker!"
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to, 
            sender=sender, 
            subject=subject, 
            html_content=html_content
        )
        api_instance.send_transac_email(send_smtp_email)
        logging.info(f"Confirmation email sent successfully to {recipient_email}")
        return True
    except FileNotFoundError:
        logging.error("email_template.html not found.")
        return False
    except ApiException as e:
        logging.error(f"Brevo API exception when sending email to {recipient_email}: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred in send_confirmation_email: {e}")
        return False
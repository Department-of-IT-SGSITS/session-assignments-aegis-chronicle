import base64
from datetime import datetime
import os
import logging
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from analysis_utils import generate_wordcloud_image
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv
load_dotenv()

# Brevo API client
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = BREVO_API_KEY
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

# Send Daily Digest to All Subscribers
def send_digest_to_all(subscribers: list, articles: list):
    if not BREVO_API_KEY:
        logging.error("BREVO_API_KEY is not set. Cannot send digest.")
        return False
    if not subscribers:
        logging.info("No subscribers to send digest to. Skipping.")
        return True
    if not articles:
        logging.info("No articles for today's digest. Skipping.")
        return True

    try:
        wordcloud_image_bytes = generate_wordcloud_image(articles)
        wordcloud_b64 = base64.b64encode(wordcloud_image_bytes).decode()

        df = pd.DataFrame(articles)
        analyzer = SentimentIntensityAnalyzer()
        df['sentiment'] = df['description'].fillna('').apply(lambda x: analyzer.polarity_scores(x)['compound'])
        df = df.sort_values(by='sentiment', ascending=False).head(10)

        articles_html = "<ul>"
        for _, row in df.iterrows():
            source = (row.get("source") or {}).get("name", "N/A")
            articles_html += f"<li><a href='{row['url']}'>{row['title']}</a><span>Source: {source}</span></li>"
        articles_html += "</ul>"

        with open('digest.html', 'r', encoding='utf-8') as f:
            html_template = f.read()

        sender = {"name": "TrendyTracker", "email": "codewithabhishek2026@gmail.com"}
        subject = f"Your Daily News Digest - {datetime.now().strftime('%B %d, %Y')}"

        for name, email in subscribers:
            personalized_html = (
                html_template
                .replace("{{ params.name }}", name)
                .replace("{{ params.articles_html }}", articles_html)
            )

            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                sender=sender,
                subject=subject,
                to=[{"email": email, "name": name}],
                html_content=personalized_html,
                attachment=[{
                    "content": wordcloud_b64,
                    "name": "wordcloud.png",
                    "contentType": "image/png",
                    "cid": "wordcloudimage"
                }]
            )
            
            api_instance.send_transac_email(send_smtp_email)

        logging.info(f"Successfully sent digest to {len(subscribers)} subscribers.")
        return True

    except Exception as e:
        logging.error(f"An unexpected error occurred in send_digest_to_all: {e}")
        return False

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
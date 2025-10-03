import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def fetch_top_headlines(max_articles):
    if not NEWS_API_KEY:
        logging.error("NEWS_API_KEY is not configured.")
        return []

    url = (
        f"https://newsapi.org/v2/top-headlines?"
        f"language=en&"
        f"pageSize={min(max_articles, 100)}&"
        f"apiKey={NEWS_API_KEY}"
    )
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        if data.get("status") == "ok":
            return data.get("articles", [])
        else:
            logging.warning(f"API Error: {data.get('message', 'Unknown error')}")
            return []
    except requests.exceptions.RequestException as e:
        logging.error(f"NewsAPI request failed: {e}")
        return []
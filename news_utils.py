import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Fetch news articles based on query and date range
@st.cache_data(ttl=3600)
def fetch_news(query, max_articles, from_date, to_date, exact_match=False):
    if not NEWS_API_KEY:
        st.error("NEWS_API_KEY is not configured.")
        return []
    if not query:
        return []

    # If exact_match is True, wrap the query in double quotes
    search_query = f'"{query}"' if exact_match else query
        
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={search_query}&"
        f"from={from_date.strftime('%Y-%m-%d')}&"
        f"to={to_date.strftime('%Y-%m-%d')}&"
        f"pageSize={min(max_articles, 100)}&"
        f"language=en&"
        f"sortBy=publishedAt&"
        f"apiKey={NEWS_API_KEY}"
    )
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        if data.get("status") == "ok":
            return data.get("articles", [])
        else:
            st.warning(f"API Error: {data.get('message', 'Unknown error')}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"NewsAPI request failed: {e}")
        return []

# Fetch top headlines
@st.cache_data(ttl=1800)
def fetch_top_headlines(max_articles):
    if not NEWS_API_KEY:
        st.error("NEWS_API_KEY is not configured.")
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
            st.warning(f"API Error: {data.get('message', 'Unknown error')}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"NewsAPI request failed: {e}")
        return []
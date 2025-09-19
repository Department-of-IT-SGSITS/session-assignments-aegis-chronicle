import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from collections import Counter
import requests
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging
from db_utils import init_db, email_exists, add_subscriber
# from email_utils import send_confirmation_email

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
if not NEWS_API_KEY:
    st.error("NEWS_API_KEY environment variable not set! Please check your .env file.")
    st.stop()
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

st.set_page_config(layout='wide')
st.title("TrendyTracker: News Trend Analyzer")

@st.cache_data(ttl=3600)
def fetch_news(query, max_articles, from_date, to_date):
    if not query:
        return []
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={query}&"
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

@st.cache_data(ttl=1800)
def fetch_top_headlines(max_articles):
    url = (
        f"https://newsapi.org/v2/top-headlines?"
        f"language=en&"
        f"pageSize={min(max_articles,100)}&"
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

with st.sidebar:
    st.header("Controls")
    mode = st.radio("Mode", ["Top Headlines", "Search"], index=0)
    query = st.text_input("Search Topic", "India", disabled=(mode == "Top Headlines"))
    num_articles = st.slider("Articles to Analyze", min_value=10, max_value=100, value=50, step=5)
    default_start = datetime.now() - timedelta(days=14)
    default_end = datetime.now()
    date_range = st.date_input(
        "Date Range (Max 30 days)",
        value=[default_start, default_end],
        max_value=datetime.now(),
        min_value=datetime.now() - timedelta(days=29),
        disabled=(mode == "Top Headlines")
    )
    st.markdown("---")
    st.caption("Analysis Options")
    use_vader = st.checkbox("Use VADER Sentiment", True)
    show_topics = st.checkbox("Show Topic Modeling", True)

def run_analysis(articles, label):
    if not articles:
        st.error("No articles found. Try switching modes or adjusting filters.")
        st.stop()
    data = [{
        "Date": a.get("publishedAt"),
        "Source": (a.get("source") or {}).get("name"),
        "Title": a.get("title"),
        "Content": a.get("description") or "",
        "URL": a.get("url")
    } for a in articles if a.get("title")]
    df = pd.DataFrame(data)
    if df.empty:
        st.error("No usable articles returned.")
        st.stop()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.tz_localize(None).dt.date
    analyzer = SentimentIntensityAnalyzer()
    df["Sentiment"] = df["Content"].astype(str).apply(lambda x: analyzer.polarity_scores(x)["compound"] if use_vader else TextBlob(x).sentiment.polarity)
    df["SentimentLabel"] = df["Sentiment"].apply(lambda s: "Positive" if s > 0.1 else "Negative" if s < -0.1 else "Neutral")
    st.header(f"Analysis: {label}")
    trend_data = df.groupby('Date', dropna=True).size().reset_index(name='Article Count')
    if not trend_data.empty:
        fig_timeline = px.line(trend_data, x='Date', y='Article Count', title='Number of Articles Over Time', markers=True)
        st.plotly_chart(fig_timeline, use_container_width=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top Keywords")
        text = " ".join(df["Title"].fillna("").tolist() + df["Content"].fillna("").tolist())
        custom_stopwords = set(str(label).lower().split()) | stop_words
        wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=custom_stopwords).generate(text) if text.strip() else WordCloud(width=800, height=400, background_color='white').generate("news world update")
        fig_wc, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig_wc)
    with col2:
        st.subheader("Sentiment Breakdown")
        sentiment_counts = df["SentimentLabel"].value_counts()
        fig_pie = px.pie(
            sentiment_counts, 
            values=sentiment_counts.values, 
            names=sentiment_counts.index, 
            title='Overall Sentiment Distribution', 
            color=sentiment_counts.index,
            color_discrete_map={
                "Positive": "#2ecc71",
                "Negative": "#e74c3c",
                "Neutral":  "#95a5a6"
            }
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    if show_topics:
        st.subheader("Detected Topics (LDA)")
        try:
            vectorizer = CountVectorizer(max_df=0.9, min_df=2, stop_words='english')
            dtm = vectorizer.fit_transform(df["Content"].astype(str))
            if dtm.shape[0] > 0 and dtm.shape[1] > 0:
                lda = LatentDirichletAllocation(n_components=3, random_state=42)
                lda.fit(dtm)
                vocab = vectorizer.get_feature_names_out()
                for idx, topic in enumerate(lda.components_):
                    top_words = [vocab[i] for i in topic.argsort()[-5:]]
                    st.write(f"**Topic #{idx + 1}:** {', '.join(top_words)}")
            else:
                st.warning("Not enough content to perform topic modeling.")
        except ValueError:
            st.warning("Not enough content to perform topic modeling.")
    st.subheader("Source Comparison")
    source_stats = df.groupby("Source", dropna=True).agg(Articles=("Content", "count"), Avg_Sentiment=("Sentiment", "mean")).sort_values("Articles", ascending=False).head(10)
    st.dataframe(source_stats.style.background_gradient(cmap="viridis", subset=["Articles"]).format({"Avg_Sentiment": "{:.2f}"}))
    st.subheader("Top Positive & Negative Headlines")
    col3, col4 = st.columns(2)
    with col3:
        st.write("Top 5 Positive Headlines")
        positive_df = df[df["Sentiment"] > 0.3].sort_values("Sentiment", ascending=False).head(5)
        st.table(positive_df[["Source", "Title"]])
    with col4:
        st.write("Top 5 Negative Headlines")
        negative_df = df[df["Sentiment"] < -0.1].sort_values("Sentiment", ascending=True).head(5)
        st.table(negative_df[["Source", "Title"]])
    st.subheader("All Collected Articles")
    st.dataframe(df[["Date", "Source", "Title", "SentimentLabel"]])
    st.download_button(
        label="Download Full Analysis (CSV)",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=f"news_analysis_{str(label).replace(' ', '_')}.csv",
        mime="text/csv"
    )

if "initialized" not in st.session_state:
    st.session_state.initialized = True

if mode == "Top Headlines":
    articles = fetch_top_headlines(num_articles)
    run_analysis(articles, "Top Headlines (Global)")
else:
    if not isinstance(date_range, (list, tuple)) or len(date_range) != 2:
        st.warning("Select a valid date range.")
        st.stop()
    start_date, end_date = date_range
    if not query:
        st.warning("Please enter a search topic.")
        st.stop()
    articles = fetch_news(query, num_articles, start_date, end_date)
    run_analysis(articles, f"'{query}'")

st.markdown("---")
init_db()
st.header("Subscribe for Nightly News Digest")

with st.form("subscribe_form", clear_on_submit=True):
    name = st.text_input("Name", placeholder="Your Name")
    email = st.text_input("Email", placeholder="your@email.com")
    submitted = st.form_submit_button("Subscribe")

    if submitted:
        logging.info(f"Subscription attempt: Name='{name}', Email='{email}'")
        if name and email:
            if email_exists(email):
                st.warning("This email is already subscribed!")
            else:
                if add_subscriber(name, email):
                    st.success(f"Thank you, {name}! A confirmation has been sent to {email}.")
                    logging.info(f"Successfully added subscriber {email}")
                    # send_confirmation_email(email)
                else:
                    st.error("Could not complete subscription. Please try again.")
        else:
            st.error("Please provide both a name and an email address.")
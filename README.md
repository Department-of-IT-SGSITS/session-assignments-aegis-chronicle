# TrendyTracker: News Trend Analyzer
## Project Description
This project is a cloud-based system designed for the analysis of trending news topics across different regions and time periods. By utilizing data from public news APIs, the platform employs Natural Language Processing (NLP) techniques to extract, monitor, and analyze emerging topics of interest. The system aims to provide researchers, media analysts, and policymakers with a tool to track evolving discussions in near real-time through an interactive visual dashboard.

The primary goal is to create a scalable platform that automates the analysis of the massive volume of news data, moving beyond the limitations of traditional manual monitoring.


## Key Features

- **Live Data Ingestion**: Fetches real-time news articles from external APIs.
- **NLP Analysis**: Processes article content using NLP methods like Latent Dirichlet Allocation (LDA) for topic modeling and VADER for sentiment analysis.
- **Trend and Sentiment Monitoring**: Identifies trending topics and tracks their sentiment orientation over time.
- **Interactive Dashboard**: A visual dashboard built with Streamlit provides users with interactive insights through timelines, word clouds, sentiment distribution pie charts, and topic clustering.
- **Custom Search**: Allows users to query articles by topic, keyword, and a specified date range.
- **Subscription Service**: Users can subscribe with their name and email to receive a "Daily News Digest".
- **Data Export**: Provides the ability to download the full analysis results as a CSV file.

## System Architecture
The system is built on a multi-layered architecture to handle data fetching, processing, and visualization efficiently.

- **Frontend / Visualization Layer**: A Streamlit dashboard serves as the user interface, displaying interactive plots and analysis results.
- **Data Source Layer**: Uses NewsAPI to fetch real-time news articles.
- **Processing Layer**: A backend layer where NLP techniques are applied, including tokenization, stopword removal, LDA for topic modeling, and VADER for sentiment analysis.
- **Storage Layer**: A PostgreSQL database hosted on Cloud SQL is used to store subscriber information for the daily digest service.
- **Mailing Service**: Brevo is integrated to send confirmation emails to new subscribers and to distribute the daily news digests.
- **Backend Microservice**: A Cloud Run Function (digest-service) is responsible for fetching subscriber data, processing the latest news, and sending the daily digest.
- **Scheduling**: A Cloud Scheduler job triggers the Cloud Run function daily to automate the digest delivery.


## Technology Stack
- **Software & Libraries**
  - **Programming Language**: Python 3.10+ 
  - **Web Framework**: Streamlit 
  - **Data Manipulation**: Pandas, NumPy
  - **Visualization**: Matplotlib, Plotly
  - **NLP**: NLTK, Scikit-learn, VADER, TextBlob, WordCloud 
  - **Database Connector**: psycopg2 
  - **Web Server**: Flask, gunicorn 
  - **Environment Management**: pip, dotenv 

- **Cloud Services & APIs**
  - **News Data**: NewsAPI 
  - **Mailing**: Brevo 
  - **Hosting & Compute**: Google Cloud Run 
  - **Scheduling**: Google Cloud Scheduler 

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/vlCa2ep6)

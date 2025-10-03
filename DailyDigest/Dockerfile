FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /service

# Copy requirements from the project root and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader stopwords

# Copy the HEADLESS utility modules and other shared utils from the project root
COPY db_utils_headless.py .
COPY news_utils_headless.py .
COPY analysis_utils.py .
COPY email_utils.py .

# Rename the headless utility modules to their expected names
RUN mv db_utils_headless.py db_utils.py
RUN mv news_utils_headless.py news_utils.py

# Copy the service-specific code and templates from the DailyDigest folder
COPY DailyDigest/digest_sender.py DailyDigest/digest.html ./

# Run the service using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "digest_sender:app"]
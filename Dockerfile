FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader stopwords

# Copy the rest of the application files into the container
COPY . .

# Expose the port of Streamlit
EXPOSE 8501

# Command to run when the container starts
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT:-8501} --server.enableCORS=false"]
import os
import logging
from flask import Flask, jsonify

# The Dockerfile renames the headless files, so imports remain clean
from db_utils import fetch_subscribers
from email_utils import send_digest_to_all
from news_utils import fetch_top_headlines

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', force=True)

@app.route('/send-digest', methods=['POST'])
def handle_digest_request():
    logging.info("Authorized digest request received. Starting process...")
    try:
        logging.info("Fetching top headlines...")
        articles = fetch_top_headlines(50)
        if not articles:
            logging.warning("No articles found to generate digest.")
            return jsonify({"status": "complete", "message": "No articles found."}), 200
        logging.info(f"Successfully fetched {len(articles)} articles.")

        logging.info("Fetching subscribers from database...")
        subscribers = fetch_subscribers()
        if not subscribers:
            logging.warning("No subscribers to send digest to.")
            return jsonify({"status": "complete", "message": "No subscribers."}), 200
        logging.info(f"Successfully fetched {len(subscribers)} subscribers.")

        logging.info("Preparing and sending digest email to all subscribers...")
        success = send_digest_to_all(subscribers, articles)
        
        if success:
            logging.info("Digest sending process completed successfully.")
            return jsonify({"status": "success", "message": f"Digest sent to {len(subscribers)} subscribers."}), 200
        else:
            logging.error("Digest sending process failed.")
            return jsonify({"status": "error", "message": "Failed to send digest."}), 500

    except Exception as e:
        logging.error(f"Critical error in digest request handler: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "An internal server error occurred."}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
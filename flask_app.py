import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

logging.basicConfig(
    filename='flask.log', 
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.route('/summarize', methods=['POST'])
def summarize():
    app.logger.info("Summarization request received.")
    
    try:
        app.logger.debug("Attempting to parse JSON data.")
        data = request.get_json()
        text = data.get("text")

        if not text:
            app.logger.warning("No text provided in request")
            return jsonify({"error": "Text input is required"}), 400

        summary = "This is a mock summary of the text."

        app.logger.info("Text summarized successfully.")
        return jsonify({"summary": summary}), 200
    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, jsonify
from summarizer import summarize_text
from fastapi import FastAPI
from fpdf import FPDF
import sqlite3
from pathlib import Path
import threading
import uvicorn

# Flask App for Summarization
flask_app = Flask(__name__)

@flask_app.route('/summarize', methods=['POST'])
def summarize():
    try:
        # Retrieve the text from the incoming JSON body
        data = request.get_json()
        text = data.get("text")

        if not text:
            return jsonify({"error": "Text input is required"}), 400

        # Call the summarizer function
        summary = summarize_text(text)

        return jsonify({"summary": summary}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# FastAPI App for PDF Export
fastapi_app = FastAPI()

def get_db_connection():
    conn = sqlite3.connect('meetings.db')
    conn.row_factory = sqlite3.Row  # To access columns as dictionary keys
    return conn

@fastapi_app.get("/export/{meeting_id}")
async def export_pdf(meeting_id: int):
    # Connect to the SQLite database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query meeting details
    cursor.execute("SELECT * FROM meetings WHERE id=?", (meeting_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return {"error": "Meeting not found"}

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.cell(200, 10, txt="Meeting Summary", ln=True, align='C')
    pdf.ln(10)

    # Meeting Summary
    pdf.multi_cell(0, 10, txt=f"Summary: {row['summary']}")

    # Action Items
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt=f"Action Items: {row['action_items']}")

    # Decisions
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt=f"Decisions: {row['decisions']}")

    # Full Transcript (optional)
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt=f"Full Transcript: {row['transcript']}")

    # Save PDF to static directory
    pdf_output_path = Path(f"static/meeting_{meeting_id}_summary.pdf")
    pdf.output(str(pdf_output_path))

    return {"message": "PDF generated successfully!", "pdf_link": str(pdf_output_path)}

# Run Flask App
def run_flask():
    flask_app.run(debug=True, use_reloader=False)

# Run FastAPI App
def run_fastapi():
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8001)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    fastapi_thread = threading.Thread(target=run_fastapi)

    flask_thread.start()
    fastapi_thread.start()

    flask_thread.join()
    fastapi_thread.join()

from flask import Flask, request, jsonify
from summarizer import summarize_text
from fastapi import FastAPI
from fpdf import FPDF
import sqlite3
from pathlib import Path
import threading
import uvicorn


flask_app = Flask(__name__)

@flask_app.route('/summarize', methods=['POST'])
def summarize():
    try:
      
        data = request.get_json()
        text = data.get("text")

        if not text:
            return jsonify({"error": "Text input is required"}), 400

       
        summary = summarize_text(text)

        return jsonify({"summary": summary}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


fastapi_app = FastAPI()

def get_db_connection():
    conn = sqlite3.connect('meetings.db')
    conn.row_factory = sqlite3.Row  
    return conn

@fastapi_app.get("/export/{meeting_id}")
async def export_pdf(meeting_id: int):

    conn = get_db_connection()
    cursor = conn.cursor()

 
    cursor.execute("SELECT * FROM meetings WHERE id=?", (meeting_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return {"error": "Meeting not found"}

    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    
    pdf.cell(200, 10, txt="Meeting Summary", ln=True, align='C')
    pdf.ln(10)

    
    pdf.multi_cell(0, 10, txt=f"Summary: {row['summary']}")

    
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt=f"Action Items: {row['action_items']}")

    
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt=f"Decisions: {row['decisions']}")

  
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt=f"Full Transcript: {row['transcript']}")

    
    pdf_output_path = Path(f"static/meeting_{meeting_id}_summary.pdf")
    pdf.output(str(pdf_output_path))

    return {"message": "PDF generated successfully!", "pdf_link": str(pdf_output_path)}


def run_flask():
    flask_app.run(debug=True, use_reloader=False)


def run_fastapi():
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8001)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    fastapi_thread = threading.Thread(target=run_fastapi)

    flask_thread.start()
    fastapi_thread.start()

    flask_thread.join()
    fastapi_thread.join()

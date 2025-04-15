from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import os
import sqlite3
from pathlib import Path
from fpdf import FPDF

from transcriber import transcribe_audio
from summarizer import summarize_text

UPLOAD_DIR = "uploads"
STATIC_DIR = "static"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def extract_sections(summary_text: str):
    sections = {"summary": "", "action_items": "", "decisions": ""}
    current = None

    for line in summary_text.splitlines():
        line = line.strip()
        if line.lower().startswith("### summary"):
            current = "summary"
        elif line.lower().startswith("### action items"):
            current = "action_items"
        elif line.lower().startswith("### key decisions"):
            current = "decisions"
        elif current and line:
            sections[current] += line + "\n"

    return sections


def get_meetings_db_connection():
    conn = sqlite3.connect('meetings.db')
    conn.row_factory = sqlite3.Row
    return conn


def insert_meeting(filename: str, transcript: str, summary: str, action_items: str = "", decisions: str = "") -> int:
    conn = get_meetings_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO meetings (transcript, summary, action_items, decisions) VALUES (?, ?, ?, ?)",
        (transcript, summary, action_items, decisions)
    )
    conn.commit()
    meeting_id = cursor.lastrowid
    conn.close()
    return meeting_id


@app.post("/process_meeting")
async def process_meeting(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())

    try:
        transcript = transcribe_audio(file_location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

    try:
        structured_output = summarize_text(transcript)
        sections = extract_sections(structured_output)
        summary = sections["summary"].strip()
        action_items = sections["action_items"].strip()
        decisions = sections["decisions"].strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

    meeting_id = insert_meeting(file.filename, transcript, summary, action_items, decisions)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Meeting Summary", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Summary:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, summary)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Action Items:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, action_items)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Decisions:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, decisions)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Transcript:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, transcript)

    pdf_output_path = Path(os.path.join(STATIC_DIR, f"meeting_{meeting_id}_summary.pdf"))
    pdf.output(str(pdf_output_path))

    return JSONResponse(content={
        "meeting_id": meeting_id,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "decisions": decisions,
        "pdf_link": f"/static/meeting_{meeting_id}_summary.pdf"
    })


@app.get("/export/{meeting_id}")
async def export_pdf(meeting_id: int):
    conn = get_meetings_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meetings WHERE id=?", (meeting_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Meeting not found")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Meeting Summary", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Summary:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, row['summary'])
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Action Items:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, row['action_items'])
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Decisions:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, row['decisions'])
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Transcript:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, row['transcript'])

    pdf_output_path = Path(os.path.join(STATIC_DIR, f"meeting_{meeting_id}_summary.pdf"))
    pdf.output(str(pdf_output_path))

    return {
        "message": "PDF generated successfully!",
        "pdf_link": f"/static/meeting_{meeting_id}_summary.pdf"
    }

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
import sqlite3
from pathlib import Path
from fpdf import FPDF

# Import functions from your existing modules
from transcriber import transcribe_audio
from summarizer import summarize_text

# Initialize FastAPI app
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from the STATIC_DIR directory
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Set up directories
UPLOAD_DIR = "uploads"
STATIC_DIR = "static"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Database helper for meetings (for transcribed + summarized meetings)
def get_meetings_db_connection():
    # We assume that your meetings.db has a table called `meetings` with columns:
    # id, transcript, summary, action_items, decisions
    conn = sqlite3.connect('meetings.db')
    conn.row_factory = sqlite3.Row  # to access rows as dicts
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

# -------------------------------
# Endpoint: Process Meeting (Upload → Transcribe → Summarize → Store)
# -------------------------------
@app.post("/process_meeting")
async def process_meeting(file: UploadFile = File(...)):
    # Save the uploaded audio file to the UPLOAD_DIR
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    # Transcribe the audio using your transcriber (supports multilingual input)
    try:
        transcript = transcribe_audio(file_location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    
    # Summarize the transcript using your summarizer
    try:
        summary = summarize_text(transcript)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")
    
    # Insert into meetings database (action items & decisions left empty, can be enhanced later)
    meeting_id = insert_meeting(file.filename, transcript, summary, action_items="", decisions="")

    return JSONResponse(content={
        "meeting_id": meeting_id,
        "transcript": transcript,
        "summary": summary,
        "pdf_link": f"/static/meeting_{meeting_id}_summary.pdf"
    })

# -------------------------------
# Endpoint: Export Meeting PDF Report
# -------------------------------
@app.get("/export/{meeting_id}")
async def export_pdf(meeting_id: int):
    conn = get_meetings_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meetings WHERE id=?", (meeting_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Generate PDF using FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.cell(200, 10, txt="Meeting Summary", ln=True, align='C')
    pdf.ln(10)
    
    # Meeting Summary Section
    pdf.multi_cell(0, 10, txt=f"Summary: {row['summary']}")
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt=f"Action Items: {row['action_items']}")
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt=f"Decisions: {row['decisions']}")
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt=f"Transcript: {row['transcript']}")

    pdf_output_path = Path(os.path.join(STATIC_DIR, f"meeting_{meeting_id}_summary.pdf"))
    pdf.output(str(pdf_output_path))

    return {"message": "PDF generated successfully!", "pdf_link": f"/static/meeting_{meeting_id}_summary.pdf"}

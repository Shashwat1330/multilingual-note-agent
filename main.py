from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
from transcriber import transcribe_audio

app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    file_location = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_location, "wb") as f:
        f.write(await file.read())

    try:
        transcript = transcribe_audio(file_location)
        return JSONResponse(content={"transcript": transcript})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
from fastapi import FastAPI, File, UploadFile
from transcriber import transcribe_audio
import shutil
import os

app = FastAPI()

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # Save uploaded file
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Run transcription
    text = transcribe_audio(temp_file_path)

    # Clean up temp file
    os.remove(temp_file_path)

    return {"transcription": text}
from fastapi import FastAPI, UploadFile, File
from transcriber import transcribe_audio
from summarizer import summarize_text

app = FastAPI()

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    audio_path = f"temp_{file.filename}"
    
    with open(audio_path, "wb") as f:
        f.write(await file.read())

    transcription = transcribe_audio(audio_path)
    summary = summarize_text(transcription)

    return {"transcription": transcription, "summary": summary}
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# Create Pydantic model for input search query
class SearchQuery(BaseModel):
    query: str

# Function to search for transcripts in the database
def search_transcripts(query):
    conn = sqlite3.connect('transcripts.db')
    cursor = conn.cursor()

    # Search for the query in the transcript column
    cursor.execute(''' 
        SELECT filename, transcript, language, timestamp 
        FROM transcripts 
        WHERE transcript LIKE ? 
    ''', ('%' + query + '%',))
    
    results = cursor.fetchall()
    conn.close()
    return results

@app.post("/search")
def search(query: SearchQuery):
    results = search_transcripts(query.query)
    if results:
        return {"results": results}
    else:
        raise HTTPException(status_code=404, detail="No matching transcripts found")
from fastapi import FastAPI
from fpdf import FPDF
import sqlite3
from pathlib import Path

app = FastAPI()

# SQLite Database connection setup
def get_db_connection():
    conn = sqlite3.connect('meetings.db')
    conn.row_factory = sqlite3.Row  # To access columns as dictionary keys
    return conn

@app.get("/export/{meeting_id}")
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

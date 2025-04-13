def transcribe_audio(file_path):
    # Placeholder logic
    return f"Transcription of {file_path}"
import whisper  # Load Whisper model once (options: tiny, base, small, medium, large)

model = whisper.load_model("base")

def transcribe_audio(audio_path):
    print(f"[INFO] Transcribing: {audio_path}")
    result = model.transcribe(audio_path)
    return result["text"]

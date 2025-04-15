import sqlite3

def create_db():
    conn = sqlite3.connect('transcripts.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transcripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            transcript TEXT NOT NULL,
            language TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def store_transcript(filename, transcript, language):
    conn = sqlite3.connect('transcripts.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO transcripts (filename, transcript, language)
        VALUES (?, ?, ?)
    ''', (filename, transcript, language))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_db()
    print("Database and table created successfully.")
    
    store_transcript("audio_file_1.mp3", "This is the transcript text for the audio file.", "English")
    print("Sample transcript stored.")

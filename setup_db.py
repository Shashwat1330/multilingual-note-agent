import sqlite3

def create_db():
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('transcripts.db')
    cursor = conn.cursor()

    # Create a table for storing transcripts
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

# Run this function once to set up the database
if __name__ == "__main__":
    create_db()
    print("Database and table created successfully.")
def store_transcript(filename, transcript, language):
    conn = sqlite3.connect('transcripts.db')
    cursor = conn.cursor()

    # Insert the transcript into the database
    cursor.execute('''
        INSERT INTO transcripts (filename, transcript, language)
        VALUES (?, ?, ?)
    ''', (filename, transcript, language))

    conn.commit()
    conn.close()

# Example usage:
store_transcript("audio_file_1.mp3", "This is the transcript text for the audio file.", "English")

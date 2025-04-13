import sqlite3

def create_meetings_db():
    conn = sqlite3.connect('meetings.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY,
            transcript TEXT,
            summary TEXT,
            action_items TEXT,
            decisions TEXT
        );
    ''')
    conn.commit()
    conn.close()
    print("meetings.db created with table 'meetings'.")

if __name__ == "__main__":
    create_meetings_db()




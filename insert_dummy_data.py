import sqlite3
import random
import string
from datetime import datetime, timedelta

# Function to generate a random string (e.g., for filename or transcript)
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Function to generate a random date within a specific range
def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_date = start_date + timedelta(days=random_days)
    return random_date

# Connect to the SQLite database
conn = sqlite3.connect('transcripts.db')
cursor = conn.cursor()

# Define the number of dummy records you want to insert
num_records = 50  # You can increase this number

# Dummy data insertion
for _ in range(num_records):
    filename = random_string(12) + ".pdf"  # Random filename
    transcript_text = "This is a dummy transcript text with a mention of a meeting."  # Random dummy transcript
    language = random.choice(['English', 'Spanish', 'French', 'German'])
    date_created = random_date(datetime(2025, 1, 1), datetime(2025, 12, 31)).strftime('%Y-%m-%d')

    # Insert dummy data into the transcripts table
    cursor.execute("""
    INSERT INTO transcripts (filename, transcript, language, date_created)
    VALUES (?, ?, ?, ?)
    """, (filename, transcript_text, language, date_created))

# Commit the transaction and close the connection
conn.commit()
conn.close()

print(f"{num_records} dummy records inserted successfully.")

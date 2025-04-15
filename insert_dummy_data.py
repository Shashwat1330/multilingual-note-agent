import sqlite3
import random
import string
from datetime import datetime, timedelta

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

conn = sqlite3.connect('transcripts.db')
cursor = conn.cursor()

num_records = 50

for _ in range(num_records):
    filename = random_string(12) + ".pdf"
    transcript_text = "This is a dummy transcript text with a mention of a meeting."
    language = random.choice(['English', 'Spanish', 'French', 'German'])
    date_created = random_date(datetime(2025, 1, 1), datetime(2025, 12, 31)).strftime('%Y-%m-%d')

    cursor.execute("""
    INSERT INTO transcripts (filename, transcript, language, date_created)
    VALUES (?, ?, ?, ?)
    """, (filename, transcript_text, language, date_created))

conn.commit()
conn.close()

print(f"{num_records} dummy records inserted successfully.")

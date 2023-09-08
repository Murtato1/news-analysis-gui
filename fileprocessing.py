import os
import re
from datetime import datetime
import openai
import sqlite3


indicators = ("gdp", "cpi", "inflation-rate", "unemployment-rate")
folder_path = "./frscraped"

start_date = "2013-01-01"
end_date = "2014-01-02"
indicator_index = 0

# Replace 'YOUR_API_KEY' with your actual OpenAI API key.
api_key = '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'
openai.api_key = api_key

def extract_date_from_filename(filename):
    match = re.search(r'gdp_(\d{4}-\d{1,2}-\d{1,2})_to_(\d{4}-\d{1,2}-\d{1,2})\.txt', filename)
    if match:
        start_date_str, end_date_str = match.groups()
        return datetime.strptime(start_date_str, "%Y-%m-%d"), datetime.strptime(end_date_str, "%Y-%m-%d")
    else:
        return None, None

selected_files = []

for filename in os.listdir(folder_path):
    if filename.endswith(".txt"):
        start_file_date, end_file_date = extract_date_from_filename(filename)
        if start_file_date and end_file_date:
            if start_file_date >= datetime.strptime(start_date, "%Y-%m-%d") and \
               end_file_date <= datetime.strptime(end_date, "%Y-%m-%d"):
                selected_files.append(filename)
                print(filename)

# Assuming you have already filtered and obtained a list of relevant article files.
article_data = []

for filename in selected_files:
    with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
        article_text = file.read()
        article_data.append(article_text)

# Define the more elaborate questions.
questions = [
    "Could you provide a detailed analysis of analysts' sentiment regarding this number?",
    "Do analysts consider this number an anomaly or outlier? If so, what factors contribute to this view?",
    "In the context of market dynamics, can you explain the significance of this number?",
    "What factors might lead analysts to reconsider their future outlook based on this data point?"
]

# Create or connect to the database
conn = sqlite3.connect("article_responses.db")

# Create the table if it doesn't exist
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS article_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        article_text TEXT,
        question TEXT,
        date TEXT,
        response TEXT
    )
''')
conn.commit()

# Function to split the article into segments based on two newlines and ask questions.
def process_article(article_text):
    segments = article_text.split('\n\n')
    for segment in segments:
        if segment.strip():  # Skip empty segments
            # Split the segment into lines
            lines = segment.strip().split('\n')

            # Extract the date from the first line (considering "Updated" prefix)
            date = lines[0].replace("Updated ", "").strip()

            # Remove the date from the segment text
            segment_text = '\n'.join(lines[1:])

            for question in questions:
                response = openai.Completion.create(
                    engine="text-davinci-002",
                    prompt=f"Segment: {segment_text}\nQuestion: {question}\nAnswer:",
                    max_tokens=150,  # Adjust the max tokens as needed for more detailed responses.
                    n=1,
                    stop=None
                )
                answer = response.choices[0].text.strip()
                # Insert the data into the database
                cursor.execute('''
                    INSERT INTO article_responses (article_text, question, date, response)
                    VALUES (?, ?, ?, ?)
                ''', (segment_text, question, date, answer))
                conn.commit()

# Loop through the articles and ask questions for each segment.
for article_text in article_data:
    process_article(article_text)

# Close the database connection when done
conn.close()

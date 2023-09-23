import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import openai
import sqlite3

# Initialize the Tkinter app
app = tk.Tk()
app.title("Article Analysis GUI")

# Replace 'YOUR_API_KEY' with your actual OpenAI API key.
api_key = 'YOUR_API_KEY'
openai.api_key = api_key

# Create or connect to the database
conn = sqlite3.connect("article_responses.db")
cursor = conn.cursor()

# Create or connect to the table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS condensed_article_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        article_text TEXT,
        date TEXT,
        question_1 TEXT,
        answer_1 TEXT,
        question_2 TEXT,
        answer_2 TEXT,
        question_3 TEXT,
        answer_3 TEXT,
        question_4 TEXT,
        answer_4 TEXT
    )
''')
conn.commit()

# Create a custom style for widgets
style = ttk.Style()
style.configure("TButton", padding=10, font=("Arial", 12))
style.configure("TLabel", font=("Arial", 12))
style.configure("TEntry", font=("Arial", 12))

# Function to extract date from filename
def extract_date_from_filename(filename):
    match = re.search(r'(\d{4}-\d{1,2}-\d{1,2})_to_(\d{4}-\d{1,2}-\d{1,2})', filename)
    if match:
        start_date_str, end_date_str = match.groups()
        return start_date_str, end_date_str
    else:
        return None, None


# Function to process articles and insert data into the database
def process_articles():
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    folder_path = folder_path_entry.get()
    prefix = prefix_entry.get()

    selected_files = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt") and filename.startswith(prefix):
            start_file_date, end_file_date = extract_date_from_filename(filename)
            if start_file_date and end_file_date:
                if start_file_date >= start_date and end_file_date <= end_date:
                    selected_files.append(filename)

    article_data = []

    for filename in selected_files:
        with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
            article_text = file.read()
            article_data.append(article_text)

    questions = [
        "Was the analyst's sentiment in this paper positive? Answer with a yes or a no. A one or two word answer is crucial, so if the answer can not be distilled into yes or no, just write either 'inconclusive' or give the general sentiment like 'slightly positive' or 'slightly negative' ",
        "Do analysts consider this number an anomaly or outlier? Answer with a yes or a no. A one or two word answer is crucial, so if the answer can not be distilled into yes or no, just write either 'inconclusive' or give the general sentiment like 'slightly positive' or 'slightly negative' ",
        "In the context of market dynamics is this number significant? Answer with a yes or a no. A one or two word answer is crucial, so if the answer can not be distilled into yes or no, just write either 'inconclusive' or give the general sentiment like 'slightly positive' or 'slightly negative' ",
        "Will this data cause people to re-assess their outlook on the market? Answer with a yes or a no. A one or two word answer is crucial, so if the answer can not be distilled into yes or no, just write either 'inconclusive' or give the general sentiment like 'slightly positive' or 'slightly negative' "
    ]

    # Within the loop where you process articles and generate responses
    for article_text in article_data:
        segments = article_text.split('\n\n')
        for segment in segments:
            if segment.strip():
                lines = segment.strip().split('\n')
                date = lines[0].replace("Updated ", "").strip()
                segment_text = '\n'.join(lines[1:])

                answers = []  # Store answers for each question
                for i, question in enumerate(questions):
                    response = openai.Completion.create(
                        engine="text-davinci-002",
                        prompt=f"Segment: {segment_text}\nQuestion: {question}\nAnswer:",
                        max_tokens=150,
                        n=1,
                        stop=None
                    )
                    answer = response.choices[0].text.strip()
                    answers.append(answer)

                # Insert the data into the condensed table
                cursor.execute('''
                    INSERT INTO condensed_article_responses (article_text, date, question_1, answer_1, question_2, answer_2, question_3, answer_3, question_4, answer_4)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (segment_text, date, questions[0], answers[0], questions[1], answers[1], questions[2], answers[2],
                      questions[3], answers[3]))
                conn.commit()

    messagebox.showinfo("Analysis Complete",
                        f"Analysis and database creation for {len(selected_files)} files is complete.")
    conn.close()


# ...

# Create and layout GUI components with styles
start_date_label = ttk.Label(app, text="Start Date (YYYY-MM-DD):")
start_date_label.grid(column=0, row=0, padx=10, pady=10)
start_date_entry = ttk.Entry(app)
start_date_entry.grid(column=1, row=0, padx=10, pady=10)
# Set the default start date
start_date_entry.insert(0, "2000-01-01")

end_date_label = ttk.Label(app, text="End Date (YYYY-MM-DD):")
end_date_label.grid(column=0, row=1, padx=10, pady=10)
end_date_entry = ttk.Entry(app)
end_date_entry.grid(column=1, row=1, padx=10, pady=10)
# Set the default end date
end_date_entry.insert(0, datetime.today().strftime('%Y-%m-%d'))

folder_path_label = ttk.Label(app, text="Folder Path:")
folder_path_label.grid(column=0, row=2, padx=10, pady=10)
folder_path_entry = ttk.Entry(app)
folder_path_entry.grid(column=1, row=2, padx=10, pady=10)
# Set the default folder path
folder_path_entry.insert(0, "./frscraped")

prefix_label = ttk.Label(app, text="File Prefix:")
prefix_label.grid(column=0, row=4, padx=10, pady=10)
prefix_entry = ttk.Entry(app)
prefix_entry.grid(column=1, row=4, padx=10, pady=10)
# Set the default file prefix
prefix_entry.insert(0, "gdp")

# ...


analyze_button = ttk.Button(app, text="Analyze and Create Database", command=process_articles)
analyze_button.grid(column=0, row=5, columnspan=2, padx=10, pady=20)

# Center the app window on the screen
# Center the app window on the screen
app.update()  # Update the app to ensure it's fully initialized
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
window_width = app.winfo_width()
window_height = app.winfo_height()
x_coordinate = (screen_width - window_width) // 2
y_coordinate = (screen_height - window_height) // 2
app.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

app.mainloop()

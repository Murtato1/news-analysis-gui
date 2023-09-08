import tkinter as tk
from tkinter import ttk
from transformers import pipeline

# Create the sentiment, question_answer, and summary pipelines
sentiment = pipeline(model="distilbert-base-uncased-finetuned-sst-2-english")
question_answer = pipeline(model="deepset/roberta-base-squad2")
summary = pipeline("summarization")

# Create a function to perform sentiment analysis
def perform_sentiment_analysis():
    text = text_entry.get("1.0", "end-1c")
    result = sentiment(text)
    sentiment_result.set(result[0]['label'] + " " + str(result[0]['score']))

# Create a function to perform question answering
def perform_question_answering():
    text = text_entry.get("1.0", "end-1c")
    question = question_entry.get()
    result = question_answer(question=question, context=text)
    question_answer_result.set(result['answer'] + " Certainty: " + str(result['score']))

# Create a function to perform summarization
def perform_summarization():
    text = text_entry.get("1.0", "end-1c")
    result = summary(text, max_length=len(text)/4)
    summarization_result.delete("1.0", "end")
    summarization_result.insert("1.0", result[0]['summary_text'])

# Create the main GUI window
root = tk.Tk()
root.title("Hugging Face Transformers GUI")

# Create and configure text input area
text_label = ttk.Label(root, text="Enter Text:")
text_label.pack()
text_entry = tk.Text(root, height=10, width=50)
text_entry.pack()

# Create sentiment analysis button and result label
sentiment_button = ttk.Button(root, text="Analyze Sentiment", command=perform_sentiment_analysis)
sentiment_button.pack()
sentiment_result = tk.StringVar()
sentiment_label = ttk.Label(root, textvariable=sentiment_result)
sentiment_label.pack()

# Create question answering input and button
question_label = ttk.Label(root, text="Ask a Question:")
question_label.pack()
question_entry = ttk.Entry(root)
question_entry.pack()
question_answer_button = ttk.Button(root, text="Answer Question", command=perform_question_answering)
question_answer_button.pack()
question_answer_result = tk.StringVar()
question_answer_label = ttk.Label(root, textvariable=question_answer_result)
question_answer_label.pack()

# Create summarization button and result text area
summarization_button = ttk.Button(root, text="Summarize", command=perform_summarization)
summarization_button.pack()
summarization_result = tk.Text(root, height=10, width=50)
summarization_result.pack()

# Start the Tkinter main loop
root.mainloop()

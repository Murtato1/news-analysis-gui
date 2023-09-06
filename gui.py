import tkinter as tk
from tkinter import ttk, messagebox
import requests

class NewsSearchApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("News Search")
        self.geometry("800x600")
        
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.title_label = ttk.Label(self.main_frame, text="News Search", font=("Arial", 24, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=20)

        self.query_label = ttk.Label(self.main_frame, text="Enter query:")
        self.query_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        self.entry = ttk.Entry(self.main_frame, font=("Arial", 14))
        self.entry.grid(row=2, column=0, sticky=tk.EW, pady=10)

        # Start and end date entries
        self.start_date_label = ttk.Label(self.main_frame, text="Start Date (YYYY-MM-DD):")
        self.start_date_label.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
        self.start_date_entry = ttk.Entry(self.main_frame, font=("Arial", 14))
        self.start_date_entry.grid(row=2, column=1, sticky=tk.EW, pady=10)

        self.end_date_label = ttk.Label(self.main_frame, text="End Date (YYYY-MM-DD):")
        self.end_date_label.grid(row=3, column=1, sticky=tk.W, pady=(0, 10))
        self.end_date_entry = ttk.Entry(self.main_frame, font=("Arial", 14))
        self.end_date_entry.grid(row=4, column=1, sticky=tk.EW, pady=10)

        self.search_button = ttk.Button(self.main_frame, text="Search", command=self.search_news)
        self.search_button.grid(row=5, column=0, columnspan=2, pady=20)

        # Paned Window for multiple output boxes
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.grid(row=6, column=0, columnspan=2, sticky=tk.EW, pady=10)

        # Textbox for Articles Scraped
        self.articles_frame = self.create_output_frame("Articles Scraped")
        self.paned_window.add(self.articles_frame)

        # Textbox for Sentiment Analysis
        self.sentiment_frame = self.create_output_frame("Sentiment Analysis")
        self.paned_window.add(self.sentiment_frame)

        # Textbox for Total Summary
        self.summary_frame = self.create_output_frame("Total Summary")
        self.paned_window.add(self.summary_frame)

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(6, weight=1)

    def create_output_frame(self, title):
        frame = ttk.LabelFrame(self.paned_window, text=title, padding="10")
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        output = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, height=10)
        output.pack(fill=tk.BOTH, expand=True)
        output.config(state=tk.DISABLED)
        scrollbar.config(command=output.yview)
        return frame

    def search_news(self):
        query = self.entry.get()
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()

        if not query:
            messagebox.showerror("Error", "Please enter a search query.")
            return

        # Add validation for date format if needed
        
        try:
            response = requests.post("http://127.0.0.1:5000/search", json={"query": query, "start_date": start_date, "end_date": end_date})
            if response.status_code == 200 and response.text:
                data = response.json()
                # Example: You can extract data from the response and fill each text box accordingly
                articles = data.get("titles", [])
                sentiment_list = data.get("sentiments", [])

                self.update_textbox(self.articles_frame, "\n".join(articles))
                self.update_textbox(self.sentiment_frame, "\n".join(sentiment_list))
            else:
                messagebox.showerror("Error", f"Server returned an error: {response.status_code}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_textbox(self, frame, text):
        textbox = frame.winfo_children()[1]  # get the Text widget from the frame
        textbox.config(state=tk.NORMAL)
        textbox.delete(1.0, tk.END)
        textbox.insert(tk.END, text)
        textbox.config(state=tk.DISABLED)

if __name__ == "__main__":
    app = NewsSearchApp()
    style = ttk.Style()
    style.theme_use('clam') 
    app.mainloop()


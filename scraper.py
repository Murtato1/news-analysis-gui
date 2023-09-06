from flask import Flask, request, jsonify
from pygooglenews import GoogleNews
from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request
import json

app = Flask(__name__)
gn = GoogleNews()

global classifier
classifier = pipeline(model="distilbert-base-uncased-finetuned-sst-2-english")


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

def sentimentAnalysis(links):
    sentiments = []
    firstlinks = links[:5]
    for link in firstlinks:
        html = urllib.request.urlopen(link).read()
        extracted_text = text_from_html(html)
        classified = classifier(extracted_text)
        addsent = (classified[0]['label'] + " " + str(round(classified[0]['score'],2)) + "\n")
        sentiments.append(addsent)
    return sentiments
	
@app.route('/search', methods=['POST'])
def search():
    data = request.json
    start_date = None
    end_date = None

    # Check if search query is provided
    if 'query' not in data:
        return jsonify({"error": "Please provide a search query using the 'query' key."}), 400
        
    if 'start_date' in data and 'end_date' in data:
    	start_date = data['start_date']
    	end_date = data['end_date']

    # Fetch the news results
    search_results = None
    if (start_date is not None and end_date is not None):
    	search_results = gn.search(data['query'], from_ = start_date, to_= end_date)
    else:
    	search_results = gn.search(data['query'])
    	
    titles = [entry['title'] + "\n" for entry in search_results['entries']]
    
    # Find links
    
    links = [entry['link'] + "\n" for entry in search_results['entries']]
    sentiments = sentimentAnalysis(links)

    return jsonify({"titles": titles, "sentiments":sentiments})


if __name__ == '__main__':
    app.run(debug=True)


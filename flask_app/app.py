from flask import Flask, request, jsonify
from utils import search_articles, concatenate_content, generate_answer
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def query():
    """
    Handles the POST request to '/query'. Extracts the query from the request,
    processes it through the search, concatenate, and generate functions,
    and returns the generated answer.
    """
    data = request.json
    user_query = data.get('query')
    if not user_query:
        return jsonify({"error": "Query not provided"}), 400

    try:
        # Step 1: Search and scrape articles
        articles = search_articles(user_query)
        
        # Step 2: Concatenate content from the scraped articles
        concatenated_content = concatenate_content(articles)
        
        # Step 3: Generate an answer using the LLM
        answer = generate_answer(concatenated_content, user_query)
        
        # Return the generated answer
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=5001)

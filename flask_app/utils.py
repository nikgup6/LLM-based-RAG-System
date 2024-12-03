import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import openai

# Load API keys from environment variables
load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

def search_articles(query):
    """
    Searches for articles using the Serper API and returns a list of formatted responses.
    """
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "gl": "us",
        "hl": "en"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        # Print the raw response for debugging
        print("Raw response data:", data)

        # Extract and format responses
        articles = []
        if 'organic' in data:
            articles = [
                {
                    'title': item.get('title', 'No Title'),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                }
                for item in data['organic'][:4]  # Limit to 3-4 responses
            ]
        elif 'answerBox' in data:
            articles = [{
                'title': data['answerBox'].get('title', 'No Title'),
                'link': data['answerBox'].get('link', ''),
                'snippet': data['answerBox'].get('snippet', '')
            }]

        return articles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching search results: {e}")
        return []

def fetch_article_content(url):
    """
    Fetches the article content, extracting headings and text.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        content = ""

        # Extract headings and paragraphs
        for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
            content += tag.get_text() + "\n"
        return content.strip()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching article content from {url}: {e}")
        return ""

def concatenate_content(articles):
    """
    Concatenates the content of the provided articles into a single string.
    """
    full_text = ""
    for article in articles:
        url = article.get("link")
        if url:
            print(f"Fetching content for article: {article.get('title')}")
            content = fetch_article_content(url)
            full_text += f"Title: {article.get('title')}\n{content}\n\n"
    return full_text

def generate_answer(content, query):
    """
    Generates an answer from the concatenated content using GPT-4.
    """
    prompt = f"Given the context below, answer the question:\n\nContext:\n{content}\n\nQuestion:\n{query}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response['choices'][0]['message']['content']
        return answer.strip()
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "An error occurred while generating the answer."



import requests
from bs4 import BeautifulSoup
import os

def fetch_website_content(url):
    """Fetches content from a given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract text from common content areas, ignoring scripts and styles
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        # Break into lines and remove leading/trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def fetch_document_content(file_path):
    """Fetches content from a local document (e.g., .txt, .md)."""
    if not os.path.exists(file_path):
        print(f"Error: Document not found at {file_path}")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"Error reading document {file_path}: {e}")
        return None

def fetch_content(source_url, source_type):
    """Fetches content based on source type."""
    if source_type == 'website':
        return fetch_website_content(source_url)
    elif source_type == 'document':
        return fetch_document_content(source_url)
    else:
        print(f"Unsupported source type: {source_type}")
        return None

if __name__ == '__main__':
    # Example usage
    print("Fetching website content...")
    website_content = fetch_content("https://www.google.com", "website")
    if website_content:
        print(f"Content length: {len(website_content)} characters")
        print(website_content[:500]) # Print first 500 characters

    print("\nFetching document content...")
    # Create a dummy document for testing
    dummy_doc_path = "aladdin-sandbox/apps/ai_newsbot/test_document.txt"
    os.makedirs(os.path.dirname(dummy_doc_path), exist_ok=True)
    with open(dummy_doc_path, "w", encoding="utf-8") as f:
        f.write("This is a test document for the AI NewsBot. It contains some sample text to be read.")

    document_content = fetch_content(dummy_doc_path, "document")
    if document_content:
        print(f"Content length: {len(document_content)} characters")
        print(document_content)

    # Clean up dummy document
    os.remove(dummy_doc_path)


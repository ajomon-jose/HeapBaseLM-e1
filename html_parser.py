import requests
from bs4 import BeautifulSoup

def fetch_and_parse_html(url: str = None, raw_html: str = None) -> str:
    """Fetches HTML from a URL or parses raw HTML and extracts clean text."""
    if url:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            html_content = response.text
        except Exception as e:
            raise ValueError(f"Failed to fetch URL: {str(e)}")
    elif raw_html:
        html_content = raw_html
    else:
        raise ValueError("Must provide either url or raw_html")

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script, style, header, footer, and nav elements
    for element in soup(["script", "style", "header", "footer", "nav"]):
        element.decompose()
        
    # Extract text and clean up whitespace
    text = soup.get_text(separator='\n')
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    clean_text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return clean_text

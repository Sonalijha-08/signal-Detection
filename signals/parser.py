import re
from typing import List, Dict
from bs4 import BeautifulSoup

# Keywords that indicate hiring activity
HIRING_KEYWORDS = [
    "hiring",
    "recruiting",
    "mass hiring",
    "scale up",
    "expansion",
    "engineering hiring",
    "campus drive",
    "new hires",
    "opening",
    "join us",
]

NUMERIC_PATTERN = re.compile(r"(\\d{1,3}(?:,\\d{3})+|\\d{2,5})\\s*\+?\s*(?:hire|hired|hirees|positions|openings|vacancies)", re.IGNORECASE)

def html_to_text(html: str) -> str:
    """Convert HTML to plain text using BeautifulSoup, stripping scripts and styles."""
    soup = BeautifulSoup(html, "html.parser")
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text(separator=" ", strip=True)

def detect_keywords(text: str) -> List[str]:
    """Return a list of hiring-related keywords found in the text (case‑insensitive)."""
    lowered = text.lower()
    found = [kw for kw in HIRING_KEYWORDS if kw in lowered]
    return found

def extract_numeric_signals(text: str) -> List[str]:
    """Extract numeric hiring signals like "500+ hires" or "1,000 engineers"."""
    matches = NUMERIC_PATTERN.findall(text)
    # Clean commas and whitespace
    cleaned = [m.replace(",", "").strip() for m in matches]
    return cleaned

def parse_article(html: str) -> Dict:
    """Parse a raw HTML article and return extracted information.

    Returns a dictionary with keys:
        text – full plain‑text content
        keywords – list of matched hiring keywords
        numeric_signals – list of numeric hiring strings
    """
    text = html_to_text(html)
    keywords = detect_keywords(text)
    numeric_signals = extract_numeric_signals(text)
    return {
        "text": text,
        "keywords": keywords,
        "numeric_signals": numeric_signals,
    }

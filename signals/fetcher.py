import requests
import urllib.parse
from typing import List, Dict

RSS_URL_TEMPLATE = "https://news.google.com/rss/search?q={query}+site:news.google.com"

def build_query(company_name: str) -> str:
    """Create a Google News RSS query for mass hiring signals for a company."""
    query = f"{company_name} mass hiring"
    return urllib.parse.quote_plus(query)

def fetch_rss(company_name: str) -> List[Dict[str, str]]:
    """Fetch RSS entries for the given company.

    Returns a list of dicts with keys: title, link, pubDate, description.
    """
    query = build_query(company_name)
    url = RSS_URL_TEMPLATE.format(query=query)
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    # Simple parsing using xml.etree
    import xml.etree.ElementTree as ET
    root = ET.fromstring(resp.content)
    items = []
    for item in root.findall('.//item'):
        items.append({
            'title': item.findtext('title') or '',
            'link': item.findtext('link') or '',
            'pubDate': item.findtext('pubDate') or '',
            'description': item.findtext('description') or ''
        })
    return items

def fetch_url(url: str) -> str:
    """Fetch raw HTML content for a given URL with basic retry logic."""
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        # In a real system we would log.
        return ""

def fetch_company_careers(company_domain: str) -> str:
    """Attempt to fetch the /careers page of a company's domain.
    Returns HTML string or empty on failure.
    """
    url = f"https://{company_domain.rstrip('/')}/careers"
    return fetch_url(url)

def fetch_content(company_name: str) -> List[str]:
    """Returns list of raw HTML strings for a company's RSS entries."""
    rss_entries = fetch_rss(company_name)
    results = []
    for entry in rss_entries:
        link = entry.get('link')
        if link:
            results.append(fetch_url(link))
    return results

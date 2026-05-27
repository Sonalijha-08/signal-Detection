import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def get_session(retries: int = 3, backoff_factor: float = 0.3, status_forcelist: tuple = (500, 502, 504)) -> requests.Session:
    """Create a requests Session with retry strategy.

    Args:
        retries: Number of total retries.
        backoff_factor: A backoff factor to apply between attempts.
        status_forcelist: HTTP status codes that trigger a retry.
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def fetch_url(url: str, timeout: int = 10) -> str:
    """Fetch the content at *url* and return text.

    Raises:
        requests.RequestException on network errors.
    """
    session = get_session()
    response = session.get(url, timeout=timeout, headers={"User-Agent": "SignalDetector/1.0"})
    response.raise_for_status()
    return response.text

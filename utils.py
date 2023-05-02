import os
import re
import unicodedata
import random

# Absolute path of the project dir
BASE_DIR = os.path.realpath(os.path.dirname(__file__))


def get_header() -> dict:
    """
    Generates HTTP headers.

    Returns:
        dict: A dictionary representing an HTTP header.

    The function returns a randomly selected header dictionary
    from a list of headers, each with a different user-agent.
    """
    headers = [
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
            "Referer": "https://www.google.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "TE": "Trailers"
        },
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
            "Referer": "https://www.google.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        },
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
            "Referer": "https://www.google.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "TE": "Trailers"
        },
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
            "Referer": "https://www.google.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    ]
    return random.choice(headers)


def normalize_text(input: str) -> str:
    """
    Returns the 'normalized' form (with compatible, non-special characters) of a Unicode string.

    Args:
        input (str): text to be processed
    Returns:
        str: Text in normal form
    """
    return unicodedata.normalize('NFKD', str(input)).encode('ascii', 'ignore').decode('ascii')


def extract_search_term(url: str) -> str:
    """
    Extract the search term from a given OLX.ro URL.

    Args:
        url (str): A string representing the URL from which the search term is to be extracted.

    Returns:
        A string representing the search term extracted,
        or None, if no search term was found in the URL.
    """
    # In OLX.ro urls, the search term is preceded by '/q-' and followed by '/'.
    match = re.search(r"(?<=(/q-))[\S-]+(?=/)", url, re.IGNORECASE)
    if match:
        query = match.group()
        query_segments = query.split("-")
        return " ".join(query_segments)
    return None

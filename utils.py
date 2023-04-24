import os
import re
import unicodedata
import random

# Cale absolută dir. proiect
BASE_DIR = os.path.realpath(os.path.dirname(__file__))


def get_header() -> dict:
    """
    Generează un dicționar aleatoriu de antete HTTP.

    Returns:
        Un dicționar care reprezintă un antet HTTP.

    Funcția returnează un dicționar de antet selectat aleatoriu dintr-o
    listă de antete, fiecare cu alt user-agent.
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
    Returneaza forma normala (fara diacritice si cu caractere compatibile) a unui string Unicode.

    Args:
        input (str): Textul care va fi procesat
    Returns:
        str: Textul in forma normala
    """
    return unicodedata.normalize('NFKD', str(input)).encode('ascii', 'ignore').decode('ascii')


def extract_search_term(url: str) -> (str | None):
    """
    Extrage termenul de căutare dintr-un URL OLX.ro dat.

    Args:
        url (str): Un șir de caractere reprezentând URL-ul din care trebuie extras termenul de căutare.

    Returns:
        Un șir de caractere reprezentând termenul de căutare extras, sau None,
        dacă nu a fost găsit niciun termen de căutare în URL.
    """
    # Termenul de cautare este precedat de '/q-' si urmat de '/'
    match = re.search(r"(?<=(/q-))[\S-]+(?=/)", url, re.IGNORECASE)
    if match:
        query = match.group()
        query_segments = query.split("-")
        return " ".join(query_segments)
    return None

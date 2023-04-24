import os
import logging
import logging_config
from multiprocessing import Pool
from scraper_manager import OlxScraper
from database_manager import DatabaseManager
from notification_manager import Messenger
from utils import BASE_DIR


scraper = OlxScraper()
db = DatabaseManager()


def load_target_urls() -> list:
    """
    Încarcă o listă de URL-uri de urmărit dintr-un fișier text denumit
    "target_urls.txt" și aflat în același director de bază cu scriptul.

    Returns:
        list: Lista de URL-uri se unde se vor colecta date. Dacă fișierul
        nu există, îl creează și returnează o listă goală.

    """
    file_path = os.path.join(BASE_DIR, "target_urls.txt")
    user_message = f"Fișierul 'target_urls.txt' a fost creat. Trebuie să adaugi în " \
        + f"el cel puțin un URL pentru a începe monitorizarea. Adaugă un URL/linie."
    try:
        with open(file_path) as f:
            target_urls = [line.strip() for line in f]
    except FileNotFoundError:
        logging.info(user_message)
        open(file_path, "w").close()
        target_urls = []
    if not target_urls:
        logging.info(user_message)
    return target_urls


def get_new_ads_urls(all_urls: list) -> list:
    """
    Returnează o listă de URL-uri de anunțuri noi (care nu se găsesc în baza de date). 
    Args:
        all_urls (list): Lista de URL-uri care trebuie comparate cu baza de date.

    Returnează:
        new_urls (list): Lista de URL-uri care nu se găsesc în baza de date
    """
    new_urls = []
    if all_urls:
        for url in all_urls:
            if not db.url_exists(url):
                new_urls.append(url)
    return new_urls


def get_new_ads_urls_for_url(target_url: str) -> list:
    """
    Extrage anunțurile pentru o anumită adresă URL și filtrează anunțurile procesate anterior.

    Args:
        target_url (str): Un string reprezintă URL-ul pentru care trebuie să se extragă noi anunțuri.

    Returns:
        List[str]: O listă de adrese URL reprezentând noile anunțuri preluate de la adresa URL dată.
    """

    try:
        ads_urls = scraper.scrape_ads_urls(target_url)
    except ValueError as error:
        logging.error(error)
        return []
    return get_new_ads_urls(ads_urls)


def main() -> None:
    """Colectează și procesează anunțurile noi și trimite
    notificări pe email și Telegram."""

    target_urls = load_target_urls()
    for target_url in target_urls:
        ads_urls = get_new_ads_urls_for_url(target_url)

        # Filtrează anunțurile deja procesate
        new_ads_urls = get_new_ads_urls(ads_urls)
        if not new_ads_urls:
            continue

        # Procesează anunțurile în paralel
        with Pool(10) as pool:
            new_ads = pool.map(scraper.get_ad_data, new_ads_urls)
        new_ads = list(filter(None, new_ads))

        message_subject, message_body = Messenger.generate_email_content(
            target_url, new_ads)
        Messenger.send_email_message(message_subject, message_body)
        Messenger.send_telegram_message(message_subject, message_body)

        # Adaugă în DB anunțurile procesate
        for url in new_ads_urls:
            db.add_entry(url)


if __name__ == "__main__":
    main()

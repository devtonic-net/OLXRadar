import re
import requests
import logging
import logging_config
from multiprocessing import Pool
from urllib.parse import urlparse
from bs4 import BeautifulSoup, ResultSet, Tag
from utils import get_header


class OlxScraper:
    """Clasa folosită la colectarea datelor de pe OLX România."""

    def __init__(self):
        # self.headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0"}
        self.headers = get_header()
        self.netloc = "www.olx.ro"
        self.schema = "https"
        self.current_page = 1
        self.last_page = None

    def parse_content(self, target_url: str) -> (BeautifulSoup | None):
        """
        Procesează conținutul de la un URL dat.

        Args:
            target_url (str): Un string reprezentând URL-ul ce va fi procesat.

        Returns:
            BeautifulSoup: Un obiect reprezentând conținutul procesat
            de la URL-ul dat sau None în caz de eroare.
        """
        try:
            r = requests.get(target_url, headers=self.headers, timeout=60)
            r.raise_for_status()
        except requests.exceptions.RequestException as error:
            logging.error(f"Eroare de conexiune: {error}")
        else:
            parsed_content = BeautifulSoup(r.text, "html.parser")
            return parsed_content

    def get_ads(self, parsed_content: BeautifulSoup) -> (ResultSet[Tag] | None):
        if parsed_content is None:
            return None
        ads = parsed_content.select("div.css-1sw7q4x")
        return ads

    def get_last_page(self, parsed_content: BeautifulSoup) -> (int | None):
        if parsed_content is not None:
            pagination_ul = parsed_content.find("ul", class_="pagination-list")
            if pagination_ul is not None:
                pages = pagination_ul.find_all("li", class_="pagination-item")
                if pages:
                    return int(pages[-1].text)
        return None

    def scrape_ads_urls(self, target_url: str) -> list:
        """
        Colectează URL-urile anunțurilor de pe o pagină OLX. Caută toate URL-urile relevante
        ale anunțurilor și le adaugă într-o mulțime. Paginile sunt parcurs pe rând,
        începând cu pagina curentă și până la ultima pagină a anunțurilor.

        Args:
            target_url (str): Adresa URL a paginii OLX de la care să înceapă căutarea.

        Returns:
            list: O listă de URL-uri relevante ale anunțurilor găsite pe pagină.

        Raises:
            ValueError: Dacă adresa URL nu este validă sau nu aparține domeniului specificat.
        """
        ads_links = set()
        if self.netloc != urlparse(target_url).netloc:
            raise ValueError(
                f"URL-ul nu este valid! OLXRadar poate procesa doar adrese de pe {self.netloc}.")
        while True:
            url = f"{target_url}/?page={self.current_page}"
            parsed_content = self.parse_content(url)
            self.last_page = self.get_last_page(parsed_content)
            ads = self.get_ads(parsed_content)
            if ads is None:
                return ads_links
            for ad in ads:
                link = ad.find("a", class_="css-rc5s2u")
                if link is not None and link.has_attr("href"):
                    link_href = link["href"]
                    if not self.is_internal_url(link_href, self.netloc):
                        continue
                    if not self.is_relevant_url(link_href):
                        continue
                    if self.is_relative_url(link_href):
                        link_href = f"{self.schema}://{self.netloc}{link_href}"
                    ads_links.add(link_href)
            if self.last_page is None or self.current_page >= self.last_page:
                break
            self.current_page += 1
        return ads_links

    def is_relevant_url(self, url: str) -> bool:
        """
        Determină dacă o anumită adresă URL este relevantă, analizând segmentul query pe care îl conține.

        Args:
            url (str): Un șir de caractere care reprezintă URL-ul a cărui relevanță trebuie verificată.

        Returnează:
            bool: 'True', dacă URL-ul este relevant, 'False' dacă nu.

        Segmentele de interogare (cum ar fi "?reason=extended-region") indică faptul că anunțul este
        adăugat la rezultatele căutării de către OLX în cazul în care nu există suficiente anunțuri
        disponibile pentru regiunea utilizatorului, deci nu este util (relevant).
        """
        segments = urlparse(url)
        if segments.query != "":
            return False
        return True

    def is_internal_url(self, url: str, domain: str) -> bool:
        """
        Verifică dacă URL-ul are același domeniu cu al paginii din care a fost extras.

        Args:
            url (str): URL-ul care trebuie verificat.
            domain (str): Domeniul paginii curente.

        Returns:
            bool: True dacă URL-ul este o legătură internă, False în caz contrar.
        """
        # URL incepe cu "/"
        if self.is_relative_url(url):
            return True
        parsed_url = urlparse(url)
        if parsed_url.netloc == domain:
            return True
        return False

    def is_relative_url(self, url: str) -> bool:
        """
        Verifica daca url-ul dat este relativ sau absolut.

        Args:
            url (str): Url-ul de verificat.

        Returns:
            True, dacă url-ul este relativ, altfel False.
        """

        parsed_url = urlparse(url)
        if not parsed_url.netloc:  # nu incepe cu nume de domeniu
            return True
        if re.search(r"^\/[\w.\-\/]+", url):  # incepe cu "/"
            return True
        return False

    def get_ad_data(self, ad_url: str) -> (dict[str] | None):
        """
        Extrage informații din pagina HTML a anunțului.

        Args:
            ad_url (str): URL-ul anunțului.

        Returns:
            dict sau None: Un dicționar care conține informațiile extrase pentru
            anunțul publicitar sau 'None', dacă lipsesc informațiile necesare.
        """
        logging.info(f"Proceseaza {ad_url}")
        content = self.parse_content(ad_url)

        if content is None:
            return None

        title = None
        if content.find("h1", class_="css-1soizd2"):
            title = content.find(
                "h1", class_="css-1soizd2").get_text(strip=True)
        price = None
        if content.find("h3", class_="css-ddweki"):
            price = content.find(
                "h3", class_="css-ddweki").get_text(strip=True)
        description = None
        if content.find("div", class_="css-bgzo2k"):
            description = content.find(
                "div", class_="css-bgzo2k").get_text(strip=True, separator="\n")
        seller = None
        if content.find("h4", class_="css-1lcz6o7"):
            seller = content.find(
                "h4", class_="css-1lcz6o7").get_text(strip=True)
        if any(item is None for item in [title, price, description]):
            return None
        ad_data = {
            "title": title,
            "price": price,
            "url": ad_url,
            "description": description
        }
        return ad_data

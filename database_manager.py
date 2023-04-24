import sqlite3
import os
from utils import BASE_DIR


class DatabaseManager():
    """
    Class responsible for database operations.
    """

    def __init__(self) -> None:
        """
        Inițializează un nou obiect Bază de date și creează tabelul 'articles', dacă acesta nu există.
        """
        self.DB = os.path.join(BASE_DIR, "database.db")
        self.conn = sqlite3.connect(self.DB)
        self.cursor = self.conn.cursor()
        sql_create_table = """
            CREATE TABLE IF NOT EXISTS ads (
                id          INTEGER     PRIMARY KEY     AUTOINCREMENT,
                url         TEXT        NOT NULL
            );
            """
        self.cursor.execute(sql_create_table)
        self.cursor.close()
        self.conn.commit()

    def url_exists(self, url: str) -> bool:
        """
        Returnează True dacă în baza de date există o intrare cu url-ul specificat, iar în caz contrar, False.

        Args:
        url (str): url-ul care trebuie verificat.

        Returns:
        bool: True dacă în baza de date există o intrare cu url-ul specificat, altfel False.
        """
        self.conn = sqlite3.connect(self.DB)
        self.cursor = self.conn.cursor()
        sql_command = f"SELECT url FROM ads WHERE url = '{url}'"
        self.cursor.execute(sql_command)
        result = self.cursor.fetchone()
        self.cursor.close()
        self.conn.commit()
        self.conn.close()
        if result:
            return True
        return False

    def add_entry(self, url: str) -> None:
        """
        Adaugă în baza de date 'articles' o nouă intrare cu url-ul,
        titlul și descrierea specificate.

        Args:
        url (str): un șir de caractere care reprezintă adresa URL a articolului
        title (str): un șir de caractere care reprezintă titlul articolului
        description (str): un șir de caractere care reprezintă descrierea articolului

        Returns:
        None.
        """
        self.conn = sqlite3.connect(self.DB)
        self.cursor = self.conn.cursor()

        sql = "INSERT INTO ads (url) VALUES(?)"
        self.cursor.execute(sql, (url,))
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

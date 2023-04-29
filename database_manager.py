import sqlite3
import os
from utils import BASE_DIR


class DatabaseManager():
    """Class responsible for the interactions with the database."""

    def __init__(self) -> None:
        """
        Init a new DB object and create the 'ads' table, if it doesn't exist.
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
        Returns True if an entry with the specified url exists
        in the database, otherwise False.

        Args:
            url (str): the url to check.

        Returns:
            bool: True if an entry with the specified url exists in
            the database, otherwise False.
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

    def add_url(self, url: str) -> None:
        """
        Adds a new entry with the specified url to the 'ads' table.

        Args:
            url (str): a string representing the URL of the item.

        Returns:
            None
        """
        self.conn = sqlite3.connect(self.DB)
        self.cursor = self.conn.cursor()

        sql = "INSERT INTO ads (url) VALUES(?)"
        self.cursor.execute(sql, (url,))
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

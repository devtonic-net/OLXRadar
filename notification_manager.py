import logging
import os
import ssl
import smtplib
import requests
from dotenv import load_dotenv
from utils import normalize_text, extract_search_term

load_dotenv()

EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


class Messenger():

    @staticmethod
    def generate_ad_string(index: int, ad: dict) -> str:
        """
        Generează corpul text al unui anunț.

        Args:
            index (int): Indicele anunțului în listă.
            ad (dict): Un dicționar care conține detalii despre anunț, inclusiv
            titlul, descrierea, prețul și adresa URL.

        Returns:
            str: O reprezentare formatată a anunțului sub formă de șir de caractere.

        """
        title = normalize_text(ad["title"]).strip()
        description = normalize_text(ad["description"]).strip()[:150]
        price = normalize_text(ad["price"]).strip()
        url = ad["url"]
        return f"{index}. {title} ({price})\n{description}...\n{url}\n\n"

    @staticmethod
    def generate_email_content(target_url: str, new_ads: list) -> tuple[str, str]:
        """
        Generează subiectul și corpul unui e-mail care conține anunțuri noi.

        Params:
            target_url (str): URL-ul paginii în care au fost găsite anunțurile.
            new_ads (List[Dict]): O listă de dicționare care conține detalii despre
            noile anunțuri: titlul, descrierea, prețul și URL-ul.

        Returns:
            Tuple[str, str]: Un tuple care conține subiectul și corpul e-mailului.

        """
        email_body_elements = []
        for index, new_ad_details in enumerate(new_ads, start=1):
            ad_string = Messenger.generate_ad_string(index, new_ad_details)
            email_body_elements.append(ad_string)

        search_term = extract_search_term(target_url)
        email_subject = f"OLXRadar: {len(new_ads)} anunțuri noi"
        if search_term is not None:
            email_subject += f" pentru termenul '{search_term.title()}'"
        email_body = "\n".join(email_body_elements)
        return email_subject, email_body

    @staticmethod
    def send_email_message(subject: str, message: str) -> None:
        """
        Trimite un e-mail cu subiectul și mesajul dat unui destinatar.

        Params:
            subiect (str): Subiectul e-mailului.
            mesaj (str): Corpul mesajului.

        Returns:
            None

        Raises:
            SMTPAuthenticationError: Dacă datele de autentificare sunt incorecte.
            SMTPException: Dacă apare o eroare în timpul trimiterii e-mailului.
        """
        try:
            subject = str(subject)
            message = str(message)
            message = f"""Subject: {subject}\n\n{message}"""
            message = normalize_text(message)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(EMAIL_SMTP_SERVER, port=465, context=context) as server:
                server.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
                server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, message)
                server.quit()
        except (smtplib.SMTPAuthenticationError, smtplib.SMTPException) as error:
            logging.error(
                f"Eroare la trimiterea notificării pe Email: {error}")
        logging.info("Notificare trimisă cu succes pe Email.")

    @staticmethod
    def send_telegram_message(message_subject: str, message_body: str) -> None:
        """
        Trimite un mesaj prin Telegram. Serviciul accepta mesaje cu lungimea de cel
        mult 4096 de caractere, asa ca notificarea va fi impartita in sectiuni de
        cel mult 4000 de semne

        Args:
            message_subject (str): Subiectul mesajului care va fi trimis.
            message_body (str): Corpul mesajului care va fi trimis.

        Returns:
            None

        Raises:
            requests.exceptions.RequestException: Dacă apare o eroare în timpul cererii.
        """
        endpoint = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        max_length = 4000
        message_batches = []
        current_message = ""
        # Imparte mesajele in sectiuni
        chunks = message_body.split("\n\n")
        for chunk in chunks:
            if len(current_message) + len(chunk) <= max_length:
                current_message += chunk + "\n\n"
            else:
                message_batches.append(current_message.strip())
                current_message = chunk + "\n\n"
        message_batches.append(current_message.strip())

        # Trimite sectiunile una cate una
        for i, message_batch in enumerate(message_batches):
            if i == 0:
                message_text = f"{message_subject}\n\n{message_batch}"
            else:
                message_text = message_batch
            params = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message_text
            }
            try:
                response = requests.get(endpoint, params=params)
                response.raise_for_status()
                if response.json()["ok"]:
                    logging.info("Notificare trimisă cu succes pe Telegram.")
                else:
                    logging.error(
                        "Eroare la trimiterea notificării pe Telegram.")
            except requests.exceptions.RequestException as error:
                logging.error(f"Eroare de conexiune cu Telegram: {error}")

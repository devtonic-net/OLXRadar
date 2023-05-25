import os
import ssl
import smtplib
import requests
import logging
from dotenv import load_dotenv
from utils import normalize_text, extract_search_term
import logging_config

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


class Messenger():
    """Class used to group the notification sending methods."""

    @staticmethod
    def generate_ad_string(index: int, ad: dict) -> str:
        """
        Generates the text body of an advertisement.

        Args:
            index (int): index of the ad in the list.
            ad (dict): A dictionary containing details about
            the ad - title, description, price and URL.

        Returns:
            str: The contents of an ad as a string.
        """
        title = normalize_text(ad["title"]).strip()
        description = normalize_text(ad["description"]).strip()[:150]
        price = normalize_text(ad["price"]).strip()
        url = ad["url"]
        return f"{index}. {title} ({price})\n{description}...\n{url}\n\n"

    @staticmethod
    def generate_email_content(target_url: str, new_ads: list) -> tuple[str, str]:
        """
        Generates the subject and the body of an email containing new ads.

        Params:
            target_url (str): URL of the page where the ads were found.
            new_ads (List[Dict]): A list of dictionaries containing details about
            the new ads - title, description, price and URL.

        Returns:
            Tuple[str, str]: A tuple containing the subject and the body of the email.

        """
        email_body_elements = []
        for index, new_ad_details in enumerate(new_ads, start=1):
            ad_string = Messenger.generate_ad_string(index, new_ad_details)
            email_body_elements.append(ad_string)

        search_term = extract_search_term(target_url)
        # Set custom notification string below
        email_subject = f"OLXRadar: {len(new_ads)} new ads"
        if search_term is not None:
            email_subject += f" for the term '{search_term.title()}'"
        email_body = "\n".join(email_body_elements)
        return email_subject, email_body

    @staticmethod
    def send_email_message(subject: str, message: str) -> None:
        """
        Send the recipient an email with the given subject and message.

        Params:
            Subject (str): Subject of the email.
            message (str): Body of the message.

        Returns:
            None

        Raises:
            SMTPAuthenticationError: If the authentication data is incorrect.
            SMTPException: If an error occurs while sending the email.
        """
        try:
            subject = str(subject)
            message = str(message)
            message = f"""Subject: {subject}\n\n{message}"""
            message = normalize_text(message)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=context) as server:
                server.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
                server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, message)
                server.quit()
        except (smtplib.SMTPAuthenticationError, smtplib.SMTPException) as error:
            logging.error(f"Error sending email notification: {error}")
        logging.info("Email notification sent successfully")

    @staticmethod
    def send_telegram_message(message_subject: str, message_body: str) -> None:
        """
        Send a message via Telegram. The service accepts messages up to
        4096 characters or less, so the notification will be divided into sections of
        no more than 4000 characters.

        Args:
            message_subject (str): The subject of the notification(s) to be sent.
            message_body (str): Body of the message to be sent.

        Returns:
            None

        Raises:
            requests.exceptions.RequestException: In case an error is generated during the transmission.
        """
        endpoint = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        max_length = 4000
        message_batches = []
        current_message = ""
        # Split messages into sections
        chunks = message_body.split("\n\n")
        for chunk in chunks:
            if len(current_message) + len(chunk) <= max_length:
                current_message += chunk + "\n\n"
            else:
                message_batches.append(current_message.strip())
                current_message = chunk + "\n\n"
        message_batches.append(current_message.strip())

        # Send each batch as a separate notification in the same chain
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
                    logging.info("Email notification sent successfully")
                else:
                    logging.error(
                        "Error sending Telegram notification")
            except requests.exceptions.RequestException as error:
                logging.error(f"Telegram connection error: {error}")

    @staticmethod
    def _get_telegram_bot_chats() -> list:
        """
        Helper function to get the details of all the chats in which
        a bot is participating.

        Returns:
            chats (list[dict]): A unique list of dictionaries, each continaing the details of
            a chat. For a private chat, the details are: 'id', 'type', 'first_name', 'last_name',
            'username'. For a group chat, the details are: 'id', 'type', 'title',
            'all_members_are_administrators'. In case of an error, it returns an emtpy list.
        """
        endpoint = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()
            results = data.get("result", [])
            chats = []
            for result in results:
                chat = result.get("message", {}).get("chat")
                if chat not in chats:
                    chats.append(chat)
            return chats
        except requests.exceptions.RequestException as error:
            logging.error(f"Error getting Telegram bot chat data: {error}")
            return []

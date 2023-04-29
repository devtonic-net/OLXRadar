![OLXRadar](https://i.imgur.com/umVlxwV.jpeg)
# OLXRadar
Get notified instantly of new listings on OLX with this Python app that sends alerts via Telegram and email.

## Prerequisites

Before running the app, you must have the following installed:

* Python 3.x
* A Gmail account and a Gmail app password (see below how to get one)
* A Telegram bot (see below how to create one)

## Installation

1. Clone/download this repository to your local machine.
2. Open a terminal and navigate to the project directory.
3. Create a new virtual environment by running the following command:
   ```
   python3 -m venv venv
   ```
4. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```
5. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
6. Setup your Telegram bot:
   1. Create a new bot by talking to the [BotFather](https://t.me/BotFather).
   2. Copy the bot token.
   3. Send a message to your bot and get the chat ID.
   4. Copy the chat ID.
   5. Create a file named `.env` in the project directory.
   4. Add the following lines to the `.env` file:
      ```
      TELEGRAM_BOT_TOKEN="your_token_here"
      TELEGRAM_CHAT_ID="your_chat_id_here"
      ```
      [👉 detailed instructions on how to get the bot token and chat ID](https://12ft.io/proxy?q=https%3A%2F%2Fmedium.com%2Fcodex%2Fusing-python-to-send-telegram-messages-in-3-simple-steps-419a8b5e5e2)


7. Setup your Gmail app password:
   1. Go to [Google Account Security](https://myaccount.google.com/security).
   2. Select **Two Step Verification** and click **App Password**.
   3. Select **Mail** and **Other (custom name)**.
   4. Enter a name for the app password, such as "OLXRadar".
   5. Copy the generated password.
   6. Add the following lines to the `.env` file:
      ```
      EMAIL_SENDER="your_sender_email_here@gmail.com"
      EMAIL_RECEIVER="your_receiver_email_here@domain.com"
      EMAIL_APP_PASSWORD="your_app_password"
      ```
8. Add a product URL to monitor:
   1. Search for a product on [www.olx.ro](https://www.olx.ro/).
   2. Copy the URL of the search results page.
   3. Add the URL to `target_urls.txt`, located in the project directory. Add one URL per line.

![How to get a search url](https://i.imgur.com/9tEANnp.png)

## Usage. How to schedule the app to run at fixed intervals

**On Windows**

Make sure you logged on as an administrator or you have the same access as an administrator, then go to:

```
Start -> Control Panel -> System and Security -> Administrative Tools -> Task Scheduler
Action -> Create Basic Task -> Type a name and Click Next
```    
Follow through the wizard.


**On Linux**
   
   1. Open the crontab configuration file by running the following command:
      ```
      crontab -e
      ```
   2. Add the following line to the end of the file to run the app every 30 minutes:
      ```
      */30 * * * * /path/to/OLXRadar/venv/bin/python /path/to/OLXRadar/main.py
      ```
      Replace `/path/to/OLXRadar` with the actual path to the project directory.

The app will fetch the list of URLs to monitor from `target_urls.txt`, scrape new ads, and send alerts via email and Telegram.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# 11/15/2023
# A program that monitors and regularly e-mails updates about the prices of silver.

import requests
import smtplib
import logging
import json

from requests.exceptions import RequestException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

config_file = open("config.json", "r")
config = json.load(config_file)

SERVICE_URL = config["SERVICE_URL"]
API_KEY = config["API_KEY"]
EMAIL_USERNAME = config["EMAIL_USERNAME"]
EMAIL_PASSWORD = config["EMAIL_PASSWORD"]
RECEIVING_EMAIL = config["RECEIVNG_EMAIL"]

logging.basicConfig(filename="silver.log", level=logging.INFO)


def get_prices():
    try:
        # Send a request to the gold/silver prices server

        ag_rsp = requests.get(SERVICE_URL.format("XAG"), headers={
            "Content-Type": "application/json",
            "x-access-token": API_KEY
        })

        ag_rsp.raise_for_status()

        au_rsp = requests.get(SERVICE_URL.format("XAU"), headers={
            "Content-Type": "application/json",
            "x-access-token": API_KEY
        })

        au_rsp.raise_for_status()

        # Retrieve the price of the silver, and gold from the JSON text.
        
        agprice = "$" + str(json.loads(ag_rsp.text)["price"])
        auprice = "$" + str(json.loads(au_rsp.text)["price"])
        
        print(f"Silver price acquired: {agprice}")
        print(f"Gold price acquired: {auprice}")

        return agprice, auprice
    
    except RequestException as e:
        print(f"Error finding prices for metals: {str(e)}")
        logging.debug(f"ERROR: {str(e)}")


def send_email():
    # Create a new email message.

    msg = MIMEMultipart()

    msg["From"] = EMAIL_USERNAME
    msg["To"] = RECEIVING_EMAIL
    msg["Subject"] = "Metal Pricing"

    price_ag, price_au = get_prices()

    msg.attach(MIMEText(f"""<p>Hello,</p>
                        <p>The current daily price of silver is: <b>{price_ag}</b></p>
                        <p>The current daily price of gold is: <b>{price_au}</b></p>""", 'html'))

    # Start a SMTP client and send the e-mail.

    try:
        server = smtplib.SMTP('smtp.gmail.com', port=587, timeout=10)
        server.ehlo()
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USERNAME, RECEIVING_EMAIL, msg.as_string())
        server.quit()

        logging.info(f"Successfully sent e-mail to {RECEIVING_EMAIL}")
        
    except Exception as e:
        print("Failed to send e-mail: Connection timeout")
        logging.debug(f"Could not send e-mail: {e}")


def main():
    send_email()


if __name__ == "__main__":
    # TODO: constantly run the file and send an email at a specific date and time
    # TODO: also implement a feature showing the previous daily price
    main()

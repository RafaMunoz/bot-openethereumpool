#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import configparser
import telebot
import pymongo
import urllib3
import json
import os
from datetime import datetime

# Go to directory
directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(directory)


# Request to API data
def requestAPI(argUrl):
    try:
        response = http.request('GET', argUrl)
        if response.status != 200:
            data_json = {"ok": False, "error_code": response.status, "description": response.data.decode('utf-8')}
        else:
            data_json = json.loads(response.data.decode('utf-8'))
        return data_json

    except Exception as e2:
        data_json = {"ok": False, "description": str(e2)}
        return data_json


# ---------- Settings Config ----------
conf = configparser.ConfigParser()
conf.read('conf/OpenEthereumPool.conf')
LOG = conf['BASIC']['pathLog']
TOKEN = conf['BASIC']['tokenBot']
MONGOCONNECTION = conf['BASIC']['connectMongoDB']
BLOCKSSTATS = conf['API']['blocksStats']
FILELOG = conf['BASIC']['fileLog']
PAYMENTS = conf['API']['payments']
# -------------------------------------
# ---------- Logging ----------
if not os.path.exists('log'):
    os.makedirs('log')

logger = logging.getLogger('checkPayments')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if FILELOG == "enabled":
    fh = logging.FileHandler(LOG)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

# -----------------------------

logger.info("--- Start CheckPayments ---")

# Object for TelegramBot
bot = telebot.TeleBot(TOKEN)

# Connect to DB
db = pymongo.MongoClient(MONGOCONNECTION).get_database()
usersCol = db.Users
paymentsCol = db.Payments
adressCol = db.Addresses

# Object for API request
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager()

# Search payments
res = requestAPI(PAYMENTS)

# Check total payments if first time save in db
total_payments = int(res["paymentsTotal"])
tpdb = paymentsCol.find_one({'_id': "paymentsTotal"})

if tpdb is not None:
    total_payments_db = tpdb["paymentsTotal"]
else:
    logger.debug("First time save payments in db")

    total_payments_db = total_payments
    paymentsCol.insert_one({'_id': "paymentsTotal", "paymentsTotal": total_payments})

    for payment in res["payments"]:
        paymentsCol.insert_one(payment)

if total_payments > total_payments_db:

    for payment_res in res["payments"]:

        address = payment_res["address"]
        timestamp = payment_res["timestamp"]
        amount = round(int(payment_res["amount"]) / 1000000000, 3)
        tx = payment_res["tx"]

        date = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S %d-%m-%Y")

        # We search if the tx has already been notified
        tx_db = paymentsCol.find_one({'tx': tx})
        logger.debug("Search tx in db: {0}".format(payment_res))

        if tx_db is None:

            owners_address = adressCol.find({"address": address})

            # Search the owners for adresses in db
            for addr in owners_address:

                name_address = addr["name"]
                user_id = addr["idUser"]

                # Send notification to users with notification = true
                users = usersCol.find(
                    {"_id": user_id,
                     "$or": [{"notification_payments": {"$exists": False}}, {"notification_payments": True}]})

                for user in users:
                    try:
                        message = "💵 *New payment!*\n\n*Date*: {0}\n*Amount*: `{1} ETH`\n*Address*: `{2}`\n" \
                                  "[+info](https://etherscan.io/tx/{3})".format(date, amount, name_address, tx)

                        bot.send_message(chat_id=user["_id"], text=message, parse_mode='Markdown')
                        logger.debug("Send message to user: {0}".format(user["_id"]))

                    except:
                        logger.error("Error send message to user: {0}".format(user["_id"]))

            # Save tx in db
            paymentsCol.insert_one(payment_res)
            logger.debug("Save tx in db: {0}".format(payment_res))

    paymentsCol.update_one({'_id': "paymentsTotal"}, {"$set": {"paymentsTotal": total_payments}}, upsert=True)

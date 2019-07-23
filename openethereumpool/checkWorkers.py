#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import configparser
import telebot
from pymongo import MongoClient
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
POOLSTATS = conf['API']['poolStats']
ADDRESSSTATS = conf['API']['addressStats']
FILELOG = bool(conf['BASIC']['fileLog'])
# -------------------------------------
# ---------- Logging ----------
if not os.path.exists('log'):
    os.makedirs('log')

logger = logging.getLogger('checkWorkers')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if FILELOG:
    fh = logging.FileHandler(LOG)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)
# -----------------------------

logger.info("--- Start CheckWorkers ---")

# Object for TelegramBot
bot = telebot.TeleBot(TOKEN)

# Connect to DB
connectDB = MongoClient(MONGOCONNECTION)
db = connectDB.OpenEthereumPool
addrCol = db.Addresses

# Object for API request
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager()

# Find adresses with notifications actived
address = addrCol.find({'notifications': True})
logger.debug("Search addresses notifications=True")

for address in address:
    try:
        idUser = address['idUser']
        addrCode = address['address']
        idDoc = address['_id']
        lastStatusWorkers = address['statusWorkers']

        textMessage = "Change workers status:\n"
        textMessage2 = "Change workers status:\n"

        logger.debug("idUser: {0}, address: {1}".format(idUser, addrCode))

        # Checks stats for address
        urlStatsAddr = ADDRESSSTATS + addrCode
        responseStats = requestAPI(urlStatsAddr)

        statusWorkers = {}
        for worker in responseStats['workers']:
            statusWorkers[worker] = responseStats['workers'][worker]['offline']

        logger.debug("Status workers for address: {0} {1}".format(addrCode, statusWorkers))

        # Compare status of workers
        for w in lastStatusWorkers:
            if lastStatusWorkers[w] != statusWorkers[w]:
                logger.debug("Change worker status {0}: {1} -> {2}".format(w, lastStatusWorkers[w], statusWorkers[w]))

                if not statusWorkers[w]:
                    textMessage2 = (textMessage2 + "   - *{0}* -> " + u"\u2705\n").format(w)

                else:
                    textMessage2 = (textMessage2 + "   - *{0}* -> " + u"\u274C\n").format(w)

        if textMessage != textMessage2:
            bot.send_message(chat_id=idUser, text=str(textMessage2), parse_mode='Markdown')
            logger.debug("Send message {0}".format(idUser))

        # Update the status workers in DB
        addrCol.update_one({"_id": idDoc},
                           {"$set": {"statusWorkers": statusWorkers, "lastCheck": datetime.now().isoformat()}})
        logger.debug("Update status workers for {0}".format(addrCode))

    except Exception as e:
        logger.error(e)

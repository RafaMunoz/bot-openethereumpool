#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import configparser
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os.path
from pymongo import MongoClient
import urllib3
import json
import re
import os
from conf.lang import translations


# Function for thousand separator
def thousandSep(number):
    return f'{int(number):,}'


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


# Function user information
def infoUser(message):
    logger.debug("New Message -> idUser: {0}, username: {1}, message: {2}".format(message.from_user.id,
                                                                                  message.from_user.username,
                                                                                  message.text))

    idUser = message.from_user.id
    name = message.from_user.first_name
    lastName = message.from_user.last_name
    username = message.from_user.username
    languageCode = message.from_user.language_code
    registrationDate = datetime.utcnow()

    userDocument = {
        '_id': str(idUser),
        'username': username,
        'name': name,
        'lastName': lastName,
        'languageCode': languageCode,
        'registrationDate': registrationDate,
        'lastMessage': {
            'type': '',
            'idMessage': '',
            'text': ''
        }
    }

    if languageCode not in translations:
        userDocument['languageApp'] = 'en'
    else:
        userDocument['languageApp'] = languageCode

    return userDocument


# Function user information on callback
def infoUserCallback(message):
    logger.debug("New Callback -> idUser: {0}, username: {1}, message: {2}".format(message.from_user.id,
                                                                                   message.from_user.username,
                                                                                   message.data))

    idUser = message.from_user.id
    name = message.from_user.first_name
    lastName = message.from_user.last_name
    username = message.from_user.username
    languageCode = message.from_user.language_code
    registrationDate = datetime.utcnow()

    userDocument = {
        '_id': str(idUser),
        'username': username,
        'name': name,
        'lastName': lastName,
        'languageCode': languageCode,
        'registrationDate': registrationDate,
        'lastMessage': {
            'type': '',
            'idMessage': '',
            'text': ''
        }
    }

    if languageCode not in translations:
        userDocument['languageApp'] = 'en'
    else:
        userDocument['languageApp'] = languageCode

    return userDocument


# Function for check if user is new
def checkUser(userDocument):
    # Find the user in the DB
    userDocument2 = userColl.find_one({"_id": userDocument['_id']})
    if userDocument2 is None:
        logger.info("New user: {0}".format(userDocument))
        userColl.insert_one(userDocument)

        return userDocument

    else:
        return userDocument2


# Keyboard to select stats
def keyboardStats1(infoUserDB):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton(translations[infoUserDB['languageApp']]['statsp2m'], callback_data="statsp2m"),
               InlineKeyboardButton(translations[infoUserDB['languageApp']]['statsaddr'], callback_data="statsaddr"))

    return markup


# Keyboard to return select stats
def keyboardStats2(infoUserCall):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(translations[infoUserCall['languageApp']]['return'], callback_data="statsReturn"))

    return markup


# Keyboard to return select stats for address
def keyboardStats3(infoUserCall):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(translations[infoUserCall['languageApp']]['return'], callback_data="statsaddr"))

    return markup


# Keyboard to return select stats for myaddrs
def keyboardReturnMyAddrs(infoUserCall):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(translations[infoUserCall['languageApp']]['return'], callback_data="myAddrs"))

    return markup


# Keyboard to list address
def keyboardAddress(infoUserCall, addresses, prefix, buttonReturn=True):
    # We get number of addresses and if it's even or odd
    i = addresses.count()
    j = 0
    modI = i % 2

    markup = InlineKeyboardMarkup()
    markup.row_width = 2

    if i == 1:
        markup.add(InlineKeyboardButton(addresses[0]['name'], callback_data=prefix + addresses[0]['address']))

    else:
        # If it's odd
        if modI == 1:
            for j in range(int((i - 1) / 2)):
                markup.add(InlineKeyboardButton(addresses[j]['name'], callback_data=prefix + addresses[j]['address']),
                           InlineKeyboardButton(addresses[j + 1]['name'],
                                                callback_data=prefix + addresses[j + 1]['address']))

            markup.add(
                InlineKeyboardButton(addresses[j + 2]['name'], callback_data=prefix + addresses[j + 2]['address']))

        # If it's even
        else:
            for j in range(int(i / 2)):
                markup.add(InlineKeyboardButton(addresses[j]['name'], callback_data=prefix + addresses[j]['address']),
                           InlineKeyboardButton(addresses[j + 1]['name'],
                                                callback_data=prefix + addresses[j + 1]['address']))

    # Button to return
    if buttonReturn:
        markup.add(
            InlineKeyboardButton(translations[infoUserCall['languageApp']]['return'], callback_data="statsReturn"))

    return markup


# Keyboard with options for address (edit, delete, view...)
def keyboardOptionsAddr(infoUserCall, address):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton(translations[infoUserCall['languageApp']]['viewStats'], callback_data="stats-" + address),
        InlineKeyboardButton(translations[infoUserCall['languageApp']]['editAddr'],
                             callback_data="editAddr-" + address),
        InlineKeyboardButton(translations[infoUserCall['languageApp']]['delAddr'], callback_data="delAddr-" + address),
        InlineKeyboardButton(translations[infoUserCall['languageApp']]['return'], callback_data="myAddrs"))

    return markup


# Keyboard confirm delete address
def keyboardDeleteAddres(infoUserCall, address):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton(translations[infoUserCall['languageApp']]['yesDelAddr'],
                             callback_data="yesDelAddr-" + address),
        InlineKeyboardButton("No", callback_data="myAddrs"))

    return markup


# Keyboard edit configuracion address (name, code)
def keyboardEditAddress(infoUserCall, address):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton(translations[infoUserCall['languageApp']]['editNameAddr'],
                             callback_data="setNameAddr-" + address),
        InlineKeyboardButton(translations[infoUserCall['languageApp']]['editCodeAddr'],
                             callback_data="setCodeAddr-" + address))

    return markup


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

logger = logging.getLogger('Pool2Mine')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if FILELOG == True:
    fh = logging.FileHandler(LOG)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)
# -----------------------------

logger.info("--- Start the bot Pool2Mine ---")

# Object for TelegramBot
bot = telebot.TeleBot(TOKEN)

# Connect to DB
connectDB = MongoClient(MONGOCONNECTION)
db = connectDB.BotPool2Mine
userColl = db.Users
addrCol = db.Addresses

# Object for API request
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager()


# ---------- Comands ----------

# Message for command /start
@bot.message_handler(commands=['start'])
def message_start(message):
    infoUserDB = checkUser(infoUser(message))
    bot.send_message(chat_id=infoUserDB['_id'], text=str(translations[infoUserDB['languageApp']]['startMessage']),
                     parse_mode='Markdown')


# Message for command /seestats
@bot.message_handler(commands=['seestats'])
def message_seestats(message):
    infoUserDB = checkUser(infoUser(message))
    bot.send_message(chat_id=infoUserDB['_id'], text=str(translations[infoUserDB['languageApp']]['stats1']),
                     reply_markup=keyboardStats1(infoUserDB))


# Message for command /myaddrs
@bot.message_handler(commands=['myaddrs'])
def message_myaddrs(message):
    infoUserDB = checkUser(infoUser(message))
    logger.debug("Search addresses for user: {0}".format(infoUserDB['_id']))
    addrs = addrCol.find({"idUser": infoUserDB['_id']})
    logger.debug("Send keyboard myAddrs to user: {0}".format(infoUserDB['_id']))

    if addrs.explain()['executionStats']['nReturned'] == 0:
        logger.info("Found 0 Address User: {0}".format(infoUserDB['_id']))
        bot.send_message(chat_id=infoUserDB['_id'],
                         text=u"\u26A0 " + str(translations[infoUserDB['languageApp']]['noneAddr']))

    else:
        bot.send_message(chat_id=infoUserDB['_id'], text=str(translations[infoUserDB['languageApp']]['selectAddr']),
                         reply_markup=keyboardAddress(infoUserDB, addrs, 'myaddr-', False))


# Message for command /newaddr
@bot.message_handler(commands=['newaddr'])
def message_newaddr(message):
    infoUserDB = checkUser(infoUser(message))
    response = bot.send_message(chat_id=infoUserDB['_id'], text=str(translations[infoUserDB['languageApp']]['newAddr']),
                                parse_mode='Markdown')
    userColl.update_one({"_id": str(infoUserDB['_id'])},
                        {"$set": {"lastMessage.type": "newaddr", "lastMessage.idMessage": str(response.message_id)}})


# Message for command /deleteaddr
@bot.message_handler(commands=['deleteaddr'])
def message_deleteaddr(message):
    infoUserDB = checkUser(infoUser(message))
    logger.debug("Search addresses for user: {0}".format(infoUserDB['_id']))
    addrs = addrCol.find({"idUser": infoUserDB['_id']})

    if addrs.explain()['executionStats']['nReturned'] == 0:
        logger.info("Found 0 Address User: {0}".format(infoUserDB['_id']))
        bot.send_message(chat_id=infoUserDB['_id'],
                         text=u"\u26A0 " + str(translations[infoUserDB['languageApp']]['noneAddr']))

    else:
        bot.send_message(chat_id=infoUserDB['_id'], text=str(translations[infoUserDB['languageApp']]['delAddrC']),
                         reply_markup=keyboardAddress(infoUserDB, addrs, 'delAddr-', False))


# Message for command /setname
@bot.message_handler(commands=['setname'])
def message_setname(message):
    infoUserDB = checkUser(infoUser(message))
    logger.debug("Search addresses for user: {0}".format(infoUserDB['_id']))
    addrs = addrCol.find({"idUser": infoUserDB['_id']})

    if addrs.explain()['executionStats']['nReturned'] == 0:
        logger.info("Found 0 Address User: {0}".format(infoUserDB['_id']))
        bot.send_message(chat_id=infoUserDB['_id'],
                         text=u"\u26A0 " + str(translations[infoUserDB['languageApp']]['noneAddr']))

    else:
        bot.send_message(chat_id=infoUserDB['_id'], text=str(translations[infoUserDB['languageApp']]['setnameAddrC']),
                         reply_markup=keyboardAddress(infoUserDB, addrs, 'setNameAddr-', False))

# Message for command /setaddress
@bot.message_handler(commands=['setaddress'])
def message_setname(message):
    infoUserDB = checkUser(infoUser(message))
    logger.debug("Search addresses for user: {0}".format(infoUserDB['_id']))
    addrs = addrCol.find({"idUser": infoUserDB['_id']})

    if addrs.explain()['executionStats']['nReturned'] == 0:
        logger.info("Found 0 Address User: {0}".format(infoUserDB['_id']))
        bot.send_message(chat_id=infoUserDB['_id'],
                         text=u"\u26A0 " + str(translations[infoUserDB['languageApp']]['noneAddr']))

    else:
        bot.send_message(chat_id=infoUserDB['_id'], text=str(translations[infoUserDB['languageApp']]['setcodeAddrC']),
                         reply_markup=keyboardAddress(infoUserDB, addrs, 'setCodeAddr-', False))

# -----------------------------

# ---------- Callbacks ----------

# Callback from inlinekeyboards
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    infoUserCall = infoUserCallback(call)

    # Send stats Pool
    if call.data == "statsp2m":
        response = requestAPI(POOLSTATS)
        logger.debug("Response API: {0}".format(response))
        hashrate = str(round(response['hashrate'] / 1000000000, 2)) + " GH"
        networkDificult = str(round(int(response['nodes'][0]['difficulty']) / 1000000000000000, 3)) + " P"
        networkHashrate = str(round(int(response['nodes'][0]['lastBeat']) / 10000000, 2)) + " TH"
        messageText = u"\U0001F465 Miners Online: *{0}*\n\n".format(response['minersTotal'])
        messageText = messageText + u"\U0001F6A7 Pool Hash Rate: *{0}*\n\n".format(hashrate)
        messageText = messageText + u"\U0001F552 Last Block Found: *{0} hours ago*\n\n".format(response['maturedTotal'])
        messageText = messageText + u"\U0001F513 Network Difficulty: *{0}*\n\n".format(networkDificult)
        messageText = messageText + u"\u26A1 Network Hash Rate: *{0}*\n\n".format(networkHashrate)
        messageText = messageText + u"\U0001F4F6 Blockchain Height: *{0}*".format(
            thousandSep(response["nodes"][0]["height"]))

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messageText,
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardStats2(infoUserCall))

    # Select address for view stats
    elif call.data == "statsaddr":
        logger.debug("Search addresses for user: {0}".format(infoUserCall['_id']))
        addrs = addrCol.find({"idUser": infoUserCall['_id']})

        if addrs.explain()['executionStats']['nReturned'] == 0:
            logger.info("Found 0 Address User: {0}".format(infoUserCall['_id']))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=u"\u26A0 " + str(translations[infoUserCall['languageApp']]['noneAddr']))

        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=translations[infoUserCall['languageApp']]['selectAddr'])
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=keyboardAddress(infoUserCall, addrs, 'stats-', True))

    # Return to select address for view stats
    elif call.data == "statsReturn":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=str(translations[infoUserCall['languageApp']]['stats1']))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardStats1(infoUserCall))

    # Search stats for one address
    elif re.search("^stats-+", call.data):
        addressCode = str(call.data).replace('stats-', '')
        logger.debug("Check stats for User: {0} Code Address {1}".format(infoUserCall['_id'], addressCode))
        urlStatsAddr = ADDRESSSTATS + addressCode
        responseStats = requestAPI(urlStatsAddr)
        logger.debug("Response API: {0}".format(responseStats))

        if 'ok' in responseStats and responseStats['error_code'] == 404:
            logger.info('No information for the address: {0}'.format(addressCode))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=translations[infoUserCall['languageApp']]['noStats'])
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=keyboardStats3(infoUserCall))
        else:
            currentHashrate = str(round(responseStats['currentHashrate'] / 1000000000, 2)) + " GH"
            hashrate = str(round(responseStats['hashrate'] / 1000000000, 2)) + " GH"

            messageText = u"\U0001F6A7  *Hashrate:*\n"
            messageText = messageText + "   - Current Hashrate (30m): *{0}*\n".format(currentHashrate)
            messageText = messageText + "   - Hashrate (3h): *{0}*\n\n".format(hashrate)
            messageText = messageText + u"\U0001F4E6 Blocks Found: *{0}*\n\n".format(
                responseStats['stats']['blocksFound'])
            messageText = messageText + u"\U0001F4B6 *Payments:*\n"
            messageText = messageText + "   - Total Payments: *{0}*\n".format(responseStats['paymentsTotal'])
            messageText = messageText + "   - Total Paid: *{0}*\n\n".format(responseStats['stats']['paid'] / 1000000000)
            messageText = messageText + u"\u2699 *Workers:*\n"
            messageText = messageText + "   - Online: *{0}*\n".format(responseStats['workersOnline'])
            messageText = messageText + "   - Offline: *{0}*\n".format(responseStats['workersOffline'])
            messageText = messageText + "   - Total: *{0}*\n".format(responseStats['workersTotal'])

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messageText,
                                  parse_mode='Markdown')
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=keyboardStats3(infoUserCall))

    # Return to keyboard myAddrs
    elif call.data == "myAddrs":
        logger.debug("Search addresses for user: {0}".format(infoUserCall['_id']))
        addrs = addrCol.find({"idUser": infoUserCall['_id']})
        logger.debug("Send keyboard myAddrs to user: {0}".format(infoUserCall['_id']))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=translations[infoUserCall['languageApp']]['selectAddr'],
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=infoUserCall['_id'], message_id=call.message.message_id,
                                      reply_markup=keyboardAddress(infoUserCall, addrs, 'myaddr-', False))

    # Send keyboard for edit information address
    elif re.search("^myaddr-+", call.data):
        logger.debug("Send keyboard edit information address {0}".format(infoUserCall['_id']))
        addressCode = str(call.data).replace('myaddr-', '')
        addresName = (addrCol.find_one({"address": addressCode, "idUser": infoUserCall['_id']}))['name']
        messageText = translations[infoUserCall['languageApp']]['viewAddr']
        messageText = messageText.replace("<NAMEADDRESS>", addresName)
        messageText = messageText.replace("<ADDRESS>", addressCode)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messageText,
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardOptionsAddr(infoUserCall, addressCode))

    # Callback to delete address
    elif re.search("^delAddr-+", call.data):
        addressCode = str(call.data).replace('delAddr-', '')
        addresName = (addrCol.find_one({"address": addressCode, "idUser": infoUserCall['_id']}))['name']
        messageText = translations[infoUserCall['languageApp']]['delAddr2']
        messageText = messageText.replace("<NAMEADDRESS>", addresName)
        messageText = messageText.replace("<ADDRESS>", addressCode)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=messageText,
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardDeleteAddres(infoUserCall, addressCode))

    # Callback confirmed delete address
    elif re.search("^yesDelAddr-+", call.data):
        addressCode = str(call.data).replace('yesDelAddr-', '')
        logger.info("Delete addres {0} user: {1}".format(addressCode, infoUserCall['_id']))
        addrCol.delete_one({"address": addressCode, "idUser": infoUserCall['_id']})
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=translations[infoUserCall['languageApp']]['addrDelOk'],
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardReturnMyAddrs(infoUserCall))

    # Callback for send keyboard to edit address
    elif re.search("^editAddr-+", call.data):
        addressCode = str(call.data).replace('editAddr-', '')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=translations[infoUserCall['languageApp']]['optEdit'],
                              parse_mode='Markdown')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyboardEditAddress(infoUserCall, addressCode))

    # Callback edit name for adress
    elif re.search("^setNameAddr-+", call.data):
        addressCode = str(call.data).replace('setNameAddr-', '')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=translations[infoUserCall['languageApp']]['newNameAddr'],
                              parse_mode='Markdown')

        logger.debug(
            "Update lastMessage.type -> setnameaddr user {0} address: {1}".format(infoUserCall['_id'], addressCode))
        userColl.update_one({"_id": str(infoUserCall['_id'])},
                            {"$set": {"lastMessage.type": "setnameaddr",
                                      "lastMessage.idMessage": str(call.message.message_id),
                                      "lastMessage.text": addressCode}})

    # Callback edit code for adress
    elif re.search("^setCodeAddr-+", call.data):
        addressCode = str(call.data).replace('setCodeAddr-', '')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=translations[infoUserCall['languageApp']]['newCodeAddr'],
                              parse_mode='Markdown')

        logger.debug(
            "Update lastMessage.type -> setCodeAddr user {0} address: {1}".format(infoUserCall['_id'], addressCode))
        userColl.update_one({"_id": str(infoUserCall['_id'])},
                            {"$set": {"lastMessage.type": "setcodeaddr",
                                      "lastMessage.idMessage": str(call.message.message_id),
                                      "lastMessage.text": addressCode}})
    else:
        logger.warning("Unidentified callback: {0}".format(call.data))


# -------------------------------

# ---------- Others messages ----------

@bot.message_handler(func=lambda message: True)
def message_other(message):
    infoUserDB = checkUser(infoUser(message))

    # Insert name for new address
    if infoUserDB['lastMessage']['type'] == 'newaddr':
        logger.debug("Save the name address on lastMessage -> idUser: {0}, nameAddr: {1}".format(infoUserDB['_id'],
                                                                                                 message.text))
        response = bot.send_message(chat_id=infoUserDB['_id'],
                                    text=str(translations[infoUserDB['languageApp']]['newAddr2']),
                                    parse_mode='Markdown')
        userColl.update_one({"_id": str(infoUserDB['_id'])}, {
            "$set": {"lastMessage.type": "newaddr2", "lastMessage.idMessage": str(response.message_id),
                     "lastMessage.text": message.text}})

    # Insert new address
    elif infoUserDB['lastMessage']['type'] == 'newaddr2':
        logger.debug('Insert new address -> idUser: {0}, nameAddr: {1}, address: {2}'.format(infoUserDB['_id'],
                                                                                             infoUserDB['lastMessage'][
                                                                                                 'text'], message.text))

        addrCol.insert_one(
            {'name': infoUserDB['lastMessage']['text'], "address": message.text, "idUser": infoUserDB['_id']})

        messageText = str(translations[infoUserDB['languageApp']]['newAddr3'])
        messageText = messageText.replace("<NAMEADDRESS>", infoUserDB['lastMessage']['text'])
        messageText = messageText.replace("<ADDRESS>", message.text)

        bot.send_message(chat_id=infoUserDB['_id'], text=messageText, parse_mode='Markdown')
        userColl.update_one({"_id": str(infoUserDB['_id'])},
                            {"$set": {"lastMessage.type": "", "lastMessage.idMessage": "", "lastMessage.text": ""}})

    # Edit address name
    elif infoUserDB['lastMessage']['type'] == 'setnameaddr':
        logger.debug("Update the name address user: {0} address: {1} new_name: {2}".format(infoUserDB['_id'],
                                                                                           infoUserDB['lastMessage'][
                                                                                               'text'], message.text))
        addrCol.update_one({"idUser": str(infoUserDB['_id']), "address": infoUserDB['lastMessage']['text']},
                           {"$set": {"name": message.text}})
        userColl.update_one({"_id": str(infoUserDB['_id'])},
                            {"$set": {"lastMessage.type": "", "lastMessage.idMessage": "", "lastMessage.text": ""}})

        infoAddr = addrCol.find_one({'idUser': str(infoUserDB['_id']), "address": infoUserDB['lastMessage']['text']})

        messageText = str(translations[infoUserDB['languageApp']]['addrUpdate'])
        messageText = messageText.replace("<NAMEADDRESS>", infoAddr['name'])
        messageText = messageText.replace("<ADDRESS>", infoAddr['address'])
        bot.send_message(chat_id=infoUserDB['_id'], text=messageText, parse_mode='Markdown')

    # Edit address code
    elif infoUserDB['lastMessage']['type'] == 'setcodeaddr':
        logger.debug("Update the code address user: {0} address: {1} new_code: {2}".format(infoUserDB['_id'],
                                                                                           infoUserDB['lastMessage'][
                                                                                               'text'], message.text))
        addrCol.update_one({"idUser": str(infoUserDB['_id']), "address": infoUserDB['lastMessage']['text']},
                           {"$set": {"address": message.text}})
        userColl.update_one({"_id": str(infoUserDB['_id'])},
                            {"$set": {"lastMessage.type": "", "lastMessage.idMessage": "", "lastMessage.text": ""}})

        infoAddr = addrCol.find_one({'idUser': str(infoUserDB['_id']), "address": message.text})

        messageText = str(translations[infoUserDB['languageApp']]['addrUpdate'])
        messageText = messageText.replace("<NAMEADDRESS>", infoAddr['name'])
        messageText = messageText.replace("<ADDRESS>", infoAddr['address'])
        bot.send_message(chat_id=infoUserDB['_id'], text=messageText, parse_mode='Markdown')

    else:
        logger.warning("Unidentified message: {0}".format(message.text))


bot.polling(none_stop=True)

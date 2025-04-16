import os
import re
from os import environ
from urllib.parse import quote_plus

id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '634637418').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-1002212156629').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
PREMIUM_USER = [int(user) if id_pattern.search(user) else user for user in environ.get('PREMIUM_USER', '5651594253').split()]
auth_channel = environ.get('AUTH_CHANNEL','')#-1002548989153')
auth_grp = environ.get('AUTH_GROUP','-1002214107507')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None
support_chat_id = environ.get('SUPPORT_CHAT_ID','')
reqst_channel = environ.get('REQST_CHANNEL_ID','')
REQST_CHANNEL = int(reqst_channel) if reqst_channel and id_pattern.search(reqst_channel) else None
SUPPORT_CHAT_ID = int(support_chat_id) if support_chat_id and id_pattern.search(support_chat_id) else None
NO_RESULTS_MSG = is_enabled((environ.get("NO_RESULTS_MSG", 'True')), False)
CHNL_LNK = "https://t.me/MINI_GAMES_ASSOCIATION"
GRP_LNK = "https://t.me/MINI_GAMES_CHAT"
PICS = ["https://telegra.ph/file/58116c99883d2d87233da.jpg","https://telegra.ph/file/53317151ec8a730451135.jpg","https://telegra.ph/file/2e797f914ce653bf844a8.jpg", "https://telegra.ph/file/fc9c42ceeab0d92ccbddd.jpg"] 


DATABASE_URI = "mongodb+srv://razerax:razerax@mg.ke2dgwg.mongodb.net/?retryWrites=true&w=majority&appName=mg"

DATABASE_NAME = environ.get('DATABASE_NAME', 'mg')


# Others
VERIFY = bool(environ.get('VERIFY', False))
SHORTLINK_URL2 = environ.get('SHORTLINK_URL', 'urlshortx.com')
SHORTLINK_API2 = environ.get('SHORTLINK_API', 'eff81ef8a6d0e76498ab428cae7d964731ca6772')
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'api.shareus.io')
SHORTLINK_API = environ.get('SHORTLINK_API', 'lVSWhw4wnGaKDSDltbmcmYGQlkK2')
SECOND_SHORTLINK_URL = environ.get('SECOND_SHORTLINK_URL', 'api.shareus.io')
SECOND_SHORTLINK_API = environ.get('SECOND_SHORTLINK_API', 'lVSWhw4wnGaKDSDltbmcmYGQlkK2')
IS_SHORTLINK = bool(environ.get('IS_SHORTLINK', True))
DELETE_CHANNELS = [int(dch) if id_pattern.search(dch) else dch for dch in environ.get('DELETE_CHANNELS', '0').split()]
PORT = environ.get("PORT", "8080")
UPDATE_CHANNEL = environ.get('CHNL_LNK', 'https://t.me/+OJPH-0u_62FmZjI9')
MSG_ALRT = environ.get('MSG_ALRT', '❤ ᴊᴏɪɴ @FILMZTUBE ❤')
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', -1002593796821))
MELCOW_NEW_USERS = is_enabled((environ.get('MELCOW_NEW_USERS', "True")), True)
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'MINI_GAMES_CHAT')
TUTORIAL = environ.get('TUTORIAL', 'https://t.me/filmztube_openlink/34')
BUY_PREMIUM = environ.get('TUTORIAL', 'https://t.me/filmztube_openlink/29')
AUTO_DELETE = is_enabled((environ.get('AUTO_DELETE', "True")), True)
MELCOW_VID = environ.get("MELCOW_VID", "https://graph.org/file/8faa88f9046f3f901e174.mp4")



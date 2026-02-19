import os
import re
from os import environ


id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '8226767954').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '8226767954').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
PREMIUM_USER = [int(user) if id_pattern.search(user) else user for user in environ.get('PREMIUM_USER', '8226767954').split()]
auth_channel = environ.get('AUTH_CHANNEL','-1002456565415')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
CHNL_LNK = "https://t.me/Comico_X"
GRP_LNK = "https://t.me/ComicoX_X"
    # List of picture URLs
PICS = [
         "https://telegra.ph/file/86d3b142f409d492262a8-8d091d5adb6e9ee30d.png",
         "https://telegra.ph/file/b5d8c07a5908e7b405c64-84dafb64c8d30ecf94.png",
         "https://telegra.ph/file/d379cf0dc4f206ca6751e-f46eb0ec6b2d1bbd8c.png",
         "https://telegra.ph/file/41fd776f78d2f08b867a5-697c7a9d0c16b011c8.png",
         "https://telegra.ph/file/893a191dd168ffe6fbac9-0cc9d923e7240393f2.png",
    ]
DATABASE_URI = "mongodb+srv://hanxsooyoung:qGsVMuuKjE12Gewz@cluster0.oooqdg5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = environ.get('DATABASE_NAME', 'cluster0')


# Others
VERIFY = bool(environ.get('VERIFY', False))
SHORTLINK_URL2 = environ.get('SHORTLINK_URL2', 'urlshortx.com')
SHORTLINK_API2 = environ.get('SHORTLINK_API2', 'eff81ef8a6d0e76498ab428cae7d964731ca6772')
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'api.shareus.io')
SHORTLINK_API = environ.get('SHORTLINK_API', 'lVSWhw4wnGaKDSDltbmcmYGQlkK2')
IS_SHORTLINK = bool(environ.get('IS_SHORTLINK', True))
PORT = environ.get("PORT", "8080")
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', -1002456565415))
MELCOW_NEW_USERS = is_enabled((environ.get('MELCOW_NEW_USERS', "True")), False)
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'ComicoX_X')
AUTO_DELETE = is_enabled((environ.get('AUTO_DELETE', "True")), True)





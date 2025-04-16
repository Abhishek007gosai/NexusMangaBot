import os
import time
import logging
import types
from pyrogram import Client, idle, __version__
from pyrogram.raw.all import layer
from pyrogram.errors import FloodWait
from aiohttp import web
import pytz
from datetime import date, datetime
from config import API_ID, API_HASH, BOT_TOKEN
from info import PORT, LOG_CHANNEL
from plugins.utils import temp
from plugins.__init__ import web_server
from script import Script


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.ERROR)


# Check for missing environment variables
if not all([BOT_TOKEN, API_ID, API_HASH]):
    logger.error("Missing one or more environment variables: TOKEN, API_ID, API_HASH")
    raise ValueError("Missing one or more environment variables: TOKEN, API_ID, API_HASH")

class Bot(Client):

    def __init__(self):
        super().__init__(
            name="bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self, **kwargs):
        await super().start(**kwargs)
        
        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username

        logging.info(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}.")

        tz = pytz.timezone('Asia/Kolkata')
        today = date.today()
        now = datetime.now(tz)
        time = now.strftime("%H:%M:%S %p")
        await self.send_message(chat_id=LOG_CHANNEL, text=Script.RESTART_TXT.format(today, time))

        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")





# Function to run the bot
def run_bot():
    while True:
        try:
            app.run()
            logger.info("Bot deployed successfully and running :)")
            # Keep the bot running
            idle()
            break  # Exit the loop if successful
        except FloodWait as e:
            wait_time = e.value
            logger.warning(f"Rate limited by Telegram. Waiting for {wait_time} seconds...")
            time.sleep(wait_time)  # Wait for the required time
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            break  # Exit the loop on other errors

if __name__ == "__main__":
    app = Bot()
    try:
        run_bot()
    except Exception as e:
        logger.error(f"An error occurred :- {e}")
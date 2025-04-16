import os
import time
import logging
import types
from pyrogram import Client, idle, __version__
from pyrogram.raw.all import layer
from pyfiglet import Figlet
from colorama import init, Fore, Style
from pyrogram.errors import FloodWait
from aiohttp import web
from datetime import date, datetime
import pytz
from typing import Union, Optional, AsyncGenerator
from info import API_ID, API_HASH, BOT_TOKEN, PORT, LOG_CHANNEL
from plugins.utils import temp
from plugins.__init__ import web_server
from script import Script

# Initialize colorama
init(autoreset=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

# Retrieve environment variables
TOKEN = os.environ.get("TOKEN", "")
API_ID = os.environ.get("API_ID", "")
API_HASH = os.environ.get("API_HASH", "")
STRING = os.environ.get("STRING", "")

# Check for missing environment variables
if not all([TOKEN, API_ID, API_HASH]):
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

    async def start(self):
        await super().start()
        
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

    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        current = offset
        while current < limit:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current + new_diff)))
            for message in messages:
                yield message
                current += 1

# Generate ASCII banner
def print_banner():
    figlet = Figlet(font='standard')
    ascii_art = figlet.renderText("BOT RUNNING")
    print(f"{Fore.BLUE}{Style.BRIGHT}{ascii_art}{Style.RESET_ALL}")

# Function to start the bot
def start_bot():
    while True:
        try:
            app.start()
            print_banner()
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

# Function to run the bot
def run_bot():
    while True:
        try:
            app.run()
            print_banner()
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
    if STRING:
        start_bot()
    else:
        run_bot()
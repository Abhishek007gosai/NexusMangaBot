
BOT_USERNAME = "comicoXbot"
BOT_NAME ="ComicoX"
DESC_TXT = f'<a href="https://t.me/{BOT_USERNAME}">{BOT_NAME}</a>'
EMPTY_DESC_TXT = f"Your reading {{title}} at {DESC_TXT}"

class Script:
    
      # Constants for text messages
    
    START_TXT = """<b>ʜᴇʟʟᴏ {} 👋, ɪ ᴀᴍ : <a href=https://t.me/{}>{}</a>.

ɪ ᴄᴀɴ ᴘʀᴏᴠɪᴅᴇ ᴍᴀɴɢᴀ, ᴍᴀɴʜᴡᴀ, ᴍᴀɴʜᴜᴀ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴊᴜsᴛ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴏʀ sᴇᴀʀᴄʜ ɴᴀᴍᴇs ɪɴ ᴘᴍ ᴀɴᴅ ᴇɴᴊᴏʏ.

★ ᴘᴏᴡᴇʀᴇᴅ ʙʏ : <a href={}>ᴄᴏᴍɪᴄᴏ𝗫 ᴜᴘᴅᴀᴛᴇs</a>
"""

    STATUS_TXT = """<b>
★ Tᴏᴛᴀʟ Usᴇʀs: <code>{}</code>
★ Tᴏᴛᴀʟ Cʜᴀᴛs: <code>{}</code>
★ Usᴇᴅ Sᴛᴏʀᴀɢᴇ: <code>{}</code>
★ Fʀᴇᴇ Sᴛᴏʀᴀɢᴇ: <code>{}</code></b>"""

    LOG_TEXT_G = """#NewGroup
Gʀᴏᴜᴘ = {}(<code>{}</code>)
Tᴏᴛᴀʟ Mᴇᴍʙᴇʀs = <code>{}</code>
Aᴅᴅᴇᴅ Bʏ - {}"""

    LOG_TEXT_P = """#NewUser
ID - <code>{}</code>
Nᴀᴍᴇ - {}"""
    MELCOW_ENG = """<b>Hᴇʟʟᴏ {} 🤪, Aɴᴅ Wᴇʟᴄᴏᴍᴇ Tᴏ {} Gʀᴏᴜᴘ ❤️</b>"""

    HELP_TXT = """<b>ʜᴇʏ {}
Here are all the commands you can use:
    
🔹 /start - Show welcome message
🔹 /help - Show this help message
🔹 /popular or /p - Browse popular manga
🔹 /search or /s [query] - Search for manga
🔹 /faq - Frequently asked questions</b>"""

    ABOUT_TXT = """<b>⚜️ ʙᴏᴛ ɴᴀᴍᴇ : {}
✯ ᴄʀᴇᴀᴛᴏʀ: <a href='https://t.me/bharath_boy'>ʙʜᴀʀᴀᴛʜ ʙᴏʏ</a>
✯ ʟɪʙʀᴀʀʏ: <a href='https://docs.pyrogram.org/'>ᴘʏʀᴏɢʀᴀᴍ</a>
✯ ʟᴀɴɢᴜᴀɢᴇ: <a href='https://www.python.org/download/releases/3.0/'>ᴘʏᴛʜᴏɴ 3</a>
✯ ᴅᴀᴛᴀʙᴀsᴇ: <a href='https://www.mongodb.com/'>ᴍᴏɴɢᴏᴅʙ</a>
✯ ʙᴏᴛ sᴇʀᴠᴇʀ: <a href='https://railway.app/'>ʀᴀɪʟᴡᴀʏ​</a>
✯ ʙᴜɪʟᴅ sᴛᴀᴛᴜs: ᴠ1.1.0 [ ʙᴇᴛᴀ ]</b>"""

    FAQ_TXT = """<b>Frequently Asked Questions - {}</b>

1️⃣ <b>How do I download manga?</b>
   - Use the /search or /s command to find manga  
   - Select a chapter  
   - Choose your preferred format (PDF/EPUB/CBZ)  

2️⃣ <b>What formats are supported?</b>
   - Available formats: <b>PDF</b>, <b>EPUB</b>, <b>CBZ</b>

3️⃣ <b>Are there download limits?</b>  
   - <b>No limits!</b> Download as much as you want.  

4️⃣ <b>Which format should I choose?</b>  
   - <b>CBZ</b>: Best for <i>manhwa/manhua</i> 
   - <b>EPUB</b>: Best for <i>manga</i> 
   - <b>PDF</b>: Try it yourself and see! 
   
5️⃣ <b>Why are some pages missing or not downloaded?</b>
   - Sometime sever issues. Try again later.
   - If the issue persists, reach out support group.
   - <b>Do not spam!</b>"""




    SOURCE_TXT = """<b>ɴᴏᴛᴇ:
- ᴛʜɪs ʙᴏᴛ ɪs ɴᴏᴛ ᴀɴ ᴏᴘᴇɴ-sᴏᴜʀᴄᴇ ᴘʀᴏᴊᴇᴄᴛ.
ᴅᴇᴠᴇʟᴏᴘᴇʀ:
- <a href="https://t.me/bharath_boy">ᴊᴜsᴛ ᴏᴡɴᴇʀ</a> [ᴏғ ᴛʜɪs ʙᴏᴛ]</b>"""

    RESTART_TXT = """
<b>ʙᴏᴛ ʀᴇsᴛᴀʀᴛᴇᴅ!

🎉 ᴅᴀᴛᴇ : <code>{}</code>
⏰ ᴛɪᴍᴇ : <code>{}</code>
🌍 ᴛɪᴍᴇᴢᴏɴᴇ : <code>ᴀsɪᴀ/ᴋᴏʟᴋᴀᴛᴀ</code>
🛠️ ʙᴜɪʟᴅ sᴛᴀᴛᴜs: <code>ᴠ2.7.1 [ sᴛᴀʙʟᴇ ]</code></b>"""

    # Links
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
    DN = "https://telegra.ph/file/293772dfd1cee81336663-a40a38558bd5606121.png"


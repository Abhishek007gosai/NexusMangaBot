import asyncio
import logging
import random
from datetime import datetime
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, LinkPreviewOptions
from pyrogram.enums import ParseMode
from pyrogram.errors import ChatAdminRequired, UserNotParticipant
from script import Script
from db.users_chats_db import db

# Assuming the function is_subscribed is in utils.py
from plugins.utils import temp, is_subscribed

# Import necessary constants
from info import AUTH_CHANNEL, CHNL_LNK, LOG_CHANNEL, GRP_LNK, ADMINS

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Define the welcome message handler
@Client.on_message(filters.command("start") & filters.private)
async def welcome(client, message):
    user_mention = message.from_user.mention
    bot_info = await client.get_me()
    bot_username = bot_info.username
    bot_name = bot_info.first_name
    images = Script.PICS[1:]
    new_image = random.choice(images)
    invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))

    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [
                InlineKeyboardButton(
                    "⤬ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ⤬",
                    url=f"http://t.me/{temp.U_NAME}?startgroup=true",
                )
            ],
            [InlineKeyboardButton("🔰 ᴍᴀɪɴ ɢʀᴏᴜᴘ 🔰", url=CHNL_LNK)],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        text = f"<a href=\"{new_image}\">&#8205;</a>" + Script.START_TXT.format(
                message.from_user.mention if message.from_user else message.chat.title,
                temp.U_NAME,
                temp.B_NAME,
            )
        await message.reply(text,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )
        await asyncio.sleep(2)
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            await client.send_message(
                LOG_CHANNEL,
                Script.LOG_TEXT_G.format(
                    message.chat.title, message.chat.id, total, "Unknown"
                ),
            )
            await db.add_chat(message.chat.id, message.chat.title)
        return
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(
            LOG_CHANNEL,
            Script.LOG_TEXT_P.format(
                message.from_user.id, message.from_user.mention),
        )

    # Check subscription status
    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))

        except ChatAdminRequired:
            logger.error("Make sure Bot is admin in Forcesub channel")
            return

        btn = [
            [
                InlineKeyboardButton(
                    "🔻 ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ 🔻", url=invite_link.invite_link
                )
            ],
            [InlineKeyboardButton(
                "↻ Cʜᴇᴄᴋ Aɢᴀɪɴ", callback_data="check_again")],
        ]

        if len(message.command) > 1 and message.command[1] != "subscribe":
            retry_url = f"https://t.me/{bot_username}?start={message.command[1]}"
            btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ", url=retry_url)])
            
        text =f"<a href=\"{new_image}\">&#8205;</a>"+ f"""<b>ʜᴇʟʟᴏ {user_mention}</b>\n\n<i>ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ sᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ...</i>\n\n<b>ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ, ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ 'ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ' ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴀɴᴅ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ, ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ '↻ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ' ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ...</b>\n\n<i>ᴛʜᴇɴ ʏᴏᴜ ᴡɪʟʟ ʙᴇ ᴀʙʟᴇ ᴛᴏ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ...</i>"""
        
        await message.reply_text(text,
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=ParseMode.HTML,
        show_caption_above_media=True,
        link_preview_options=LinkPreviewOptions(
            is_disabled=False,
            prefer_small_media=False,
            prefer_large_media=True,
            show_above_text=True
        )
            
        )
        # await client.send_photo(
        #     chat_id=message.from_user.id,
        #     photo=Script.PICS[2],
        #     caption=f"""<b>ʜᴇʟʟᴏ {user_mention}</b>\n\n<i>ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ sᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ...</i>\n\n<b>ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ, ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ 'ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ' ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴀɴᴅ ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ, ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ '↻ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ' ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ...</b>\n\n<i>ᴛʜᴇɴ ʏᴏᴜ ᴡɪʟʟ ʙᴇ ᴀʙʟᴇ ᴛᴏ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ...</i>""",
        #     reply_markup=InlineKeyboardMarkup(btn),
        #     parse_mode=ParseMode.HTML,
        # )
        
       
        return

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "⤬ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ⤬",
                    url=f"http://t.me/{bot_username}?startgroup=true",
                )
            ],
            [
                InlineKeyboardButton("⚜️ MAIN ᴄʜᴀɴɴᴇʟ", url=CHNL_LNK),
                InlineKeyboardButton("🔱 MAIN ɢʀᴏᴜᴘ", url=GRP_LNK),
            ],
            [
                InlineKeyboardButton("🔰 ʜᴇʟᴘ", callback_data="help"),
                InlineKeyboardButton("⚠️ ᴀʙᴏᴜᴛ", callback_data="about"),
                InlineKeyboardButton("❓ FAQ", callback_data="faq"),
            ],
            [InlineKeyboardButton("CLOSE", callback_data="deletemsg")],
        ]
    )

    invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
    welcome_text =f"<a href=\"{new_image}\">&#8205;</a>" + Script.START_TXT.format(
        user_mention, bot_username, bot_name, invite_link.invite_link
    )
    await message.reply_text(welcome_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        show_caption_above_media=True,
        link_preview_options=LinkPreviewOptions(
            is_disabled=False,
            prefer_small_media=False,
            prefer_large_media=True,
            show_above_text=True
        )
        )

    # await message.reply_photo(
    #     photo=Script.PICS[0],
    #     caption=welcome_text,
    #     reply_markup=keyboard,
    #     parse_mode=ParseMode.HTML,
    # )


async def safe_edit_text(
    message, new_text, reply_markup=None, parse_mode=ParseMode.HTML
):
    if message.text != new_text:
        await message.edit_text(
            new_text, reply_markup=reply_markup, parse_mode=parse_mode
        )


@Client.on_message(filters.command("send") & filters.user(ADMINS))
async def send_msg(bot, message):
    if not message.reply_to_message:
        await message.reply_text(
            "<b>Use this command as a reply to any message using the target chat id. For example: /send userid</b>"
        )
        return

    try:
        target_id = int(message.text.split(" ", 1)[1])
        user = await bot.get_users(target_id)

        # Check if the user exists in the correct collection
        user_exists = await db.col.find_one({"id": target_id})

        if user_exists:
            await message.reply_to_message.copy(target_id)
            await message.reply_text(
                f"<b>Your message has been successfully sent to {user.mention}.</b>"
            )
        else:
            await message.reply_text("<b>This user hasn't started this bot yet!</b>")

    except Exception as e:
        await message.reply_text(f"<b>Error: {e}</b>")


@Client.on_callback_query(filters.regex(r"^(check_again|help|about|faq|deletemsg|start)$"))
async def callback_query_handler(client, query):
    data = query.data
    images = Script.PICS[1:]
    new_image = random.choice(images)
    bot_info = await client.get_me()
    bot_username = bot_info.username
    bot_name = bot_info.first_name

    if data == "check_again":
        invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        loading_text = "<b>ᴄʜᴇᴄᴋɪɴɢ ʏᴏᴜʀ sᴜʙsᴄʀɪᴘᴛɪᴏɴ sᴛᴀᴛᴜs...</b>"
        await query.message.edit_text(
            text=loading_text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔻 ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ 🔻", url=invite_link.invite_link
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "↻ Cʜᴇᴄᴋ Aɢᴀɪɴ", callback_data="check_again"
                        )
                    ],
                ]
            ),
            parse_mode=ParseMode.HTML,
        )
        await asyncio.sleep(1.5)  # Simulate loading time

        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.message.edit_text(
                text="<b>sᴏʀʀʏ</b>\n\n<i>ʏᴏᴜ ᴀʀᴇ sᴛɪʟʟ ɴᴏᴛ ɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ. ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴀɴᴅ ᴘʀᴇss '↻ ᴄʜᴇᴄᴋ ᴀɢᴀɪɴ'.</i>",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔻 ᴊᴏɪɴ ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ 🔻", url=invite_link.invite_link
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "↻ Cʜᴇᴄᴋ Aɢᴀɪɴ", callback_data="check_again"
                            )
                        ],
                    ]
                ),
                parse_mode=ParseMode.HTML,
            )
        else:
            await query.message.edit_text(
                text="<b>Thanks!</b>\n\n<i>You are now subscribed. You can use the bot by using:</i>\n<blockquote>/start</blockquote>",
                parse_mode=ParseMode.HTML,
            )
        await query.answer("Message updated!")
        return

    # Handle help and about with a back button to menu
    if data == "help":
        new_caption = f"<a href=\"{new_image}\">&#8205;</a>" + Script.HELP_TXT.format(query.from_user.mention)
    elif data == "about":
        new_caption = f"<a href=\"{new_image}\">&#8205;</a>" + Script.ABOUT_TXT.format(bot_name)
    elif data == "faq":
        new_caption = f"<a href=\"{new_image}\">&#8205;</a>" +Script.FAQ_TXT.format(bot_name)
    elif data == "deletemsg":
        await query.message.delete()
        return
    elif data == "start":
        invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        user_mention = query.from_user.mention
        new_caption = f"<a href=\"{new_image}\">&#8205;</a>"+ Script.START_TXT.format(
            user_mention, bot_username, bot_name, invite_link.invite_link
        )

    # Create the appropriate reply_markup for each condition
    if data in ["help", "about", "faq"]:
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="start")]]
        )
    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⤬ Aᴅᴅ Mᴇ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ⤬",
                        url=f"http://t.me/{bot_username}?startgroup=true",
                    )
                ],
                [
                    InlineKeyboardButton("⚜️ MAIN ᴄʜᴀɴɴᴇʟ", url=CHNL_LNK),
                    InlineKeyboardButton("🔱 MAIN ɢʀᴏᴜᴘ", url=GRP_LNK),
                ],
                [
                    InlineKeyboardButton("🔰 ʜᴇʟᴘ", callback_data="help"),
                    InlineKeyboardButton("⚠️ ᴀʙᴏᴜᴛ", callback_data="about"),
                    InlineKeyboardButton("❓ FAQ", callback_data="faq"),
                ],
                [InlineKeyboardButton("CLOSE", callback_data="deletemsg")],
            ]
        )

    # await client.edit_message_media(
    #     chat_id=query.message.chat.id,
    #     message_id=query.message.id,
    #     media=InputMediaPhoto(new_image),
    # )

    
    await query.message.edit_text(
        text="Updating...", reply_markup=reply_markup, parse_mode=ParseMode.HTML, show_caption_above_media=True,
        link_preview_options=LinkPreviewOptions(
            is_disabled=False,
            prefer_small_media=False,
            prefer_large_media=True,
            show_above_text=True
    )
    )


    await query.message.edit_text(
        text=new_caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML , show_caption_above_media=True,
        link_preview_options=LinkPreviewOptions(
            is_disabled=False,
            prefer_small_media=False,
            prefer_large_media=True,
            show_above_text=True
    )
    )

    await query.answer("Message updated!")

@Client.on_message(filters.command("faq"))
async def send_help(client, message):
    bot_info = await client.get_me()
    bot_name = bot_info.first_name
    text=Script.FAQ_TXT.format(bot_name)
    # Send FAQ text with HTML formatting
    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

@Client.on_message(filters.command("help"))
async def send_faq(client, message):

    text=Script.HELP_TXT.format(message.from_user.mention)
    await message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

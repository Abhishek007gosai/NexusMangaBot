import logging
import re
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions
from scraper import AsyncMangaKakalotClient
from plugins.callbacks import set_callback_payload, get_callback_payload, set_callback_data, get_callback_data
from plugins.keyboards import build_dynamic_keyboard, build_pagination_row
from plugins.file_downloaders import send_cbz_file, send_pdf_file, send_epub_file
from config import API_ID, API_HASH, BOT_TOKEN
from script import Script


logger = logging.getLogger(__name__)
scraper_client = AsyncMangaKakalotClient()


    
@Client.on_message(filters.command(["popular", "p"]))
async def handle_popular_command(client, message):
    """
    Handle the /popular command to show popular manga listings.
    
    Args:
        client: The Pyrogram Client instance
        message: The message object containing the command
        
    Displays:
        - Paginated list of popular manga
        - Each entry is a button linking to manga details
    """
    page = 1
    sub_page = 1
    popular_manga = await scraper_client.popular(page=page)
    
    if not popular_manga:
        await message.reply_text("No popular manga found!")
        return

    # Calculate values locally
    total_items = len(popular_manga)
    items_per_page = 24
    show_subpage = total_items > items_per_page
    page_display = (
        f"Page {page}" 
        if not show_subpage 
        else f"Page {page}.{sub_page}"
    )

    # Build UI components
    keyboard = build_dynamic_keyboard(
        popular_manga[(sub_page-1)*items_per_page: sub_page*items_per_page],
        buttons_per_row=2,
        callback_prefix="details",
        origin_data={"origin": "popular", "listing_page": page, "listing_sub_page": sub_page}
    )

    pagination_row = build_pagination_row(
        prefix="popular",
        page=page,
        sub_page=sub_page, 
        total_items=total_items,
        items_per_page=items_per_page
    )

    # Compose message
    text = f"📚 Popular Manga ({page_display}):\n"
    keyboard.append(pagination_row)

    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
@Client.on_message(filters.command(["search","s"]))
async def handle_search_command(client, message):
    """
    Handle the /search command to search for manga by query.
    
    Args:
        client: The Pyrogram Client instance
        message: The message object containing the command and search query
        
    Displays:
        - Paginated list of search results matching the query
        - Each entry is a button linking to manga details
    """
    query = " ".join(message.command[1:])
    page = 1
    sub_page = 1
    items_per_page = 20  # Explicitly set pagination size

    if not query:
        await message.reply_text("Please provide a search query! Ex: /search one piece or /s one piece")
        return

    search_results = await scraper_client.search(query, page=page)
    if not search_results:
        await message.reply_text("No results found.")
        return

    # Calculate pagination parameters locally
    total_items = len(search_results)
    show_subpage = total_items > items_per_page
    page_display = (
        f"Page {page}" 
        if not show_subpage 
        else f"Page {page}-{sub_page}"
    )

    # Build interface components
    keyboard = build_dynamic_keyboard(
        search_results[(sub_page-1)*items_per_page : sub_page*items_per_page],
        buttons_per_row=2,
        callback_prefix="details",
        origin_data={
            "origin": "search", 
            "query": query, 
            "listing_page": page, 
            "listing_sub_page": sub_page
        }
    )

    pagination_row = build_pagination_row(
        prefix="search",
        page=page,
        sub_page=sub_page,
        total_items=total_items,
        items_per_page=items_per_page,
        query=query
    )

    # Compose message
    text = f"🔍 Search results for '{query}' ({page_display}):\n"
    keyboard.append(pagination_row)

    await message.reply_text(
        text, 
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )


@Client.on_callback_query(filters.regex(r"^popular\|"))
async def handle_popular_callback(client, callback_query):
    """
    Handle callback queries for paginating popular manga listings.
    
    Args:
        client: The Pyrogram Client instance
        callback_query: The callback query containing pagination data
        
    Displays:
        - Updated paginated list of popular manga
        - Each entry is a button linking to manga details
    """
    data = callback_query.data.split("|")
    page = int(data[1])
    sub_page = int(data[2])

    page = max(1, page)
    sub_page = max(1, sub_page)

    popular_manga = await scraper_client.popular(page=page)
    if not popular_manga:
        await callback_query.answer("No more manga!", show_alert=True)
        return

    start_idx = (sub_page - 1) * 24
    end_idx = sub_page * 24
    items = popular_manga[start_idx:end_idx]
    total_items = len(popular_manga)
    items_per_page = 24
    show_subpage = total_items > items_per_page
    page_display = (
        f"Page {page}" 
        if not show_subpage
        else f"Page {page}.{sub_page}"
    )


    text = f"📚 Popular Manga ({page_display}):\n"
    keyboard = build_dynamic_keyboard(
    items, buttons_per_row=2, callback_prefix="details",
    origin_data={"origin": "popular", "listing_page": page, "listing_sub_page": sub_page}
    )

    pagination_row = build_pagination_row(
        "popular", page, sub_page, total_items=len(popular_manga), items_per_page=items_per_page
    )
    keyboard.append(pagination_row)

    await callback_query.message.edit_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await callback_query.answer()


@Client.on_callback_query(filters.regex(r"^search\|"))
async def handle_search_callback(client, callback_query):
    """
    Handle callback queries for paginating search results.
    
    Args:
        client: The Pyrogram Client instance
        callback_query: The callback query containing pagination data
        
    Displays:
        - Updated paginated list of search results
        - Each entry is a button linking to manga details
    """
    parts = callback_query.data.split("|")
    query = "|".join(parts[1:-2])
    page = int(parts[-2])
    sub_page = int(parts[-1])

    page = max(1, page)
    sub_page = max(1, sub_page)

    search_results = await scraper_client.search(query, page=page)
    if not search_results:
        await callback_query.answer("No more results!", show_alert=True)
        return

    start_idx = (sub_page - 1) * 20
    end_idx = sub_page * 20
    items = search_results[start_idx:end_idx]
    total_items = len(search_results)
    items_per_page = 24
    show_subpage = total_items > items_per_page
    page_display = (
        f"Page {page}" 
        if not show_subpage
        else f"Page {page}.{sub_page}"
    )

    text = f"🔍 Search results for '{query}' ({page_display}):\n"
    keyboard = build_dynamic_keyboard(
    items, buttons_per_row=2, callback_prefix="details",
    origin_data={"origin": "search", "query": query, "listing_page": page, "listing_sub_page": sub_page}
    )

    pagination_row = build_pagination_row(
        "search", page, sub_page, total_items=len(search_results), query=query
    )
    keyboard.append(pagination_row)

    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML,
    )
    await callback_query.answer()

@Client.on_callback_query(filters.regex(r"^(?!check_again$|help$|about$|deletemsg$|faq$|start$).+"))
async def handle_callback(client, callback_query):

    payload = get_callback_payload(callback_query.data)

    action = payload.get("action")
    sent_msg = None

    try:
        if action == "details":
            origin = payload.get("origin")
            key = payload.get("key")
            # Optional chapter page; default to 1
            chap_page = int(payload.get("chap_page", 1))

            if origin == "popular":
                listing_page = int(payload.get("listing_page"))
                listing_sub_page = int(payload.get("listing_sub_page"))
                query = None
            elif origin == "search":
                query = payload.get("query")
                listing_page = int(payload.get("listing_page"))
                listing_sub_page = int(payload.get("listing_sub_page"))
        
            else:
                origin = None

            manga_details = await scraper_client.details(get_callback_data(key))
            if not manga_details:
                await callback_query.answer("Error fetching details.", show_alert=True)
                return

            manga_chapters = await scraper_client.chapters(get_callback_data(key))
            if not manga_chapters:
                text = (
                    f"<b>Title:</b> {manga_details.get('title', 'N/A')}\n"
                    f"<b>Status:</b> {manga_details.get('status', 'N/A')}\n"
                    f"<b>Genres:</b> {', '.join(manga_details.get('genres', []))}\n\n"
                    f"<b>Description:</b>\n <blockquote expandable>{manga_details.get('description', 'No description')} </blockquote>\n\n"
                    "No chapters available."
                )
                await callback_query.message.edit_text(text, parse_mode=ParseMode.HTML)
                return

            per_page = 20
            total_pages = (len(manga_chapters) + per_page - 1) // per_page
            chap_page = max(1, min(chap_page, total_pages))
            start = (chap_page - 1) * per_page
            end = start + per_page
            current_chapters = manga_chapters[start:end]
            current_chapters = [
                {"title": re.sub(r'\bChapter\b', "Ch", chapter["title"], flags=re.IGNORECASE), "url": chapter["url"]}
                for chapter in current_chapters
            ]

            
            manga_details = await scraper_client.details(get_callback_data(key))
            if not manga_details:
                await callback_query.answer("Error fetching details.", show_alert=True)
                return
            graph_url = manga_details.get("graph_url", "")
            text = ""
            if graph_url:
                text += f"<a href=\"{graph_url}\">&#8205;</a>"

            text += (
                f"<b>Title:</b> {manga_details.get('title', 'N/A')}\n"
                f"<b>Status:</b> {manga_details.get('status', 'N/A')}\n"
                f"<b>Genres:</b> {', '.join(manga_details.get('genres', []))}\n\n"
                f"<b>Description:</b>\n<blockquote expandable>{manga_details.get('description', 'No description')} </blockquote>\n\n"
                f"<b>Chapters (Page {chap_page}/{total_pages}):</b>"
            )

            if origin:
                choose_origin = {
                    "origin": origin,
                    "listing_page": listing_page,
                    "listing_sub_page": listing_sub_page,
                    "chap_page": chap_page,
                    "details_key": key 
                }
                if origin == "search":
                    choose_origin["query"] = query
                
                chapter_keyboard = build_dynamic_keyboard(
                    current_chapters,
                    buttons_per_row=4,
                    callback_prefix="choose",
                    origin_data=choose_origin
                )
            else:
                chapter_keyboard = build_dynamic_keyboard(
                    current_chapters, buttons_per_row=4, callback_prefix="choose"
                )


            # Build pagination row for chapters
            pagination_row = []

            if chap_page > 1:
                prev_chap = chap_page - 1
                prev_payload = {"action": "details", "key": key, "chap_page": prev_chap}
                if origin:
                    prev_payload.update({
                        "origin": origin,
                        "listing_page": listing_page,
                        "listing_sub_page": listing_sub_page,

                    })
                    if origin == "search":
                        prev_payload["query"] = query
                prev_button = InlineKeyboardButton("⬅️ Previous", callback_data=set_callback_payload(prev_payload))
                pagination_row.append(prev_button)

            # Page indicator (non-clickable)
            pagination_row.append(InlineKeyboardButton(f"Page {chap_page}/{total_pages}", callback_data="ignore"))

            if chap_page < total_pages:
                next_chap = chap_page + 1
                next_payload = {"action": "details", "key": key, "chap_page": next_chap}
                if origin:
                    next_payload.update({
                        "origin": origin,
                        "listing_page": listing_page,
                        "listing_sub_page": listing_sub_page,

                        
                    })
                    if origin == "search":
                        next_payload["query"] = query
                next_button = InlineKeyboardButton("Next ➡️", callback_data=set_callback_payload(next_payload))
                pagination_row.append(next_button)

            # Append the pagination row to the chapter_keyboard
            chapter_keyboard.append(pagination_row)

            if origin == "popular":
                back_data = f"popular|{listing_page}|{listing_sub_page}"
            elif origin == "search":
                back_data = f"search|{query}|{listing_page}|{listing_sub_page}"
            
            else:
                back_data = "ignore"

            back_button = InlineKeyboardButton("◀️ Back", callback_data=back_data)
            chapter_keyboard.append([back_button])



            await callback_query.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(chapter_keyboard),
                parse_mode=ParseMode.HTML,
                show_caption_above_media=True,
                link_preview_options=LinkPreviewOptions(
                    is_disabled=False,
                    prefer_small_media=False,
                    prefer_large_media=True,
                    show_above_text=True
                )
            )
            await callback_query.answer()

        elif action == "choose":
            origin = payload.get("origin")
            key = payload.get("key")
            details_key = payload.get("details_key")
            chap_page = int(payload.get("chap_page", 1))
            if origin == "search":
                query = payload.get("query")
            else:
                query = None



            chapter_url = get_callback_data(key)
            if not chapter_url:
                await callback_query.answer("Error: Chapter URL not found.", show_alert=True)
                return

            manga_url = scraper_client.get_manga_from_chapter(chapter_url)

            download_buttons = [
                InlineKeyboardButton("PDF", callback_data=set_callback_payload({"action": "download", "fmt": "pdf", "key": set_callback_data("dl", chapter_url)})),
                InlineKeyboardButton("EPUB", callback_data=set_callback_payload({"action": "download", "fmt": "epub", "key": set_callback_data("dl", chapter_url)})),
                InlineKeyboardButton("CBZ", callback_data=set_callback_payload({"action": "download", "fmt": "cbz", "key": set_callback_data("dl", chapter_url)}))
            ]

            # Fixed version
            back_payload = {"action": "details", "key": details_key, "chap_page": chap_page}
            if origin:
                back_payload.update({
                    "origin": origin, 
                    "listing_page": payload.get("listing_page"), 
                    "listing_sub_page": payload.get("listing_sub_page")
                })
                if origin == "search":
                    back_payload["query"] = payload.get("query")

            back_data = set_callback_payload(back_payload)


            keyboard = [
                download_buttons,
                [InlineKeyboardButton("◀️ Back", callback_data=back_data)]
            ]
            text = "<b>Select format:\n\n</b>"
            text += f"<a href=\"{Script.DN}\">&#8205;</a>"
            text += "See /faq to know more about the formats."
            await callback_query.message.edit_text(text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.HTML,
                show_caption_above_media=True,
                link_preview_options=LinkPreviewOptions(
                    is_disabled=False,
                    prefer_small_media=False,
                    prefer_large_media=True,
                    show_above_text=True
                )
            )
            await callback_query.answer()


        elif action == "download":
            fmt = payload.get("fmt")
            key = payload.get("key")
            chapter_url = get_callback_data(key)
            if not chapter_url:
                await callback_query.answer("Error: Chapter URL not found.", show_alert=True)
                return

            try:
                if fmt == "pdf":
                    asyncio.create_task(send_pdf_file(client, callback_query, chapter_url))
                elif fmt == "epub":
                    asyncio.create_task(send_epub_file(client, callback_query, chapter_url))
                elif fmt == "cbz":
                    asyncio.create_task(send_cbz_file(client, callback_query, chapter_url))
                    return
            except Exception as e:
                logging.error(f"Download error: {e}")
                if sent_msg:
                    await sent_msg.edit_text("❌ Error during download")
    except Exception as e:
        logging.error(f"Callback error: {e}")
        await callback_query.answer("An error occurred.", show_alert=True)

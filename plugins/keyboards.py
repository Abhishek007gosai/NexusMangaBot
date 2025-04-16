from pyrogram.types import InlineKeyboardButton
from plugins.callbacks import set_callback_data, set_callback_payload




def build_dynamic_keyboard(items, buttons_per_row=2, callback_prefix="details", origin_data: dict = None):
    keyboard = []
    current_row = []
    for idx, item in enumerate(items):
        title = item.get("title")
        url = item.get("url")
        if title and url:
            # Create a base payload for the button.
            payload = {"action": callback_prefix, "key": set_callback_data(callback_prefix, url)}
            if origin_data:
                payload.update(origin_data)
            # Instead of encoding the full JSON, store it and return a short key.
            current_callback = set_callback_payload(payload)
            current_row.append(InlineKeyboardButton(title, callback_data=current_callback))
            if (idx + 1) % buttons_per_row == 0:
                keyboard.append(current_row)
                current_row = []
    if current_row:
        keyboard.append(current_row)
    return keyboard




def build_pagination_row(prefix, page, sub_page, total_items, items_per_page=20, query=None):
    pagination_row = []
    items_per_page = items_per_page or 20
    show_subpage = total_items > items_per_page
    if page > 1 or sub_page > 1:
        if sub_page > 1:
            prev_page = page
            prev_sub = sub_page - 1
        else:
            prev_page = page - 1
            prev_sub = (total_items // items_per_page) or 1

        if query:
            prev_data = f"{prefix}|{query}|{prev_page}|{prev_sub}"
        else:
            prev_data = f"{prefix}|{prev_page}|{prev_sub}"

        pagination_row.append(
            InlineKeyboardButton("⬅️ Previous", callback_data=prev_data)
        )


    page_display = (
                f"Page {page}" 
                if not show_subpage 
                else f"Page {page}-{sub_page}"
            )
    pagination_row.append(InlineKeyboardButton(page_display, callback_data="ignore"))

    if total_items <= sub_page * items_per_page:
        next_page = page + 1
        next_sub = 1
    else:
        next_page = page
        next_sub = sub_page + 1

    if query:
        next_data = f"{prefix}|{query}|{next_page}|{next_sub}"
    else:
        next_data = f"{prefix}|{next_page}|{next_sub}"

    pagination_row.append(InlineKeyboardButton("Next ➡️", callback_data=next_data))

    return pagination_row
import time
import logging
from pyrogram.types import Message

logger = logging.getLogger(__name__)


async def update_progress(current, total, message: Message, start_time, last_update_time=None):
    current_time = time.time()
    if last_update_time and (current_time - last_update_time[0]) < 1:
        return last_update_time[0]

    elapsed_time = current_time - start_time
    percent_complete = (current / total) * 100
    upload_speed = current / elapsed_time if elapsed_time > 0 else 0
    estimated_time_remaining = (total - current) / \
        upload_speed if upload_speed > 0 else 0

    progress_message = (
        f"📤 Uploading: {percent_complete:.2f}%\n"
        f"📦 {current / 1024 / 1024:.2f}MB / {total / 1024 / 1024:.2f}MB\n"
        f"🚀 {upload_speed / 1024:.2f}KB/s | ETA: {int(estimated_time_remaining)}s"
    )

    try:
        await message.edit_text(progress_message)
        return current_time
    except Exception as error:
        logger.error(f"Progress update error: {error}")
        return last_update_time[0] if last_update_time else current_time

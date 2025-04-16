from plugins.progress import update_progress
from scraper import AsyncMangaKakalotClient
from pyrogram.enums import ParseMode
from ebooklib import epub
from PIL import Image
from collections import defaultdict
import os
import time
import zipfile
import tempfile
import asyncio
import shutil
import logging

logger = logging.getLogger(__name__)


def _format_page_ranges(page_numbers):
    """Convert a list of page numbers to a compact range string (e.g. '1-3,5,7-9')"""
    if not page_numbers:
        return ""

    # Convert all numbers to strings and remove duplicates
    str_pages = sorted(set(str(p) if isinstance(
        p, (int, float)) else p for p in page_numbers))
    try:
        # Convert back to integers for range detection
        unique_pages = sorted([int(p) for p in str_pages])
    except ValueError:
        # If conversion fails, return comma-separated strings
        return ",".join(str_pages)

    ranges = []
    start = unique_pages[0]

    for i in range(1, len(unique_pages)):
        if unique_pages[i] != unique_pages[i-1] + 1:
            if start == unique_pages[i-1]:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{unique_pages[i-1]}")
            start = unique_pages[i]

    # Add the last range
    if start == unique_pages[-1]:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{unique_pages[-1]}")

    return ", ".join(ranges)


progress = update_progress
user_semaphores = defaultdict(lambda: asyncio.Semaphore(3))
scraper_client = AsyncMangaKakalotClient()


async def _download_pages(pages, out_dir, progress_callback):
    page_results = [None] * len(pages)
    failed_pages = []
    total_pages = len(pages)

    async def download_page(page_idx, page):
        image_path = os.path.normpath(
            os.path.join(out_dir, f"{page['index']:03}.jpg"))
        result, failed_page = await scraper_client.download_image(
            page["url"],
            image_path,
            page["page_number"]
        )
        if progress_callback:
            progress_callback(current=page_idx+1, total=total_pages)
        if failed_page:
            failed_pages.append(failed_page)
        return (page_idx, result)

    tasks = [download_page(i, page) for i, page in enumerate(pages)]
    responses = await asyncio.gather(*tasks)
    for page_idx, result in responses:
        page_results[page_idx] = result
    image_files = [r for r in page_results if r is not None]
    image_files.sort()
    return (image_files, failed_pages) if image_files else (None, failed_pages)


async def _create_epub(image_files, file_name):
    book = epub.EpubBook()
    book.set_identifier('id123456')
    book.set_title(file_name)
    book.set_language('en')

    for idx, img_path in enumerate(image_files):
        with open(img_path, 'rb') as img_file:
            img_content = img_file.read()
        img_item = epub.EpubItem(
            uid=f'image_{idx}',
            file_name=f'images/image_{idx}.jpg',
            media_type='image/jpeg',
            content=img_content
        )
        book.add_item(img_item)

        chapter_content = f'''
            <html>
            <head>
                <style>
                    img {{ display: block; margin: 0; padding: 0; border: none; width: 100%; height: auto; }}
                    body {{ margin: 0; padding: 0; }}
                </style>
            </head>
            <body>
                <img src="images/image_{idx}.jpg"/>
            </body>
            </html>
        '''
        chapter = epub.EpubHtml(
            title=f'Manga Chapter {idx + 1}',
            file_name=f'chapter_{idx}.xhtml',
            lang='en'
        )
        chapter.content = chapter_content
        book.add_item(chapter)

    book.toc = tuple(epub.Link(
        f'chapter_{idx}.xhtml', f'Manga Chapter {idx + 1}', f'chapter_{idx}') for idx in range(len(image_files)))
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(file_name, book, {})


async def send_file(client, callback_query, chapter_url, fmt):
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    semaphore = user_semaphores[user_id]

    try:
        await asyncio.wait_for(semaphore.acquire(), timeout=1.0)
    except asyncio.TimeoutError:
        await callback_query.answer("Too many concurrent downloads. Please wait a few seconds.", show_alert=True)
        return

    temp_dir = None
    try:
        manga_name, chap_num = await scraper_client._get_chapter_info(chapter_url)
        pages = await scraper_client.pages(chapter_url)
        if not pages:
            await client.send_message(chat_id, "Failed to fetch chapter.")
            logger.error("Failed to fetch chapter from URL: %s", chapter_url)

        temp_dir = tempfile.mkdtemp()
        download_status_msg = await client.send_message(chat_id, f"Downloading pages... 0/{len(pages)}")

        def dl_progress(current, total):
            nonlocal download_status_msg
            if current - last_update["value"] >= 5 or current == total:
                last_update["value"] = current
                text = f"Downloading pages... {current}/{total}"
                asyncio.create_task(download_status_msg.edit_text(text))

        last_update = {"value": -5}
        download_success = False
        image_files, failed_pages = await _download_pages(pages, temp_dir, progress_callback=dl_progress)

        # Wait for any pending progress updates
        await asyncio.sleep(0.5)

        if not image_files:  # None or empty list
            await download_status_msg.edit_text("Failed to download any pages.")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return
        else:
            download_success = True

        file_name = f"{manga_name}_chap{chap_num}.{fmt}"
        file_path = os.path.join(temp_dir, file_name)

        if fmt == "cbz":
            with zipfile.ZipFile(file_path, "w") as zipf:
                for img in image_files:
                    zipf.write(img, os.path.basename(img))
        elif fmt == "pdf":
            pdf_pages = []
            for img in image_files:
                try:
                    img_pil = Image.open(img)
                    if img_pil.mode != "RGB":
                        img_pil = img_pil.convert("RGB")
                    pdf_pages.append(img_pil)
                except Exception as e:
                    logger.error(f"Error processing image {img}: {e}")
            if not pdf_pages:
                await download_status_msg.edit_text("Failed to create PDF (no valid images).")
                shutil.rmtree(temp_dir, ignore_errors=True)
                return
            pdf_pages[0].save(file_path, save_all=True,
                              append_images=pdf_pages[1:], format="PDF")
        elif fmt == "epub":
            await _create_epub(image_files, file_path)

        try:
            await download_status_msg.edit_text(f"Uploading {fmt.upper()}...")
        except Exception as e:
            logger.error(f"Upload message edit failed: {e}")

        cap = f"Here's your {fmt.upper()}!\n\nFailed pages:<blockquote expandable>{str(_format_page_ranges(failed_pages))}</blockquote>" if failed_pages else f"Here's your {fmt.upper()}!"

        start_time = time.time()
        await client.send_document(
            chat_id=chat_id,
            document=file_path,
            file_name=os.path.basename(file_path),
            caption=cap,
            progress=progress,
            progress_args=(download_status_msg, start_time),
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
    finally:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
        semaphore.release()


async def send_cbz_file(client, callback_query, chapter_url):
    await send_file(client, callback_query, chapter_url, "cbz")


async def send_pdf_file(client, callback_query, chapter_url):
    await send_file(client, callback_query, chapter_url, "pdf")


async def send_epub_file(client, callback_query, chapter_url):
    await send_file(client, callback_query, chapter_url, "epub")

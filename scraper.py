from script import EMPTY_DESC_TXT, DESC_TXT
import string
import secrets
import config
import piexif
from ebooklib import epub
from io import BytesIO
from PIL.ExifTags import TAGS
from PIL import Image
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import asyncio
import aiohttp
import aiofiles
import re
import os
import time
import logging
from db.users_chats_db import db


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
try:
    import motor.motor_asyncio
except ImportError:
    motor = None


class AsyncMangaKakalotClient:
    MIRRORS = [
        "https://www.mangakakalot.gg",
        "https://www.mangakakalove.com",
        "https://www.nelomanga.net/",
        "https://www.natomanga.com/",
        "https://www.manganato.gg/",
        "https://www.mangabats.com/",
    ]
    BROWSER_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }

    def __init__(self):
        self._session = None
        self._mirror_index = 0
        

    async def _ensure_session(self):
        if self._session is None:
            loop = asyncio.get_running_loop()
            self._session = aiohttp.ClientSession(loop=loop)

    def _current_mirror(self):
        return self.MIRRORS[self._mirror_index]

    def _switch_mirror(self):
        self._mirror_index = (self._mirror_index + 1) % len(self.MIRRORS)
        return self._current_mirror()

    async def _request(self, path, params=None, retries=5):
        await self._ensure_session()
        for _ in range(retries):
            mirror = self._current_mirror()
            url = urljoin(mirror, path)
            headers = {**self.BROWSER_HEADERS, "Referer": mirror + "/"}
            try:
                async with self._session.get(
                    url, headers=headers, params=params, timeout=15
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Status code: {response.status}")
                    return await response.text()
            except Exception as e:
                logger.warning(
                    f"Request failed on mirror {mirror}: {e}. Switching mirror..."
                )
                self._switch_mirror()
        return None

    def _sanitize_filename(self, name):
        return re.sub(r'[\\/*?"<>|-]', " ", name).strip()

    async def _get_chapter_info(self, chapter_url):
        html = await self._request(chapter_url)
        if not html:
            return None, None
        soup = BeautifulSoup(html, "html.parser")
        manga_name = "Unknown"
        manga_link = soup.select_one('a[href*="/manga/"], a[href*="/read-"]')

        if manga_link:
            href = manga_link.get("href", "")

            manga_name = self._extract_manga_name_from_url(href) or manga_link.get_text(
                strip=True
            )
        chapter_num = "0"
        title_tag = soup.select_one("h1, h2, h3")

        if title_tag:
            match = re.search(
                r"Chapter\s+(\d+\.?\d*)", title_tag.get_text(), re.IGNORECASE
            )
            if match:
                chapter_num = self._extract_chapnum_from_url(
                    chapter_url
                ) or match.group(1)

        return self._sanitize_filename(manga_name), chapter_num

    @staticmethod
    def _extract_chapnum_from_url(url):
        path = urlparse(url).path
        if "chapter-" in path:
            chapnum = path.split("chapter-")[-1].split("/")[0]
            return chapnum.replace("-", ".")
        return None

    @staticmethod
    def _extract_pagenum_from_url(url: str) -> str:
        match = re.search(r"/(\d+)(?:\.[a-z]+)?$", url)
        return str(int(match.group(1)) + 1) if match else None

    @staticmethod
    def _extract_manga_name_from_url(url):
        path = urlparse(url).path
        if "/manga/" in path:
            return path.split("/manga/")[-1].split("/")[0]

        return None

    async def popular(self, page=1):
        # cache_key = f"popular:{page}"
        # cached = await self.get_cache(cache_key)
        # if cached is not None:
        #     return cached

        html = await self._request(f"/manga-list/hot-manga?page={page}")
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select("div.truyen-list > div.list-truyen-item-wrap")
        result = []
        for el in items:
            a = el.select_one("h3 a, h3.title a, a")
            if not a:
                continue
            href = a["href"]
            title = a.get("title") or a.get_text(strip=True)
            if not title:
                title = "Untitled"
            img = el.select_one("img")
            thumb = img["src"] if img and img.has_attr("src") else ""
            result.append(
                {"title": title.strip(), "url": href, "thumbnail": thumb})
        # await self.set_cache(cache_key, result)
        return result

    async def search(self, query, page=1):
        # cache_key = f"search:{query}:{page}"
        # cached = await self.get_cache(cache_key)
        # if cached is not None:
        #     return cached

        if query.strip():
            path = f"/search/story/{self._normalize(query)}"
            html = await self._request(path, params={"page": page})
        else:
            html = await self._request("/", params={"page": page})
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select(
            ".panel_story_list .story_item, div.list-truyen-item-wrap")
        results = []
        for item in items:
            title_tag = item.select_one(".story_name a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            href = title_tag["href"]
            if not title:
                title = self._extract_manga_name_from_url(href) or "Untitled"
            title = self._sanitize_filename(title)
            img_tag = item.select_one("img")
            thumb = img_tag["src"] if img_tag else ""
            if title and href:
                results.append(
                    {"title": title, "url": href, "thumbnail": thumb})
        # await self.set_cache(cache_key, results)
        return results

    async def details(self, manga_path):
        cache_key = f"details:{manga_path}"
        cached = await db.get_cache(cache_key)
        if cached is not None:
            return cached

        html = await self._request(manga_path)
        if not html:
            return {
                "title": "Error",
                "status": "UNKNOWN",
                "genres": [],
                "description": "",
                "thumbnail": "",
                "graph_url": "",
            }

        soup = BeautifulSoup(html, "html.parser")
        info = soup.select_one("div.manga-info-top, div.panel-story-info")

        title = ""
        if info and (title_el := info.select_one("h1, h2, h3")):
            title = title_el.get_text(strip=True)
        title = self._sanitize_filename(
            title or self._extract_manga_name_from_url(
                manga_path) or "Untitled"
        )

        # Extract status
        status = "Unknown"
        if info:
            for node in info.find_all(["li", "tr"]):
                txt = node.get_text(" ", strip=True).lower()
                if "status" in txt:
                    status = (
                        "Ongoing"
                        if "ongoing" in txt
                        else "Completed" if "completed" in txt else status
                    )
                    break

        genres = []
        if info:
            for node in info.find_all(["li", "tr"]):
                txt = node.get_text(" ", strip=True).lower()
                if "genres" in txt:
                    genres = [a.get_text(strip=True)
                              for a in node.find_all("a")]
                    break

        desc_elem = soup.select_one(
            "div#noidungm, div#panel-story-info-description, div#contentBox"
        )

        if desc_elem:
            for h2 in desc_elem.find_all("h2"):
                h2.decompose()
            desc = desc_elem.get_text("\n", strip=True)
        else:
            desc = EMPTY_DESC_TXT.format(title=title)

        desc = re.sub(
            r"You are reading.*?to your bookmark\.", "", desc, flags=re.DOTALL
        ).strip()
        r_p = r"""(?:\>?\(?https?://\S+|\w+\.\S+|(?:[\w-]+\.)+\w+)"""
        desc = re.sub(r"-+", "", desc)
        desc = re.sub(r_p, "", desc, flags=re.IGNORECASE | re.VERBOSE)
        desc = re.sub(r"\s+", " ", desc).strip()
        desc = desc[:900] + "..." if len(desc) > 900 else desc

        # Get thumbnail
        thumb_elem = soup.select_one(
            "div.manga-info-pic img, span.info-image img")
        thumb = thumb_elem["src"] if thumb_elem and thumb_elem.has_attr(
            "src") else ""
        graph_url = ""

        if thumb:
            try:
                temp_file = f"temp_{int(time.time())}.jpg"
                path = await self.download_image(thumb, temp_file)
                if path:
                    graph_url = await self.upload_to_envs(temp_file)
                    try:
                        os.remove(temp_file)
                    except:
                        pass
            except Exception as e:
                logger.error(f"Error generating preview: {e}")

        manga_details = {
            "title": title,
            "status": status,
            "genres": genres,
            "description": desc,
            "thumbnail": thumb,
            "graph_url": graph_url,
        }

        await db.set_cache(cache_key, manga_details, expire=600)
        return manga_details

    async def chapters(self, manga_path):
        html = await self._request(manga_path)
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.select(
            "div.chapter-list div.row, ul.row-content-chapter li")
        return [
            {"title": a.get_text(strip=True), "url": a["href"]}
            for el in rows
            if (a := el.select_one("a"))
        ][::-1]

    async def pages(self, chapter_url):
        html = await self._request(chapter_url)
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        page_images = soup.select("div.container-chapter-reader img")
        if page_images:
            return [
                {
                    "index": idx + 1,
                    "url": img["src"].strip(),
                    "page_number": self._extract_pagenum_from_url(img["src"].strip())
                    or re.search(r"page (\d+(?:\.\d+)?)", img["title"].strip()).group(
                        1
                    ),
                }
                for idx, img in enumerate(page_images)
                if img.has_attr("src")
            ]
        return []

    def _extract_array(self, js, name):
        m = re.search(rf"{name}\s*=\s*\[([^\]]+)\]", js)
        if not m:
            return []
        items = m.group(1).split(",")
        clean = []
        for it in items:
            s = it.strip().strip('"').replace("\\/", "/")
            clean.append(s.rstrip("/"))
        return clean

    async def download_image(self, url, out_path, pageno=None, retries=6):
        await self._ensure_session()
        headers = {**self.BROWSER_HEADERS,
                   "Referer": self._current_mirror() + "/"}

        for attempt in range(retries):
            try:

                async with self._session.get(
                    url, headers=headers, timeout=15
                ) as response:
                    if response.status == 200:
                        content = await response.read()
                        with open(out_path, "wb") as f:
                            f.write(content)
                        return (out_path, None)

                    if response.status in [403, 404]:
                        old_mirror = self._current_mirror()
                        self._switch_mirror()
                        headers["Referer"] = self._current_mirror() + "/"

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2**attempt * 0.1)

            except Exception as e:
                import traceback

                traceback.print_exc()
                break
        return (None, pageno)

    async def download_pages_concurrent(
        self, pages, out_dir="pages", max_workers=10, progress_callback=None
    ):
        os.makedirs(out_dir, exist_ok=True)
        page_results = [None] * len(pages)
        total_pages = len(pages)

        async def download_page(page_idx, page):
            result = await self.download_image(
                page["url"],
                os.path.join(out_dir, f"{page['index']:03}.jpg"),
                page["page_number"],
            )
            if progress_callback:
                progress_callback(current=page_idx + 1, total=total_pages)
            return (page_idx, result)

        tasks = [download_page(i, page) for i, page in enumerate(pages)]
        responses = await asyncio.gather(*tasks)
        for page_idx, result in responses:
            page_results[page_idx] = result
        image_files = [r for r in page_results if r is not None]
        image_files.sort()
        return image_files

    def get_manga_from_chapter(self, chapter_url):
        return urlunparse(
            urlparse(chapter_url)._replace(
                path="/".join(urlparse(chapter_url).path.split("/")[:-1])
            )
        )

    async def generate_random_string(self, length: int = 12) -> str:
        characters = string.ascii_letters + string.digits
        return "".join(secrets.choice(characters) for _ in range(length))

    async def upload_to_envs(self, filepath):
        try:
            rndm = await self.generate_random_string()

            async with aiohttp.ClientSession() as session:
                ext = os.path.splitext(filepath)[1]

                with open(filepath, "rb") as f:
                    form = aiohttp.FormData()
                    form.add_field(
                        "file", f, filename=f"{rndm}{ext}", content_type="image/png"
                    )

                    async with session.post("https://envs.sh/", data=form) as response:
                        if response.status == 200:
                            base_url = (await response.text()).strip()
                            return f"{base_url}?{rndm}=1"
                        return None

        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            return None

    def _normalize(self, q):
        q = q.lower()
        q = re.sub(r"[àáạảãâầấậẩẫăằắặẳẵ]", "a", q)
        q = re.sub(r"[èéẹẻẽêềếệểễ]", "e", q)
        q = re.sub(r"[ìíịỉĩ]", "i", q)
        q = re.sub(r"[òóọỏõôồốộổỗơờớợởỡ]", "o", q)
        q = re.sub(r"[ùúụủũưừứựửữ]", "u", q)
        q = re.sub(r"[ỳýỵỷỹ]", "y", q)
        q = re.sub(r"đ", "d", q)
        q = re.sub(r'[!@%\^\\*\(\)\+=<>?/,.:;\'"&\#\[\]~\-\$_ ]+', "_", q)
        q = re.sub(r"_+_+", "_", q)
        q = re.sub(r"^_+|_+$", "", q)
        return q

    async def close(self):
        if self._session:
            await self._session.close()

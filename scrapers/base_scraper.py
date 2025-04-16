import abc
from typing import List, Dict, Optional

class BaseMangaScraper(abc.ABC):
    """Abstract base class for all manga scrapers"""
    
    @abc.abstractmethod
    async def search(self, query: str, page: int = 1) -> List[Dict]:
        """Search manga - returns list of {title, url, thumbnail}"""
        pass

    @abc.abstractmethod
    async def popular(self, page: int = 1) -> List[Dict]:
        """Get popular manga - returns same format as search"""
        pass

    @abc.abstractmethod
    async def details(self, manga_url: str) -> Dict:
        """Get manga details - returns {
            'title': str,
            'status': str, 
            'genres': List[str],
            'description': str,
            'thumbnail': str,
            'graph_url': str
        }"""
        pass

    @abc.abstractmethod
    async def chapters(self, manga_url: str) -> List[Dict]:
        """Get chapters list - returns [{'title': str, 'url': str}]"""
        pass

    @abc.abstractmethod
    async def pages(self, chapter_url: str) -> List[Dict]:
        """Get chapter pages - returns [{'index': int, 'url': str}]"""
        pass

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """Common filename sanitizer"""
        import re
        return re.sub(r'[\\/*?"<>|]', ' ', name).strip()

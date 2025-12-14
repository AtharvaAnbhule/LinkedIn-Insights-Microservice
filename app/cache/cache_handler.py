from typing import Optional, Any
from app.core.cache import cache
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class CacheHandler:
   

    @staticmethod
    def _get_page_key(page_id: str) -> str:
       
        return f"page:{page_id}"

    @staticmethod
    def _get_page_posts_key(page_id: str, page: int, limit: int) -> str:
       
        return f"page:{page_id}:posts:p{page}:l{limit}"

    @staticmethod
    def _get_page_followers_key(page_id: str, page: int, limit: int) -> str:
       
        return f"page:{page_id}:followers:p{page}:l{limit}"

    @staticmethod
    def _get_search_key(
        min_followers: Optional[int],
        max_followers: Optional[int],
        industry: Optional[str],
        name: Optional[str],
        page: int,
        limit: int
    ) -> str:
       
        parts = ["search"]

        if min_followers is not None:
            parts.append(f"minf{min_followers}")
        if max_followers is not None:
            parts.append(f"maxf{max_followers}")
        if industry:
            parts.append(f"ind{industry}")
        if name:
            parts.append(f"name{name}")

        parts.append(f"p{page}")
        parts.append(f"l{limit}")

        return ":".join(parts)

    async def get_page(self, page_id: str) -> Optional[Any]:
       
        key = self._get_page_key(page_id)
        return await cache.get(key)

    async def set_page(self, page_id: str, data: Any, ttl: int = None) -> bool:
       
        key = self._get_page_key(page_id)
        return await cache.set(key, data, ttl or settings.CACHE_TTL)

    async def get_page_posts(self, page_id: str, page: int, limit: int) -> Optional[Any]:
        
        key = self._get_page_posts_key(page_id, page, limit)
        return await cache.get(key)

    async def set_page_posts(
        self,
        page_id: str,
        page: int,
        limit: int,
        data: Any,
        ttl: int = None
    ) -> bool:
        
        key = self._get_page_posts_key(page_id, page, limit)
        return await cache.set(key, data, ttl or settings.CACHE_TTL)

    async def get_page_followers(self, page_id: str, page: int, limit: int) -> Optional[Any]:
       
        key = self._get_page_followers_key(page_id, page, limit)
        return await cache.get(key)

    async def set_page_followers(
        self,
        page_id: str,
        page: int,
        limit: int,
        data: Any,
        ttl: int = None
    ) -> bool:
       
        key = self._get_page_followers_key(page_id, page, limit)
        return await cache.set(key, data, ttl or settings.CACHE_TTL)

    async def get_search_results(
        self,
        min_followers: Optional[int],
        max_followers: Optional[int],
        industry: Optional[str],
        name: Optional[str],
        page: int,
        limit: int
    ) -> Optional[Any]:
        
        key = self._get_search_key(min_followers, max_followers, industry, name, page, limit)
        return await cache.get(key)

    async def set_search_results(
        self,
        min_followers: Optional[int],
        max_followers: Optional[int],
        industry: Optional[str],
        name: Optional[str],
        page: int,
        limit: int,
        data: Any,
        ttl: int = None
    ) -> bool:
       
        key = self._get_search_key(min_followers, max_followers, industry, name, page, limit)
        return await cache.set(key, data, ttl or settings.CACHE_TTL)

    async def invalidate_page(self, page_id: str) -> int:
      
        pattern = f"page:{page_id}:*"
        count = await cache.clear_pattern(pattern)

        # Also clear the page details cache
        await cache.delete(self._get_page_key(page_id))

        logger.info(f"Invalidated {count + 1} cache entries for page {page_id}")
        return count + 1

    async def invalidate_search(self) -> int:
       
        pattern = "search:*"
        count = await cache.clear_pattern(pattern)
        logger.info(f"Invalidated {count} search cache entries")
        return count


cache_handler = CacheHandler()

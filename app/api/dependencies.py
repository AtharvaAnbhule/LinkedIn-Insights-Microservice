from typing import AsyncGenerator

from app.core.database import database
from app.repositories.page_repository import PageRepository
from app.repositories.post_repository import PostRepository
from app.repositories.user_repository import UserRepository
from app.scrapers.linkedin_scraper import LinkedInScraper
from app.cache.cache_handler import CacheHandler
from app.services.page_service import PageService


async def get_page_repository() -> PageRepository:
    """Dependency for page repository"""
    return PageRepository(database.get_db())


async def get_post_repository() -> PostRepository:
    """Dependency for post repository"""
    return PostRepository(database.get_db())


async def get_user_repository() -> UserRepository:
    """Dependency for user repository"""
    return UserRepository(database.get_db())


async def get_linkedin_scraper() -> AsyncGenerator[LinkedInScraper, None]:
    """Dependency for LinkedIn scraper with cleanup"""
    scraper = LinkedInScraper()
    try:
        yield scraper
    finally:
        await scraper.close()


async def get_cache_handler() -> CacheHandler:
    """Dependency for cache handler"""
    return CacheHandler()


async def get_page_service(
    page_repo: PageRepository,
    post_repo: PostRepository,
    user_repo: UserRepository,
    scraper: LinkedInScraper,
    cache_handler: CacheHandler
) -> PageService:
    """Dependency for page service"""
    return PageService(page_repo, post_repo, user_repo, scraper, cache_handler)

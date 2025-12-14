from typing import List, Optional, Dict, Any
from math import ceil

from app.repositories.page_repository import PageRepository
from app.repositories.post_repository import PostRepository
from app.repositories.user_repository import UserRepository
from app.scrapers.linkedin_scraper import LinkedInScraper
from app.cache.cache_handler import CacheHandler
from app.models.page import (
    PageCreate,
    PageResponse,
    PageSearchFilters,
    PageSearchResponse
)
from app.models.post import PostResponse, PostListResponse
from app.models.user import SocialMediaUserResponse, SocialMediaUserCreate
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class PageService:
    """Service layer for page operations"""

    def __init__(
        self,
        page_repo: PageRepository,
        post_repo: PostRepository,
        user_repo: UserRepository,
        scraper: LinkedInScraper,
        cache_handler: CacheHandler
    ):
        self.page_repo = page_repo
        self.post_repo = post_repo
        self.user_repo = user_repo
        self.scraper = scraper
        self.cache_handler = cache_handler

    async def get_page_details(self, page_id: str) -> PageResponse:
        """
        Get page details with caching and scraping fallback.

        Flow:
        1. Check Redis cache
        2. If not cached, check MongoDB
        3. If not in DB, scrape data
        4. Store in DB and cache
        """
        logger.info(f"Fetching page details for: {page_id}")

        # Step 1: Check cache
        cached_data = await self.cache_handler.get_page(page_id)
        if cached_data:
            logger.info(f"Page {page_id} found in cache")
            return PageResponse(**cached_data)

        # Step 2: Check database
        page_data = await self.page_repo.get_by_page_id(page_id)

        if page_data:
            logger.info(f"Page {page_id} found in database")
            # Cache the result
            await self.cache_handler.set_page(page_id, page_data)
            return PageResponse(**page_data)

        # Step 3: Scrape data
        logger.info(f"Page {page_id} not found, scraping...")
        scraped_data = await self.scraper.scrape_page_details(page_id)

        # Step 4: Store in database
        page_create = PageCreate(**scraped_data)
        page_data = await self.page_repo.create_page(page_create)

        # Step 5: Cache the result
        await self.cache_handler.set_page(page_id, page_data)

        return PageResponse(**page_data)

    async def search_pages(self, filters: PageSearchFilters) -> PageSearchResponse:
        """
        Search pages with filters and pagination.

        Results are cached for better performance.
        """
        logger.info(f"Searching pages with filters: {filters.model_dump()}")

        # Check cache
        cached_data = await self.cache_handler.get_search_results(
            min_followers=filters.min_followers,
            max_followers=filters.max_followers,
            industry=filters.industry,
            name=filters.name,
            page=filters.page,
            limit=filters.limit
        )

        if cached_data:
            logger.info("Search results found in cache")
            return PageSearchResponse(**cached_data)

        # Calculate pagination
        skip = (filters.page - 1) * filters.limit

        # Search database
        pages, total = await self.page_repo.search_pages(
            min_followers=filters.min_followers,
            max_followers=filters.max_followers,
            industry=filters.industry,
            name=filters.name,
            skip=skip,
            limit=filters.limit
        )

        # Calculate total pages
        total_pages = ceil(total / filters.limit) if total > 0 else 0

        response_data = {
            "total": total,
            "page": filters.page,
            "limit": filters.limit,
            "pages": total_pages,
            "data": [PageResponse(**page) for page in pages]
        }

        # Cache results
        await self.cache_handler.set_search_results(
            min_followers=filters.min_followers,
            max_followers=filters.max_followers,
            industry=filters.industry,
            name=filters.name,
            page=filters.page,
            limit=filters.limit,
            data=response_data
        )

        return PageSearchResponse(**response_data)

    async def get_page_posts(
        self,
        page_id: str,
        page: int = 1,
        limit: int = 15
    ) -> PostListResponse:
        """
        Get posts for a specific page with pagination.

        If posts don't exist, scrape them.
        """
        logger.info(f"Fetching posts for page: {page_id}")

        # Check cache
        cached_data = await self.cache_handler.get_page_posts(page_id, page, limit)
        if cached_data:
            logger.info(f"Posts for page {page_id} found in cache")
            return PostListResponse(**cached_data)

        # Calculate pagination
        skip = (page - 1) * limit

        # Get posts from database
        posts, total = await self.post_repo.get_posts_by_page_id(page_id, skip, limit)

        # If no posts found, scrape them
        if not posts:
            logger.info(f"No posts found for {page_id}, scraping...")

            # Ensure page exists
            page_exists = await self.page_repo.page_exists(page_id)
            if not page_exists:
                # Create page first
                await self.get_page_details(page_id)

            # Scrape posts
            scraped_posts = await self.scraper.scrape_page_posts(page_id, limit)

            # Store posts in database
            for post_data in scraped_posts:
                from app.models.post import PostCreate
                post_create = PostCreate(**post_data)
                await self.post_repo.create_post(post_create)

            # Fetch again from database
            posts, total = await self.post_repo.get_posts_by_page_id(page_id, skip, limit)

        # Calculate total pages
        total_pages = ceil(total / limit) if total > 0 else 0

        response_data = {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": total_pages,
            "data": [PostResponse(**post) for post in posts]
        }

        # Cache results
        await self.cache_handler.set_page_posts(page_id, page, limit, response_data)

        return PostListResponse(**response_data)

    async def get_page_followers(
        self,
        page_id: str,
        page: int = 1,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get followers for a specific page with pagination.

        If followers don't exist, scrape them.
        """
        logger.info(f"Fetching followers for page: {page_id}")

        # Check cache
        cached_data = await self.cache_handler.get_page_followers(page_id, page, limit)
        if cached_data:
            logger.info(f"Followers for page {page_id} found in cache")
            return cached_data

        # Calculate pagination
        skip = (page - 1) * limit

        # Get followers from database
        followers, total = await self.user_repo.get_followers_by_page_id(page_id, skip, limit)

        # If no followers found, scrape them
        if not followers:
            logger.info(f"No followers found for {page_id}, scraping...")

            # Ensure page exists
            page_exists = await self.page_repo.page_exists(page_id)
            if not page_exists:
                # Create page first
                await self.get_page_details(page_id)

            # Scrape followers
            scraped_followers = await self.scraper.scrape_page_followers(page_id, limit)

            # Store followers in database
            for follower_data in scraped_followers:
                user_create = SocialMediaUserCreate(**follower_data)
                await self.user_repo.create_user(user_create)

            # Fetch again from database
            followers, total = await self.user_repo.get_followers_by_page_id(page_id, skip, limit)

        # Calculate total pages
        total_pages = ceil(total / limit) if total > 0 else 0

        response_data = {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": total_pages,
            "data": [SocialMediaUserResponse(**follower) for follower in followers]
        }

        # Cache results
        await self.cache_handler.set_page_followers(page_id, page, limit, response_data)

        return response_data

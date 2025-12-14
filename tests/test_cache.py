import pytest
import json

from app.cache.cache_handler import CacheHandler


@pytest.mark.asyncio
async def test_cache_set_and_get(redis_client):
    """Test setting and getting cache values"""
    cache_handler = CacheHandler()

    page_id = "test-page"
    page_data = {
        "page_id": page_id,
        "name": "Test Page",
        "followers_count": 1000
    }


    result = await cache_handler.set_page(page_id, page_data, ttl=60)
    assert result is True


    cached_data = await cache_handler.get_page(page_id)
    assert cached_data is not None
    assert cached_data["page_id"] == page_id
    assert cached_data["name"] == "Test Page"


@pytest.mark.asyncio
async def test_cache_expiry(redis_client):
    """Test cache TTL expiration"""
    cache_handler = CacheHandler()

    page_id = "test-page-ttl"
    page_data = {"page_id": page_id, "name": "TTL Test"}


    await cache_handler.set_page(page_id, page_data, ttl=1)


    cached_data = await cache_handler.get_page(page_id)
    assert cached_data is not None


    import asyncio
    await asyncio.sleep(2)


    cached_data = await cache_handler.get_page(page_id)
    assert cached_data is None


@pytest.mark.asyncio
async def test_cache_invalidation(redis_client):
    """Test cache invalidation"""
    cache_handler = CacheHandler()

    page_id = "test-page-invalidate"

    await cache_handler.set_page(page_id, {"page_id": page_id}, ttl=300)
    await cache_handler.set_page_posts(page_id, 1, 10, {"posts": []}, ttl=300)
    await cache_handler.set_page_followers(page_id, 1, 10, {"followers": []}, ttl=300)


    count = await cache_handler.invalidate_page(page_id)
    assert count > 0


    cached_data = await cache_handler.get_page(page_id)
    assert cached_data is None

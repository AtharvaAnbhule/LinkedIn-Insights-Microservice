import pytest
from datetime import datetime

from app.repositories.page_repository import PageRepository
from app.models.page import PageCreate


@pytest.mark.asyncio
async def test_page_repository_create(test_db, sample_page_data):
    """Test creating a page in repository"""
    repo = PageRepository(test_db)

    page_create = PageCreate(**sample_page_data)
    page = await repo.create_page(page_create)

    assert page is not None
    assert page["page_id"] == sample_page_data["page_id"]
    assert page["name"] == sample_page_data["name"]
    assert "created_at" in page
    assert "updated_at" in page


@pytest.mark.asyncio
async def test_page_repository_get_by_id(test_db, sample_page_data):
    """Test getting a page by page_id"""
    repo = PageRepository(test_db)

    # Create page
    page_create = PageCreate(**sample_page_data)
    await repo.create_page(page_create)

    # Retrieve page
    page = await repo.get_by_page_id(sample_page_data["page_id"])

    assert page is not None
    assert page["page_id"] == sample_page_data["page_id"]


@pytest.mark.asyncio
async def test_page_repository_search(test_db):
    """Test searching pages with filters"""
    repo = PageRepository(test_db)

    # Create multiple pages
    pages_data = [
        {
            "page_id": "tech-company-1",
            "name": "Tech Company One",
            "url": "https://linkedin.com/company/tech-1",
            "industry": "Technology",
            "followers_count": 5000
        },
        {
            "page_id": "tech-company-2",
            "name": "Tech Company Two",
            "url": "https://linkedin.com/company/tech-2",
            "industry": "Technology",
            "followers_count": 15000
        },
        {
            "page_id": "finance-company",
            "name": "Finance Company",
            "url": "https://linkedin.com/company/finance",
            "industry": "Finance",
            "followers_count": 8000
        }
    ]

    for page_data in pages_data:
        page_create = PageCreate(**page_data)
        await repo.create_page(page_create)

    # Test industry filter
    pages, total = await repo.search_pages(industry="Technology", limit=10)
    assert total == 2
    assert len(pages) == 2

    # Test followers filter
    pages, total = await repo.search_pages(min_followers=10000, limit=10)
    assert total == 1
    assert pages[0]["page_id"] == "tech-company-2"

    # Test name filter
    pages, total = await repo.search_pages(name="Tech", limit=10)
    assert total == 2


@pytest.mark.asyncio
async def test_page_exists(test_db, sample_page_data):
    """Test checking if page exists"""
    repo = PageRepository(test_db)

    # Should not exist initially
    exists = await repo.page_exists(sample_page_data["page_id"])
    assert not exists

    # Create page
    page_create = PageCreate(**sample_page_data)
    await repo.create_page(page_create)

    # Should exist now
    exists = await repo.page_exists(sample_page_data["page_id"])
    assert exists

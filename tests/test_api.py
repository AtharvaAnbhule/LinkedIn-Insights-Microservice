import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    with patch("app.core.database.database.ping", return_value=True), \
         patch("app.core.cache.cache.ping", return_value=True):

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_get_page_details_endpoint():
    """Test get page details endpoint"""
    mock_page_data = {
        "page_id": "test-company",
        "name": "Test Company",
        "url": "https://linkedin.com/company/test-company",
        "description": "Test description",
        "industry": "Technology",
        "followers_count": 1000,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }

    with patch("app.services.page_service.PageService.get_page_details") as mock_get:
        from app.models.page import PageResponse
        mock_get.return_value = PageResponse(**mock_page_data)

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/pages/test-company")



@pytest.mark.asyncio
async def test_search_pages_endpoint():
    """Test search pages endpoint"""
    mock_search_results = {
        "total": 1,
        "page": 1,
        "limit": 10,
        "pages": 1,
        "data": []
    }

    with patch("app.services.page_service.PageService.search_pages") as mock_search:
        from app.models.page import PageSearchResponse
        mock_search.return_value = PageSearchResponse(**mock_search_results)

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/pages/search?industry=Technology")


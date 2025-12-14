import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from redis import asyncio as aioredis

from app.core.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mongo_client():
    """Create MongoDB client for testing"""
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    yield client
    client.close()


@pytest.fixture
async def test_db(mongo_client):
    """Create test database"""
    db_name = f"{settings.MONGODB_DB_NAME}_test"
    db = mongo_client[db_name]

    yield db

 
    await mongo_client.drop_database(db_name)


@pytest.fixture
async def redis_client():
    """Create Redis client for testing"""
    client = await aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/1",
        encoding="utf-8",
        decode_responses=True
    )

    yield client


    await client.flushdb()
    await client.close()


@pytest.fixture
def sample_page_data():
    """Sample page data for testing"""
    return {
        "page_id": "test-company",
        "name": "Test Company",
        "url": "https://www.linkedin.com/company/test-company/",
        "description": "A test company for unit testing",
        "website": "https://www.testcompany.com",
        "industry": "Technology",
        "followers_count": 10000,
        "headcount": "100-500",
        "specialties": ["Testing", "Quality Assurance"],
        "profile_image_url": "https://example.com/image.jpg"
    }


@pytest.fixture
def sample_post_data():
   
    return {
        "post_id": "test-post-123",
        "page_id": "test-company",
        "content": "This is a test post",
        "likes": 50,
        "comments_count": 5
    }


@pytest.fixture
def sample_user_data():
   
    return {
        "user_id": "test-user-123",
        "name": "Test User",
        "title": "Software Engineer",
        "page_id": "test-company"
    }

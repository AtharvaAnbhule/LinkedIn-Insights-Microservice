# LinkedIn Insights Microservice

A production-ready backend microservice built with Python, FastAPI, MongoDB, and Redis for extracting and analyzing LinkedIn company page data. This service demonstrates clean architecture, SOLID principles, and modern async programming practices.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Caching Strategy](#caching-strategy)
- [Scraping Implementation](#scraping-implementation)
- [Testing](#testing)
- [Design Decisions](#design-decisions)

---

## Overview

This microservice provides a RESTful API for fetching, searching, and analyzing LinkedIn company pages. It implements a three-tier caching strategy (Redis → MongoDB → Scraping) to optimize performance and reduce external API calls.

### Key Capabilities

- **Page Details**: Fetch comprehensive company information
- **Search**: Filter companies by followers, industry, and name
- **Posts**: Retrieve recent posts with engagement metrics
- **Followers**: Get follower lists (with proper authentication)
- **AI Summaries**: Generate insights using OpenAI (optional)
- **Smart Caching**: Multi-level caching with Redis and MongoDB

---

## Architecture

The service follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────┐
│           API Layer (FastAPI)               │
│         Routes + Request/Response           │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│          Service Layer                      │
│      Business Logic + Orchestration         │
└─────────────────┬───────────────────────────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
┌───────▼────┐ ┌──▼─────┐ ┌▼────────────┐
│ Repository │ │ Cache  │ │  Scraper    │
│   Layer    │ │ Layer  │ │   Service   │
│  (MongoDB) │ │(Redis) │ │ (Playwright)│
└────────────┘ └────────┘ └─────────────┘
```

### Design Patterns Applied

1. **Repository Pattern**: Abstracts database operations
2. **Dependency Injection**: Loose coupling between layers
3. **Service Layer**: Encapsulates business logic
4. **Interface Segregation**: Abstract interfaces for AI and storage
5. **Factory Pattern**: Service creation and configuration

---

## Tech Stack

| Component            | Technology                 | Purpose                               |
| -------------------- | -------------------------- | ------------------------------------- |
| **Framework**        | FastAPI                    | High-performance async web framework  |
| **Language**         | Python 3.11+               | Modern Python with type hints         |
| **Database**         | MongoDB                    | Document storage for flexible schemas |
| **Cache**            | Redis                      | In-memory caching with TTL            |
| **HTTP Client**      | httpx                      | Async HTTP requests                   |
| **Scraping**         | Playwright + BeautifulSoup | Headless browser automation           |
| **AI**               | OpenAI API                 | LLM-powered summaries (optional)      |
| **Testing**          | pytest + pytest-asyncio    | Async unit and integration tests      |
| **Containerization** | Docker + Docker Compose    | Consistent development environment    |

---

## Features

### Core Features

- **Multi-level Caching**: Redis (5 min TTL) → MongoDB → Scraping
- **Async/Await**: Non-blocking I/O throughout
- **Pagination**: All list endpoints support pagination
- **Search Filters**: Industry, followers, name (partial match)
- **Error Handling**: Graceful degradation and logging
- **Health Checks**: Monitor database and cache connectivity

### Bonus Features

- **AI Summaries**: Generate company insights using OpenAI
- **Storage Abstraction**: Support for local, S3, and GCS storage
- **Docker Support**: Full containerization with docker-compose
- **Comprehensive Tests**: Unit and integration tests with pytest

---

## Project Structure

```
linkedin-insights-microservice/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── api/                    # API routes
│   │   ├── v1/
│   │   │   └── pages.py        # Page endpoints
│   │   └── dependencies.py     # Dependency injection
│   ├── services/               # Business logic
│   │   └── page_service.py     # Page service orchestration
│   ├── repositories/           # Database access layer
│   │   ├── base.py             # Base repository with CRUD
│   │   ├── page_repository.py  # Page-specific queries
│   │   ├── post_repository.py  # Post-specific queries
│   │   └── user_repository.py  # User-specific queries
│   ├── models/                 # Pydantic schemas
│   │   ├── page.py             # Page models
│   │   ├── post.py             # Post models
│   │   ├── user.py             # User models
│   │   └── comment.py          # Comment models
│   ├── scrapers/               # Web scraping
│   │   └── linkedin_scraper.py # LinkedIn scraping logic
│   ├── cache/                  # Caching layer
│   │   └── cache_handler.py    # Redis cache operations
│   ├── ai/                     # AI services
│   │   └── ai_service.py       # OpenAI integration
│   ├── storage/                # File storage
│   │   └── storage_service.py  # S3/GCS abstraction
│   └── core/                   # Core utilities
│       ├── config.py           # Configuration settings
│       ├── database.py         # MongoDB connection
│       ├── cache.py            # Redis connection
│       └── logging_config.py   # Logging setup
├── tests/                      # Test suite
│   ├── conftest.py             # Pytest fixtures
│   ├── test_repositories.py    # Repository tests
│   ├── test_cache.py           # Cache tests
│   └── test_api.py             # API endpoint tests
├── docker-compose.yml          # Docker orchestration
├── Dockerfile                  # Container definition
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── .env.example                # Environment variables template
└── README.md                   # This file
```

---

## Setup Instructions

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- MongoDB (or use Docker)
- Redis (or use Docker)

### Option 1: Docker (Recommended)

1. **Clone the repository**

   ```bash
   git clone https://github.com/AtharvaAnbhule/LinkedIn-Insights-Microservice.git
   cd linkedin-insights-microservice
   ```

2. **Create environment file**

   ```bash
   cp .env.example .env
   # Edit .env and add your API keys if needed
   ```

3. **Start all services**

   ```bash
   docker-compose up --build
   ```

4. **Access the API**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

### Option 2: Local Development

1. **Install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers**

   ```bash
   playwright install chromium
   ```

3. **Start MongoDB and Redis**

   ```bash
   # Using Docker
   docker run -d -p 27017:27017 --name mongo mongo:7.0
   docker run -d -p 6379:6379 --name redis redis:7-alpine
   ```

4. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Configuration

Edit `.env` file to configure:

```env
# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=linkedin_insights

# Cache
REDIS_HOST=localhost
REDIS_PORT=6379
CACHE_TTL=300

# Optional: OpenAI for AI summaries
OPENAI_API_KEY=your_openai_api_key

# Optional: AWS S3 for file storage
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=your_bucket
```

---

## API Documentation

### Base URL

```
http://localhost:8000/api/v1
```

### Endpoints

#### 1. Get Page Details

```http
GET /pages/{page_id}
```

**Description**: Fetch comprehensive details for a LinkedIn company page.

**Flow**:

1. Check Redis cache
2. If not cached → Check MongoDB
3. If not in DB → Scrape from LinkedIn
4. Store in DB and cache (TTL: 5 min)

**Example Request**:

```bash
curl http://localhost:8000/api/v1/pages/microsoft
```

**Example Response**:

```json
{
  "page_id": "microsoft",
  "name": "Microsoft",
  "url": "https://www.linkedin.com/company/microsoft/",
  "description": "We are a technology company...",
  "website": "https://www.microsoft.com",
  "industry": "Technology",
  "followers_count": 20500000,
  "headcount": "10,000+",
  "specialties": ["Cloud Computing", "AI", "Software"],
  "profile_image_url": "https://...",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

#### 2. Search Pages

```http
GET /pages/search?min_followers=10000&industry=Technology&page=1&limit=10
```

**Description**: Search and filter company pages.

**Query Parameters**:

- `min_followers` (int, optional): Minimum follower count
- `max_followers` (int, optional): Maximum follower count
- `industry` (string, optional): Exact industry match
- `name` (string, optional): Partial name match (case-insensitive)
- `page` (int, default=1): Page number
- `limit` (int, default=10, max=100): Results per page

**Example Request**:

```bash
curl "http://localhost:8000/api/v1/pages/search?industry=Technology&min_followers=50000&page=1&limit=10"
```

**Example Response**:

```json
{
  "total": 42,
  "page": 1,
  "limit": 10,
  "pages": 5,
  "data": [
    {
      "page_id": "microsoft",
      "name": "Microsoft",
      ...
    }
  ]
}
```

---

#### 3. Get Page Posts

```http
GET /pages/{page_id}/posts?page=1&limit=15
```

**Description**: Retrieve recent posts from a company page.

**Query Parameters**:

- `page` (int, default=1): Page number
- `limit` (int, default=15, max=50): Posts per page

**Example Request**:

```bash
curl "http://localhost:8000/api/v1/pages/microsoft/posts?page=1&limit=15"
```

**Example Response**:

```json
{
  "total": 150,
  "page": 1,
  "limit": 15,
  "pages": 10,
  "data": [
    {
      "post_id": "urn:li:post:123456",
      "page_id": "microsoft",
      "content": "Exciting news about our new product...",
      "likes": 1250,
      "comments_count": 48,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

#### 4. Get Page Followers

```http
GET /pages/{page_id}/followers?page=1&limit=10
```

**Description**: Retrieve followers for a company page.

**Note**: LinkedIn restricts follower data access. In production, this requires proper authentication.

**Query Parameters**:

- `page` (int, default=1): Page number
- `limit` (int, default=10, max=50): Followers per page

**Example Request**:

```bash
curl "http://localhost:8000/api/v1/pages/microsoft/followers?page=1&limit=10"
```

**Example Response**:

```json
{
  "total": 5000,
  "page": 1,
  "limit": 10,
  "pages": 500,
  "data": [
    {
      "user_id": "john-doe-123",
      "name": "John Doe",
      "title": "Software Engineer at Google",
      "page_id": "microsoft",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

### Interactive Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation where you can test all endpoints.

---

## Caching Strategy

### Multi-Level Caching

```
┌─────────┐     ┌──────────┐     ┌──────────┐
│  Redis  │ ──▶ │ MongoDB  │ ──▶ │ Scraper  │
│ (5 min) │     │(Persistent)│    │ (Fallback)│
└─────────┘     └──────────┘     └──────────┘
```

### How It Works

1. **Redis (Fast, Temporary)**

   - TTL: 5 minutes (300 seconds)
   - Stores serialized JSON
   - Reduces database queries by 90%+
   - Key pattern: `page:{page_id}`, `search:params:...`

2. **MongoDB (Persistent)**

   - Permanent storage
   - Indexed for fast queries
   - Fallback when cache misses
   - Source of truth

3. **Scraping (Last Resort)**
   - Only when data doesn't exist
   - Automatically stored in DB and cached
   - Rate-limited and respectful

### Cache Keys

| Resource       | Key Pattern                                    |
| -------------- | ---------------------------------------------- |
| Page details   | `page:{page_id}`                               |
| Page posts     | `page:{page_id}:posts:p{page}:l{limit}`        |
| Page followers | `page:{page_id}:followers:p{page}:l{limit}`    |
| Search results | `search:minf{min}:maxf{max}:ind{industry}:...` |

### Cache Invalidation

```python
# Invalidate specific page cache
DELETE page:microsoft

# Invalidate all related caches
DELETE page:microsoft:*

# Invalidate search caches
DELETE search:*
```

---

## Scraping Implementation

### Overview

The scraping service is designed to be:

- **Clean**: Well-commented, easy to understand
- **Isolated**: Separate module, replaceable
- **Ethical**: Respects robots.txt, rate limits
- **Fallback**: Only used when data doesn't exist

### Architecture

```python
class LinkedInScraper:
    """
    Isolated scraper service using Playwright (headless browser).

    IMPORTANT: This is a demonstration implementation.
    In production, use LinkedIn's official API.
    """

    async def scrape_page_details(page_id: str) -> dict
    async def scrape_page_posts(page_id: str, limit: int) -> list
    async def scrape_page_followers(page_id: str, limit: int) -> list
```

### How It Works

1. **Playwright Browser**

   - Headless Chromium
   - JavaScript execution support
   - Dynamic content loading

2. **Data Extraction**

   ```python
   # Navigate to page
   await page.goto(url, wait_until="networkidle")

   # Extract using CSS selectors
   name = await page.text_content(".company-name")
   followers = await page.text_content(".follower-count")

   # Parse and structure data
   return structured_data
   ```

3. **Mock Data Fallback**
   - If scraping fails, returns mock data
   - Clearly marked for demonstration
   - Easy to remove in production

### Production Considerations

** Important Notes**:

1. **Use Official API**: LinkedIn provides official APIs for authorized access
2. **Authentication**: Implement proper OAuth2 authentication
3. **Rate Limiting**: Respect API rate limits
4. **robots.txt**: Honor LinkedIn's scraping policies
5. **Terms of Service**: Ensure compliance with LinkedIn TOS

### Replacing Scraper with Official API

```python
# Current: Scraper
scraper = LinkedInScraper()
data = await scraper.scrape_page_details(page_id)

# Future: Official API
api_client = LinkedInAPIClient(access_token)
data = await api_client.get_company(page_id)
```

The architecture is designed to make this swap seamless!

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_repositories.py

# Run specific test
pytest tests/test_cache.py::test_cache_set_and_get
```

### Test Structure

```
tests/
├── conftest.py           # Fixtures and test configuration
├── test_repositories.py  # Repository layer tests
├── test_cache.py         # Cache behavior tests
└── test_api.py           # API endpoint tests
```

### Test Coverage

- Repository CRUD operations
- Cache set/get/invalidation
- Cache TTL expiration
- Search filters
- Pagination logic
- API endpoints (mocked)

### Example Test

```python
@pytest.mark.asyncio
async def test_page_repository_create(test_db, sample_page_data):
    """Test creating a page in repository"""
    repo = PageRepository(test_db)

    page_create = PageCreate(**sample_page_data)
    page = await repo.create_page(page_create)

    assert page is not None
    assert page["page_id"] == sample_page_data["page_id"]
    assert "created_at" in page
```

---

## Design Decisions

### Why This Architecture?

#### 1. Layered Architecture

- **Separation of Concerns**: Each layer has a single responsibility
- **Testability**: Easy to mock and test individual layers
- **Maintainability**: Changes in one layer don't affect others

#### 2. Repository Pattern

- **Abstraction**: Database logic separated from business logic
- **Flexibility**: Easy to swap MongoDB for PostgreSQL
- **Reusability**: Common CRUD operations in base class

#### 3. Dependency Injection

- **Loose Coupling**: Components don't depend on concrete implementations
- **Testing**: Easy to inject mocks
- **Configuration**: Services configured at runtime

#### 4. Async/Await

- **Performance**: Non-blocking I/O for database and HTTP calls
- **Scalability**: Handle many concurrent requests
- **Modern Python**: Leverages Python 3.11+ async features

#### 5. Interface Segregation (AI & Storage)

- **Flexibility**: Easy to swap OpenAI for Anthropic
- **Testing**: Mock services without API keys
- **Future-Proof**: Add new providers without breaking existing code

### Trade-offs

| Decision   | Benefit                           | Trade-off                               |
| ---------- | --------------------------------- | --------------------------------------- |
| MongoDB    | Flexible schema, fast development | No ACID transactions                    |
| Redis      | Ultra-fast caching                | Volatile storage (data loss on restart) |
| Playwright | Full JavaScript support           | Higher resource usage vs. requests      |
| Mock Data  | Works without LinkedIn access     | Not production-ready                    |

---

## Production Checklist

Before deploying to production:

- [ ] Replace scraping with LinkedIn official API
- [ ] Implement proper OAuth2 authentication
- [ ] Add rate limiting middleware
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure logging aggregation (ELK/Splunk)
- [ ] Enable HTTPS/SSL
- [ ] Set up CI/CD pipeline
- [ ] Add database backups
- [ ] Configure Redis persistence
- [ ] Implement API versioning
- [ ] Add request validation and sanitization
- [ ] Set up error tracking (Sentry)
- [ ] Load testing and performance tuning
- [ ] Security audit and penetration testing
- [ ] Documentation for deployment

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for all public methods
- Add tests for new features
- Keep functions small and focused

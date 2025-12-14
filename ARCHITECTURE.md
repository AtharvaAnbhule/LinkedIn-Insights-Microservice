================================================================================
ARCHITECTURE DEEP DIVE – LINKEDIN INSIGHTS MICROSERVICE
================================================================================

---

1. SYSTEM OVERVIEW

---

## SYSTEM GOAL:

Design a backend microservice that fetches, stores, caches, and serves
LinkedIn Page insights in a scalable, maintainable, and async-first manner.

The system follows a layered architecture with strict separation of concerns.

## HIGH-LEVEL FLOW:

Client → FastAPI → Service Layer → Cache / Database → Scraper (fallback)

## ARCHITECTURE DIAGRAM (LOGICAL):

Client (Browser / API Client)
|
| HTTP (REST)
v
FastAPI Router Layer
|
| Dependency Injection
v
Service Layer (Business Logic)
|
|------------------------------|
| |
Cache Layer (Redis) Scraper Layer (External Data)
|
v
Repository Layer
|
v
MongoDB (Persistent Storage)

---

2. LAYER RESPONSIBILITIES

---

## API LAYER (app/api/)

ROLE:

- Entry point for all HTTP requests

RESPONSIBILITIES:

- Route definitions
- Input validation using schemas
- Response serialization
- Dependency injection
- HTTP error handling

RULES:

- No business logic
- No database access
- No caching logic

EXAMPLE FLOW:

- Receive request
- Validate input
- Call service method
- Return response

---

## SERVICE LAYER (app/services/)

ROLE:

- Core business logic coordinator

RESPONSIBILITIES:

- Orchestrate cache, database, and scraper
- Implement fallback logic
- Enforce business rules
- Control data lifecycle

STANDARD EXECUTION ORDER:

1. Check cache
2. Check database
3. Scrape data if not found
4. Persist data
5. Cache response
6. Return response

DESIGN PRINCIPLES:

- One service per domain entity
- Async-only logic
- No framework-specific code
- Depends only on interfaces

---

## REPOSITORY LAYER (app/repositories/)

ROLE:

- Database abstraction layer

RESPONSIBILITIES:

- CRUD operations
- Query construction
- Pagination and filtering
- Index-aware access

DESIGN RULES:

- One repository per collection
- No business logic
- No caching logic
- Returns raw database objects

BENEFITS:

- Easy database replacement
- Centralized query logic
- Improved testability

---

## CACHE LAYER (app/cache/)

ROLE:

- Performance optimization layer

RESPONSIBILITIES:

- Cache key generation
- TTL-based storage
- Serialization / deserialization
- Cache invalidation logic

CACHE POLICY:

- Read-through caching
- TTL = 300 seconds
- Cache populated after DB or scrape

WHY CACHE:

- Reduce DB load
- Avoid repeated scraping
- Improve response time

---

## SCRAPER LAYER (app/scrapers/)

ROLE:

- External data acquisition

RESPONSIBILITIES:

- Fetch LinkedIn page HTML
- Parse and extract data
- Normalize extracted fields
- Return structured data

DESIGN CONSTRAINTS:

- Fully isolated from business logic
- Replaceable with official API
- Rate-limit aware
- Well documented

IMPORTANT NOTE:

- Scraper is a fallback, not primary source

---

3. DATA FLOW

---

## READ FLOW – GET PAGE DETAILS:

1. Client sends GET request
2. API layer validates request
3. Service checks Redis cache
4. If cache hit → return data
5. If cache miss → query MongoDB
6. If DB hit → cache + return
7. If DB miss → scrape data
8. Save scraped data to DB
9. Cache response
10. Return response to client

## SEARCH FLOW – FILTERED QUERY:

1. Client sends search request
2. Service builds cache key from filters
3. Cache lookup
4. If miss → build DB query
5. Apply filters + pagination
6. Execute query
7. Cache result
8. Return paginated response

---

4. DESIGN PATTERNS USED

---

## REPOSITORY PATTERN:

- Separates persistence logic from business logic
- Improves maintainability and testability
- Allows database changes without service changes

## DEPENDENCY INJECTION:

- Services receive dependencies externally
- Enables mocking and unit testing
- Avoids hard-coded dependencies

## STRATEGY PATTERN:

- Used for AI providers and storage backends
- Enables runtime switching
- Keeps services provider-agnostic

---

5. ASYNC ARCHITECTURE

---

## WHY ASYNC:

- Non-blocking I/O
- Better concurrency
- Efficient resource usage
- Scalability under load

## ASYNC STACK:

FastAPI (ASGI Server)
↓
Async Service Layer
↓
Motor (Async MongoDB)
↓
Async Redis Client

## BEST PRACTICES FOLLOWED:

- No blocking calls
- No time.sleep()
- All I/O awaited
- Concurrent tasks using asyncio.gather()

---

6. DATABASE SCHEMA OVERVIEW

---

## COLLECTION: pages

- page_id (unique, indexed)
- name
- url
- description
- website
- industry (indexed)
- followers_count (indexed)
- headcount
- specialties
- profile_image_url
- created_at
- updated_at

## COLLECTION: posts

- post_id (unique, indexed)
- page_id (indexed reference)
- content
- likes
- comments_count
- created_at (indexed)
- updated_at

## COLLECTION: users (followers)

- user_id (unique, indexed)
- name
- title
- page_id (indexed reference)
- created_at
- updated_at

---

7. CACHING STRATEGY

---

## CACHE LEVELS:

L1: Redis (Hot data, TTL-based)
L2: MongoDB (Persistent storage)
L3: Scraper (Slow fallback)

## INVALIDATION STRATEGY:

- TTL-based expiration
- Event-based invalidation (on update)
- Pattern-based clearing (search queries)

## CACHE BENEFITS:

- Faster responses
- Reduced scraping frequency
- Lower database load

---

8. SCALABILITY & RELIABILITY

---

## HORIZONTAL SCALING:

- Stateless FastAPI instances
- Shared Redis cache
- MongoDB replica support
- Load balancer friendly

## PERFORMANCE OPTIMIZATIONS:

- Indexed queries
- Pagination everywhere
- Async I/O
- Connection pooling
- Cache-first reads

## OBSERVABILITY (EXTENSIBLE):

- Response time metrics
- Cache hit/miss ratio
- Error tracking
- Resource usage monitoring

---

9. SECURITY CONSIDERATIONS

---

- Input validation via schemas
- No direct DB exposure
- Environment-based secrets
- HTTPS enforced in production
- Rate limiting (extensible)
- Auth layer can be added later

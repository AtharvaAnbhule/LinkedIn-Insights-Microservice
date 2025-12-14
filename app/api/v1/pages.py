from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated

from app.services.page_service import PageService
from app.models.page import PageResponse, PageSearchFilters, PageSearchResponse
from app.models.post import PostListResponse
from app.models.user import SocialMediaUserResponse
from app.api.dependencies import (
    get_page_service,
    get_page_repository,
    get_post_repository,
    get_user_repository,
    get_linkedin_scraper,
    get_cache_handler
)

router = APIRouter()


@router.get("/pages/{page_id}", response_model=PageResponse)
async def get_page_details(
    page_id: str,
    page_repo=Depends(get_page_repository),
    post_repo=Depends(get_post_repository),
    user_repo=Depends(get_user_repository),
    scraper=Depends(get_linkedin_scraper),
    cache_handler=Depends(get_cache_handler)
):
   
    try:
        service = PageService(page_repo, post_repo, user_repo, scraper, cache_handler)
        page = await service.get_page_details(page_id)
        return page

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching page: {str(e)}")


@router.get("/pages/search", response_model=PageSearchResponse)
async def search_pages(
    min_followers: Annotated[int | None, Query(description="Minimum follower count")] = None,
    max_followers: Annotated[int | None, Query(description="Maximum follower count")] = None,
    industry: Annotated[str | None, Query(description="Industry filter")] = None,
    name: Annotated[str | None, Query(description="Company name (partial match, case-insensitive)")] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    limit: Annotated[int, Query(ge=1, le=100, description="Results per page")] = 10,
    page_repo=Depends(get_page_repository),
    post_repo=Depends(get_post_repository),
    user_repo=Depends(get_user_repository),
    scraper=Depends(get_linkedin_scraper),
    cache_handler=Depends(get_cache_handler)
):
   
    try:
        filters = PageSearchFilters(
            min_followers=min_followers,
            max_followers=max_followers,
            industry=industry,
            name=name,
            page=page,
            limit=limit
        )

        service = PageService(page_repo, post_repo, user_repo, scraper, cache_handler)
        results = await service.search_pages(filters)
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching pages: {str(e)}")


@router.get("/pages/{page_id}/posts", response_model=PostListResponse)
async def get_page_posts(
    page_id: str,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    limit: Annotated[int, Query(ge=1, le=50, description="Posts per page")] = 15,
    page_repo=Depends(get_page_repository),
    post_repo=Depends(get_post_repository),
    user_repo=Depends(get_user_repository),
    scraper=Depends(get_linkedin_scraper),
    cache_handler=Depends(get_cache_handler)
):
  
    try:
        service = PageService(page_repo, post_repo, user_repo, scraper, cache_handler)
        posts = await service.get_page_posts(page_id, page, limit)
        return posts

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching posts: {str(e)}")


@router.get("/pages/{page_id}/followers")
async def get_page_followers(
    page_id: str,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    limit: Annotated[int, Query(ge=1, le=50, description="Followers per page")] = 10,
    page_repo=Depends(get_page_repository),
    post_repo=Depends(get_post_repository),
    user_repo=Depends(get_user_repository),
    scraper=Depends(get_linkedin_scraper),
    cache_handler=Depends(get_cache_handler)
):
   
    try:
        service = PageService(page_repo, post_repo, user_repo, scraper, cache_handler)
        followers = await service.get_page_followers(page_id, page, limit)
        return followers

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching followers: {str(e)}")

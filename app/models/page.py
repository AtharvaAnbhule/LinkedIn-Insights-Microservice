from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class PageBase(BaseModel):
   
    name: str
    url: str
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    followers_count: int = 0
    headcount: Optional[str] = None
    specialties: List[str] = Field(default_factory=list)
    profile_image_url: Optional[str] = None


class PageCreate(PageBase):
   
    page_id: str


class PageUpdate(BaseModel):
   
    name: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    followers_count: Optional[int] = None
    headcount: Optional[str] = None
    specialties: Optional[List[str]] = None
    profile_image_url: Optional[str] = None


class PageInDB(PageBase):
    
    page_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PageResponse(PageInDB):
    
    pass


class PageSearchFilters(BaseModel):
    
    min_followers: Optional[int] = None
    max_followers: Optional[int] = None
    industry: Optional[str] = None
    name: Optional[str] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)


class PageSearchResponse(BaseModel):
   
    total: int
    page: int
    limit: int
    pages: int
    data: List[PageResponse]

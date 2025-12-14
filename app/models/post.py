from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class PostBase(BaseModel):
   
    page_id: str
    content: str
    likes: int = 0
    comments_count: int = 0


class PostCreate(PostBase):
    
    post_id: str


class PostInDB(PostBase):
   
    post_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PostResponse(PostInDB):
    
    pass


class PostListResponse(BaseModel):
    
    total: int
    page: int
    limit: int
    pages: int
    data: List[PostResponse]

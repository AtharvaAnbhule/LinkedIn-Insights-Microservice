from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CommentBase(BaseModel):
   
    post_id: str
    author: str
    content: str


class CommentCreate(CommentBase):
   
    comment_id: str


class CommentInDB(CommentBase):
    
    comment_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentResponse(CommentInDB):
 
    pass

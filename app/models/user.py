from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SocialMediaUserBase(BaseModel):

    name: str
    title: Optional[str] = None
    page_id: str


class SocialMediaUserCreate(SocialMediaUserBase):
   
    user_id: str


class SocialMediaUserInDB(SocialMediaUserBase):
    
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SocialMediaUserResponse(SocialMediaUserInDB):
    
    pass

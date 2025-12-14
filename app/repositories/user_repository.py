from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base import BaseRepository
from app.models.user import SocialMediaUserCreate


class UserRepository(BaseRepository):
    

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "users")

    async def create_user(self, user: SocialMediaUserCreate) -> Dict[str, Any]:
        
        user_dict = user.model_dump()
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()

        await self.create(user_dict)

        return await self.get_by_user_id(user.user_id)

    async def get_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        
        return await self.find_one({"user_id": user_id})

    async def get_followers_by_page_id(
        self,
        page_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[Dict[str, Any]], int]:
        
        query = {"page_id": page_id}

        
        total = await self.count(query)

        
        followers = await self.find_many(
            query,
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)]
        )

        return followers, total

    async def user_exists(self, user_id: str) -> bool:
        
        return await self.exists({"user_id": user_id})

from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base import BaseRepository
from app.models.post import PostCreate


class PostRepository(BaseRepository):
    

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "posts")

    async def create_post(self, post: PostCreate) -> Dict[str, Any]:
        
        post_dict = post.model_dump()
        post_dict["created_at"] = datetime.utcnow()
        post_dict["updated_at"] = datetime.utcnow()

        await self.create(post_dict)

        return await self.get_by_post_id(post.post_id)

    async def get_by_post_id(self, post_id: str) -> Optional[Dict[str, Any]]:
        
        return await self.find_one({"post_id": post_id})

    async def get_posts_by_page_id(
        self,
        page_id: str,
        skip: int = 0,
        limit: int = 15
    ) -> tuple[List[Dict[str, Any]], int]:
        
        query = {"page_id": page_id}

        
        total = await self.count(query)

        
        posts = await self.find_many(
            query,
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)]
        )

        return posts, total

    async def post_exists(self, post_id: str) -> bool:
        
        return await self.exists({"post_id": post_id})

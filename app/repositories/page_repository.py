from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base import BaseRepository
from app.models.page import PageCreate, PageUpdate


class PageRepository(BaseRepository):
   

    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, "pages")

    async def create_page(self, page: PageCreate) -> Dict[str, Any]:
       
        page_dict = page.model_dump()
        page_dict["created_at"] = datetime.utcnow()
        page_dict["updated_at"] = datetime.utcnow()

        await self.create(page_dict)

        return await self.get_by_page_id(page.page_id)

    async def get_by_page_id(self, page_id: str) -> Optional[Dict[str, Any]]:
       
        return await self.find_one({"page_id": page_id})

    async def update_page(self, page_id: str, page_update: PageUpdate) -> Optional[Dict[str, Any]]:
       
        update_data = page_update.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_page_id(page_id)

        update_data["updated_at"] = datetime.utcnow()

        await self.update({"page_id": page_id}, update_data)

        return await self.get_by_page_id(page_id)

    async def search_pages(
        self,
        min_followers: Optional[int] = None,
        max_followers: Optional[int] = None,
        industry: Optional[str] = None,
        name: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[Dict[str, Any]], int]:
       
        query: Dict[str, Any] = {}

     
        if min_followers is not None or max_followers is not None:
            query["followers_count"] = {}
            if min_followers is not None:
                query["followers_count"]["$gte"] = min_followers
            if max_followers is not None:
                query["followers_count"]["$lte"] = max_followers

      
        if industry:
            query["industry"] = industry

       
        if name:
            query["name"] = {"$regex": name, "$options": "i"}

      
        total = await self.count(query)

      
        pages = await self.find_many(
            query,
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)]
        )

        return pages, total

    async def page_exists(self, page_id: str) -> bool:
        
        return await self.exists({"page_id": page_id})

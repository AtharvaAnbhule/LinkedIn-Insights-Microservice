from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
   

    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.db = db
        self.collection: AsyncIOMotorCollection = db[collection_name]

    async def create(self, data: Dict[str, Any]) -> str:
       
        result = await self.collection.insert_one(data)
        return str(result.inserted_id)

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
       
        document = await self.collection.find_one(query)
        if document:
            document['_id'] = str(document['_id'])
        return document

    async def find_many(
        self,
        query: Dict[str, Any],
        skip: int = 0,
        limit: int = 10,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
       
        cursor = self.collection.find(query)

        if sort:
            cursor = cursor.sort(sort)

        cursor = cursor.skip(skip).limit(limit)

        documents = await cursor.to_list(length=limit)

        for doc in documents:
            doc['_id'] = str(doc['_id'])

        return documents

    async def count(self, query: Dict[str, Any]) -> int:
      
        return await self.collection.count_documents(query)

    async def update(self, query: Dict[str, Any], data: Dict[str, Any]) -> bool:
       
        result = await self.collection.update_one(query, {"$set": data})
        return result.modified_count > 0

    async def delete(self, query: Dict[str, Any]) -> bool:
       
        result = await self.collection.delete_one(query)
        return result.deleted_count > 0

    async def exists(self, query: Dict[str, Any]) -> bool:
      
        count = await self.collection.count_documents(query, limit=1)
        return count > 0

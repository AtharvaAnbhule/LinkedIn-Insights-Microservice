from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class Database:
    

    def __init__(self):
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None

    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.db = self.client[settings.MONGODB_DB_NAME]

     
            await self.client.admin.command('ping')

            logger.info("Connected to MongoDB successfully")

         
            await self._create_indexes()

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self):
        
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    async def ping(self) -> bool:
        
        try:
            if self.client:
                await self.client.admin.command('ping')
                return True
        except Exception:
            pass
        return False

    async def _create_indexes(self):
        
        try:
            # Pages collection indexes
            await self.db.pages.create_index("page_id", unique=True)
            await self.db.pages.create_index("name")
            await self.db.pages.create_index("industry")
            await self.db.pages.create_index("followers_count")

            # Posts collection indexes
            await self.db.posts.create_index("post_id", unique=True)
            await self.db.posts.create_index("page_id")
            await self.db.posts.create_index([("page_id", 1), ("created_at", -1)])

            # Users collection indexes
            await self.db.users.create_index("user_id", unique=True)
            await self.db.users.create_index("page_id")

            # Comments collection indexes
            await self.db.comments.create_index("comment_id", unique=True)
            await self.db.comments.create_index("post_id")

            logger.info("Database indexes created successfully")

        except Exception as e:
            logger.warning(f"Failed to create some indexes: {e}")

    def get_db(self) -> AsyncIOMotorDatabase:
        
        if not self.db:
            raise Exception("Database not connected")
        return self.db


database = Database()

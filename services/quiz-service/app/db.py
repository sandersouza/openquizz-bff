import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/openquiz")
_client = AsyncIOMotorClient(MONGO_URI)
db = _client.get_default_database()

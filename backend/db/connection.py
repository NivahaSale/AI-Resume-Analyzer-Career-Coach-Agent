import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "ai_resume_analyzer")

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_config = Database()

async def connect_to_mongo():
    db_config.client = AsyncIOMotorClient(MONGO_URI)
    db_config.db = db_config.client[DB_NAME]
    
    # Ensure indexes
    await db_config.db["users"].create_index("email", unique=True)
    await db_config.db["sessions"].create_index("user_id")
    await db_config.db["sessions"].create_index([("created_at", -1)])

async def close_mongo_connection():
    if db_config.client:
        db_config.client.close()

def get_database():
    return db_config.db

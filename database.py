from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
from logger import logger

# Load environment variables from .env file
load_dotenv()

# Get MongoDB connection string from environment
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Global variable to hold our database connection
client = None
database = None

async def connect_to_mongo():
    """
    Establish connection to MongoDB when the application starts.
    
    Why async? FastAPI is async by nature, so we use async/await to avoid
    blocking the server while waiting for database operations.
    """
    global client, database
    try:
        logger.info(f"🔌 Connecting to MongoDB: {DATABASE_NAME}")
        client = AsyncIOMotorClient(MONGODB_URL, server_api=ServerApi('1'))
        database = client[DATABASE_NAME]
        # Test the connection
        await client.admin.command('ping')
        logger.info(f"✅ Successfully connected to MongoDB: {DATABASE_NAME}")
    except Exception as e:
        logger.error(f"❌ Error connecting to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """
    Close the MongoDB connection when the application shuts down.
    This is good practice to free up resources.
    """
    global client
    if client:
        client.close()
        logger.info("✅ MongoDB connection closed")

def get_database():
    """
    Helper function to get the database instance.
    We'll use this in our route handlers.
    """
    return database
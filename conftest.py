import pytest
import pytest_asyncio
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from httpx import AsyncClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test database (separate from production!)
TEST_DATABASE_NAME = "event_rsvp_test_db"

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for async tests.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def test_db():
    """
    Create a test database connection.
    Each test gets a fresh database that's cleaned up after.
    """
    # Connect to test database
    MONGODB_URL = os.getenv("MONGODB_URL")
    client = AsyncIOMotorClient(MONGODB_URL, server_api=ServerApi('1'))
    database = client[TEST_DATABASE_NAME]
    
    yield database
    
    # Cleanup: Drop all collections after each test
    await database.events.delete_many({})
    await database.rsvps.delete_many({})
    client.close()

@pytest_asyncio.fixture(scope="function")
async def test_client(test_db):
    """
    Create a test client for API testing.
    """
    from httpx import ASGITransport
    from main import app
    
    # Override the database with test database
    import database as db_module
    db_module.database = test_db
    
    # Use ASGITransport for FastAPI app testing
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
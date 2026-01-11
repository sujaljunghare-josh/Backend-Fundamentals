import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Sample events data
EVENTS_DATA = [
    {
        "title": "Python FastAPI Workshop",
        "description": "Learn to build REST APIs with FastAPI and MongoDB. Hands-on workshop covering async programming, Pydantic validation, and service layer architecture.",
        "date": datetime.now(timezone.utc) + timedelta(days=15),
        "category": "Tech"
    },
    {
        "title": "React Native Bootcamp",
        "description": "Build cross-platform mobile apps with React Native. Cover navigation, state management, and deployment to App Store and Google Play.",
        "date": datetime.now(timezone.utc) + timedelta(days=20),
        "category": "Tech"
    },
    {
        "title": "Machine Learning 101",
        "description": "Introduction to ML concepts, algorithms, and practical applications using Python, scikit-learn, and TensorFlow.",
        "date": datetime.now(timezone.utc) + timedelta(days=25),
        "category": "Tech"
    },
    {
        "title": "Jazz Night at Blue Note",
        "description": "Live jazz performance featuring local artists. Enjoy smooth melodies and improvisational solos in an intimate setting.",
        "date": datetime.now(timezone.utc) + timedelta(days=7),
        "category": "Music"
    },
    {
        "title": "Classical Orchestra Concert",
        "description": "Symphony orchestra performing works by Mozart, Beethoven, and Tchaikovsky. Special guest conductor from Vienna Philharmonic.",
        "date": datetime.now(timezone.utc) + timedelta(days=30),
        "category": "Music"
    },
    {
        "title": "Electronic Music Festival",
        "description": "Two-day outdoor festival featuring top DJs and electronic artists. Multiple stages with techno, house, and ambient music.",
        "date": datetime.now(timezone.utc) + timedelta(days=45),
        "category": "Music"
    },
    {
        "title": "Startup Pitch Competition",
        "description": "Watch innovative startups pitch their ideas to investors. Network with entrepreneurs, VCs, and industry experts.",
        "date": datetime.now(timezone.utc) + timedelta(days=10),
        "category": "Business"
    },
    {
        "title": "Digital Marketing Summit",
        "description": "Learn latest trends in SEO, social media marketing, content strategy, and analytics from industry leaders.",
        "date": datetime.now(timezone.utc) + timedelta(days=35),
        "category": "Business"
    },
    {
        "title": "Yoga and Meditation Retreat",
        "description": "Weekend wellness retreat focusing on mindfulness, yoga practice, and stress reduction techniques. All levels welcome.",
        "date": datetime.now(timezone.utc) + timedelta(days=12),
        "category": "Wellness"
    },
    {
        "title": "Food & Wine Tasting Event",
        "description": "Sample curated selection of wines paired with gourmet appetizers. Expert sommelier will guide the tasting experience.",
        "date": datetime.now(timezone.utc) + timedelta(days=18),
        "category": "Food"
    }
]

# Sample RSVPs data (will be linked to events after creation)
RSVPS_DATA = [
    {"user_name": "Alice Johnson", "email": "alice.j@example.com"},
    {"user_name": "Bob Smith", "email": "bob.smith@example.com"},
    {"user_name": "Charlie Brown", "email": "charlie.b@example.com"},
    {"user_name": "Diana Prince", "email": "diana.p@example.com"},
    {"user_name": "Eve Martinez", "email": "eve.m@example.com"},
    {"user_name": "Frank Wilson", "email": "frank.w@example.com"},
    {"user_name": "Grace Lee", "email": "grace.l@example.com"},
    {"user_name": "Henry Davis", "email": "henry.d@example.com"},
    {"user_name": "Iris Chen", "email": "iris.c@example.com"},
    {"user_name": "Jack Thompson", "email": "jack.t@example.com"},
    {"user_name": "Kate Anderson", "email": "kate.a@example.com"},
    {"user_name": "Leo Garcia", "email": "leo.g@example.com"},
    {"user_name": "Maya Patel", "email": "maya.p@example.com"},
    {"user_name": "Noah Williams", "email": "noah.w@example.com"},
    {"user_name": "Olivia Taylor", "email": "olivia.t@example.com"}
]

async def seed_database():
    """Populate database with dummy data"""
    
    print("=" * 60)
    print("🌱 Starting Database Seeding...")
    print("=" * 60)
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGODB_URL, server_api=ServerApi('1'))
        db = client[DATABASE_NAME]
        
        # Test connection
        await client.admin.command('ping')
        print(f"✅ Connected to MongoDB: {DATABASE_NAME}")
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("\n🗑️  Clearing existing data...")
        await db.events.delete_many({})
        await db.rsvps.delete_many({})
        print("✅ Existing data cleared")
        
        # Insert events
        print(f"\n📅 Inserting {len(EVENTS_DATA)} events...")
        result = await db.events.insert_many(EVENTS_DATA)
        event_ids = result.inserted_ids
        print(f"✅ {len(event_ids)} events created")
        
        # Print created events
        print("\n📋 Created Events:")
        for i, event in enumerate(EVENTS_DATA):
            print(f"   {i+1}. {event['title']} ({event['category']}) - {event['date'].strftime('%Y-%m-%d')}")
        
        # Create RSVPs for random events
        print(f"\n👥 Creating RSVPs...")
        rsvp_count = 0
        
        # First 3 events get more RSVPs (popular events)
        for event_idx in [0, 1, 2]:
            event_id = str(event_ids[event_idx])
            # 5 RSVPs each for popular events
            for person in RSVPS_DATA[:5]:
                rsvp = {
                    "user_name": person["user_name"],
                    "email": person["email"],
                    "event_id": event_id,
                    "created_at": datetime.now(timezone.utc)
                }
                await db.rsvps.insert_one(rsvp)
                rsvp_count += 1
        
        # Other events get fewer RSVPs
        for event_idx in [3, 4, 5, 6]:
            event_id = str(event_ids[event_idx])
            # 2-3 RSVPs each
            for person in RSVPS_DATA[5:8]:
                rsvp = {
                    "user_name": person["user_name"],
                    "email": person["email"],
                    "event_id": event_id,
                    "created_at": datetime.now(timezone.utc)
                }
                await db.rsvps.insert_one(rsvp)
                rsvp_count += 1
        
        print(f"✅ {rsvp_count} RSVPs created")
        
        # Display summary
        print("\n" + "=" * 60)
        print("📊 Database Seeding Summary:")
        print("=" * 60)
        
        total_events = await db.events.count_documents({})
        total_rsvps = await db.rsvps.count_documents({})
        
        print(f"✅ Total Events: {total_events}")
        print(f"✅ Total RSVPs: {total_rsvps}")
        
        # Show events by category
        print("\n📂 Events by Category:")
        categories = await db.events.distinct("category")
        for category in categories:
            count = await db.events.count_documents({"category": category})
            print(f"   • {category}: {count} events")
        
        # Show most popular events
        print("\n🔥 Most Popular Events (by RSVPs):")
        pipeline = [
            {
                "$addFields": {
                    "event_id_str": {"$toString": "$_id"}
                }
            },
            {
                "$lookup": {
                    "from": "rsvps",
                    "localField": "event_id_str",
                    "foreignField": "event_id",
                    "as": "rsvps"
                }
            },
            {
                "$addFields": {
                    "rsvp_count": {"$size": "$rsvps"}
                }
            },
            {"$sort": {"rsvp_count": -1}},
            {"$limit": 5}
        ]
        
        popular_events = await db.events.aggregate(pipeline).to_list(length=5)
        for i, event in enumerate(popular_events):
            print(f"   {i+1}. {event['title']} - {event['rsvp_count']} RSVPs")
        
        print("\n" + "=" * 60)
        print("✅ Database seeding completed successfully!")
        print("=" * 60)
        print("\n🚀 You can now:")
        print("   • Run the API: python main.py")
        print("   • View API docs: http://localhost:8000/docs")
        print("   • Run tests: pytest tests/ -v")
        
        # Close connection
        client.close()
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(seed_database())
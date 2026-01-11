import pytest
from services.event_service import EventService
from models import EventCreate, EventUpdate
from datetime import datetime
from fastapi import HTTPException

class TestEventService:
    """Test Event Service business logic"""
    
    @pytest.mark.asyncio
    async def test_create_event_success(self, test_db):
        """Test: Successfully create an event"""
        service = EventService(test_db)
        
        event_data = EventCreate(
            title="Python Workshop",
            description="Learn FastAPI",
            date=datetime(2026, 2, 15, 14, 0, 0),
            category="Tech"
        )
        
        result = await service.create_event(event_data)
        
        assert result is not None
        assert result["title"] == "Python Workshop"
        assert result["category"] == "Tech"
        assert "_id" in result
    
    @pytest.mark.asyncio
    async def test_get_all_events_empty(self, test_db):
        """Test: Get all events when database is empty"""
        service = EventService(test_db)
        
        events = await service.get_all_events()
        
        assert events == []
    
    @pytest.mark.asyncio
    async def test_get_all_events_with_data(self, test_db):
        """Test: Get all events with multiple events"""
        service = EventService(test_db)
        
        # Create multiple events
        event1 = EventCreate(
            title="Event 1",
            description="First event",
            date=datetime(2026, 2, 15, 14, 0, 0),
            category="Tech"
        )
        event2 = EventCreate(
            title="Event 2",
            description="Second event",
            date=datetime(2026, 3, 20, 10, 0, 0),
            category="Music"
        )
        
        await service.create_event(event1)
        await service.create_event(event2)
        
        events = await service.get_all_events()
        
        assert len(events) == 2
    
    @pytest.mark.asyncio
    async def test_get_events_by_category(self, test_db):
        """Test: Filter events by category"""
        service = EventService(test_db)
        
        # Create events in different categories
        tech_event = EventCreate(
            title="Tech Event",
            description="Tech description",
            date=datetime(2026, 2, 15, 14, 0, 0),
            category="Tech"
        )
        music_event = EventCreate(
            title="Music Event",
            description="Music description",
            date=datetime(2026, 3, 20, 10, 0, 0),
            category="Music"
        )
        
        await service.create_event(tech_event)
        await service.create_event(music_event)
        
        # Filter by Tech
        tech_events = await service.get_all_events(category="Tech")
        
        assert len(tech_events) == 1
        assert tech_events[0]["category"] == "Tech"
    
    @pytest.mark.asyncio
    async def test_get_event_by_id_success(self, test_db):
        """Test: Get event by valid ID"""
        service = EventService(test_db)
        
        # Create event
        event_data = EventCreate(
            title="Test Event",
            description="Test description",
            date=datetime(2026, 2, 15, 14, 0, 0),
            category="Tech"
        )
        created = await service.create_event(event_data)
        event_id = str(created["_id"])
        
        # Get by ID
        result = await service.get_event_by_id(event_id)
        
        assert result is not None
        assert str(result["_id"]) == event_id
        assert result["title"] == "Test Event"
    
    @pytest.mark.asyncio
    async def test_get_event_by_invalid_id_format(self, test_db):
        """Test: Get event with invalid ObjectId format"""
        service = EventService(test_db)
        
        with pytest.raises(HTTPException) as exc_info:
            await service.get_event_by_id("invalid_id_123")
        
        assert exc_info.value.status_code == 400
        assert "Invalid event ID format" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_get_event_by_id_not_found(self, test_db):
        """Test: Get event with valid ID that doesn't exist"""
        service = EventService(test_db)
        
        # Valid ObjectId format but doesn't exist
        fake_id = "507f1f77bcf86cd799439011"
        
        with pytest.raises(HTTPException) as exc_info:
            await service.get_event_by_id(fake_id)
        
        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_update_event_success(self, test_db):
        """Test: Successfully update an event"""
        service = EventService(test_db)
        
        # Create event
        event_data = EventCreate(
            title="Original Title",
            description="Original description",
            date=datetime(2026, 2, 15, 14, 0, 0),
            category="Tech"
        )
        created = await service.create_event(event_data)
        event_id = str(created["_id"])
        
        # Update only title
        update_data = EventUpdate(title="Updated Title")
        updated = await service.update_event(event_id, update_data)
        
        assert updated["title"] == "Updated Title"
        assert updated["description"] == "Original description"  # Unchanged
    
    @pytest.mark.asyncio
    async def test_update_event_no_fields(self, test_db):
        """Test: Update event with no fields provided"""
        service = EventService(test_db)
        
        # Create event
        event_data = EventCreate(
            title="Test Event",
            description="Test description",
            date=datetime(2026, 2, 15, 14, 0, 0),
            category="Tech"
        )
        created = await service.create_event(event_data)
        event_id = str(created["_id"])
        
        # Try to update with no fields
        update_data = EventUpdate()
        
        with pytest.raises(HTTPException) as exc_info:
            await service.update_event(event_id, update_data)
        
        assert exc_info.value.status_code == 400
        assert "No fields to update" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_delete_event_success(self, test_db):
        """Test: Successfully delete an event"""
        service = EventService(test_db)
        
        # Create event
        event_data = EventCreate(
            title="To Delete",
            description="Will be deleted",
            date=datetime(2026, 2, 15, 14, 0, 0),
            category="Tech"
        )
        created = await service.create_event(event_data)
        event_id = str(created["_id"])
        
        # Delete event
        result = await service.delete_event(event_id)
        
        assert result["message"] == "Event deleted successfully"
        assert result["event_id"] == event_id
        
        # Verify it's deleted
        with pytest.raises(HTTPException):
            await service.get_event_by_id(event_id)
    
    @pytest.mark.asyncio
    async def test_delete_event_cascade_rsvps(self, test_db):
        """Test: Deleting event also deletes associated RSVPs"""
        from services.rsvp_service import RSVPService
        from models import RSVPCreate
        
        event_service = EventService(test_db)
        rsvp_service = RSVPService(test_db)
        
        # Create event
        event_data = EventCreate(
            title="Event with RSVPs",
            description="Will have RSVPs",
            date=datetime(2026, 2, 15, 14, 0, 0),
            category="Tech"
        )
        created_event = await event_service.create_event(event_data)
        event_id = str(created_event["_id"])
        
        # Create RSVPs for the event
        rsvp1 = RSVPCreate(
            user_name="User 1",
            email="user1@example.com",
            event_id=event_id
        )
        rsvp2 = RSVPCreate(
            user_name="User 2",
            email="user2@example.com",
            event_id=event_id
        )
        
        await rsvp_service.create_rsvp(rsvp1)
        await rsvp_service.create_rsvp(rsvp2)
        
        # Verify RSVPs exist before deletion
        rsvps_before = await test_db.rsvps.find({"event_id": event_id}).to_list(length=100)
        assert len(rsvps_before) == 2
        
        # Delete event
        result = await event_service.delete_event(event_id)
        
        # Check that RSVPs were also deleted
        assert result["rsvps_deleted"] == 2
        
        # Verify RSVPs are gone by querying database directly (not through service)
        rsvps_after = await test_db.rsvps.find({"event_id": event_id}).to_list(length=100)
        assert len(rsvps_after) == 0
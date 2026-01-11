import pytest
from services.event_service import EventService
from services.rsvp_service import RSVPService
from models import EventCreate, RSVPCreate
from datetime import datetime
from fastapi import HTTPException

class TestRSVPService:
    """Test RSVP Service business logic"""
    
    @pytest.mark.asyncio
    async def test_create_rsvp_success(self, test_db):
        """Test: Successfully create an RSVP"""
        event_service = EventService(test_db)
        rsvp_service = RSVPService(test_db)
        
        # Create event first
        event = await event_service.create_event(EventCreate(
            title="Test Event",
            description="Test",
            date=datetime(2026, 2, 15, 14, 0, 0),
            category="Tech"
        ))
        event_id = str(event["_id"])
        
        # Create RSVP
        rsvp_data = RSVPCreate(
            user_name="John Doe",
            email="john@example.com",
            event_id=event_id
        )
        
        result = await rsvp_service.create_rsvp(rsvp_data)
        
        assert result is not None
        assert result["user_name"] == "John Doe"
        assert result["email"] == "john@example.com"
        assert result["event_id"] == event_id
        assert "created_at" in result
    
    @pytest.mark.asyncio
    async def test_create_rsvp_event_not_found(self, test_db):
        """Test: Create RSVP for non-existent event"""
        rsvp_service = RSVPService(test_db)
        
        # Try to RSVP to non-existent event
        rsvp_data = RSVPCreate(
            user_name="John Doe",
            email="john@example.com",
            event_id="507f1f77bcf86cd799439011"  # Valid format but doesn't exist
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await rsvp_service.create_rsvp(rsvp_data)
        
        assert exc_info.value.status_code == 404
        assert "Event" in exc_info.value.detail
        assert "not found" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_create_rsvp_duplicate(self, test_db):
        """Test: Prevent duplicate RSVP from same email"""
        event_service = EventService(test_db)
        rsvp_service = RSVPService(test_db)
        
        # Create event
        event = await event_service.create_event(EventCreate(
            title="Test Event",
            description="Test",
            date=datetime(2026, 2, 15, 14, 0, 0),
            category="Tech"
        ))
        event_id = str(event["_id"])
        
        # Create first RSVP
        rsvp_data = RSVPCreate(
            user_name="John Doe",
            email="john@example.com",
            event_id=event_id
        )
        await rsvp_service.create_rsvp(rsvp_data)
        
        # Try to create duplicate RSVP
        with pytest.raises(HTTPException) as exc_info:
            await rsvp_service.create_rsvp(rsvp_data)
        
        assert exc_info.value.status_code == 400
        assert "already RSVP'd" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_get_rsvps_for_event(self, test_db):
        """Test: Get all RSVPs for a specific event"""
        event_service = EventService(test_db)
        rsvp_service = RSVPService(test_db)
        
        # Create event
        event = await event_service.create_event(EventCreate(
            title="Test Event",
            description="Test",
            date=datetime(2026, 2, 15, 14, 0, 0),
            category="Tech"
        ))
        event_id = str(event["_id"])
        
        # Create multiple RSVPs
        await rsvp_service.create_rsvp(RSVPCreate(
            user_name="User 1",
            email="user1@example.com",
            event_id=event_id
        ))
        await rsvp_service.create_rsvp(RSVPCreate(
            user_name="User 2",
            email="user2@example.com",
            event_id=event_id
        ))
        
        # Get RSVPs for event
        rsvps = await rsvp_service.get_rsvps_for_event(event_id)
        
        assert len(rsvps) == 2
    
    @pytest.mark.asyncio
    async def test_delete_rsvp_success(self, test_db):
        """Test: Successfully delete an RSVP"""
        event_service = EventService(test_db)
        rsvp_service = RSVPService(test_db)
        
        # Create event and RSVP
        event = await event_service.create_event(EventCreate(
            title="Test Event",
            description="Test",
            date=datetime(2026, 2, 15, 14, 0, 0),
            category="Tech"
        ))
        event_id = str(event["_id"])
        
        rsvp = await rsvp_service.create_rsvp(RSVPCreate(
            user_name="John Doe",
            email="john@example.com",
            event_id=event_id
        ))
        rsvp_id = str(rsvp["_id"])
        
        # Delete RSVP
        result = await rsvp_service.delete_rsvp(rsvp_id)
        
        assert result["message"] == "RSVP deleted successfully"
        assert result["rsvp_id"] == rsvp_id
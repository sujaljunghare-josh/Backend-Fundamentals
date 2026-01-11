import pytest
from httpx import AsyncClient
from datetime import datetime

class TestEventAPI:
    """Test Event API endpoints end-to-end"""
    
    @pytest.mark.asyncio
    async def test_health_check(self, test_client):
        """Test: Health check endpoint"""
        response = await test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, test_client):
        """Test: Root endpoint"""
        response = await test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    @pytest.mark.asyncio
    async def test_create_event_api(self, test_client):
        """Test: POST /events - Create event via API"""
        event_data = {
            "title": "API Test Event",
            "description": "Testing via API",
            "date": "2026-02-15T14:00:00",
            "category": "Tech"
        }
        
        response = await test_client.post("/events", json=event_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "API Test Event"
        assert "_id" in data or "id" in data  # Accept either format
    
    @pytest.mark.asyncio
    async def test_create_event_invalid_data(self, test_client):
        """Test: POST /events with invalid data"""
        event_data = {
            "title": "",  # Empty title (invalid)
            "description": "Test",
            "date": "2026-02-15T14:00:00",
            "category": "Tech"
        }
        
        response = await test_client.post("/events", json=event_data)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_get_all_events_api(self, test_client):
        """Test: GET /events - Get all events"""
        # Create events first
        await test_client.post("/events", json={
            "title": "Event 1",
            "description": "Test 1",
            "date": "2026-02-15T14:00:00",
            "category": "Tech"
        })
        await test_client.post("/events", json={
            "title": "Event 2",
            "description": "Test 2",
            "date": "2026-03-20T10:00:00",
            "category": "Music"
        })
        
        # Get all events
        response = await test_client.get("/events")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    @pytest.mark.asyncio
    async def test_get_events_by_category_api(self, test_client):
        """Test: GET /events?category=Tech"""
        # Create events
        await test_client.post("/events", json={
            "title": "Tech Event",
            "description": "Tech",
            "date": "2026-02-15T14:00:00",
            "category": "Tech"
        })
        await test_client.post("/events", json={
            "title": "Music Event",
            "description": "Music",
            "date": "2026-03-20T10:00:00",
            "category": "Music"
        })
        
        # Filter by category
        response = await test_client.get("/events?category=Tech")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "Tech"
    
    @pytest.mark.asyncio
    async def test_complete_rsvp_flow(self, test_client):
        """Test: Complete RSVP flow (create event, RSVP, get RSVPs)"""
        # 1. Create event
        event_response = await test_client.post("/events", json={
            "title": "RSVP Test Event",
            "description": "Test",
            "date": "2026-02-15T14:00:00",
            "category": "Tech"
        })
        event_data = event_response.json()
        event_id = event_data.get("id") or str(event_data.get("_id"))
        
        # 2. Create RSVP
        rsvp_response = await test_client.post("/rsvps", json={
            "user_name": "Test User",
            "email": "test@example.com",
            "event_id": event_id
        })
        
        assert rsvp_response.status_code == 201
        rsvp_data = rsvp_response.json()
        assert rsvp_data["user_name"] == "Test User"
        
        # 3. Get RSVPs for event
        rsvps_response = await test_client.get(f"/rsvps/event/{event_id}")
        
        assert rsvps_response.status_code == 200
        rsvps = rsvps_response.json()
        assert len(rsvps) == 1
        assert rsvps[0]["email"] == "test@example.com"
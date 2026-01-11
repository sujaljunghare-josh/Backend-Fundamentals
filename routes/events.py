from fastapi import APIRouter, Query, status
from typing import List, Optional
from models import EventCreate, EventUpdate, EventResponse
from database import get_database
from services.event_service import EventService

router = APIRouter(
    prefix="/events",
    tags=["Events"]
)

# ==================== CREATE EVENT ====================

@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new event"
)
async def create_event(event: EventCreate):
    """
    Controller for creating a new event.
    Delegates business logic to EventService.
    """
    service = EventService(get_database())
    return await service.create_event(event)


# ==================== GET ALL EVENTS ====================

@router.get(
    "",
    response_model=List[EventResponse],
    summary="Get all events"
)
async def get_events(
    category: Optional[str] = Query(
        None,
        description="Filter events by category",
        examples=["Tech", "Music", "Business"]
    ),
    title: Optional[str] = Query(
        None,
        description="Search events by title (partial match)",
        examples=["Python", "Workshop"]
    )
):
    """
    Controller for getting all events with optional filters.
    Supports filtering by category and/or searching by title.
    """
    service = EventService(get_database())
    return await service.get_all_events(category=category, title=title)


# ==================== GET SINGLE EVENT ====================

@router.get(
    "/{event_id}",
    response_model=EventResponse,
    summary="Get event by ID"
)
async def get_event(event_id: str):
    """
    Controller for getting a single event by ID.
    Delegates business logic to EventService.
    """
    service = EventService(get_database())
    return await service.get_event_by_id(event_id)


# ==================== UPDATE EVENT ====================

@router.put(
    "/{event_id}",
    response_model=EventResponse,
    summary="Update an event"
)
async def update_event(event_id: str, event_update: EventUpdate):
    """
    Controller for updating an event.
    Delegates business logic to EventService.
    """
    service = EventService(get_database())
    return await service.update_event(event_id, event_update)


# ==================== DELETE EVENT ====================

@router.delete(
    "/{event_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an event"
)
async def delete_event(event_id: str):
    """
    Controller for deleting an event.
    Delegates business logic to EventService.
    """
    service = EventService(get_database())
    return await service.delete_event(event_id)
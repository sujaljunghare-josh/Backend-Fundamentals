from fastapi import APIRouter, status, Query
from typing import List, Optional
from models import RSVPCreate, RSVPResponse
from database import get_database
from services.rsvp_service import RSVPService

router = APIRouter(
    prefix="/rsvps",
    tags=["RSVPs"]
)

# ==================== CREATE RSVP ====================

@router.post(
    "",
    response_model=RSVPResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new RSVP"
)
async def create_rsvp(rsvp: RSVPCreate):
    """
    Controller for creating a new RSVP.
    Delegates business logic to RSVPService.
    """
    service = RSVPService(get_database())
    return await service.create_rsvp(rsvp)


# ==================== GET ALL RSVPs ====================

@router.get(
    "",
    response_model=List[RSVPResponse],
    summary="Get all RSVPs"
)
async def get_all_rsvps(
    user_name: Optional[str] = Query(None, description="Filter by user name"),
    email: Optional[str] = Query(None, description="Filter by email")
):
    """
    Controller for getting all RSVPs with optional filters.
    Delegates business logic to RSVPService.
    """
    service = RSVPService(get_database())
    return await service.get_all_rsvps(user_name=user_name, email=email)

# ==================== GET RSVPs FOR EVENT ====================

@router.get(
    "/event/{event_id}",
    response_model=List[RSVPResponse],
    summary="Get RSVPs for an event"
)
async def get_event_rsvps(event_id: str):
    """
    Controller for getting RSVPs for a specific event.
    Delegates business logic to RSVPService.
    """
    service = RSVPService(get_database())
    return await service.get_rsvps_for_event(event_id)


# ==================== DELETE RSVP ====================

@router.delete(
    "/{rsvp_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an RSVP"
)
async def delete_rsvp(rsvp_id: str):
    """
    Controller for deleting an RSVP.
    Delegates business logic to RSVPService.
    """
    service = RSVPService(get_database())
    return await service.delete_rsvp(rsvp_id)
from bson import ObjectId
from typing import List, Dict, Optional
from datetime import datetime, timezone
from fastapi import HTTPException, status
from models import RSVPCreate
from logger import logger

class RSVPService:
    """
    Service layer for RSVP operations.
    Contains all business logic and database operations for RSVPs.
    """
    
    def __init__(self, database):
        """
        Initialize with database connection.
        
        Args:
            database: MongoDB database instance
        """
        self.db = database
    
    async def create_rsvp(self, rsvp: RSVPCreate) -> Dict:
        """
        Create a new RSVP.
        """
        logger.info(
            f"👥 Creating RSVP: user='{rsvp.user_name}', "
            f"email='{rsvp.email}', event_id='{rsvp.event_id}'"
        )
        
        # Validate event ID format
        if not ObjectId.is_valid(rsvp.event_id):
            logger.warning(f"⚠️  Invalid event ID format: {rsvp.event_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID format"
            )
        
        try:
            # Check if event exists
            event = await self.db.events.find_one({"_id": ObjectId(rsvp.event_id)})
            if not event:
                logger.warning(f"⚠️  Event not found for RSVP: {rsvp.event_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Event with ID {rsvp.event_id} not found"
                )
            
            # Check for duplicate RSVP
            existing_rsvp = await self.db.rsvps.find_one({
                "email": rsvp.email,
                "event_id": rsvp.event_id
            })
            
            if existing_rsvp:
                logger.warning(
                    f"⚠️  Duplicate RSVP attempt: email='{rsvp.email}', "
                    f"event_id='{rsvp.event_id}'"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You have already RSVP'd to this event"
                )
            
            # Prepare RSVP document
            rsvp_dict = rsvp.model_dump()
            rsvp_dict["created_at"] = datetime.now(timezone.utc)
            
            # Insert into database
            result = await self.db.rsvps.insert_one(rsvp_dict)
            
            # Fetch and return created document
            created_rsvp = await self.db.rsvps.find_one({"_id": result.inserted_id})
            
            logger.info(
                f"✅ RSVP created successfully: ID={created_rsvp['_id']}, "
                f"user='{rsvp.user_name}', event='{event['title']}'"
            )
            
            return created_rsvp
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error creating RSVP: {e}")
            raise
    
    async def get_all_rsvps(self, user_name: Optional[str] = None, email: Optional[str] = None) -> List[Dict]:
        """
        Get all RSVPs with optional filters.
        """
        filters = []
        if user_name:
            filters.append(f"user_name='{user_name}'")
        if email:
            filters.append(f"email='{email}'")
        
        filter_str = " AND ".join(filters) if filters else "no filters"
        logger.debug(f"🔍 Fetching RSVPs with {filter_str}")
        
        # Build query filter
        query = {}
        
        if user_name:
            # Case-insensitive regex search
            query["user_name"] = {"$regex": f"^{user_name}$", "$options": "i"}
        
        if email:
            # Case-insensitive regex search
            query["email"] = {"$regex": f"^{email}$", "$options": "i"}
        
        try:
            # Fetch RSVPs with filters
            rsvps = await self.db.rsvps.find(query).to_list(length=500)
            logger.info(f"✅ Found {len(rsvps)} RSVPs ({filter_str})")
            return rsvps
        
        except Exception as e:
            logger.error(f"❌ Error fetching RSVPs: {e}")
            raise
    
    async def get_rsvps_for_event(self, event_id: str) -> List[Dict]:
        """
        Get all RSVPs for a specific event.
        """
        logger.debug(f"🔍 Fetching RSVPs for event: {event_id}")
        
        # Validate event ID format
        if not ObjectId.is_valid(event_id):
            logger.warning(f"⚠️  Invalid event ID format: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID format"
            )
        
        try:
            # Check if event exists
            event = await self.db.events.find_one({"_id": ObjectId(event_id)})
            if not event:
                logger.warning(f"⚠️  Event not found: {event_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Event with ID {event_id} not found"
                )
            
            # Get all RSVPs for this event
            rsvps = await self.db.rsvps.find({"event_id": event_id}).to_list(length=500)
            
            logger.info(
                f"✅ Found {len(rsvps)} RSVPs for event: "
                f"ID={event_id}, Title='{event['title']}'"
            )
            
            return rsvps
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error fetching RSVPs for event {event_id}: {e}")
            raise
    
    async def delete_rsvp(self, rsvp_id: str) -> Dict:
        """
        Delete an RSVP (cancel attendance).
        """
        logger.warning(f"🗑️  Deleting RSVP: {rsvp_id}")
        
        # Validate ObjectId
        if not ObjectId.is_valid(rsvp_id):
            logger.warning(f"⚠️  Invalid RSVP ID format: {rsvp_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid RSVP ID format"
            )
        
        try:
            # Delete RSVP
            result = await self.db.rsvps.delete_one({"_id": ObjectId(rsvp_id)})
            
            if result.deleted_count == 0:
                logger.warning(f"⚠️  RSVP not found for deletion: {rsvp_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"RSVP with ID {rsvp_id} not found"
                )
            
            logger.info(f"✅ RSVP deleted successfully: ID={rsvp_id}")
            
            return {
                "message": "RSVP deleted successfully",
                "rsvp_id": rsvp_id
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error deleting RSVP {rsvp_id}: {e}")
            raise
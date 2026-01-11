from bson import ObjectId
from typing import List, Optional, Dict
from fastapi import HTTPException, status
from models import EventCreate, EventUpdate
from logger import logger

class EventService:
    """
    Service layer for Event operations.
    Contains all business logic and database operations for events.
    """
    
    def __init__(self, database):
        """
        Initialize with database connection.
        
        Args:
            database: MongoDB database instance
        """
        self.db = database
    
    async def create_event(self, event: EventCreate) -> Dict:
        """
        Create a new event.
        """
        logger.info(f"📅 Creating new event: '{event.title}' in category '{event.category}'")
        
        # Convert to dict for MongoDB
        event_dict = event.model_dump()
        
        try:
            # Insert into database
            result = await self.db.events.insert_one(event_dict)
            
            # Fetch and return created document
            created_event = await self.db.events.find_one({"_id": result.inserted_id})
            
            if not created_event:
                logger.error(f"❌ Failed to create event: '{event.title}'")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create event"
                )
            
            logger.info(f"✅ Event created successfully: ID={created_event['_id']}, Title='{event.title}'")
            return created_event
        
        except Exception as e:
            logger.error(f"❌ Error creating event '{event.title}': {e}")
            raise
    
    async def get_all_events(self, category: Optional[str] = None, title: Optional[str] = None) -> List[Dict]:
        """
        Get all events with optional filters.
        """
        filters = []
        if category:
            filters.append(f"category='{category}'")
        if title:
            filters.append(f"title contains '{title}'")
        
        filter_str = " AND ".join(filters) if filters else "no filters"
        logger.debug(f"🔍 Fetching events with {filter_str}")
        
        # Build query
        query = {}
        
        if category:
            # Case-insensitive exact match for category
            query["category"] = {"$regex": f"^{category}$", "$options": "i"}
        
        if title:
            # Case-insensitive partial match for title (contains)
            query["title"] = {"$regex": title, "$options": "i"}
        
        try:
            # Fetch from database
            events = await self.db.events.find(query).to_list(length=100)
            logger.info(f"✅ Found {len(events)} events ({filter_str})")
            return events
        
        except Exception as e:
            logger.error(f"❌ Error fetching events: {e}")
            raise
    
    async def get_event_by_id(self, event_id: str) -> Dict:
        """
        Get a single event by ID.
        """
        logger.debug(f"🔍 Fetching event by ID: {event_id}")
        
        # Validate ObjectId format
        if not ObjectId.is_valid(event_id):
            logger.warning(f"⚠️  Invalid event ID format: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID format"
            )
        
        try:
            # Find event
            event = await self.db.events.find_one({"_id": ObjectId(event_id)})
            
            if not event:
                logger.warning(f"⚠️  Event not found: {event_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Event with ID {event_id} not found"
                )
            
            logger.info(f"✅ Event found: ID={event_id}, Title='{event['title']}'")
            return event
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error fetching event {event_id}: {e}")
            raise
    
    async def update_event(self, event_id: str, event_update: EventUpdate) -> Dict:
        """
        Update an event.
        """
        logger.info(f"✏️  Updating event: {event_id}")
        
        # Validate ObjectId
        if not ObjectId.is_valid(event_id):
            logger.warning(f"⚠️  Invalid event ID format: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID format"
            )
        
        # Get only provided fields
        update_data = event_update.model_dump(exclude_unset=True)
        
        if not update_data:
            logger.warning(f"⚠️  No fields to update for event: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        logger.debug(f"Update fields: {', '.join(update_data.keys())}")
        
        try:
            # Update in database
            result = await self.db.events.update_one(
                {"_id": ObjectId(event_id)},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                logger.warning(f"⚠️  Event not found for update: {event_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Event with ID {event_id} not found"
                )
            
            # Fetch and return updated document
            updated_event = await self.db.events.find_one({"_id": ObjectId(event_id)})
            logger.info(f"✅ Event updated successfully: ID={event_id}")
            
            return updated_event
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error updating event {event_id}: {e}")
            raise
    
    async def delete_event(self, event_id: str) -> Dict:
        """
        Delete an event and all associated RSVPs.
        """
        logger.warning(f"🗑️  Deleting event: {event_id}")
        
        # Validate ObjectId
        if not ObjectId.is_valid(event_id):
            logger.warning(f"⚠️  Invalid event ID format: {event_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid event ID format"
            )
        
        try:
            # Delete event
            result = await self.db.events.delete_one({"_id": ObjectId(event_id)})
            
            if result.deleted_count == 0:
                logger.warning(f"⚠️  Event not found for deletion: {event_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Event with ID {event_id} not found"
                )
            
            # Cascade delete: Remove all RSVPs for this event
            rsvp_result = await self.db.rsvps.delete_many({"event_id": event_id})
            
            logger.info(
                f"✅ Event deleted successfully: ID={event_id}, "
                f"RSVPs deleted={rsvp_result.deleted_count}"
            )
            
            return {
                "message": "Event deleted successfully",
                "event_id": event_id,
                "rsvps_deleted": rsvp_result.deleted_count
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error deleting event {event_id}: {e}")
            raise
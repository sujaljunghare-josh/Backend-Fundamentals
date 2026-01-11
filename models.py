from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from bson import ObjectId

# Custom type for MongoDB ObjectId
class PyObjectId(ObjectId):
    """
    Custom Pydantic type for MongoDB ObjectId.
    
    Why? MongoDB uses ObjectId for _id fields, but Pydantic doesn't know
    how to validate it by default. This teaches Pydantic to handle ObjectIds.
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        from pydantic_core import core_schema
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

# ==================== EVENT MODELS ====================

class EventBase(BaseModel):
    """
    Base Event model with core fields.
    We'll reuse this in Create and Update operations.
    """
    title: str = Field(..., min_length=1, max_length=200, description="Event title")
    description: str = Field(..., min_length=1, max_length=2000, description="Event description")
    date: datetime = Field(..., description="Event date and time")
    category: str = Field(..., min_length=1, max_length=50, description="Event category (e.g., Tech, Music)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Python FastAPI Workshop",
                "description": "Learn to build REST APIs with FastAPI",
                "date": "2026-02-15T14:00:00",
                "category": "Tech"
            }
        }
    )

class EventCreate(EventBase):
    """
    Model for creating a new event.
    Inherits all fields from EventBase.
    No ID needed - MongoDB generates it.
    """
    pass

class EventUpdate(BaseModel):
    """
    Model for updating an event.
    All fields are optional so you can update just one field.
    
    Why Optional? Partial updates! User can update just the title without
    sending the entire event object.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    date: Optional[datetime] = None
    category: Optional[str] = Field(None, min_length=1, max_length=50)

class EventResponse(EventBase):
    """
    Model for returning event data to the client.
    Includes the MongoDB _id field.
    """
    id: PyObjectId = Field(alias="_id", description="MongoDB ObjectId")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# ==================== RSVP MODELS ====================

class RSVPBase(BaseModel):
    """
    Base RSVP model.
    Links a user to an event.
    """
    user_name: str = Field(..., min_length=1, max_length=100, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    event_id: str = Field(..., description="ID of the event to RSVP to")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_name": "John Doe",
                "email": "john@example.com",
                "event_id": "507f1f77bcf86cd799439011"
            }
        }
    )

class RSVPCreate(RSVPBase):
    """
    Model for creating a new RSVP.
    """
    pass

class RSVPResponse(RSVPBase):
    """
    Model for returning RSVP data.
    Includes ID and timestamp.
    """
    id: PyObjectId = Field(alias="_id", description="MongoDB ObjectId")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="RSVP creation time")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
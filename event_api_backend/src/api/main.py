from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4

app = FastAPI(
    title="Event Management API",
    description="API for managing events (CRUD). Provides endpoints to create, retrieve, update, and delete events. Uses in-memory storage.",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Events",
            "description": "Operations for creating, reading, updating, and deleting events.",
        }
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory events database
event_db = {}

# ----------------- Models -----------------

class EventBase(BaseModel):
    """Base Event schema with common fields."""
    title: str = Field(..., description="Title of the event")
    description: Optional[str] = Field(None, description="Description of the event")
    location: Optional[str] = Field(None, description="Location where event will happen")
    start_time: str = Field(..., description="Event start time in ISO8601 format")
    end_time: str = Field(..., description="Event end time in ISO8601 format")

class EventCreate(EventBase):
    """Schema for creating a new event."""
    pass

class EventUpdate(BaseModel):
    """Schema for updating an event; all fields optional."""
    title: Optional[str] = Field(None, description="Title of the event")
    description: Optional[str] = Field(None, description="Description of the event")
    location: Optional[str] = Field(None, description="Location where event will happen")
    start_time: Optional[str] = Field(None, description="Event start time in ISO8601 format")
    end_time: Optional[str] = Field(None, description="Event end time in ISO8601 format")

class Event(EventBase):
    """Event response schema (includes ID)."""
    id: str = Field(..., description="Unique event identifier")

# ------------- API Endpoints --------------

# PUBLIC_INTERFACE
@app.get("/", summary="Health Check", response_model=dict, tags=["Health"])
def health_check():
    """Health check endpoint.
    Returns a simple message indicating the API is running.
    """
    return {"message": "Healthy"}

# PUBLIC_INTERFACE
@app.post(
    "/events/",
    response_model=Event,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new event",
    tags=["Events"],
    responses={
        201: {"description": "Event created successfully", "model": Event},
        422: {"description": "Validation Error"}
    }
)
def create_event(event: EventCreate):
    """Creates a new event resource.
    
    Args:
        event (EventCreate): Event to create.
    
    Returns:
        Event: Created event with unique ID.
    """
    event_id = str(uuid4())
    event_data = event.dict()
    event_obj = Event(id=event_id, **event_data)
    event_db[event_id] = event_obj
    return event_obj

# PUBLIC_INTERFACE
@app.get(
    "/events/",
    response_model=List[Event],
    summary="List all events",
    tags=["Events"],
    responses={
        200: {"description": "List of all events", "model": List[Event]},
    }
)
def list_events():
    """Retrieves all events."""
    return list(event_db.values())

# PUBLIC_INTERFACE
@app.get(
    "/events/{event_id}",
    response_model=Event,
    summary="Get an event by ID",
    tags=["Events"],
    responses={
        200: {"description": "Event found", "model": Event},
        404: {"description": "Event not found"},
    }
)
def get_event(event_id: str):
    """Retrieves an event by its unique identifier.
    
    Args:
        event_id (str): The ID of the event to retrieve.
    
    Returns:
        Event: Event object if found.
    """
    event = event_db.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

# PUBLIC_INTERFACE
@app.put(
    "/events/{event_id}",
    response_model=Event,
    summary="Update an event by ID",
    tags=["Events"],
    responses={
        200: {"description": "Event updated", "model": Event},
        404: {"description": "Event not found"},
    }
)
def update_event(event_id: str, event_update: EventUpdate):
    """Updates the specified event.

    Args:
        event_id (str): The ID of the event to update.
        event_update (EventUpdate): The fields to update.

    Returns:
        Event: The updated event object.
    """
    event = event_db.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    update_data = event_update.dict(exclude_unset=True)
    updated_event = event.copy(update=update_data)
    event_db[event_id] = updated_event
    return updated_event

# PUBLIC_INTERFACE
@app.delete(
    "/events/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an event by ID",
    tags=["Events"],
    responses={
        204: {"description": "Event deleted"},
        404: {"description": "Event not found"},
    }
)
def delete_event(event_id: str):
    """Deletes a specific event by its ID.

    Args:
        event_id (str): The ID of the event to delete.
    """
    if event_id not in event_db:
        raise HTTPException(status_code=404, detail="Event not found")
    del event_db[event_id]
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProspectBase(BaseModel):
    lead_serial_number: int  # This is now the primary key
    is_dropped: bool
    is_won: bool
    end_date: Optional[datetime] = None
    date: Optional[datetime] = None
    organization_name: str
    contact_person: str
    primary_phone_number: str
    other_phone_number: Optional[str] = None
    email: str
    industry: str
    service_needed: str
    lead_source: str
    city: str
    country: str
    value_of_lead: str
    milestone_level: int
    owner_id: int
    points: int
    website: Optional[str]

class ProspectCreate(ProspectBase):
    pass

class ProspectUpdate(BaseModel):
    # Only include fields that can be updated
    is_won: Optional[bool] = None
    end_date: Optional[datetime] = None
    points: Optional[int] = None

class ProspectOut(ProspectBase):
    # Remove id and use lead_serial_number as the primary identifier
    class Config:
        orm_mode = True

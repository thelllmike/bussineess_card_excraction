from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    verified: bool
    is_signed_up_by_google: bool
    email_address: str
    created_on: datetime
    account_type: str
    phone_number: str
    authorized_to_company_details: bool
    password: str
    name: str
    is_blocked: bool
    is_agent_suspended: bool
    profile_image: Optional[str] = None
    profile_type: str
    organization_id: int
    user_logged_in: bool

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from .base import Base  # Import Base from your base.py module

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    verified = Column(Boolean, default=False)
    is_signed_up_by_google = Column(Boolean, default=False, name="isSignedUpByGoogle")
    email_address = Column(String, index=True)
    created_on = Column(DateTime)
    account_type = Column(String)
    phone_number = Column(String)
    authorized_to_company_details = Column(Boolean, default=False, name="authorized_to_company_details")
    password = Column(String)
    name = Column(String)
    is_blocked = Column(Boolean, default=False, name="isBlocked")
    is_agent_suspended = Column(Boolean, default=False, name="is_agent_suspended")
    profile_image = Column(String, nullable=True)
    profile_type = Column(String)
    organization_id = Column(Integer)
    user_logged_in = Column(Boolean, default=False, name="user_logged_in")

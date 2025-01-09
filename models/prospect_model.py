from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Prospect(Base):
    __tablename__ = 'prospects'
    
    lead_serial_number = Column(Integer, primary_key=True)
    is_dropped = Column(Boolean)
    is_won = Column(Boolean)
    end_date = Column(DateTime)
    date = Column(DateTime)
    organization_name = Column(String)
    contact_person = Column(String)
    primary_phone_number = Column(String)
    other_phone_number = Column(String)
    email = Column(String)
    industry = Column(String)
    service_needed = Column(String)
    lead_source = Column(String)
    city = Column(String)
    country = Column(String)
    value_of_lead = Column(String)
    milestone_level = Column(Integer)
    owner_id = Column(Integer)
    points = Column(Integer)
    website = Column(String)

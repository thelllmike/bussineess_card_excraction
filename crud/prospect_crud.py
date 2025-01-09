from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.prospect_model import Prospect
from schemas.prospect_schema import ProspectCreate, ProspectUpdate

def get_prospect(db: Session, lead_serial_number: int):
    """
    Retrieve a single prospect by its lead serial number.
    """
    return db.query(Prospect).filter(Prospect.lead_serial_number == lead_serial_number).first()

def get_prospects(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve multiple prospects with optional pagination.
    """
    return db.query(Prospect).offset(skip).limit(limit).all()

def create_prospect(db: Session, prospect: ProspectCreate):
    # Check if a prospect with the given serial number already exists
    existing_prospect = db.query(Prospect).filter(Prospect.lead_serial_number == prospect.lead_serial_number).first()
    if existing_prospect:
        # Raise an HTTPException if the prospect already exists
        raise HTTPException(status_code=400, detail="A prospect with this serial number already exists.")
    
    # If no existing prospect, proceed to create a new one
    new_prospect = Prospect(**prospect.dict())
    db.add(new_prospect)
    db.commit()
    db.refresh(new_prospect)
    return new_prospect


def update_prospect(db: Session, lead_serial_number: int, updates: ProspectUpdate):
    """
    Update a prospect's details based on the lead serial number.
    """
    db_prospect = db.query(Prospect).filter(Prospect.lead_serial_number == lead_serial_number).first()
    if not db_prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")
    
    for var, value in updates.dict(exclude_unset=True).items():
        setattr(db_prospect, var, value) if value is not None else None
    db.commit()
    db.refresh(db_prospect)
    return db_prospect

def delete_prospect(db: Session, lead_serial_number: int):
    """
    Delete a prospect using its lead serial number.
    """
    db_prospect = db.query(Prospect).filter(Prospect.lead_serial_number == lead_serial_number).first()
    if not db_prospect:
        raise HTTPException(status_code=404, detail="Prospect not found")
    
    db.delete(db_prospect)
    db.commit()
    return True
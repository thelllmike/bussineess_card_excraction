from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from crud.prospect_crud import get_prospect, create_prospect, update_prospect, delete_prospect
from schemas.prospect_schema import ProspectCreate, ProspectOut, ProspectUpdate
from dependencies import get_db

router = APIRouter()

@router.post("/prospects/", response_model=ProspectOut)
def create_prospect_endpoint(prospect: ProspectCreate, db: Session = Depends(get_db)):
    return create_prospect(db=db, prospect=prospect)

@router.get("/prospects/{lead_serial_number}", response_model=ProspectOut)
def read_prospect(lead_serial_number: int, db: Session = Depends(get_db)):
    db_prospect = get_prospect(db, lead_serial_number=lead_serial_number)
    if db_prospect is None:
        raise HTTPException(status_code=404, detail="Prospect not found")
    return db_prospect

@router.put("/prospects/{lead_serial_number}", response_model=ProspectOut)
def update_prospect_endpoint(lead_serial_number: int, prospect: ProspectUpdate, db: Session = Depends(get_db)):
    return update_prospect(db=db, lead_serial_number=lead_serial_number, updates=prospect)

@router.delete("/prospects/{lead_serial_number}", status_code=204)
def delete_prospect_endpoint(lead_serial_number: int, db: Session = Depends(get_db)):
    if not delete_prospect(db, lead_serial_number):
        raise HTTPException(status_code=404, detail="Prospect not found")
    return {"ok": True}

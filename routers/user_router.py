from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.user_schema import UserCreate
from crud.user_crud import create_user
from database import SessionLocal

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/users/", response_model=UserCreate)
async def create_user_route(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = create_user(db=db, user_data=user)
        return db_user
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))

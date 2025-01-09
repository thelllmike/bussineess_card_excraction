from sqlalchemy.orm import Session
from models.user_model import User  # Assuming you have this model
from schemas.user_schema import UserCreate

def get_user_by_email(db: Session, email_address: str):
    return db.query(User).filter(User.email_address == email_address).first()

def create_user(db: Session, user_data: UserCreate):
    existing_user = get_user_by_email(db, user_data.email_address)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email address already in use")
    new_user = User(**user_data.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
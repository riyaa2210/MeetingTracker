from sqlalchemy.orm import Session
import models, schemas
from auth import hash_password


# ---------- USER ----------

def create_user(db: Session, user: schemas.UserCreate):
    hashed = hash_password(user.password)

    db_user = models.User(
        email=user.email,
        hashed_password=hashed
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(
        models.User.email == email
    ).first()


# ---------- MEETING ----------

def create_meeting(db: Session, meeting: schemas.MeetingCreate, user_id: int):
    db_meeting = models.Meeting(
        **meeting.dict(),
        owner_id=user_id
    )
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting


def get_meeting(db: Session, meeting_id: int):
    return db.query(models.Meeting).filter(
        models.Meeting.id == meeting_id
    ).first()


def get_user_meetings(db: Session, user_id: int):
    return db.query(models.Meeting).filter(
        models.Meeting.owner_id == user_id
    ).all()


# ---------- ACTION ----------

def create_action(db: Session, meeting_id: int, action: schemas.ActionCreate):
    db_action = models.ActionItem(
        **action.dict(),
        meeting_id=meeting_id
    )
    db.add(db_action)
    db.commit()
    db.refresh(db_action)
    return db_action

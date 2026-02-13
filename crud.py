from sqlalchemy.orm import Session
import models, schemas
from auth import hash_password


# -------------------------
# USER OPERATIONS
# -------------------------

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


# -------------------------
# MEETING OPERATIONS
# -------------------------

def create_meeting(db: Session, meeting: schemas.MeetingCreate, user_id: int):
    db_meeting = models.Meeting(
        **meeting.dict(),
        owner_id=user_id
    )
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting


def get_meetings(db: Session):
    return db.query(models.Meeting).all()


def get_meeting(db: Session, meeting_id: int):
    return db.query(models.Meeting).filter(
        models.Meeting.id == meeting_id
    ).first()


def update_meeting(db: Session, meeting_id: int, meeting: schemas.MeetingUpdate):
    db_meeting = db.query(models.Meeting).filter(
        models.Meeting.id == meeting_id
    ).first()

    if not db_meeting:
        return None

    update_data = meeting.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_meeting, key, value)

    db.commit()
    db.refresh(db_meeting)
    return db_meeting


def delete_meeting(db: Session, meeting_id: int):
    db_meeting = db.query(models.Meeting).filter(
        models.Meeting.id == meeting_id
    ).first()

    if not db_meeting:
        return False

    db.delete(db_meeting)
    db.commit()
    return True


# -------------------------
# ACTION ITEM OPERATIONS
# -------------------------

def create_action(db: Session, meeting_id: int, action: schemas.ActionCreate):
    db_action = models.ActionItem(
        **action.dict(),
        meeting_id=meeting_id
    )
    db.add(db_action)
    db.commit()
    db.refresh(db_action)
    return db_action


def update_action(db: Session, action_id: int, action: schemas.ActionUpdate):
    db_action = db.query(models.ActionItem).filter(
        models.ActionItem.id == action_id
    ).first()

    if not db_action:
        return None

    update_data = action.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_action, key, value)

    db.commit()
    db.refresh(db_action)
    return db_action


def delete_action(db: Session, action_id: int):
    db_action = db.query(models.ActionItem).filter(
        models.ActionItem.id == action_id
    ).first()

    if not db_action:
        return False

    db.delete(db_action)
    db.commit()
    return True

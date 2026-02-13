from pydantic import BaseModel, EmailStr
from typing import List, Optional

# --- ACTION ITEM SCHEMAS ---
class ActionBase(BaseModel):
    task: str
    assigned_to: str
    status: str = "pending"
    due_date: Optional[str] = None

class ActionCreate(ActionBase):
    pass

class ActionUpdate(BaseModel):
    task: Optional[str] = None
    assigned_to: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None

class Action(ActionBase):
    id: int
    meeting_id: int

    class Config:
        from_attributes = True

# --- MEETING SCHEMAS ---
class MeetingBase(BaseModel):
    title: str
    description: str
    date: str

class MeetingCreate(MeetingBase):
    pass

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None

class Meeting(MeetingBase):
    id: int
    owner_id: int
    actions: List[Action] = []

    class Config:
        from_attributes = True

# --- USER SCHEMAS ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    meetings: List[Meeting] = []

    class Config:
        from_attributes = True

# --- AUTH SCHEMAS ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
from pydantic import BaseModel, EmailStr,Field
from typing import List, Optional


# ---------- ACTION ----------

class ActionBase(BaseModel):
    task: str
    assigned_to: str
    status: str = "pending"
    due_date: Optional[str] = None


class ActionCreate(ActionBase):
    pass


class ActionUpdate(BaseModel):
    status: Optional[str] = None


class Action(ActionBase):
    id: int
    meeting_id: int

    class Config:
        from_attributes = True


# ---------- MEETING ----------

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
    actions: List[Action] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ---------- USER ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


# ---------- TOKEN ----------

class Token(BaseModel):
    access_token: str
    token_type: str

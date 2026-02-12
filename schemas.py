from pydantic import BaseModel
from typing import List, Optional


class ActionBase(BaseModel):
    task: str
    assigned_to: Optional[str] = None
    status: Optional[str] = "pending"
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

    model_config = {
        "from_attributes": True
    }


class MeetingBase(BaseModel):
    title: str
    description: Optional[str] = None
    date: Optional[str] = None


class MeetingCreate(MeetingBase):
    pass


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None

class Meeting(MeetingBase):
    id: int
    actions: List[Action] = []

    model_config = {
        "from_attributes": True
    }

class UserCreate(BaseModel):
    email: str
    password: str


class User(BaseModel):
    id: int
    email: str

    model_config = {
        "from_attributes": True
    }


class Token(BaseModel):
    access_token: str
    token_type: str

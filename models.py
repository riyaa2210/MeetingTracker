from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    meetings = relationship("Meeting", back_populates="owner", cascade="all, delete")

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    date = Column(String, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"),index=True)

    owner = relationship("User", back_populates="meetings")
    actions = relationship("ActionItem", back_populates="meeting", cascade="all, delete")


class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    task = Column(String, nullable=False)
    assigned_to = Column(String, nullable=False)
    status = Column(String, default="pending")
    due_date = Column(String, nullable=True)

    meeting_id = Column(Integer, ForeignKey("meetings.id"),index=True)

    meeting = relationship("Meeting", back_populates="actions")

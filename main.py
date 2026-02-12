from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, SessionLocal
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from auth import create_access_token, verify_password, SECRET_KEY, ALGORITHM
from weasyprint import HTML
from fastapi.responses import Response

models.Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI(title="Meeting Outcome Tracker 🚀")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_email(db, email)
    if user is None:
        raise credentials_exception

    return user
@app.get("/")
def home():
    return {"message": "Meeting Outcome Tracker Running 🔥"}


# Create Meeting
@app.post("/meetings/", response_model=schemas.Meeting)
def create_meeting(meeting: schemas.MeetingCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_meeting(db, meeting, user_id=current_user.id)


# Get All Meetings
@app.get("/meetings/", response_model=list[schemas.Meeting])
def get_meetings(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Meeting).filter(models.Meeting.owner_id == current_user.id).all()


# Get Single Meeting
@app.get("/meetings/{meeting_id}", response_model=schemas.Meeting)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = crud.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


# Add Action Item
@app.post("/meetings/{meeting_id}/actions/", response_model=schemas.Action)
def add_action(meeting_id: int, action: schemas.ActionCreate, db: Session = Depends(get_db)):
    return crud.create_action(db, meeting_id, action)

@app.put("/meetings/{meeting_id}", response_model=schemas.Meeting)
def update_meeting(meeting_id: int, meeting: schemas.MeetingUpdate, db: Session = Depends(get_db)):
    updated = crud.update_meeting(db, meeting_id, meeting)
    if not updated:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return updated

@app.delete("/meetings/{meeting_id}")
def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_meeting(db, meeting_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return {"message": "Meeting deleted successfully"}
@app.put("/actions/{action_id}", response_model=schemas.Action)
def update_action(action_id: int, action: schemas.ActionUpdate, db: Session = Depends(get_db)):
    updated = crud.update_action(db, action_id, action)
    if not updated:
        raise HTTPException(status_code=404, detail="Action not found")
    return updated

@app.delete("/actions/{action_id}")
def delete_action(action_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_action(db, action_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Action not found")
    return {"message": "Action deleted successfully"}

@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/meetings/{meeting_id}/export-pdf")
def export_pdf(meeting_id: int, db: Session = Depends(get_db)):
    meeting = crud.get_meeting(db, meeting_id)
    # Render HTML template with meeting data
    html_out = render_template("minutes.html", meeting=meeting) 
    pdf = HTML(string=html_out).write_pdf()
    return Response(content=pdf, media_type="application/pdf")
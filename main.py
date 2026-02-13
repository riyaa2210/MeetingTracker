from fastapi import FastAPI, Depends, HTTPException, Response
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, SessionLocal
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from auth import create_access_token, verify_password, SECRET_KEY, ALGORITHM
from ai_services import analyze_meeting_sentiment
from exports_services import create_pdf # Fixed import

models.Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI(title="Meeting Outcome Tracker 🚀")

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

# --- MEETING ENDPOINTS ---

@app.post("/meetings/", response_model=schemas.Meeting)
def create_meeting(meeting: schemas.MeetingCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.create_meeting(db, meeting, user_id=current_user.id)

@app.get("/meetings/", response_model=list[schemas.Meeting])
def get_meetings(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Meeting).filter(models.Meeting.owner_id == current_user.id).all()

@app.get("/meetings/{meeting_id}", response_model=schemas.Meeting)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = crud.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

# --- EXPORT & AI ENDPOINTS ---

@app.get("/meetings/{meeting_id}/health")
def get_meeting_health(meeting_id: int, db: Session = Depends(get_db)):
    meeting = crud.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    analysis = analyze_meeting_sentiment(meeting.description)
    return {"analysis": analysis}

@app.get("/meetings/{meeting_id}/export")
def export_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = crud.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Corrected function call to match exports_services.py
    pdf_content = create_pdf(meeting, meeting.actions)
    return Response(
        content=pdf_content, 
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=meeting_{meeting_id}.pdf"}
    )

# --- AUTH ENDPOINTS ---

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
from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from fastapi.middleware.cors import CORSMiddleware
import os
import models, schemas, crud
from database import engine, get_db
from auth import create_access_token, verify_password, SECRET_KEY, ALGORITHM
from ai_services import analyze_meeting_sentiment
from exports_services import create_pdf

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Meeting Outcome Tracker 🚀")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (development only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
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
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path, media_type="text/html")
    return {"message": "Meeting Outcome Tracker Running 🔥"}


@app.get("/dashboard.html")
def dashboard():
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "dashboard.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path, media_type="text/html")
    return {"message": "Dashboard not found"}


@app.get("/meeting.html")
def meeting():
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "meeting.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path, media_type="text/html")
    return {"message": "Meeting page not found"}


@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    return crud.create_user(db, user)

@app.post("/meetings/{meeting_id}/actions", response_model=schemas.Action)
def add_action(
    meeting_id: int,
    action: schemas.ActionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    meeting = crud.get_meeting(db, meeting_id)

    if not meeting or meeting.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return crud.create_action(db, meeting_id, action)


@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/meetings/", response_model=schemas.Meeting)
def create_meeting(
    meeting: schemas.MeetingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_meeting(db, meeting, current_user.id)


@app.get("/meetings/", response_model=list[schemas.Meeting])
def get_meetings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_user_meetings(db, current_user.id)


@app.get("/meetings/{meeting_id}", response_model=schemas.Meeting)
def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    meeting = crud.get_meeting(db, meeting_id)

    if not meeting or meeting.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return meeting


@app.get("/meetings/{meeting_id}/health")
def get_meeting_health(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    meeting = crud.get_meeting(db, meeting_id)

    if not meeting or meeting.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return analyze_meeting_sentiment(meeting.description)


@app.get("/meetings/{meeting_id}/export")
def export_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    meeting = crud.get_meeting(db, meeting_id)

    if not meeting or meeting.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Meeting not found")

    pdf_content = create_pdf(meeting, meeting.actions)

    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=meeting_{meeting_id}.pdf"}
    )


# Catch-all route for SPA navigation - serves index.html for unmapped routes
@app.get("/{full_path:path}")
def catch_all(full_path: str):
    # Don't catch API routes or static files
    if full_path.startswith("api/") or full_path.startswith("static/"):
        raise HTTPException(status_code=404, detail="Not found")
    
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path, media_type="text/html")
    return {"message": "Page not found"}

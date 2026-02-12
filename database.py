import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# 1. Load the .env file
load_dotenv()

# 2. Get the URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL")

# 3. Check if it exists (Good for debugging!)
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")

# 4. Create the engine
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("⚠️ Database URL environment variable is not set.")

def create_db_if_not_exists(url: str):
    db_url = make_url(url)
    temp_engine = create_engine(db_url.set(database='mysql'))

    try:
        with temp_engine.connect() as conn:
            conn.execute(text("COMMIT")) 
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_url.database}"))
            print(f"✅ Database Jawara siap digunakan/sudah dibuat.")
    except Exception as e:
        print(f"⚠️ Gagal cek database (mungkin sudah ada atau akses ditolak): {e}")
    finally:
        temp_engine.dispose()

create_db_if_not_exists(DATABASE_URL)

# Set up the database engine and session
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
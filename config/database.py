from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os

# Load environment variables from .env file
load_dotenv()

# Detect environment
IS_TESTING = os.getenv("TESTING", "false").lower() == "true"
IS_CI = os.getenv("CI", "false").lower() == "true"

# Database configuration
if IS_TESTING or IS_CI:
    # Use SQLite for testing/CI
    DATABASE_URL = "sqlite:///:memory:"
    print("🧪 Testing mode: Using SQLite in-memory database")
else:
    # Use MySQL for local development
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root@localhost:3306/pbl_marketplace")
    print(f"✅ Development mode: Using {DATABASE_URL}")

def create_db_if_not_exists(url: str):
    """Create database if needed (skip for SQLite)"""
    # SQLite doesn't need explicit database creation
    if "sqlite" in url.lower():
        return
    
    try:
        from sqlalchemy.engine.url import make_url
        db_url = make_url(url)
        temp_engine = create_engine(db_url.set(database='mysql'))

        try:
            with temp_engine.connect() as conn:
                conn.execute(text("COMMIT")) 
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_url.database}"))
                print(f"✅ MySQL database '{db_url.database}' siap digunakan.")
        except Exception as e:
            print(f"⚠️ Gagal cek database: {e}")
        finally:
            temp_engine.dispose()
    except Exception as e:
        print(f"ℹ️ Skipping database creation: {e}")

# Create DB if needed (skip for SQLite)
if "sqlite" not in DATABASE_URL.lower():
    create_db_if_not_exists(DATABASE_URL)

# Set up the database engine and session
# For SQLite, use check_same_thread=False for testing
if "sqlite" in DATABASE_URL.lower():
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
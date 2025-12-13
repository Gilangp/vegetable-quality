"""
Pytest configuration and fixtures
"""
import pytest
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from config.database import Base

# Load .env.test for testing environment
# This ensures tests use SQLite in-memory instead of live MySQL
test_env_file = os.path.join(os.path.dirname(__file__), "..", ".env.test")
if os.path.exists(test_env_file):
    load_dotenv(test_env_file, override=True)
else:
    load_dotenv()

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")


@pytest.fixture(scope="session")
def db_engine():
    """Create database engine"""
    engine = create_engine(DATABASE_URL, echo=False)
    # Create all tables
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def db(db_engine) -> Generator[Session, None, None]:
    """Create a new database session for each test"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_rt_user(db: Session):
    """Create a test RT user"""
    from app.models.user import User
    from app.services.auth_service import AuthService
    
    auth_service = AuthService()
    hashed_password = auth_service.hash_password("rtpassword")
    
    user = User(
        name="RT Test User",
        username="rt",
        email="rt@test.com",
        password=hashed_password,
        phone="0812345678",
        role="rt"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin_user(db: Session):
    """Create a test admin user"""
    from app.models.user import User
    from app.services.auth_service import AuthService
    
    auth_service = AuthService()
    hashed_password = auth_service.hash_password("adminpassword")
    
    user = User(
        name="Admin Test User",
        username="admin",
        email="admin@test.com",
        password=hashed_password,
        phone="0812345679",
        role="admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

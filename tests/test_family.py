import os

# Ensure tests run in testing mode (use in-memory DB when possible)
os.environ["TESTING"] = "true"

from pytest import raises
from pydantic_core import ValidationError
from app.schemas.family import FamilyCreate, FamilyUpdate

# --- Integration-style family flow test (moved from test_family_flow.py) ---
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database import Base
from app.models.house import House
from app.models.resident_model import Resident
from app.controllers.family import FamilyController


# Test FamilyCreate Schema Validation

def test_create_family_valid():
    """Test valid family creation"""
    family = FamilyCreate(
        family_number="001",
        head_resident_id=1
    )
    assert family.family_number == "001"
    assert family.head_resident_id == 1


def test_create_family_without_head():
    """Test family creation without head_resident_id"""
    family = FamilyCreate(
        family_number="002",
        head_resident_id=None
    )
    assert family.family_number == "002"
    assert family.head_resident_id is None


def test_create_family_empty_number():
    """Test family creation with empty number"""
    with raises(ValidationError) as excinfo:
        FamilyCreate(
            family_number="",
            head_resident_id=1
        )
    assert "empty" in str(excinfo.value).lower()


def test_create_family_whitespace_number():
    """Test family creation with whitespace only"""
    with raises(ValidationError) as excinfo:
        FamilyCreate(
            family_number="   ",
            head_resident_id=1
        )
    assert "empty" in str(excinfo.value).lower()


def test_create_family_strips_whitespace():
    """Test family number is trimmed"""
    family = FamilyCreate(
        family_number="  003  ",
        head_resident_id=None
    )
    assert family.family_number == "003"


# Test FamilyUpdate Schema Validation

def test_update_family_valid():
    """Test valid family update"""
    update = FamilyUpdate(
        family_number="001-A",
        head_resident_id=2
    )
    assert update.family_number == "001-A"
    assert update.head_resident_id == 2


def test_update_family_partial():
    """Test partial family update"""
    update = FamilyUpdate(
        family_number="004",
        head_resident_id=None
    )
    assert update.family_number == "004"
    assert update.head_resident_id is None


def test_update_family_empty_fields():
    """Test update with empty fields (allowed)"""
    update = FamilyUpdate(
        family_number=None,
        head_resident_id=None
    )
    assert update.family_number is None
    assert update.head_resident_id is None


def test_update_family_empty_number():
    """Test update with empty family number (not allowed)"""
    with raises(ValidationError) as excinfo:
        FamilyUpdate(
            family_number="",
            head_resident_id=1
        )
    assert "empty" in str(excinfo.value).lower()


def test_update_family_strips_whitespace():
    """Test update family number is trimmed"""
    update = FamilyUpdate(
        family_number="  005  ",
        head_resident_id=None
    )
    assert update.family_number == "005"


def setup_module(module):
    # create a local in-memory SQLite engine and session factory for tests
    global engine, SessionLocal
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # create tables in this in-memory DB using project models' metadata
    Base.metadata.create_all(bind=engine)


def teardown_module(module):
    # attempt to drop tables; ignore circular-drop warnings/errors in some dialects
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception:
        pass


def test_add_and_remove_member_flow():
    db = SessionLocal()
    try:
        # create a house (required by Resident.house_id foreign key)
        house = House(house_number="H1")
        db.add(house)
        db.commit()
        db.refresh(house)

        controller = FamilyController(db)

        # create two families
        family1 = controller.create_family(FamilyCreate(family_number="F001"))
        family2 = controller.create_family(FamilyCreate(family_number="F002"))
        assert family1.id is not None and family2.id is not None

        # create resident in family2 (family_id is non-nullable)
        resident = Resident(nik="NIK1", name="Resident One", family_id=family2.id, house_id=house.id)
        db.add(resident)
        db.commit()
        db.refresh(resident)

        # move resident to family1 using add_resident_to_family
        updated = controller.add_resident_to_family(family1.id, resident.id)
        assert updated.family_id == family1.id

        # cannot remove if resident is head of family (should raise)
        family1.head_resident_id = resident.id
        db.commit()
        with pytest.raises(HTTPException):
            controller.remove_resident_from_family(family1.id, resident.id)

        # unset head; removal should unassign resident from the family
        family1.head_resident_id = None
        db.commit()
        resp = controller.remove_resident_from_family(family1.id, resident.id)
        assert isinstance(resp, dict)
        # verify resident is unassigned
        r2 = db.query(Resident).filter(Resident.id == resident.id).first()
        assert r2.family_id is None

    finally:
        db.close()

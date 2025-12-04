import os

# Ensure tests run in testing mode (use in-memory DB when possible)
os.environ["TESTING"] = "true"

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database import Base
from app.controllers.house import HouseController
from app.schemas.house import HouseCreate, HouseUpdate
from app.models.house import House
from app.models.family import Family
from app.models.resident_model import Resident


def test_house_create_schema_validation():
    h = HouseCreate(house_number="A-101", address="Jl. Mawar", rt="001", rw="002")
    assert h.house_number == "A-101"
    assert h.address == "Jl. Mawar"


def setup_module(module):
    global engine, SessionLocal
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module(module):
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception:
        pass


def test_house_controller_crud_flow():
    db = SessionLocal()
    try:
        controller = HouseController(db)

        # Create house
        created = controller.create_house(HouseCreate(house_number="H1", address="Addr1", rt="001", rw="002"))
        assert created.id is not None

        # Get house
        got = controller.get_house(created.id)
        assert got.id == created.id
        assert got.house_number == "H1"

        # Update house
        updated = controller.update_house(created.id, HouseUpdate(house_number="H1A"))
        assert updated.house_number == "H1A"

        # List houses
        houses = controller.list_houses()
        assert any(h.id == created.id for h in houses)

        # Create family and resident to test delete prevention
        fam = Family(family_number="F1")
        db.add(fam)
        db.commit()
        db.refresh(fam)

        resident = Resident(nik="NIKX", name="Res X", family_id=fam.id, house_id=created.id)
        db.add(resident)
        db.commit()
        db.refresh(resident)

        # Attempt to delete house with resident should raise
        with pytest.raises(HTTPException):
            controller.delete_house(created.id)

        # Remove resident then delete
        db.delete(resident)
        db.commit()

        resp = controller.delete_house(created.id)
        assert resp.get("message") is not None

    finally:
        db.close()

import os

# Ensure tests run in testing mode (use in-memory DB when possible)
os.environ["TESTING"] = "true"

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database import Base
from app.models.house import House
from app.models.resident_model import Resident
from app.controllers.family import FamilyController
from app.schemas.family import FamilyCreate


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


def test_transfer_resident_between_families():
    db = SessionLocal()
    try:
        # create required house
        house = House(house_number="H-T1")
        db.add(house)
        db.commit()
        db.refresh(house)

        controller = FamilyController(db)

        # create two families
        f1 = controller.create_family(FamilyCreate(family_number="TF001"))
        f2 = controller.create_family(FamilyCreate(family_number="TF002"))

        # add a resident in family1
        r = Resident(nik="TR001", name="Transfer Resident", family_id=f1.id, house_id=house.id)
        db.add(r)
        db.commit()
        db.refresh(r)

        # transfer resident to family2
        updated = controller.add_resident_to_family(f2.id, r.id)
        assert updated.family_id == f2.id

    finally:
        db.close()


def test_adding_resident_to_same_family_raises():
    db = SessionLocal()
    try:
        house = House(house_number="H-T2")
        db.add(house)
        db.commit()
        db.refresh(house)

        controller = FamilyController(db)
        f = controller.create_family(FamilyCreate(family_number="TF003"))

        r = Resident(nik="TR002", name="Same Family Resident", family_id=f.id, house_id=house.id)
        db.add(r)
        db.commit()
        db.refresh(r)

        with pytest.raises(HTTPException) as excinfo:
            controller.add_resident_to_family(f.id, r.id)

        assert "sudah terdaftar di keluarga ini" in str(excinfo.value.detail).lower()

    finally:
        db.close()


def test_remove_head_resident_is_rejected():
    db = SessionLocal()
    try:
        house = House(house_number="H-T3")
        db.add(house)
        db.commit()
        db.refresh(house)

        controller = FamilyController(db)
        f = controller.create_family(FamilyCreate(family_number="TF004"))

        r = Resident(nik="TR003", name="Head Resident", family_id=f.id, house_id=house.id)
        db.add(r)
        db.commit()
        db.refresh(r)

        # set as head
        f.head_resident_id = r.id
        db.commit()

        with pytest.raises(HTTPException) as excinfo:
            controller.remove_resident_from_family(f.id, r.id)

        assert "tidak dapat menghapus kepala keluarga" in str(excinfo.value.detail).lower()

    finally:
        db.close()

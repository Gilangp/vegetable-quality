import pytest
from app.controllers.house import HouseController
from app.models.house import House as HouseModel
from app.models.resident_model import Resident as ResidentModel
from app.models.family import Family as FamilyModel
from fastapi import HTTPException
import uuid


def create_house(db, status='available'):
    h = HouseModel(house_number='T1', address='Addr', rt='001', rw='002', status=status)
    db.add(h)
    db.commit()
    db.refresh(h)
    return h


def create_family(db):
    f = FamilyModel(family_number=f'FAM{str(uuid.uuid4())[:8]}')
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


def create_resident(db, house_id, family_id=None, name='Res'):
    r = ResidentModel(house_id=house_id, family_id=family_id, name=name)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def test_assign_to_available_house_sets_occupied_and_assigns_resident(db):
    controller = HouseController(db)

    prev_house = create_house(db, status='available')
    target_house = create_house(db, status='available')

    # create resident assigned to prev_house
    resident = create_resident(db, house_id=prev_house.id, family_id=None)

    # assign to target
    res = controller.assign_resident_to_house(target_house.id, resident.id)

    assert res.house_id == target_house.id

    # refresh houses
    db.refresh(target_house)
    db.refresh(prev_house)
    assert target_house.status == 'occupied'
    assert prev_house.status == 'available'


def test_assign_to_occupied_by_same_family_succeeds(db):
    controller = HouseController(db)

    fam = create_family(db)
    other_house = create_house(db, status='available')
    occupied_house = create_house(db, status='occupied')

    # occupant from same family
    occupant = create_resident(db, house_id=occupied_house.id, family_id=fam.id)
    resident = create_resident(db, house_id=other_house.id, family_id=fam.id)

    res = controller.assign_resident_to_house(occupied_house.id, resident.id)

    assert res.house_id == occupied_house.id


def test_assign_to_occupied_by_different_family_fails(db):
    controller = HouseController(db)

    fam1 = create_family(db)
    fam2 = create_family(db)
    other_house = create_house(db, status='available')
    occupied_house = create_house(db, status='occupied')

    occupant = create_resident(db, house_id=occupied_house.id, family_id=fam1.id)
    resident = create_resident(db, house_id=other_house.id, family_id=fam2.id)

    with pytest.raises(HTTPException) as exc:
        controller.assign_resident_to_house(occupied_house.id, resident.id)

    assert exc.value.status_code == 403

from pytest import raises
from pydantic_core import ValidationError
from app.schemas.family import FamilyCreate, FamilyUpdate


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

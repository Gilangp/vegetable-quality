from datetime import date, timedelta
from pytest import raises
from app.schemas.auth import RegisterRequest
from pydantic_core import ValidationError


# Test RegisterRequest Schema Validation

def test_register_schema_valid():
    """Test valid RegisterRequest schema"""
    request = RegisterRequest(
        nik="1234567890123456",
        family_number="1234567890123456",
        name="John Doe",
        username="johndoe",
        email="john@example.com",
        password="securepassword123",
        password_confirm="securepassword123",
        birth_date=date(2000, 1, 1),
        birth_place="Jakarta",
        gender="Laki-laki",
        phone="081234567890",
    )
    assert request.nik == "1234567890123456"
    assert request.family_number == "1234567890123456"
    assert request.name == "John Doe"


def test_register_schema_invalid_nik_length():
    """Test RegisterRequest with invalid NIK length"""
    with raises(ValidationError) as excinfo:
        RegisterRequest(
            nik="123",
            family_number="1234567890123456",
            name="Test User",
            username="testuser",
            email="test@example.com",
            password="password123",
            password_confirm="password123",
            birth_date=date(2000, 1, 1),
            birth_place="Jakarta",
            gender="Laki-laki",
            phone="081234567890",
        )
    assert "16" in str(excinfo.value) or "digit" in str(excinfo.value).lower()


def test_register_schema_invalid_nik_non_digit():
    """Test RegisterRequest with non-digit NIK"""
    with raises(ValidationError) as excinfo:
        RegisterRequest(
            nik="123456789012345a",
            name="Test User",
            username="testuser",
            email="test@example.com",
            password="password123",
            password_confirm="password123",
            birth_date=date(2000, 1, 1),
            birth_place="Jakarta",
            gender="Laki-laki",
            phone="081234567890",
        )
    assert "digit" in str(excinfo.value).lower() or "angka" in str(excinfo.value).lower()


def test_register_schema_invalid_gender():
    """Test RegisterRequest with invalid gender"""
    with raises(ValidationError) as excinfo:
        RegisterRequest(
            nik="1234567890123456",
            name="Test User",
            username="testuser",
            email="test@example.com",
            password="password123",
            password_confirm="password123",
            birth_date=date(2000, 1, 1),
            birth_place="Jakarta",
            gender="Invalid",
            phone="081234567890",
        )
    assert "Laki-laki" in str(excinfo.value) or "Perempuan" in str(excinfo.value)


def test_register_schema_future_birth_date():
    """Test RegisterRequest with future birth date"""
    future_date = date.today() + timedelta(days=365)
    with raises(ValidationError) as excinfo:
        RegisterRequest(
            nik="1234567890123456",
            name="Test User",
            username="testuser",
            email="test@example.com",
            password="password123",
            password_confirm="password123",
            birth_date=future_date,
            birth_place="Jakarta",
            gender="Laki-laki",
            phone="081234567890",
        )
    assert "future" in str(excinfo.value).lower() or "masa depan" in str(excinfo.value).lower()


def test_register_schema_password_mismatch():
    """Test RegisterRequest with mismatched passwords"""
    with raises(ValidationError) as excinfo:
        RegisterRequest(
            nik="1234567890123456",
            name="Test User",
            username="testuser",
            email="test@example.com",
            password="password123",
            password_confirm="differentpassword",
            birth_date=date(2000, 1, 1),
            birth_place="Jakarta",
            gender="Laki-laki",
            phone="081234567890",
        )
    assert "do not match" in str(excinfo.value).lower() or "not match" in str(excinfo.value).lower()


def test_register_schema_short_password():
    """Test RegisterRequest with password too short"""
    with raises(ValidationError) as excinfo:
        RegisterRequest(
            nik="1234567890123456",
            name="Test User",
            username="testuser",
            email="test@example.com",
            password="pass",
            password_confirm="pass",
            birth_date=date(2000, 1, 1),
            birth_place="Jakarta",
            gender="Laki-laki",
            phone="081234567890",
        )
    assert "6" in str(excinfo.value) or "at least" in str(excinfo.value).lower()


def test_register_schema_short_username():
    """Test RegisterRequest with username too short"""
    with raises(ValidationError) as excinfo:
        RegisterRequest(
            nik="1234567890123456",
            name="Test User",
            username="ab",
            email="test@example.com",
            password="password123",
            password_confirm="password123",
            birth_date=date(2000, 1, 1),
            birth_place="Jakarta",
            gender="Laki-laki",
            phone="081234567890",
        )
    assert "3" in str(excinfo.value) or "at least" in str(excinfo.value).lower()


def test_register_schema_invalid_username_chars():
    """Test RegisterRequest with invalid username characters"""
    with raises(ValidationError) as excinfo:
        RegisterRequest(
            nik="1234567890123456",
            name="Test User",
            username="test@user!",
            email="test@example.com",
            password="password123",
            password_confirm="password123",
            birth_date=date(2000, 1, 1),
            birth_place="Jakarta",
            gender="Laki-laki",
            phone="081234567890",
        )
    assert "letter" in str(excinfo.value).lower() or "number" in str(excinfo.value).lower()


def test_register_schema_invalid_gender():
    """Test RegisterRequest schema validation for invalid gender"""
    with raises(ValidationError) as excinfo:
        RegisterRequest(
            nik="1234567890123456",
            name="Test User",
            username="testuser",
            email="test@example.com",
            password="password123",
            password_confirm="password123",
            birth_date=date(2000, 1, 1),
            birth_place="Jakarta",
            gender="Invalid",
            phone="081234567890",
        )

    assert "Laki-laki" in str(excinfo.value) or "Perempuan" in str(excinfo.value)

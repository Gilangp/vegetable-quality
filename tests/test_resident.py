from app.schemas.residents import ResidentBase
from datetime import date, timedelta
from pydantic import ValidationError
from pytest import raises

# --- TEST KASUS POSITIF (BERHASIL) ---

def test_create_resident_valid():
    resident = ResidentBase(
        name="John Doe",
        birth_date=date(1990, 1, 1),
        birth_place="New York",
        gender="Laki-laki",
        nik="1234567890123456",
        phone="08123456789",
        status="Single",
    )

    assert resident.name == "John Doe"
    assert resident.nik == "1234567890123456"

# --- TEST KASUS NEGATIF (HARUS ERROR) ---

def test_fail_invalid_nik_length():
    with raises(ValidationError) as excinfo:
        ResidentBase(
            name="Jane Doe",
            birth_date=date(1992, 2, 2),
            birth_place="Los Angeles",
            gender="Perempuan",
            nik="123", # Salah (terlalu pendek)
            phone="555-5678",
            status="Married",
        )
    # Memastikan pesan error mengandung kata "16 digit"
    assert "16 digit" in str(excinfo.value)

def test_fail_create_resident_with_future_birth_date():
    future_date = date.today() + timedelta(days=365)
    
    with raises(ValidationError) as excinfo:
        ResidentBase(
            name="Alice Smith",
            birth_date=future_date, 
            birth_place="Chicago",
            gender="Perempuan",
            nik="6543210987654321",
            phone="555-9876",
            status="Single",
        )

    assert "masa depan" in str(excinfo.value)

def test_fail_create_resident_with_empty_name():
    with raises(ValidationError) as excinfo:
        ResidentBase(
            name="",
            birth_date=date(1985, 5, 5),
            birth_place="Houston",
            gender="Laki-laki",
            nik="1122334455667788",
            phone="555-4321",
            status="Married",
        )

    assert "Nama tidak boleh kosong" in str(excinfo.value)

def test_fail_create_resident_with_invalid_gender():
    with raises(ValidationError) as excinfo:
        ResidentBase(
            name="Bob Johnson",
            birth_date=date(1975, 3, 3),
            birth_place="Phoenix",
            gender="Unknown",
            nik="9988776655443322",
            phone="555-8765",
            status="Single",
        )

    assert "Gender harus Laki-laki atau Perempuan" in str(excinfo.value)
from datetime import date
from pytest import raises
from pydantic_core import ValidationError
from app.schemas.resident_approval import ResidentApprovalUpdate


# Test ResidentApprovalUpdate Schema Validation

def test_approve_with_valid_data():
    """Test valid approve request"""
    request = ResidentApprovalUpdate(
        status="approved",
        note="Data valid, assigned to family",
        family_id=5
    )
    assert request.status == "approved"
    assert request.family_id == 5


def test_approve_without_family_id():
    """Test approve without required family_id"""
    with raises(ValidationError) as excinfo:
        ResidentApprovalUpdate(
            status="approved",
            note="Data valid",
            family_id=None
        )
    assert "family_id is required" in str(excinfo.value).lower()


def test_reject_with_note():
    """Test valid reject request"""
    request = ResidentApprovalUpdate(
        status="rejected",
        note="NIK sudah terdaftar",
        family_id=None
    )
    assert request.status == "rejected"
    assert request.note == "NIK sudah terdaftar"


def test_reject_without_note():
    """Test reject without note is okay"""
    request = ResidentApprovalUpdate(
        status="rejected",
        note=None,
        family_id=None
    )
    assert request.status == "rejected"
    assert request.note is None


def test_invalid_status():
    """Test invalid approval status"""
    with raises(ValidationError) as excinfo:
        ResidentApprovalUpdate(
            status="invalid_status",
            note="Test",
            family_id=5
        )
    assert "approved" in str(excinfo.value).lower() or "rejected" in str(excinfo.value).lower()


def test_approve_with_family_id_zero():
    """Test approve with family_id=0 should still fail"""
    with raises(ValidationError) as excinfo:
        ResidentApprovalUpdate(
            status="approved",
            note="Test",
            family_id=0
        )
    # family_id 0 is falsy but should pass validator - actual family check is in controller
    # This test verifies schema only allows required field, not actual family existence


def test_reject_with_family_id_ignored():
    """Test reject ignores family_id"""
    request = ResidentApprovalUpdate(
        status="rejected",
        note="Test",
        family_id=5  # Should be ignored when rejecting
    )
    assert request.status == "rejected"
    assert request.family_id == 5  # Stored but not used

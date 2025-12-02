"""
Integration test untuk registration & approval flow

Test scenario:
1. Warga register dengan family_number baru
   - Family auto-created
   - Resident status = pending
   - Approval status = pending_approval

2. RT approve tanpa family_id
   - Resident status = aktif
   - Jadi head_resident jika family baru
   - Bisa login

3. Warga register dengan family_number yang sudah ada
   - Assign ke family yang ada
   - RT approve
   - Tidak jadi head_resident (sudah ada)
"""

from datetime import date
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.models.user import User
from app.models.resident_model import Resident
from app.models.family import Family
from app.models.resident_approval import ResidentApproval
from app.controllers.auth import AuthController
from app.controllers.resident_approval import ResidentApprovalController
from app.schemas.auth import RegisterRequest


class TestRegistrationFlow:
    """Test registration & approval flow"""
    
    def test_register_with_new_family(self, db: Session):
        """
        Test: Warga register dengan family_number baru
        
        Expected:
        - Family auto-created
        - Resident created dengan status = "pending"
        - Approval created dengan status = "pending_approval"
        - User created dengan role = "warga"
        """
        auth_controller = AuthController(db)
        
        # Prepare data
        register_data = RegisterRequest(
            nik="1234567890123456",
            family_number="1111111111111111",  # New family number
            name="Adi Wijaya",
            gender="Laki-laki",
            birth_place="Jakarta",
            birth_date=date(1995, 5, 15),
            username="adi_wijaya",
            email="adi@example.com",
            phone="08987654321",
            password="password123",
            password_confirm="password123"
        )
        
        # Register
        user = auth_controller.register(register_data)
        
        # Verify user
        assert user.username == "adi_wijaya"
        assert user.role == "warga"
        assert user.resident_id is not None
        
        # Verify resident
        resident = db.query(Resident).filter(Resident.id == user.resident_id).first()
        assert resident is not None
        assert resident.nik == "1234567890123456"
        assert resident.status == "pending"  # Status harus pending, bukan aktif
        assert resident.family_id is not None
        
        # Verify family auto-created
        family = db.query(Family).filter(Family.id == resident.family_id).first()
        assert family is not None
        assert family.family_number == "1111111111111111"
        assert family.head_resident_id is None  # Belum di-assign sebagai head
        
        # Verify approval
        approval = db.query(ResidentApproval).filter(
            ResidentApproval.resident_id == resident.id
        ).first()
        assert approval is not None
        assert approval.status == "pending_approval"
        assert approval.nik == "1234567890123456"
    
    def test_approve_without_family_id(self, db: Session, test_rt_user):
        """
        Test: RT approve tanpa family_id
        
        Expected:
        - Resident status = "aktif"
        - Resident jadi head_resident (keluarga baru)
        - Bisa login
        """
        # Setup: Register dulu
        auth_controller = AuthController(db)
        register_data = RegisterRequest(
            nik="2234567890123456",
            family_number="2222222222222222",
            name="Budi Santoso",
            gender="Laki-laki",
            birth_place="Bandung",
            birth_date=date(1990, 3, 20),
            username="budi_santoso",
            email="budi@example.com",
            phone="08987654321",
            password="password123",
            password_confirm="password123"
        )
        user = auth_controller.register(register_data)
        resident = db.query(Resident).filter(Resident.id == user.resident_id).first()
        approval = db.query(ResidentApproval).filter(
            ResidentApproval.resident_id == resident.id
        ).first()
        
        # Approve tanpa family_id
        approval_controller = ResidentApprovalController(db)
        from app.schemas.resident_approval import ResidentApprovalUpdate
        
        approval_data = ResidentApprovalUpdate(
            status="approved"
            # family_id NOT provided
        )
        
        result = approval_controller.approve_resident(approval.id, approval_data, test_rt_user)
        
        # Verify approval
        assert result.status == "approved"
        assert result.approved_by == test_rt_user.id
        
        # Verify resident
        resident_updated = db.query(Resident).filter(Resident.id == resident.id).first()
        assert resident_updated.status == "aktif"
        
        # Verify family head_resident
        family = db.query(Family).filter(Family.id == resident.family_id).first()
        assert family.head_resident_id == resident.id  # Jadi head_resident
    
    def test_register_with_existing_family(self, db: Session):
        """
        Test: Warga register dengan family_number yang sudah ada
        
        Expected:
        - Assign ke family yang ada
        - Tidak jadi head_resident
        """
        # Setup: Create family dulu
        family = Family(
            family_number="3333333333333333",
            head_resident_id=None
        )
        db.add(family)
        db.flush()
        
        # Create first resident (akan jadi head)
        resident1 = Resident(
            nik="3134567890123456",
            name="Eka Pratama",
            family_id=family.id,
            house_id=1,
            status="aktif",
            gender="Laki-laki",
            birth_date=date(1995, 5, 15),
            birth_place="Jakarta"
        )
        db.add(resident1)
        db.flush()
        
        family.head_resident_id = resident1.id
        db.commit()
        
        # Register warga baru dengan family_number yang sama
        auth_controller = AuthController(db)
        register_data = RegisterRequest(
            nik="3234567890123456",
            family_number="3333333333333333",  # Existing family
            name="Fita Wijaya",
            gender="Perempuan",
            birth_place="Jakarta",
            birth_date=date(1998, 7, 22),
            username="fita_wijaya",
            email="fita@example.com",
            phone="08987654322",
            password="password123",
            password_confirm="password123"
        )
        
        user2 = auth_controller.register(register_data)
        resident2 = db.query(Resident).filter(Resident.id == user2.resident_id).first()
        
        # Verify assign ke family yang sama
        assert resident2.family_id == family.id
        assert resident2.status == "pending"
        
        # Verify head_resident tidak berubah
        family_updated = db.query(Family).filter(Family.id == family.id).first()
        assert family_updated.head_resident_id == resident1.id  # Masih resident1
    
    def test_approve_with_reassign_family(self, db: Session, test_rt_user):
        """
        Test: RT approve + reassign ke family lain
        
        Expected:
        - Resident reassign ke family_id yang diberikan
        - Tidak jadi head_resident (sudah ada head di family lain)
        """
        # Setup: Register warga
        auth_controller = AuthController(db)
        register_data = RegisterRequest(
            nik="4234567890123456",
            family_number="4444444444444444",
            name="Gita Kusuma",
            gender="Perempuan",
            birth_place="Surabaya",
            birth_date=date(1996, 9, 30),
            username="gita_kusuma",
            email="gita@example.com",
            phone="08987654323",
            password="password123",
            password_confirm="password123"
        )
        user = auth_controller.register(register_data)
        resident = db.query(Resident).filter(Resident.id == user.resident_id).first()
        approval = db.query(ResidentApproval).filter(
            ResidentApproval.resident_id == resident.id
        ).first()
        
        # Setup: Create family lain dengan head
        family_target = Family(
            family_number="4555555555555555",
            head_resident_id=None
        )
        db.add(family_target)
        db.flush()
        
        resident_head = Resident(
            nik="4134567890123456",
            name="Hendra Wijaya",
            family_id=family_target.id,
            house_id=1,
            status="aktif",
            gender="Laki-laki",
            birth_date=date(1994, 1, 10),
            birth_place="Surabaya"
        )
        db.add(resident_head)
        db.flush()
        
        family_target.head_resident_id = resident_head.id
        db.commit()
        
        # Approve + reassign ke family_target
        approval_controller = ResidentApprovalController(db)
        
        from app.schemas.resident_approval import ResidentApprovalUpdate
        approval_data = ResidentApprovalUpdate(
            status="approved",
            family_id=family_target.id  # Reassign
        )
        
        result = approval_controller.approve_resident(approval.id, approval_data, test_rt_user)
        
        # Verify
        assert result.status == "approved"
        
        resident_updated = db.query(Resident).filter(Resident.id == resident.id).first()
        assert resident_updated.status == "aktif"
        assert resident_updated.family_id == family_target.id
        
        # Head tidak berubah (masih resident_head)
        family_updated = db.query(Family).filter(Family.id == family_target.id).first()
        assert family_updated.head_resident_id == resident_head.id
    
    def test_register_age_validation(self, db: Session):
        """Test: Warga < 17 tahun tidak bisa register"""
        from fastapi import HTTPException
        
        auth_controller = AuthController(db)
        
        # Register dengan umur < 17
        register_data = RegisterRequest(
            nik="5234567890123456",
            family_number="5555555555555555",
            name="Anak Muda",
            gender="Laki-laki",
            birth_place="Jakarta",
            birth_date=date(2010, 1, 1),  # Umur < 17
            username="anak_muda",
            email="anak@example.com",
            phone="08987654324",
            password="password123",
            password_confirm="password123"
        )
        
        # Should raise exception
        try:
            auth_controller.register(register_data)
            assert False, "Should raise HTTPException for age < 17"
        except HTTPException as e:
            assert "17 tahun" in e.detail or "Anak-anak" in e.detail

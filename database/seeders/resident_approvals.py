from app.models.resident_approval import ResidentApproval
from app.models.resident_model import Resident
from config.database import SessionLocal
from faker import Faker
from typing import List
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

fake = Faker('id_ID')

def resident_approvals():
    db = SessionLocal()
    try:
        if db.query(ResidentApproval).first():
            print("⚠️ Resident approvals table already seeded.")
            return

        # Get existing residents
        existing_residents = db.query(Resident).all()
        if not existing_residents:
            print("Error: Residents table is empty.")
            return

        statuses = ["pending_approval", "approved", "rejected"]
        approvals_data: List[ResidentApproval] = []

        for i in range(15):
            resident = random.choice(existing_residents)
            status = random.choice(statuses)
            approval = ResidentApproval(
                resident_id=resident.id,
                name=resident.name,
                nik=resident.nik,
                gender=resident.gender,
                birth_place=resident.birth_place,
                birth_date=str(resident.birth_date),
                phone=resident.phone,
                address=fake.address(),
                family_number=str(random.randint(1000000000000000, 9999999999999999)),
                status=status,
                created_at=fake.date_time_this_month(),
                updated_at=fake.date_time_this_month()
            )
            approvals_data.append(approval)

        db.add_all(approvals_data)
        db.commit()
        print(f"✅ Successfully seeded {len(approvals_data)} resident approvals.")
    except Exception as e:
        print(f"❌ Error seeding resident approvals table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    resident_approvals()

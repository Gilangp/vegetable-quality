from app.models.resident_approval import ResidentApproval
from app.models.user import User
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

        existing_users = db.query(User).filter(User.role == "ketua_rt").all()
        
        if not existing_users:
            print("❌ Error: No ketua_rt users found.")
            existing_users = db.query(User).all()

        statuses = ["pending_approval", "approved", "rejected"]
        approvals_data: List[ResidentApproval] = []

        for i in range(15):
            status = random.choice(statuses)
            approval = ResidentApproval(
                resident_id=None if status == "pending_approval" else random.randint(1, 5),
                name=fake.name(),
                nik=str(fake.unique.random_number(digits=16, fix_len=True)),
                gender=random.choice(["Laki-laki", "Perempuan"]),
                birth_place=fake.city(),
                birth_date=fake.date_of_birth(minimum_age=17, maximum_age=80),
                phone=fake.phone_number(),
                address=fake.address(),
                status=status,
                note=fake.sentence() if status == "rejected" else None,
                approved_by=random.choice(existing_users).id if status != "pending_approval" else None,
                created_at=fake.date_time_this_month()
            )
            approvals_data.append(approval)

        db.add_all(approvals_data)
        db.commit()
        print(f"✅ Successfully seeded {len(approvals_data)} resident approvals.")
    except Exception as e:
        print(f"❌ Error seeding resident_approvals table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    resident_approvals()

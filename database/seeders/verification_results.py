from app.models.verification_result import VerificationResult
from app.models.resident_model import Resident
from config.database import SessionLocal
from faker import Faker
from typing import List
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

fake = Faker('id_ID')

def verification_results():
    db = SessionLocal()
    try:
        if db.query(VerificationResult).first():
            print("⚠️ Verification results table already seeded.")
            return

        existing_residents = db.query(Resident).all()
        
        if not existing_residents:
            print("❌ Error: Residents table is empty.")
            return

        vegetables = ["Tomat", "Bayam", "Cabai", "Bawang", "Wortel", "Kubis", "Selada", "Terong", "Labu", "Ketimun"]
        results = ["utuh", "tidak_utuh"]
        verifications_data: List[VerificationResult] = []

        for i in range(25):
            result = random.choice(results)
            verification = VerificationResult(
                resident_id=random.choice(existing_residents).id,
                vegetable_name=random.choice(vegetables),
                image=fake.file_name(extension="jpg"),
                result=result,
                is_valid_for_marketplace=True if result == "utuh" else random.choice([True, False]),
                created_at=fake.date_time_this_month()
            )
            verifications_data.append(verification)

        db.add_all(verifications_data)
        db.commit()
        print(f"✅ Successfully seeded {len(verifications_data)} verification results.")
    except Exception as e:
        print(f"❌ Error seeding verification_results table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    verification_results()

from app.models.family_mutation import FamilyMutation
from app.models.family import Family
from config.database import SessionLocal
from faker import Faker
from typing import List
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

fake = Faker('id_ID')

def family_mutations():
    db = SessionLocal()
    try:
        if db.query(FamilyMutation).first():
            print("⚠️ Family mutations table already seeded.")
            return

        existing_families = db.query(Family).all()
        
        if not existing_families:
            print("❌ Error: Families table is empty.")
            return

        mutation_types = ["pindah_masuk", "pindah_keluar"]
        mutations_data: List[FamilyMutation] = []

        for family in existing_families[:5]:
            mutation = FamilyMutation(
                family_id=family.id,
                mutation_type=random.choice(mutation_types),
                description=fake.sentence(),
                created_at=fake.date_time_this_year()
            )
            mutations_data.append(mutation)

        db.add_all(mutations_data)
        db.commit()
        print(f"✅ Successfully seeded {len(mutations_data)} family mutations.")
    except Exception as e:
        print(f"❌ Error seeding family_mutations table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    family_mutations()

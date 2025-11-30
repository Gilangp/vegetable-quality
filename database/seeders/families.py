from app.models.families import Families 
from config.database import SessionLocal
from faker import Faker
from typing import List
import os, random, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

fake = Faker('id_ID')

def families():
    db = SessionLocal()
    try:
        if db.query(Families).first():
            print("⚠️ Families table already seeded.")
            return

        families_data: List[Families] = []

        for i in range(10):
            family = Families(
                id=i+1,
                family_number=random.randint(1000, 9999),
                head_resident_id=None,
                created_at=fake.date_time_this_decade(),
                updated_at=fake.date_time_this_decade()
            )

            families_data.append(family)

        db.add_all(families_data)
        db.commit()
        print(f"✅ Successfully seeded {len(families_data)} families.")
    except Exception as e:
        print(f"❌ Error seeding families table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    families()
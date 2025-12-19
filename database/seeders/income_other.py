from app.models.income_other import IncomeOther
from config.database import SessionLocal
from faker import Faker
from typing import List
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

fake = Faker('id_ID')

def income_other():
    db = SessionLocal()
    try:
        if db.query(IncomeOther).first():
            print("⚠️ Income other table already seeded.")
            return

        sources = ["donatur", "warga", "sponsor"]
        others_data: List[IncomeOther] = []

        for i in range(15):
            other = IncomeOther(
                description=fake.sentence(),
                source=random.choice(sources),
                amount=random.choice([100000, 250000, 500000, 1000000]),
                created_at=fake.date_time_this_month()
            )
            others_data.append(other)

        db.add_all(others_data)
        db.commit()
        print(f"✅ Successfully seeded {len(others_data)} income other records.")
    except Exception as e:
        print(f"❌ Error seeding income_other table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    income_other()

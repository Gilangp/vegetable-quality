from app.models.income import Income
from config.database import SessionLocal
from faker import Faker
from typing import List
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

fake = Faker('id_ID')

def incomes():
    db = SessionLocal()
    try:
        if db.query(Income).first():
            print("⚠️ Incomes table already seeded.")
            return

        related_tables = ["bills", "donations", "other"]
        incomes_data: List[Income] = []

        for i in range(30):
            income = Income(
                related_table=random.choice(related_tables),
                related_id=random.randint(1, 20),
                amount=random.choice([50000, 75000, 100000, 150000, 250000, 500000]),
                created_at=fake.date_time_this_month()
            )
            incomes_data.append(income)

        db.add_all(incomes_data)
        db.commit()
        print(f"✅ Successfully seeded {len(incomes_data)} incomes.")
    except Exception as e:
        print(f"❌ Error seeding incomes table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    incomes()

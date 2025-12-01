from app.models.income_bill import IncomeBill
from app.models.resident_model import Resident
from app.models.income_category import IncomeCategory
from config.database import SessionLocal
from faker import Faker
from typing import List
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

fake = Faker('id_ID')

def income_bills():
    db = SessionLocal()
    try:
        if db.query(IncomeBill).first():
            print("⚠️ Income bills table already seeded.")
            return

        existing_residents = db.query(Resident).all()
        existing_categories = db.query(IncomeCategory).all()
        
        if not existing_residents or not existing_categories:
            print("❌ Error: Residents or Categories table is empty.")
            return

        statuses = ["unpaid", "paid"]
        bills_data: List[IncomeBill] = []

        for resident in existing_residents[:10]:
            for i in range(random.randint(1, 3)):
                bill = IncomeBill(
                    resident_id=resident.id,
                    category_id=random.choice(existing_categories).id,
                    amount=random.choice([50000, 75000, 100000, 150000]),
                    due_date=fake.date_object(),
                    status=random.choice(statuses),
                    created_at=fake.date_time_this_month()
                )
                bills_data.append(bill)

        db.add_all(bills_data)
        db.commit()
        print(f"✅ Successfully seeded {len(bills_data)} income bills.")
    except Exception as e:
        print(f"❌ Error seeding income_bills table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    income_bills()

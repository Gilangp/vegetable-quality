from app.models.spending import Spending
from config.database import SessionLocal
from faker import Faker
from typing import List
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

fake = Faker('id_ID')

def spendings():
    db = SessionLocal()
    try:
        if db.query(Spending).first():
            print("⚠️ Spendings table already seeded.")
            return

        spendings_data: List[Spending] = []

        spending_titles = [
            "Perbaikan jalan",
            "Pembangunan jembatan",
            "Renovasi balai pertemuan",
            "Pembelian peralatan kebersihan",
            "Perbaikan sistem air bersih",
            "Pemeliharaan lampu jalan",
            "Pelatihan keselamatan",
            "Bantuan sosial",
            "Pembelian peralatan olahraga",
            "Pembangunan taman"
        ]

        for i in range(20):
            spending = Spending(
                title=fake.random.choice(spending_titles),
                amount=random.choice([500000, 1000000, 2500000, 5000000]),
                description=fake.paragraph(),
                proof_image=fake.file_name(extension="jpg") if i % 2 == 0 else None,
                proof_file=fake.file_name(extension="pdf") if i % 3 == 0 else None,
                created_at=fake.date_time_this_month()
            )
            spendings_data.append(spending)

        db.add_all(spendings_data)
        db.commit()
        print(f"✅ Successfully seeded {len(spendings_data)} spendings.")
    except Exception as e:
        print(f"❌ Error seeding spendings table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    spendings()

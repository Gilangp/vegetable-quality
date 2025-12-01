from app.models.income_category import IncomeCategory
from config.database import SessionLocal
from typing import List
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def income_categories():
    db = SessionLocal()
    try:
        if db.query(IncomeCategory).first():
            print("⚠️ Income categories table already seeded.")
            return

        categories_data: List[IncomeCategory] = [
            IncomeCategory(
                name="Iuran Bulanan",
                description="Iuran warga bulanan untuk operasional RT/RW"
            ),
            IncomeCategory(
                name="Iuran Tahunan",
                description="Iuran warga tahunan untuk pembangunan"
            ),
            IncomeCategory(
                name="Iuran Kegiatan",
                description="Iuran untuk kegiatan khusus"
            ),
            IncomeCategory(
                name="Iuran Kebersihan",
                description="Iuran untuk kebersihan lingkungan"
            ),
            IncomeCategory(
                name="Iuran Keamanan",
                description="Iuran untuk sistem keamanan"
            ),
            IncomeCategory(
                name="Iuran Sosial",
                description="Iuran untuk bantuan sosial"
            ),
        ]

        db.add_all(categories_data)
        db.commit()
        print(f"✅ Successfully seeded {len(categories_data)} income categories.")
    except Exception as e:
        print(f"❌ Error seeding income_categories table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    income_categories()

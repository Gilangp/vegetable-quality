from app.models.marketplace_product import MarketplaceProduct
from app.models.resident_model import Resident
from app.models.verification_result import VerificationResult
from config.database import SessionLocal
from faker import Faker
from typing import List
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

fake = Faker('id_ID')

def marketplace_products():
    db = SessionLocal()
    try:
        if db.query(MarketplaceProduct).first():
            print("⚠️ Marketplace products table already seeded.")
            return

        existing_residents = db.query(Resident).all()
        existing_verifications = db.query(VerificationResult).filter(
            VerificationResult.is_valid_for_marketplace == True
        ).all()
        
        if not existing_residents or not existing_verifications:
            print("❌ Error: Residents or Verifications table is empty.")
            return

        statuses = ["active", "inactive", "rejected"]
        products_data: List[MarketplaceProduct] = []

        for verification in existing_verifications[:15]:
            product = MarketplaceProduct(
                resident_id=verification.resident_id,
                verification_id=verification.id,
                name=f"{verification.vegetable_name} Segar",
                price=random.choice([15000, 20000, 25000, 30000, 35000, 40000]),
                stock=random.randint(5, 50),
                description=fake.sentence(),
                image=verification.image,
                status=random.choice(statuses),
                created_at=fake.date_time_this_month()
            )
            products_data.append(product)

        db.add_all(products_data)
        db.commit()
        print(f"✅ Successfully seeded {len(products_data)} marketplace products.")
    except Exception as e:
        print(f"❌ Error seeding marketplace_products table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    marketplace_products()

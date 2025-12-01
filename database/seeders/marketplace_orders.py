from app.models.marketplace_order import MarketplaceOrder
from app.models.resident_model import Resident
from app.models.marketplace_product import MarketplaceProduct
from config.database import SessionLocal
from faker import Faker
from typing import List
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

fake = Faker('id_ID')

def marketplace_orders():
    db = SessionLocal()
    try:
        if db.query(MarketplaceOrder).first():
            print("⚠️ Marketplace orders table already seeded.")
            return

        existing_residents = db.query(Resident).all()
        existing_products = db.query(MarketplaceProduct).filter(
            MarketplaceProduct.status == "active"
        ).all()
        
        if not existing_residents or not existing_products:
            print("❌ Error: Residents or Products table is empty.")
            return

        statuses = ["pending", "paid", "delivered", "cancelled"]
        orders_data: List[MarketplaceOrder] = []

        for i in range(30):
            product = random.choice(existing_products)
            quantity = random.randint(1, 10)
            total_price = product.price * quantity
            
            order = MarketplaceOrder(
                buyer_id=random.choice(existing_residents).id,
                product_id=product.id,
                quantity=quantity,
                total_price=total_price,
                status=random.choice(statuses),
                created_at=fake.date_time_this_month()
            )
            orders_data.append(order)

        db.add_all(orders_data)
        db.commit()
        print(f"✅ Successfully seeded {len(orders_data)} marketplace orders.")
    except Exception as e:
        print(f"❌ Error seeding marketplace_orders table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    marketplace_orders()

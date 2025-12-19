from app.models.house import House
from config.database import SessionLocal
from faker import Faker
from typing import List
import os, random, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

fake = Faker('id_ID')

def houses():
    db = SessionLocal()
    try:
        if db.query(House).first():
            print("⚠️ Houses table already seeded.")
            return

        houses_data: List[House] = []

        for i in range(10):
            house = House(
                id=i+1,
                house_number=str(random.randint(1, 99)),
                address=fake.address(),
                rt=str(random.randint(1, 10)),
                rw=str(random.randint(1, 10)),
                created_at=fake.date_time_this_decade(),
                updated_at=fake.date_time_this_decade()
            )
            houses_data.append(house)

        db.add_all(houses_data)
        db.commit()
        print(f"✅ Successfully seeded {len(houses_data)} houses.")
    except Exception as e:
        print(f"❌ Error seeding houses table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    houses()
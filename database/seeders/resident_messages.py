from app.models.resident_message import ResidentMessage
from app.models.resident_model import Resident
from config.database import SessionLocal
from faker import Faker
from typing import List
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

fake = Faker('id_ID')

def resident_messages():
    db = SessionLocal()
    try:
        if db.query(ResidentMessage).first():
            print("⚠️ Resident messages table already seeded.")
            return

        existing_residents = db.query(Resident).all()
        
        if not existing_residents:
            print("❌ Error: Residents table is empty.")
            return

        statuses = ["pending", "read", "resolved"]
        messages_data: List[ResidentMessage] = []

        for i in range(20):
            message = ResidentMessage(
                resident_id=random.choice(existing_residents).id,
                subject=fake.sentence(nb_words=5),
                message=fake.paragraph(),
                status=random.choice(statuses),
                created_at=fake.date_time_this_month()
            )
            messages_data.append(message)

        db.add_all(messages_data)
        db.commit()
        print(f"✅ Successfully seeded {len(messages_data)} resident messages.")
    except Exception as e:
        print(f"❌ Error seeding resident_messages table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    resident_messages()

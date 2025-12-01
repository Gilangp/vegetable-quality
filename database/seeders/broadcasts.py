from app.models.broadcast import Broadcast
from app.models.user import User
from config.database import SessionLocal
from faker import Faker
from typing import List
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

fake = Faker('id_ID')

def broadcasts():
    db = SessionLocal()
    try:
        if db.query(Broadcast).first():
            print("⚠️ Broadcasts table already seeded.")
            return

        existing_users = db.query(User).filter(User.role.in_(["admin", "ketua_rw", "ketua_rt"])).all()
        
        if not existing_users:
            print("❌ Error: No authorized users found.")
            existing_users = db.query(User).all()

        broadcasts_data: List[Broadcast] = []

        for i in range(12):
            broadcast = Broadcast(
                title=fake.sentence(nb_words=8),
                message=fake.paragraph(nb_sentences=4),
                sent_by=random.choice(existing_users).id,
                created_at=fake.date_time_this_month()
            )
            broadcasts_data.append(broadcast)

        db.add_all(broadcasts_data)
        db.commit()
        print(f"✅ Successfully seeded {len(broadcasts_data)} broadcasts.")
    except Exception as e:
        print(f"❌ Error seeding broadcasts table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    broadcasts()

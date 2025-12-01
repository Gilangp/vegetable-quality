from app.models.user import User
from app.models.resident_model import Resident
from config.database import SessionLocal
from faker import Faker
import hashlib
from typing import List
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

fake = Faker('id_ID')

def users():
    db = SessionLocal()
    try:
        if db.query(User).first():
            print("⚠️ Users table already seeded.")
            return

        # Create admin user
        admin_user = User(
            resident_id=None,
            name="Admin",
            username="admin",
            email="admin@localhost.com",
            password=hashlib.sha256("admin123".encode()).hexdigest(),
            phone="081234567890",
            role="admin"
        )
        
        users_data: List[User] = [admin_user]

        # Get existing residents
        existing_residents = db.query(Resident).all()
        
        roles = ["ketua_rt", "ketua_rw", "bendahara", "sekretaris", "warga"]
        
        # Create users linked to residents
        for i, resident in enumerate(existing_residents[:10]):  # Limit to 10 residents
            role = random.choice(roles)
            user = User(
                resident_id=resident.id,
                name=resident.name,
                username=f"user_{resident.id}",
                email=f"user{resident.id}@localhost.com",
                password=hashlib.sha256("password123".encode()).hexdigest(),
                phone=resident.phone,
                role=role
            )
            users_data.append(user)

        db.add_all(users_data)
        db.commit()
        print(f"✅ Successfully seeded {len(users_data)} users.")
    except Exception as e:
        print(f"❌ Error seeding users table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    users()

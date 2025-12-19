from app.models.activity_log import ActivityLog
from app.models.user import User
from config.database import SessionLocal
from faker import Faker
from typing import List
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

fake = Faker('id_ID')

def activity_logs():
    db = SessionLocal()
    try:
        if db.query(ActivityLog).first():
            print("⚠️ Activity logs table already seeded.")
            return

        existing_users = db.query(User).all()
        
        if not existing_users:
            print("❌ Error: Users table is empty.")
            return

        actions = ["create", "update", "delete", "view", "download", "upload"]
        activity_logs_data: List[ActivityLog] = []

        for i in range(30):
            log = ActivityLog(
                user_id=random.choice(existing_users).id,
                action=random.choice(actions),
                description=fake.sentence(),
                created_at=fake.date_time_this_month()
            )
            activity_logs_data.append(log)

        db.add_all(activity_logs_data)
        db.commit()
        print(f"✅ Successfully seeded {len(activity_logs_data)} activity logs.")
    except Exception as e:
        print(f"❌ Error seeding activity_logs table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    activity_logs()

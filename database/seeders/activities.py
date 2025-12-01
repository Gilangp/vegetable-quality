from app.models.activity import Activity
from config.database import SessionLocal
from faker import Faker
from typing import List
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

fake = Faker('id_ID')

def activities():
    db = SessionLocal()
    try:
        if db.query(Activity).first():
            print("⚠️ Activities table already seeded.")
            return

        activities_data: List[Activity] = []

        for i in range(10):
            activity = Activity(
                title=fake.sentence(nb_words=6),
                description=fake.paragraph(nb_sentences=5),
                date=fake.date_object(),
                location=fake.city(),
                created_at=fake.date_time_this_month()
            )
            activities_data.append(activity)

        db.add_all(activities_data)
        db.commit()
        print(f"✅ Successfully seeded {len(activities_data)} activities.")
    except Exception as e:
        print(f"❌ Error seeding activities table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    activities()

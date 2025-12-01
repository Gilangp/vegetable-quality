from app.models.channel import Channel
from config.database import SessionLocal
from faker import Faker
from typing import List
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

fake = Faker('id_ID')

def channels():
    db = SessionLocal()
    try:
        if db.query(Channel).first():
            print("⚠️ Channels table already seeded.")
            return

        channels_data: List[Channel] = [
            Channel(
                name="Bank Mandiri",
                account_number="1234567890",
                holder_name="RT/RW 01/02"
            ),
            Channel(
                name="Bank BCA",
                account_number="9876543210",
                holder_name="Ketua RT"
            ),
            Channel(
                name="Bank BNI",
                account_number="5555666777",
                holder_name="Bendahara RT"
            ),
            Channel(
                name="OVO",
                account_number="08123456789",
                holder_name="RT/RW"
            ),
            Channel(
                name="GCash",
                account_number="09123456789",
                holder_name="Community Fund"
            ),
        ]

        db.add_all(channels_data)
        db.commit()
        print(f"✅ Successfully seeded {len(channels_data)} payment channels.")
    except Exception as e:
        print(f"❌ Error seeding channels table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    channels()

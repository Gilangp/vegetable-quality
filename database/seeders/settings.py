from app.models.setting import Setting
from config.database import SessionLocal
from typing import List
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def settings():
    db = SessionLocal()
    try:
        if db.query(Setting).first():
            print("⚠️ Settings table already seeded.")
            return

        settings_data: List[Setting] = [
            Setting(key="app_name", value="PCVK Marketplace Jawara"),
            Setting(key="app_version", value="1.0.0"),
            Setting(key="app_description", value="Platform Komunitas Verifikasi Kualitas Sayuran"),
            Setting(key="maintenance_mode", value="false"),
            Setting(key="allow_registration", value="true"),
            Setting(key="require_email_verification", value="true"),
            Setting(key="currency", value="IDR"),
            Setting(key="items_per_page", value="10"),
            Setting(key="max_upload_size", value="5242880"),
            Setting(key="allowed_image_types", value="jpg,jpeg,png,gif"),
        ]

        db.add_all(settings_data)
        db.commit()
        print(f"✅ Successfully seeded {len(settings_data)} settings.")
    except Exception as e:
        print(f"❌ Error seeding settings table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    settings()

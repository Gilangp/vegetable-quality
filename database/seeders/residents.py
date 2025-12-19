from app.models.family import Family
from app.models.house import House
from app.models.resident_model import Resident
from config.database import SessionLocal
from faker import Faker
from typing import List
import os
import random
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

fake = Faker('id_ID')

def residents():
    db = SessionLocal()
    try:
        if not db.query(Resident).first():
            existing_family_ids = [f.id for f in db.query(Family.id).all()]
            existing_house_ids = [h.id for h in db.query(House.id).all()]

            if not existing_family_ids or not existing_house_ids:
                print("Error: Families or Houses table is empty.")
                return

            religions = ["Islam", "Kristen", "Katolik", "Hindu", "Buddha", "Khonghucu"]
            blood_types = ["A", "B", "AB", "O", "-"]
            educations = ["SD", "SMP", "SMA", "D3", "S1", "S2", "S3"]
            occupations = ["PNS", "Swasta", "Wiraswasta", "Petani", "Buruh", "Guru", "Dokter", "Pengusaha", "Tidak Bekerja"]

            residents_data: List[Resident] = []

            for id in existing_family_ids:
                gender_options = ["Laki-laki", "Perempuan"]
                selected_gender = random.choice(gender_options)

                if selected_gender == "Laki-laki":
                    fake_name = fake.name_male()
                else:
                    fake_name = fake.name_female()

                resident = Resident(
                    family_id=id,
                    house_id=random.choice(existing_house_ids),
                    nik=str(fake.unique.random_number(digits=16, fix_len=True)),
                    name=fake_name,
                    phone=fake.phone_number(),
                    birth_place=fake.city(),
                    birth_date=fake.date_of_birth(minimum_age=17, maximum_age=80),
                    gender=selected_gender,
                    religion=random.choice(religions),
                    blood_type=random.choice(blood_types),
                    education=random.choice(educations),
                    occupation=random.choice(occupations),
                    status=random.choice(["aktif", "pindah", "meninggal"])
                )

                residents_data.append(resident)

            db.add_all(residents_data)
            db.commit()
            print(
                f"[OK] Successfully seeded {len(residents_data)} residents (1 per family).")
        else:
            print("[OK] Residents table already seeded.")

        all_families = db.query(Family).all()
        for family in all_families:
            candidate = db.query(Resident).filter(Resident.family_id == family.id).first()
            if candidate:
                family.head_resident_id = candidate.id
                db.add(family)

        db.commit()
        print("[OK] Successfully updated ID of head residents for families.")

    except Exception as e:
        print(f"[ERROR] Error seeding residents table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    residents()
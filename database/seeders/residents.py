from app.models.families import Families
from app.models.houses import Houses
from app.models.residents import Residents
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
        if not db.query(Residents).first():
            existing_family_ids = [f.id for f in db.query(Families.id).all()]
            existing_house_ids = [h.id for h in db.query(Houses.id).all()]

            if not existing_family_ids or not existing_house_ids:
                print("Error: Families or Houses table is empty.")
                return

            residents_data: List[Residents] = []

            for id in existing_family_ids:
                gender_options = ["Laki-laki", "Perempuan"]
                selected_gender = random.choice(gender_options)

                if selected_gender == "Laki-laki":
                    fake_name = fake.name_male()
                else:
                    fake_name = fake.name_female()

                resident = Residents(
                    family_id=id,
                    house_id=random.choice(existing_house_ids),
                    nik=str(fake.unique.random_number(digits=16, fix_len=True)),
                    name=fake_name,
                    phone=fake.phone_number(),
                    birth_place=fake.city(),
                    birth_date=fake.date_of_birth(minimum_age=17, maximum_age=80),
                    gender=selected_gender,
                    status=random.choice(["Menikah", "Belum Menikah", "Cerai Hidup", "Cerai Mati"]),
                    religion=random.choice(["Islam", "Kristen Protestan", "Katolik", "Hindu", "Buddha", "Konghucu"]),
                    blood_type=random.choice(["A", "B", "AB", "O"]),
                    education=random.choice(["SD", "SMP", "SMA", "Diploma", "Sarjana", "Magister", "Doktor"]),
                    occupation=fake.job()
                )

                residents_data.append(resident)

            db.add_all(residents_data)
            db.commit()
            print(
                f"✅ Successfully seeded {len(residents_data)} residents (1 per family).")
        else:
            print("✅ Residents table already seeded.")

        all_families = db.query(Families).all()
        for family in all_families:
            candidate = db.query(Residents).filter(Residents.family_id == family.id).first()
            if candidate:
                family.head_resident_id = candidate.id
                db.add(family)

        db.commit()
        print("✅ Successfully updated ID of head residents for families.")

    except Exception as e:
        print(f"❌ Error seeding residents table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    residents()
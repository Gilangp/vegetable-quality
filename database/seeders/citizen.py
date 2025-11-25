from config.database import SessionLocal
from database.migrations.citizen import Citizen as CitizenDB
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def citizen():
    db = SessionLocal()
    try:
        if db.query(CitizenDB).first():
            print("⚠️ Citizen table already seeded.")
            return

        citizens = [
            CitizenDB(
                nik=350700000001,
                nama="Budi Santoso",
                nomor_telepon="08123456789",
                tempat_lahir="Malang",
                tanggal_lahir="1990-01-01",
                jenis_kelamin="Laki-laki",
                agama="Islam",
                golongan_darah="O",
                peran_keluarga="Kepala Keluarga",
                pendidikan_terakhir="S1",
                pekerjaan="Programmer",
                status="Menikah"
            ),
            CitizenDB(
                nik=350700000002,
                nama="Siti Aminah",
                nomor_telepon="08198765432",
                tempat_lahir="Surabaya",
                tanggal_lahir="1992-05-20",
                jenis_kelamin="Perempuan",
                agama="Islam",
                golongan_darah="A",
                peran_keluarga="Istri",
                pendidikan_terakhir="D3",
                pekerjaan="Guru",
                status="Menikah"
            ),
        ]

        db.add_all(citizens)
        db.commit()
        print("✅ Citizen table seeded successfully.")
    except Exception as e:
        print(f"❌ Error seeding citizen table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    citizen()
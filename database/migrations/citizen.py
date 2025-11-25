from config.database import Base, engine
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column
import sys, os

sys.path.append(os.getcwd())

class Citizen(Base):
    __tablename__ = "warga"

    nik: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    nama: Mapped[str] = mapped_column(String(100), nullable=False)
    nomor_telepon: Mapped[int|str] = mapped_column(String(15), nullable=False)
    tempat_lahir: Mapped[str] = mapped_column(String(50), nullable=False)
    tanggal_lahir: Mapped[str] = mapped_column(String(10), nullable=False)
    jenis_kelamin: Mapped[str] = mapped_column(String(10), nullable=False)
    agama: Mapped[str] = mapped_column(String(20), nullable=False)
    golongan_darah: Mapped[str] = mapped_column(String(5), nullable=False)
    peran_keluarga: Mapped[str] = mapped_column(String(20), nullable=False)
    pendidikan_terakhir: Mapped[str] = mapped_column(String(50), nullable=False)
    pekerjaan: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    def __repr__(self) -> str:
        return f"<Citizen(nik={self.nik}, nama={self.nama})>"

Base.metadata.create_all(bind=engine)
from pydantic import BaseModel

class Citizen(BaseModel):
    nik: int
    nama: str
    nomor_telepon: str
    tempat_lahir: str
    tanggal_lahir: str
    jenis_kelamin: str
    agama: str
    golongan_darah: str
    peran_keluarga: str
    pendidikan_terakhir: str
    pekerjaan: str
    status: str

    class Config:
        from_attributes = True
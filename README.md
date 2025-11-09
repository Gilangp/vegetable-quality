<h1 align="center">🥦 API Deteksi Keutuhan Sayur</h1>

Ini adalah repositori backend untuk Proyek Pembelajaran Berbasis Proyek (Project Based Learning) mata kuliah Pengolahan Citra dan Visi Komputer.

Proyek ini bertujuan untuk membuat API yang dapat menganalisis gambar sayuran dan menentukan keutuhannya (misalnya "Segar" atau "Busuk") menggunakan model _Computer Vision_. API ini dirancang untuk digunakan oleh aplikasi _frontend_ (Flutter).

## 🚀 Fitur Utama

- **Endpoint Prediksi:** Menerima _file_ gambar dan mengembalikan hasil prediksi dalam format JSON.
- **Halaman Uji Coba:** Menyediakan halaman HTML sederhana untuk menguji _endpoint_ langsung dari _browser_.
- **Kualitas Kode Terjaga:** Dikonfigurasi dengan `Ruff`, `Black`, dan `MyPy` untuk memastikan kode tetap bersih, seragam, dan _type-safe_.

## 🛠️ Stack Teknologi

- **Backend:** Python 3.10+
- **Framework API:** FastAPI
- **Pemrosesan Gambar:** OpenCV-Python, Pillow
- **Machine Learning:** TensorFlow (atau PyTorch/Scikit-learn)
- **Testing:** PyTest

---

## 🏁 Panduan Setup & Instalasi

Panduan ini ditujukan untuk anggota tim yang menggunakan Windows (CMD/PowerShell).

### 1. Prasyarat

- Pastikan kamu sudah meng-install **Python 3.10** atau yang lebih baru.
- Pastikan **Git** sudah ter-install.

### 2. Instalasi

1.  **Clone Repositori**

    ```bash
    git clone https://github.com/a6iyyu/vegetable-quality
    cd vegetable-quality
    ```

2.  **Jalankan Skrip Inisialisasi**
    Buka folder proyek di File Explorer, lalu **double-click** file `init.bat`.

    Atau, jalankan dari terminal (CMD/PowerShell):

    ```bash
    .\init.bat
    ```

    Skrip ini akan secara otomatis:

    - Membuat _virtual environment_ Python di dalam folder `venv`.
    - Meng-install semua _library_ yang dibutuhkan dari `requirements.txt`.
    - Meng-install semua _library_ development dari `requirements-dev.txt`.

3.  **Aktifkan Virtual Environment (PENTING!)**
    Setelah skrip `init.bat` selesai, kamu **harus** mengaktifkan venv-nya secara manual di terminalmu.

    - **Jika pakai CMD:**
      ```bash
      venv\Scripts\activate
      ```
    - **Jika pakai PowerShell:**
      `bash
    .\venv\Scripts\Activate.ps1
    `
      Kamu akan tahu venv aktif jika ada `(venv)` di awal _prompt_ terminalmu.

4.  **Jalankan Server**
    Setelah venv aktif, jalankan server FastAPI dengan Uvicorn:

    ```bash
    uvicorn main:app --reload
    ```

    - `--reload` akan membuat server otomatis _restart_ setiap kali kamu menyimpan perubahan pada file `.py`.

5.  **Buka Halaman Uji Coba**
    Buka _browser_ dan pergi ke **http://127.0.0.1:8000/**.
    Kamu akan melihat halaman HTML untuk meng-upload gambar dan menguji API.

---

## 🔬 API Endpoint

### `POST /predict`

Menganalisis gambar sayur yang di-upload dan mengembalikan prediksi.

- **Request Body:** `multipart/form-data`

  - `file`: (file) Gambar yang akan dianalisis (.jpg atau .png).

- **Respons Sukses (200 OK):**

  ```json
  {
    "message": "Analisis gambar berhasil",
    "data": {
      "prediction": "Segar",
      "confidence": 0.9542
    }
  }
  ```

- **Respons Error (400 Bad Request):**
  ```json
  {
    "detail": "Tipe file tidak valid. Harap unggah .jpg atau .png"
  }
  ```

---

## 📜 Panduan Kontribusi (Untuk Tim)

Untuk menjaga kualitas dan keseragaman kode, mohon ikuti aturan berikut **sebelum melakukan `git commit`**.

Pastikan _virtual environment_ (`venv`) sudah aktif.

### 1. Format Kode (Otomatis)

Jalankan perintah ini untuk merapikan format kodemu secara otomatis:

```bash
# Jalankan Black untuk format
black .

# Jalankan Ruff untuk format import dan fix cepat
ruff check --fix .

# Jalankan MyPy untuk type checking
mypy .
```

### 2. Jalankan Pengujian Otomatis

Jalankan perintah ini untuk menjalankan pengujian otomatis:

```bash
pytest
```

👨‍💻 Tim Pengembang

- Ahmad Dzul Fadhli Hannan — 2341720106

- Gilang Purnomo — 2341720042

- Mochammad Firmandika Jati Kusuma — 2341720229

- Rafi Abiyyu Airlangga — 2341720115
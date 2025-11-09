@echo off

echo Mengecek lingkungan virtual...

if not exist "venv\Scripts\activate" (
    echo Membuat lingkungan virtual...
    python -m venv venv
) else (
    echo Lingkungan virtual Python sudah ada.
)

echo Memasang dependensi dari requirements.txt...
call "venv\Scripts\pip.exe" install -r requirements.txt

echo:
echo Sekarang, aktifkan venv dengan menjalankan perintah venv\Scripts\activate
echo:

"""
Controller untuk klasifikasi prediksi sayur.
"""

import os
import tempfile
import shutil
from fastapi import HTTPException
from services.vegetable_classifier import get_classifier


class PredictionController:
    """Controller untuk handle business logic prediksi sayur."""

    @staticmethod
    def validate_file(content_type: str) -> None:
        """
        Validasi tipe file yang diizinkan.

        Args:
            content_type: MIME type dari file

        Raises:
            HTTPException: Jika tipe file tidak valid
        """
        allowed_types = {"image/jpeg", "image/png", "image/bmp"}
        if content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Tipe file tidak valid. Harap unggah .jpg, .png, atau .bmp"
            )

    @staticmethod
    def validate_file_size(file_size: int, max_size: int = 10 * 1024 * 1024) -> None:
        """
        Validasi ukuran file.

        Args:
            file_size: Ukuran file dalam bytes
            max_size: Ukuran maksimal (default 10MB)

        Raises:
            HTTPException: Jika ukuran file terlalu besar
        """
        if file_size > max_size:
            raise HTTPException(
                status_code=413,
                detail="Ukuran file terlalu besar. Maksimal 10MB."
            )

    @staticmethod
    def predict(file_contents: bytes, filename: str) -> dict:
        """
        Jalankan prediksi pada file gambar.

        Args:
            file_contents: Binary contents dari file gambar
            filename: Nama file asli

        Returns:
            Dictionary berisi hasil prediksi

        Raises:
            HTTPException: Jika terjadi error saat prediksi
        """
        # Simpan file sementara
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, filename)

        try:
            # Tulis file ke temp directory
            with open(temp_file_path, "wb") as f:
                f.write(file_contents)

            # Jalankan prediksi
            classifier = get_classifier()
            result = classifier.predict(temp_file_path)

            return {
                "message": "Analisis gambar berhasil",
                "data": result
            }

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
        finally:
            # Cleanup temp directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

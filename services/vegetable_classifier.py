"""
Layanan klasifikasi sayur menggunakan TFLite model.
"""

import os
import numpy as np
import cv2
import tensorflow as tf
from pathlib import Path


class VegetableClassifier:
    """Layanan untuk klasifikasi keutuhan sayur (Utuh/Tidak Utuh)."""

    def __init__(self, model_path: str = "models/model_mobilenetv2_classifier.tflite"):
        """
        Inisialisasi classifier dengan TFLite model.

        Args:
            model_path: Path ke file TFLite model
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model tidak ditemukan di {model_path}")

        self.model_path = model_path
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        # get input and output details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        # class labels
        self.class_labels = ["Utuh", "Tidak Utuh"]

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Pre-process gambar untuk model (resize, normalize, brightness, dll).

        Args:
            image: Gambar dalam format BGR (dari cv2.imread)

        Returns:
            Gambar yang sudah di-preprocess dalam format float32 (0-1)
        """
        # 1. Resize ke 224 × 224 piksel
        image = cv2.resize(image, (224, 224))

        # 2. BGR → RGB conversion
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # 3. Normalisasi awal 0-1
        img = image.astype(np.float32) / 255.0

        # 4. Brightness & Contrast Adjustment
        img_tf = tf.constant(img)
        brightness_delta = 0.1
        img_tf = tf.image.adjust_brightness(img_tf, brightness_delta)
        contrast_factor = 1.3
        img_tf = tf.image.adjust_contrast(img_tf, contrast_factor)
        img = img_tf.numpy()
        img = np.clip(img, 0, 1)

        # 5. Histogram Equalization pada Kanal V (HSV)
        from skimage.color import rgb2hsv, hsv2rgb
        from skimage import exposure

        img_hsv = rgb2hsv(img)
        v_channel = img_hsv[:, :, 2]
        v_channel_eq = exposure.equalize_adapthist(v_channel)
        img_hsv[:, :, 2] = v_channel_eq
        img = hsv2rgb(img_hsv)

        # 6. Saturation Enhancement
        img_hsv_final = rgb2hsv(img)
        saturation_boost = 1.2
        img_hsv_final[:, :, 1] = np.clip(
            img_hsv_final[:, :, 1] * saturation_boost, 0, 1
        )
        img = hsv2rgb(img_hsv_final)

        return np.clip(img, 0, 1).astype(np.float32)

    def predict(self, image_path: str) -> dict:
        """
        Prediksi keutuhan sayur dari gambar.

        Args:
            image_path: Path ke file gambar

        Returns:
            Dictionary berisi:
            - prediction: Label prediksi ("Utuh" atau "Tidak Utuh")
            - confidence: Confidence score (0-1)
            - class_probabilities: Probabilitas untuk setiap kelas
        """
        # load dan preprocess gambar
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Tidak bisa membaca gambar dari {image_path}")

        processed_image = self.preprocess_image(image)

        # Add batch dimension: (224, 224, 3) → (1, 224, 224, 3)
        input_data = np.expand_dims(processed_image, axis=0)

        # Set input tensor
        self.interpreter.set_tensor(
            self.input_details[0]["index"],
            input_data.astype(self.input_details[0]["dtype"]),
        )

        # Run inference
        self.interpreter.invoke()

        # Get output tensor
        output_data = self.interpreter.get_tensor(self.output_details[0]["index"])

        # Parse results
        probabilities = output_data[0]  # (2,) array
        predicted_class_idx = np.argmax(probabilities)
        confidence = float(probabilities[predicted_class_idx])

        return {
            "prediction": self.class_labels[predicted_class_idx],
            "confidence": confidence,
            "class_probabilities": {
                "utuh": float(probabilities[0]),
                "tidak_utuh": float(probabilities[1]),
            },
        }

    def predict_batch(self, image_paths: list) -> list:
        """
        Prediksi batch gambar sekaligus.

        Args:
            image_paths: List of paths ke gambar

        Returns:
            List of prediction results
        """
        results = []
        for image_path in image_paths:
            try:
                result = self.predict(image_path)
                results.append({"status": "success", **result})
            except Exception as e:
                results.append({"status": "error", "message": str(e)})
        return results


# global classifier instance (lazy loading)
_classifier = None


def get_classifier() -> VegetableClassifier:
    """Get atau inisialisasi classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = VegetableClassifier()
    return _classifier

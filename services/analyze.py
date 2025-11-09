from models.prediction import PredictionData

class Analyze:
    def __init__(self):
        pass

    def analyze(self, image_bytes: bytes) -> PredictionData:
        """
        Menganalisis bytes gambar dan mengembalikan hasil prediksi.
        Ganti placeholder di bawah ini dengan logika CV/ML-mu.
        """
        print("Menganalisis gambar... (menggunakan logika palsu)")
        
        if len(image_bytes) % 2 == 0:
            predicted_class_name = "Segar"
            confidence_score = 0.95
        else:
            predicted_class_name = "Busuk"
            confidence_score = 0.88

        return PredictionData(prediction=predicted_class_name, confidence=confidence_score)
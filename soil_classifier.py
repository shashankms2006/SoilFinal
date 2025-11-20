"""
Roboflow soil image classification module
Classifies soil type from uploaded images
"""

import requests
import tempfile
from typing import Tuple, Optional
from PIL import Image
import io


class SoilClassifier:
    """Soil type classifier using Roboflow API"""

    def __init__(self, api_key: str = "U17grkzGByVPjq4Lp3bh"):
        self.api_key = api_key
        self.api_url = "https://serverless.roboflow.com"
        self.model_id = "soil-classification-project/2"

    def classify_image(self, image_file) -> Tuple[str, float]:
        """
        Classify soil type from image file
        
        Args:
            image_file: File object or path to image
            
        Returns:
            Tuple of (soil_type, confidence)
        """
        try:
            # Handle both file objects and paths
            if isinstance(image_file, str):
                with open(image_file, 'rb') as f:
                    image_data = f.read()
            else:
                image_data = image_file.read()

            files = {"file": ("image.jpg", image_data, "image/jpeg")}
            
            response = requests.post(
                f"{self.api_url}/{self.model_id}",
                params={"api_key": self.api_key},
                files=files,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                
                if "predictions" in result and result["predictions"]:
                    predictions = result["predictions"]
                    
                    # Find top prediction
                    top_pred = max(
                        predictions.items(),
                        key=lambda x: x[1].get("confidence", 0)
                    )
                    
                    soil_type = top_pred[0]
                    confidence = top_pred[1].get("confidence", 0.0)
                    
                    return soil_type, confidence

            return "Unknown", 0.0

        except Exception as e:
            return "Unknown", 0.0

    def classify_from_path(self, image_path: str) -> Tuple[str, float]:
        """Classify soil type from image path"""
        return self.classify_image(image_path)

    def get_all_predictions(self, image_file) -> dict:
        """Get all predictions with confidence scores"""
        try:
            if isinstance(image_file, str):
                with open(image_file, 'rb') as f:
                    image_data = f.read()
            else:
                image_data = image_file.read()

            files = {"file": ("image.jpg", image_data, "image/jpeg")}
            
            response = requests.post(
                f"{self.api_url}/{self.model_id}",
                params={"api_key": self.api_key},
                files=files,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if "predictions" in result:
                    return result["predictions"]

            return {}

        except Exception as e:
            return {}

"""Droppings detection model loading and inference helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import numpy as np
from tensorflow.keras.models import load_model

from utils.image_processing import load_and_preprocess_image


DROPPINGS_CLASSES = ["Normal", "Bloody", "Watery", "Green", "Yellow"]


class DroppingsDetector:
    def __init__(self, model_path: str = "models/saved_models/droppings_model.h5") -> None:
        self.model_path = Path(model_path)
        self.model = None

    def load(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Droppings model not found at: {self.model_path}")
        self.model = load_model(self.model_path)

    def predict(self, image_path: str) -> Tuple[str, float, Dict[str, float]]:
        if self.model is None:
            self.load()

        image = load_and_preprocess_image(image_path, target_size=(224, 224))
        probabilities = self.model.predict(np.expand_dims(image, axis=0), verbose=0)[0]
        top_index = int(np.argmax(probabilities))
        label = DROPPINGS_CLASSES[top_index]
        confidence = float(probabilities[top_index] * 100)
        class_map = {DROPPINGS_CLASSES[i]: float(probabilities[i] * 100) for i in range(len(DROPPINGS_CLASSES))}
        return label, confidence, class_map

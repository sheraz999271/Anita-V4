"""Image preprocessing utilities using OpenCV."""

from __future__ import annotations

from typing import Tuple

import cv2
import numpy as np


def load_and_preprocess_image(image_path: str, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
    """Read image via OpenCV, convert to RGB, resize, and normalize [0,1]."""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Unable to open image: {image_path}")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, target_size)
    image = image.astype("float32") / 255.0
    return image

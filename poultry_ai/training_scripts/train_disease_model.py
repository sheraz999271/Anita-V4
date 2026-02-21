"""Training script for bird disease classification CNN."""

from __future__ import annotations

import os

from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator


DATA_DIR = "poultry_ai/data/disease"
MODEL_OUT = "poultry_ai/models/saved_models/disease_model.h5"
IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 15


def build_model(input_shape=(224, 224, 3), num_classes=4):
    model = models.Sequential(
        [
            layers.Input(shape=input_shape),
            layers.Conv2D(32, (3, 3), activation="relu"),
            layers.MaxPooling2D(2, 2),
            layers.Conv2D(64, (3, 3), activation="relu"),
            layers.MaxPooling2D(2, 2),
            layers.Conv2D(128, (3, 3), activation="relu"),
            layers.MaxPooling2D(2, 2),
            layers.Flatten(),
            layers.Dense(128, activation="relu"),
            layers.Dropout(0.3),
            layers.Dense(num_classes, activation="softmax"),
        ]
    )
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    return model


def main() -> None:
    datagen = ImageDataGenerator(rescale=1.0 / 255, validation_split=0.2)

    train_data = datagen.flow_from_directory(
        DATA_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="training",
    )
    val_data = datagen.flow_from_directory(
        DATA_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="validation",
    )

    model = build_model(num_classes=4)
    model.fit(train_data, validation_data=val_data, epochs=EPOCHS)

    os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)
    model.save(MODEL_OUT)
    print(f"Disease model saved to: {MODEL_OUT}")


if __name__ == "__main__":
    main()

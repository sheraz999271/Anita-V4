# Poultry AI Desktop Management Software

Production-style desktop software for poultry farm monitoring, AI-assisted detection, records, and analytics.

## Project Structure

```text
poultry_ai/
├── main.py
├── README.md
├── requirements.txt
├── database/
│   ├── __init__.py
│   └── db_manager.py
├── models/
│   ├── __init__.py
│   ├── disease_model.py
│   └── droppings_model.py
├── training_scripts/
│   ├── train_disease_model.py
│   └── train_droppings_model.py
├── ui/
│   ├── __init__.py
│   └── main_window.py
└── utils/
    ├── __init__.py
    ├── decision_engine.py
    ├── image_processing.py
    └── reporting.py
```

## Features

- **PyQt6 Desktop UI** with sections for dashboard, records, reports, and settings.
- **Bird Disease Detection CNN** (`Healthy`, `Newcastle`, `CRD`, `Coccidiosis`).
- **Droppings Detection CNN** (`Normal`, `Bloody`, `Watery`, `Green`, `Yellow`).
- **OpenCV preprocessing** (load, resize to `224x224`, normalize).
- **Decision Engine rules** for mortality and droppings patterns.
- **SQLite CRUD** with automatic mortality rate and feed conversion ratio calculations.
- **Matplotlib charts** for mortality trend, feed trend, and disease history.
- Disclaimer integrated into UI:
  > This AI provides suggestion only. Consult veterinarian for final diagnosis.

## Setup

1. Create and activate virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

2. Install dependencies:

```bash
pip install -r poultry_ai/requirements.txt
```

## Run Desktop App

```bash
python poultry_ai/main.py
```

## Model Training

Prepare image folders before training:

- Disease dataset path: `poultry_ai/data/disease/`
  - `Healthy/`, `Newcastle/`, `CRD/`, `Coccidiosis/`
- Droppings dataset path: `poultry_ai/data/droppings/`
  - `Normal/`, `Bloody/`, `Watery/`, `Green/`, `Yellow/`

Then run:

```bash
python poultry_ai/training_scripts/train_disease_model.py
python poultry_ai/training_scripts/train_droppings_model.py
```

Saved models:

- `poultry_ai/models/saved_models/disease_model.h5`
- `poultry_ai/models/saved_models/droppings_model.h5`

## Build Executable (PyInstaller)

```bash
pyinstaller --noconfirm --windowed --name PoultryAI poultry_ai/main.py
```

Executable will be available inside the `dist/` directory.

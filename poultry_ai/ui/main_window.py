"""Main PyQt6 GUI for Poultry AI Management software."""

from __future__ import annotations

import os
from typing import Optional

import cv2
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from database.db_manager import DatabaseManager, PoultryRecord
from models.disease_model import DiseaseDetector
from models.droppings_model import DroppingsDetector
from utils.decision_engine import evaluate_management_rules
from utils.reporting import generate_trend_charts


DISCLAIMER = "This AI provides suggestion only. Consult veterinarian for final diagnosis."


class PoultryAIMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Poultry AI Management")
        self.resize(1280, 820)

        self.db = DatabaseManager("poultry_ai/database/poultry_ai.db")
        self.disease_detector = DiseaseDetector("poultry_ai/models/saved_models/disease_model.h5")
        self.droppings_detector = DroppingsDetector("poultry_ai/models/saved_models/droppings_model.h5")

        self.current_disease_prediction = "Unknown"
        self.current_droppings_prediction = "Unknown"

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.dashboard_tab = QWidget()
        self.records_tab = QWidget()
        self.reports_tab = QWidget()
        self.settings_tab = QWidget()

        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.records_tab, "Record Keeping")
        self.tabs.addTab(self.reports_tab, "Reports & Analytics")
        self.tabs.addTab(self.settings_tab, "Settings")

        self._build_dashboard_tab()
        self._build_records_tab()
        self._build_reports_tab()
        self._build_settings_tab()

        self.refresh_records_table()

    def _build_dashboard_tab(self) -> None:
        layout = QGridLayout()

        self.disease_group = self._build_upload_group(
            "Bird Disease Detection", self.handle_disease_upload
        )
        self.droppings_group = self._build_upload_group(
            "Droppings Detection", self.handle_droppings_upload
        )

        decision_group = QGroupBox("Management Decision Engine")
        decision_layout = QVBoxLayout()
        self.alerts_list = QListWidget()
        decision_layout.addWidget(self.alerts_list)
        self.evaluate_btn = QPushButton("Evaluate Current Farm Status")
        self.evaluate_btn.clicked.connect(self.run_decision_engine)
        decision_layout.addWidget(self.evaluate_btn)
        decision_group.setLayout(decision_layout)

        disclaimer_label = QLabel(DISCLAIMER)
        disclaimer_label.setWordWrap(True)
        disclaimer_label.setStyleSheet("color: #b00; font-weight: bold;")

        layout.addWidget(self.disease_group, 0, 0)
        layout.addWidget(self.droppings_group, 0, 1)
        layout.addWidget(decision_group, 1, 0, 1, 2)
        layout.addWidget(disclaimer_label, 2, 0, 1, 2)

        self.dashboard_tab.setLayout(layout)

    def _build_upload_group(self, title: str, handler) -> QGroupBox:
        group = QGroupBox(title)
        vbox = QVBoxLayout()

        image_label = QLabel("No image selected")
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setMinimumHeight(240)
        image_label.setStyleSheet("border: 1px solid #ddd; background: #f8f8f8;")

        result_label = QLabel("Prediction: --")
        confidence_label = QLabel("Confidence: --")
        upload_btn = QPushButton("Upload Image")
        upload_btn.clicked.connect(lambda: handler(image_label, result_label, confidence_label))

        vbox.addWidget(image_label)
        vbox.addWidget(result_label)
        vbox.addWidget(confidence_label)
        vbox.addWidget(upload_btn)
        group.setLayout(vbox)

        return group

    def _build_records_tab(self) -> None:
        root = QHBoxLayout()

        form_group = QGroupBox("Add / Update Record")
        form = QFormLayout()

        self.date_input = QLineEdit()
        self.flock_size_input = QLineEdit()
        self.mortality_input = QLineEdit()
        self.feed_used_input = QLineEdit()
        self.avg_weight_input = QLineEdit()
        self.droppings_input = QLineEdit()
        self.disease_input = QLineEdit()

        form.addRow("Date (YYYY-MM-DD)", self.date_input)
        form.addRow("Flock Size", self.flock_size_input)
        form.addRow("Mortality", self.mortality_input)
        form.addRow("Feed Used (kg)", self.feed_used_input)
        form.addRow("Average Weight (kg)", self.avg_weight_input)
        form.addRow("Droppings Status", self.droppings_input)
        form.addRow("Disease Detected", self.disease_input)

        buttons = QHBoxLayout()
        create_btn = QPushButton("Create")
        update_btn = QPushButton("Update Selected")
        delete_btn = QPushButton("Delete Selected")

        create_btn.clicked.connect(self.create_record)
        update_btn.clicked.connect(self.update_record)
        delete_btn.clicked.connect(self.delete_record)

        buttons.addWidget(create_btn)
        buttons.addWidget(update_btn)
        buttons.addWidget(delete_btn)
        form.addRow(buttons)

        form_group.setLayout(form)

        self.records_table = QTableWidget()
        self.records_table.setColumnCount(10)
        self.records_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Date",
                "Flock Size",
                "Mortality",
                "Feed Used",
                "Avg Weight",
                "Droppings",
                "Disease",
                "Mortality Rate %",
                "FCR",
            ]
        )
        self.records_table.cellClicked.connect(self.populate_form_from_row)

        root.addWidget(form_group, 1)
        root.addWidget(self.records_table, 2)

        self.records_tab.setLayout(root)

    def _build_reports_tab(self) -> None:
        layout = QVBoxLayout()
        generate_btn = QPushButton("Generate Charts")
        generate_btn.clicked.connect(self.generate_reports)

        self.reports_output = QTextEdit()
        self.reports_output.setReadOnly(True)

        layout.addWidget(generate_btn)
        layout.addWidget(self.reports_output)

        self.reports_tab.setLayout(layout)

    def _build_settings_tab(self) -> None:
        layout = QVBoxLayout()
        text = QTextEdit()
        text.setReadOnly(True)
        text.setText(
            "Settings Overview\n\n"
            "- Configure model paths in ui/main_window.py\n"
            "- Ensure TensorFlow models exist in poultry_ai/models/saved_models\n"
            "- Build executable with:\n"
            "  pyinstaller --noconfirm --windowed --name PoultryAI poultry_ai/main.py"
        )
        layout.addWidget(text)
        self.settings_tab.setLayout(layout)

    def handle_disease_upload(self, image_label: QLabel, result_label: QLabel, confidence_label: QLabel) -> None:
        self._handle_upload(
            image_label,
            result_label,
            confidence_label,
            self.disease_detector,
            is_disease=True,
        )

    def handle_droppings_upload(self, image_label: QLabel, result_label: QLabel, confidence_label: QLabel) -> None:
        self._handle_upload(
            image_label,
            result_label,
            confidence_label,
            self.droppings_detector,
            is_disease=False,
        )

    def _handle_upload(
        self,
        image_label: QLabel,
        result_label: QLabel,
        confidence_label: QLabel,
        detector,
        is_disease: bool,
    ) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp)",
        )
        if not file_path:
            return

        try:
            self._show_preview(file_path, image_label)
            label, confidence, _ = detector.predict(file_path)
            result_label.setText(f"Prediction: {label}")
            confidence_label.setText(f"Confidence: {confidence:.2f}%")

            if is_disease:
                self.current_disease_prediction = label
            else:
                self.current_droppings_prediction = label
        except Exception as exc:
            QMessageBox.critical(self, "Prediction Error", str(exc))

    def _show_preview(self, file_path: str, image_label: QLabel) -> None:
        image = cv2.imread(file_path)
        if image is None:
            raise ValueError("Could not read selected image.")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = image.shape
        q_image = QImage(image.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        image_label.setPixmap(pixmap.scaled(320, 240, Qt.AspectRatioMode.KeepAspectRatio))

    def create_record(self) -> None:
        try:
            record = self._record_from_form()
            self.db.create_record(record)
            self.refresh_records_table()
            QMessageBox.information(self, "Success", "Record created.")
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def update_record(self) -> None:
        row = self.records_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select a record to update.")
            return

        record_id = int(self.records_table.item(row, 0).text())
        try:
            self.db.update_record(record_id, self._record_from_form())
            self.refresh_records_table()
            QMessageBox.information(self, "Success", "Record updated.")
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def delete_record(self) -> None:
        row = self.records_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Selection", "Please select a record to delete.")
            return

        record_id = int(self.records_table.item(row, 0).text())
        try:
            self.db.delete_record(record_id)
            self.refresh_records_table()
            QMessageBox.information(self, "Success", "Record deleted.")
        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))

    def _record_from_form(self) -> PoultryRecord:
        return PoultryRecord(
            date=self.date_input.text().strip(),
            flock_size=int(self.flock_size_input.text()),
            mortality=int(self.mortality_input.text()),
            feed_used=float(self.feed_used_input.text()),
            avg_weight=float(self.avg_weight_input.text()),
            droppings_status=self.droppings_input.text().strip() or self.current_droppings_prediction,
            disease_detected=self.disease_input.text().strip() or self.current_disease_prediction,
        )

    def refresh_records_table(self) -> None:
        records = self.db.fetch_all_records()
        self.records_table.setRowCount(len(records))

        for row_index, record in enumerate(records):
            mortality_rate = self.db.mortality_rate(record["flock_size"], record["mortality"])
            fcr = self.db.feed_conversion_ratio(record["feed_used"], record["avg_weight"])

            values = [
                record["id"],
                record["date"],
                record["flock_size"],
                record["mortality"],
                record["feed_used"],
                record["avg_weight"],
                record["droppings_status"],
                record["disease_detected"],
                f"{mortality_rate:.2f}",
                f"{fcr:.2f}",
            ]

            for col_index, value in enumerate(values):
                self.records_table.setItem(row_index, col_index, QTableWidgetItem(str(value)))

        self.records_table.resizeColumnsToContents()

    def populate_form_from_row(self, row: int, _column: int) -> None:
        self.date_input.setText(self.records_table.item(row, 1).text())
        self.flock_size_input.setText(self.records_table.item(row, 2).text())
        self.mortality_input.setText(self.records_table.item(row, 3).text())
        self.feed_used_input.setText(self.records_table.item(row, 4).text())
        self.avg_weight_input.setText(self.records_table.item(row, 5).text())
        self.droppings_input.setText(self.records_table.item(row, 6).text())
        self.disease_input.setText(self.records_table.item(row, 7).text())

    def run_decision_engine(self) -> None:
        try:
            flock_size = int(self.flock_size_input.text() or "0")
            mortality = int(self.mortality_input.text() or "0")
            feed_used = float(self.feed_used_input.text() or "0")
            droppings = self.droppings_input.text().strip() or self.current_droppings_prediction

            mortality_rate = self.db.mortality_rate(flock_size, mortality)
            alerts = evaluate_management_rules(mortality_rate, droppings, feed_used, flock_size)

            self.alerts_list.clear()
            for msg in alerts:
                self.alerts_list.addItem(msg)
        except Exception as exc:
            QMessageBox.critical(self, "Decision Engine", str(exc))

    def generate_reports(self) -> None:
        try:
            records = self.db.fetch_all_records()
            if not records:
                QMessageBox.information(self, "Reports", "No records available for chart generation.")
                return

            outputs = generate_trend_charts(records, output_dir="poultry_ai/reports")
            lines = ["Charts generated:"] + [f"- {name}: {path}" for name, path in outputs.items()]
            self.reports_output.setText("\n".join(lines))

            if os.path.exists(outputs["mortality_trend"]):
                QMessageBox.information(self, "Reports", "Report charts created successfully.")
        except Exception as exc:
            QMessageBox.critical(self, "Reports", str(exc))

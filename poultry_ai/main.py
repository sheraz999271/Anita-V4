"""Application entry point for Poultry AI desktop software."""

import sys
from PyQt6.QtWidgets import QApplication

from ui.main_window import PoultryAIMainWindow


def main() -> None:
    """Boot and run the Qt application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Poultry AI Management")

    window = PoultryAIMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Drive Formatter Pro
--------------------
A professional, cross-platform-aware (Windows-focused) disk formatting
utility built with Python and PyQt6.

Entry point: run this file to launch the application.
    python main.py

Requires: PyQt6, psutil (optional, for non-Windows drive listing)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from ui.main_window import MainWindow


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Drive Formatter Pro")
    app.setOrganizationName("DriveFormatterPro")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

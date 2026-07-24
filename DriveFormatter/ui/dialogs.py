# -*- coding: utf-8 -*-
"""Dialog windows used across the application."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QCheckBox, QGridLayout, QSpinBox, QGroupBox, QTextEdit,
    QDialogButtonBox, QWidget, QFrame,
)

from i18n.translations import tr, LANGUAGES, LANGUAGE_DIRECTION
from ui.themes import THEME_NAMES


class ConfirmFormatDialog(QDialog):
    """Requires the user to type the drive letter to confirm a destructive format."""

    def __init__(self, lang: str, drive_letter: str, parent=None):
        super().__init__(parent)
        self.lang = lang
        self.drive_letter = drive_letter.rstrip("\\").rstrip(":") + ":"
        self.setWindowTitle(tr(lang, "confirm_title"))
        self.setMinimumWidth(420)
        self.setLayoutDirection(LANGUAGE_DIRECTION.get(lang, Qt.LayoutDirection.LeftToRight))

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        warn_icon = QLabel("⚠")
        warn_icon.setStyleSheet("font-size: 32px; color: #C42B1C;")
        warn_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(warn_icon)

        message = QLabel(tr(lang, "confirm_message", drive=self.drive_letter))
        message.setWordWrap(True)
        layout.addWidget(message)

        self.input = QLineEdit()
        self.input.setPlaceholderText(tr(lang, "confirm_placeholder"))
        self.input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.input)

        btn_row = QHBoxLayout()
        self.cancel_btn = QPushButton(tr(lang, "button_cancel"))
        self.cancel_btn.setProperty("flat", "true")
        self.cancel_btn.clicked.connect(self.reject)

        self.ok_btn = QPushButton(tr(lang, "button_format"))
        self.ok_btn.setProperty("danger", "true")
        self.ok_btn.setEnabled(False)
        self.ok_btn.clicked.connect(self.accept)

        btn_row.addWidget(self.cancel_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(self.ok_btn)
        layout.addLayout(btn_row)

    def _on_text_changed(self, text: str):
        self.ok_btn.setEnabled(text.strip().upper() == self.drive_letter.upper())

    @staticmethod
    def confirm(lang: str, drive_letter: str, parent=None) -> bool:
        dialog = ConfirmFormatDialog(lang, drive_letter, parent)
        return dialog.exec() == QDialog.DialogCode.Accepted


class SettingsDialog(QDialog):
    def __init__(self, lang: str, current_theme: str, settings_manager, parent=None):
        super().__init__(parent)
        self.lang = lang
        self.settings_manager = settings_manager
        self.selected_language = lang
        self.selected_theme = current_theme

        self.setWindowTitle(tr(lang, "settings_title"))
        self.setMinimumWidth(380)
        self.setLayoutDirection(LANGUAGE_DIRECTION.get(lang, Qt.LayoutDirection.LeftToRight))

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        grid = QGridLayout()
        grid.setVerticalSpacing(10)

        grid.addWidget(QLabel(tr(lang, "settings_language")), 0, 0)
        self.lang_combo = QComboBox()
        for code, name in LANGUAGES.items():
            self.lang_combo.addItem(name, code)
        idx = list(LANGUAGES.keys()).index(lang)
        self.lang_combo.setCurrentIndex(idx)
        grid.addWidget(self.lang_combo, 0, 1)

        grid.addWidget(QLabel(tr(lang, "settings_theme")), 1, 0)
        self.theme_combo = QComboBox()
        theme_keys = THEME_NAMES
        theme_labels = {
            "win11_light": tr(lang, "theme_win11_light"),
            "win11_dark": tr(lang, "theme_win11_dark"),
            "win11_default": tr(lang, "theme_win11_default"),
            "red": tr(lang, "theme_red"),
            "blue": tr(lang, "theme_blue"),
        }
        for key in theme_keys:
            self.theme_combo.addItem(theme_labels[key], key)
        self.theme_combo.setCurrentIndex(theme_keys.index(current_theme))
        grid.addWidget(self.theme_combo, 1, 1)

        layout.addLayout(grid)

        self.confirm_check = QCheckBox(tr(lang, "settings_confirm_required"))
        self.confirm_check.setChecked(self.settings_manager.require_confirmation)
        layout.addWidget(self.confirm_check)

        self.sound_check = QCheckBox(tr(lang, "settings_sound"))
        self.sound_check.setChecked(self.settings_manager.play_sound)
        layout.addWidget(self.sound_check)

        self.startup_check = QCheckBox(tr(lang, "settings_startup_scan"))
        self.startup_check.setChecked(self.settings_manager.startup_scan)
        layout.addWidget(self.startup_check)

        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self._on_accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _on_accept(self):
        self.selected_language = self.lang_combo.currentData()
        self.selected_theme = self.theme_combo.currentData()
        self.settings_manager.require_confirmation = self.confirm_check.isChecked()
        self.settings_manager.play_sound = self.sound_check.isChecked()
        self.settings_manager.startup_scan = self.startup_check.isChecked()
        self.accept()


class AboutDialog(QDialog):
    def __init__(self, lang: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr(lang, "about_title"))
        self.setMinimumWidth(380)
        self.setLayoutDirection(LANGUAGE_DIRECTION.get(lang, Qt.LayoutDirection.LeftToRight))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        icon = QLabel("💽")
        icon.setStyleSheet("font-size: 42px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        text = QLabel(tr(lang, "about_text"))
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text)

        close_btn = QPushButton(tr(lang, "button_close"))
        close_btn.setProperty("accent", "true")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class DiskInfoDialog(QDialog):
    def __init__(self, lang: str, drive_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr(lang, "action_disk_info"))
        self.setMinimumWidth(420)
        self.setLayoutDirection(LANGUAGE_DIRECTION.get(lang, Qt.LayoutDirection.LeftToRight))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        from core.drive_manager import format_bytes

        rows = [
            (tr(lang, "details_drive"), drive_info.letter),
            (tr(lang, "details_label"), drive_info.label or "-"),
            (tr(lang, "details_fs"), drive_info.filesystem or "-"),
            (tr(lang, "details_total"), format_bytes(drive_info.total_bytes)),
            (tr(lang, "details_used"), format_bytes(drive_info.used_bytes)),
            (tr(lang, "details_free"), format_bytes(drive_info.free_bytes)),
            (tr(lang, "details_type"), tr(lang, drive_info.drive_type_key)),
            (tr(lang, "details_serial"), drive_info.serial_number or "-"),
        ]

        grid = QGridLayout()
        grid.setVerticalSpacing(8)
        for i, (key, value) in enumerate(rows):
            key_label = QLabel(key)
            key_label.setProperty("subtext", "true")
            val_label = QLabel(str(value))
            val_label.setStyleSheet("font-weight: 600;")
            grid.addWidget(key_label, i, 0)
            grid.addWidget(val_label, i, 1)
        layout.addLayout(grid)

        close_btn = QPushButton(tr(lang, "button_close"))
        close_btn.setProperty("accent", "true")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class WipePassesDialog(QDialog):
    def __init__(self, lang: str, parent=None):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(tr(lang, "action_wipe"))
        self.setLayoutDirection(LANGUAGE_DIRECTION.get(lang, Qt.LayoutDirection.LeftToRight))
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        msg = QLabel(tr(lang, "wipe_confirm"))
        msg.setWordWrap(True)
        layout.addWidget(msg)

        row = QHBoxLayout()
        row.addWidget(QLabel(tr(lang, "wipe_passes")))
        self.passes_spin = QSpinBox()
        self.passes_spin.setRange(1, 7)
        self.passes_spin.setValue(1)
        row.addWidget(self.passes_spin)
        layout.addLayout(row)

        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def passes(self) -> int:
        return self.passes_spin.value()

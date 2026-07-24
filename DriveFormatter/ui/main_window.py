# -*- coding: utf-8 -*-
"""Main application window for Drive Formatter Pro."""

from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QActionGroup, QFont, QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QLineEdit, QComboBox, QCheckBox, QRadioButton, QButtonGroup, QGroupBox,
    QTextEdit, QProgressBar, QSplitter, QFrame, QToolBar, QStatusBar,
    QMessageBox, QFileDialog, QApplication, QSizePolicy,
)

from core.drive_manager import (
    list_drives, format_bytes, is_admin, relaunch_as_admin,
    DriveInfo, IS_WINDOWS,
)
from core.format_engine import FormatWorker, CheckDiskWorker, SecureWipeWorker, eject_drive
from core.settings_manager import SettingsManager
from i18n.translations import tr, LANGUAGES, LANGUAGE_DIRECTION, LANGUAGE_FONT
from ui.themes import build_stylesheet, THEME_NAMES
from ui.dialogs import (
    ConfirmFormatDialog, SettingsDialog, AboutDialog, DiskInfoDialog, WipePassesDialog,
)

FILESYSTEMS_BY_TYPE = {
    "removable": ["FAT32", "exFAT", "NTFS"],
    "fixed": ["NTFS", "exFAT", "FAT32", "ReFS"],
    "unknown": ["NTFS", "exFAT", "FAT32"],
    "network": ["NTFS"],
    "cdrom": [],
}

ALLOCATION_UNITS = ["default", "4096", "8192", "16384", "32768", "65536"]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        self.lang = self.settings.language
        self.theme = self.settings.theme
        self.drives: list[DriveInfo] = []
        self.selected_drive: DriveInfo | None = None
        self.active_worker = None

        self.setMinimumSize(1080, 680)
        self.resize(1180, 720)

        self._build_ui()
        self._apply_language(self.lang)
        self._apply_theme(self.theme)

        if self.settings.startup_scan:
            QTimer.singleShot(200, self.refresh_drives)

    # ------------------------------------------------------------------ UI BUILD

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self._build_menu_bar()
        self._build_toolbar()

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(16, 16, 16, 16)
        body_layout.setSpacing(16)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        body_layout.addWidget(splitter)

        root_layout.addWidget(body, 1)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel()
        self.status_bar.addWidget(self.status_label)
        self.admin_label = QLabel()
        self.status_bar.addPermanentWidget(self.admin_label)

    def _build_menu_bar(self):
        menu_bar = self.menuBar()

        self.file_menu = menu_bar.addMenu("")
        self.action_refresh = QAction(self)
        self.action_refresh.triggered.connect(self.refresh_drives)
        self.action_refresh.setShortcut("F5")
        self.file_menu.addAction(self.action_refresh)
        self.file_menu.addSeparator()
        self.action_exit = QAction(self)
        self.action_exit.triggered.connect(self.close)
        self.file_menu.addAction(self.action_exit)

        self.tools_menu = menu_bar.addMenu("")
        self.action_disk_info = QAction(self)
        self.action_disk_info.triggered.connect(self.show_disk_info)
        self.tools_menu.addAction(self.action_disk_info)

        self.action_check_disk = QAction(self)
        self.action_check_disk.triggered.connect(self.run_check_disk)
        self.tools_menu.addAction(self.action_check_disk)

        self.action_eject = QAction(self)
        self.action_eject.triggered.connect(self.run_eject)
        self.tools_menu.addAction(self.action_eject)

        self.action_wipe = QAction(self)
        self.action_wipe.triggered.connect(self.run_secure_wipe)
        self.tools_menu.addAction(self.action_wipe)

        self.tools_menu.addSeparator()
        self.action_settings = QAction(self)
        self.action_settings.triggered.connect(self.open_settings)
        self.tools_menu.addAction(self.action_settings)

        self.view_menu = menu_bar.addMenu("")
        self.language_menu = self.view_menu.addMenu("")
        self.language_group = QActionGroup(self)
        self.language_actions = {}
        for code, name in LANGUAGES.items():
            act = QAction(name, self, checkable=True)
            act.setChecked(code == self.lang)
            act.triggered.connect(lambda checked, c=code: self._apply_language(c))
            self.language_group.addAction(act)
            self.language_menu.addAction(act)
            self.language_actions[code] = act

        self.theme_menu = self.view_menu.addMenu("")
        self.theme_group = QActionGroup(self)
        self.theme_actions = {}
        for key in THEME_NAMES:
            act = QAction(key, self, checkable=True)
            act.setChecked(key == self.theme)
            act.triggered.connect(lambda checked, k=key: self._apply_theme(k))
            self.theme_group.addAction(act)
            self.theme_menu.addAction(act)
            self.theme_actions[key] = act

        self.help_menu = menu_bar.addMenu("")
        self.action_about = QAction(self)
        self.action_about.triggered.connect(self.show_about)
        self.help_menu.addAction(self.action_about)

    def _build_toolbar(self):
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(self.toolbar.iconSize())
        self.addToolBar(self.toolbar)

        self.toolbar_refresh_btn = QPushButton("⟳")
        self.toolbar_refresh_btn.setProperty("flat", "true")
        self.toolbar_refresh_btn.clicked.connect(self.refresh_drives)
        self.toolbar.addWidget(self.toolbar_refresh_btn)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(spacer)

        self.title_label = QLabel()
        self.title_label.setProperty("heading", "true")
        self.toolbar.addWidget(self.title_label)

        spacer2 = QWidget()
        spacer2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.toolbar.addWidget(spacer2)

    def _build_left_panel(self) -> QWidget:
        frame = QFrame()
        frame.setObjectName("CardFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self.drives_title = QLabel()
        self.drives_title.setProperty("heading", "true")
        layout.addWidget(self.drives_title)

        self.drives_table = QTableWidget(0, 6)
        self.drives_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.drives_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.drives_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.drives_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.drives_table.verticalHeader().setVisible(False)
        self.drives_table.setAlternatingRowColors(True)
        self.drives_table.itemSelectionChanged.connect(self._on_drive_selected)
        layout.addWidget(self.drives_table, 1)

        log_frame = QFrame()
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(0, 8, 0, 0)
        log_layout.setSpacing(6)

        log_header = QHBoxLayout()
        self.log_title = QLabel()
        self.log_title.setProperty("heading", "true")
        log_header.addWidget(self.log_title)
        log_header.addStretch(1)
        self.clear_log_btn = QPushButton("🗑")
        self.clear_log_btn.setProperty("flat", "true")
        self.clear_log_btn.clicked.connect(self.clear_log)
        log_header.addWidget(self.clear_log_btn)
        self.save_log_btn = QPushButton("💾")
        self.save_log_btn.setProperty("flat", "true")
        self.save_log_btn.clicked.connect(self.save_log)
        log_header.addWidget(self.save_log_btn)
        log_layout.addLayout(log_header)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFixedHeight(160)
        log_layout.addWidget(self.log_view)

        layout.addWidget(log_frame)
        return frame

    def _build_right_panel(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Details card
        self.details_frame = QFrame()
        self.details_frame.setObjectName("CardFrame")
        details_layout = QVBoxLayout(self.details_frame)
        details_layout.setContentsMargins(16, 16, 16, 16)
        details_layout.setSpacing(8)

        header_row = QHBoxLayout()
        self.details_title = QLabel()
        self.details_title.setProperty("heading", "true")
        header_row.addWidget(self.details_title)
        header_row.addStretch(1)
        self.system_badge = QLabel()
        self.system_badge.setProperty("badge_system", "true")
        self.system_badge.setVisible(False)
        header_row.addWidget(self.system_badge)
        details_layout.addLayout(header_row)

        self.details_grid_labels = {}
        rows = ["details_drive", "details_label", "details_fs", "details_total",
                "details_used", "details_free", "details_type", "details_serial"]
        for key in rows:
            row = QHBoxLayout()
            k_label = QLabel()
            k_label.setProperty("subtext", "true")
            k_label.setMinimumWidth(140)
            v_label = QLabel("-")
            v_label.setStyleSheet("font-weight: 600;")
            row.addWidget(k_label)
            row.addWidget(v_label, 1)
            details_layout.addLayout(row)
            self.details_grid_labels[key] = (k_label, v_label)

        self.usage_bar = QProgressBar()
        self.usage_bar.setRange(0, 100)
        self.usage_bar.setValue(0)
        details_layout.addWidget(self.usage_bar)

        layout.addWidget(self.details_frame)

        # Format options card
        self.format_frame = QFrame()
        self.format_frame.setObjectName("CardFrame")
        format_layout = QVBoxLayout(self.format_frame)
        format_layout.setContentsMargins(16, 16, 16, 16)
        format_layout.setSpacing(10)

        self.format_title = QLabel()
        self.format_title.setProperty("heading", "true")
        format_layout.addWidget(self.format_title)

        self.label_volume_label = QLabel()
        format_layout.addWidget(self.label_volume_label)
        self.volume_label_input = QLineEdit()
        self.volume_label_input.setMaxLength(32)
        format_layout.addWidget(self.volume_label_input)

        self.label_filesystem = QLabel()
        format_layout.addWidget(self.label_filesystem)
        self.filesystem_combo = QComboBox()
        format_layout.addWidget(self.filesystem_combo)

        self.label_allocation = QLabel()
        format_layout.addWidget(self.label_allocation)
        self.allocation_combo = QComboBox()
        for unit in ALLOCATION_UNITS:
            self.allocation_combo.addItem(unit, unit)
        format_layout.addWidget(self.allocation_combo)

        self.label_format_type = QLabel()
        format_layout.addWidget(self.label_format_type)
        radio_row = QHBoxLayout()
        self.radio_quick = QRadioButton()
        self.radio_full = QRadioButton()
        self.radio_quick.setChecked(True)
        self.format_type_group = QButtonGroup(self)
        self.format_type_group.addButton(self.radio_quick)
        self.format_type_group.addButton(self.radio_full)
        radio_row.addWidget(self.radio_quick)
        radio_row.addWidget(self.radio_full)
        format_layout.addLayout(radio_row)

        self.compression_check = QCheckBox()
        format_layout.addWidget(self.compression_check)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        format_layout.addWidget(self.progress_bar)

        btn_row = QHBoxLayout()
        self.format_btn = QPushButton()
        self.format_btn.setProperty("danger", "true")
        self.format_btn.clicked.connect(self.start_format)
        self.stop_btn = QPushButton()
        self.stop_btn.setVisible(False)
        self.stop_btn.clicked.connect(self.stop_operation)
        btn_row.addWidget(self.format_btn, 1)
        btn_row.addWidget(self.stop_btn)
        format_layout.addLayout(btn_row)

        layout.addWidget(self.format_frame)
        layout.addStretch(1)

        self._set_form_enabled(False)
        return container

    # ------------------------------------------------------------------ LANGUAGE / THEME

    def _apply_language(self, lang: str):
        self.lang = lang
        self.settings.language = lang
        direction = LANGUAGE_DIRECTION.get(lang, Qt.LayoutDirection.LeftToRight)
        QApplication.instance().setLayoutDirection(direction)
        self.setLayoutDirection(direction)

        font_family = LANGUAGE_FONT.get(lang, "Segoe UI")
        app_font = QFont(font_family, 10)
        QApplication.instance().setFont(app_font)

        self.setWindowTitle(tr(lang, "app_title"))
        self.title_label.setText(tr(lang, "app_title"))

        self.file_menu.setTitle(tr(lang, "menu_file"))
        self.action_refresh.setText(tr(lang, "action_refresh"))
        self.action_refresh.setToolTip(tr(lang, "tooltip_refresh"))
        self.action_exit.setText(tr(lang, "action_exit"))

        self.tools_menu.setTitle(tr(lang, "menu_tools"))
        self.action_disk_info.setText(tr(lang, "action_disk_info"))
        self.action_check_disk.setText(tr(lang, "action_check_disk"))
        self.action_eject.setText(tr(lang, "action_eject"))
        self.action_wipe.setText(tr(lang, "action_wipe"))
        self.action_settings.setText(tr(lang, "action_settings"))

        self.view_menu.setTitle(tr(lang, "menu_view"))
        self.language_menu.setTitle(tr(lang, "menu_language"))
        self.theme_menu.setTitle(tr(lang, "menu_theme"))
        for key, act in self.theme_actions.items():
            act.setText(tr(lang, f"theme_{key}"))

        self.help_menu.setTitle(tr(lang, "menu_help"))
        self.action_about.setText(tr(lang, "action_about"))

        for code, act in self.language_actions.items():
            act.setChecked(code == lang)

        self.drives_title.setText(tr(lang, "drives_panel_title"))
        self.log_title.setText(tr(lang, "log_panel_title"))
        self.details_title.setText(tr(lang, "details_panel_title"))
        self.system_badge.setText(tr(lang, "system_drive_badge"))

        self._set_table_headers()
        for key, (k_label, _) in self.details_grid_labels.items():
            k_label.setText(tr(lang, key))

        self.format_title.setText(tr(lang, "format_panel_title"))
        self.label_volume_label.setText(tr(lang, "label_volume_label"))
        self.label_filesystem.setText(tr(lang, "label_filesystem"))
        self.label_allocation.setText(tr(lang, "label_allocation"))
        self.label_format_type.setText(tr(lang, "label_format_type"))
        self.radio_quick.setText(tr(lang, "format_quick"))
        self.radio_full.setText(tr(lang, "format_full"))
        self.compression_check.setText(tr(lang, "checkbox_compression"))
        self.format_btn.setText(tr(lang, "button_format"))
        self.format_btn.setToolTip(tr(lang, "tooltip_format"))
        self.stop_btn.setText(tr(lang, "button_stop"))

        self.allocation_combo.setItemText(0, tr(lang, "allocation_default"))

        self.status_label.setText(tr(lang, "status_ready"))
        self.admin_label.setText(
            "✔ Admin" if is_admin() else "✖ " + tr(lang, "status_admin_required")
        )

        self._refresh_details_panel()
        self._populate_table()

    def _apply_theme(self, theme_key: str):
        self.theme = theme_key
        self.settings.theme = theme_key
        stylesheet = build_stylesheet(theme_key, LANGUAGE_FONT.get(self.lang, "Segoe UI"))
        QApplication.instance().setStyleSheet(stylesheet)
        for key, act in self.theme_actions.items():
            act.setChecked(key == theme_key)

    def _set_table_headers(self):
        headers = [
            tr(self.lang, "col_drive"),
            tr(self.lang, "col_label"),
            tr(self.lang, "col_filesystem"),
            tr(self.lang, "col_total"),
            tr(self.lang, "col_free"),
            tr(self.lang, "col_type"),
        ]
        self.drives_table.setHorizontalHeaderLabels(headers)

    # ------------------------------------------------------------------ DRIVE LOGIC

    def refresh_drives(self):
        self.status_label.setText(tr(self.lang, "status_scanning"))
        QApplication.processEvents()
        self.drives = list_drives()
        self._populate_table()
        self.status_label.setText(tr(self.lang, "status_ready"))
        self.log(f"{tr(self.lang, 'action_refresh')}: {len(self.drives)} drives found")

    def _populate_table(self):
        self.drives_table.setRowCount(0)
        for drive in self.drives:
            row = self.drives_table.rowCount()
            self.drives_table.insertRow(row)
            values = [
                drive.letter,
                drive.label or "-",
                drive.filesystem or "-",
                format_bytes(drive.total_bytes),
                format_bytes(drive.free_bytes),
                tr(self.lang, drive.drive_type_key),
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if drive.is_system and col == 0:
                    item.setForeground(Qt.GlobalColor.red)
                self.drives_table.setItem(row, col, item)

    def _on_drive_selected(self):
        rows = self.drives_table.selectionModel().selectedRows()
        if not rows:
            self.selected_drive = None
            self._set_form_enabled(False)
            self._refresh_details_panel()
            return
        idx = rows[0].row()
        if idx >= len(self.drives):
            return
        self.selected_drive = self.drives[idx]
        self._set_form_enabled(True)
        self._refresh_details_panel()
        self._populate_filesystem_options()
        self.volume_label_input.setText(self.selected_drive.label)

    def _populate_filesystem_options(self):
        self.filesystem_combo.clear()
        if not self.selected_drive:
            return
        options = FILESYSTEMS_BY_TYPE.get(self.selected_drive.drive_type_key, ["NTFS"])
        for fs in options:
            self.filesystem_combo.addItem(fs, fs)
        if self.selected_drive.filesystem:
            idx = self.filesystem_combo.findText(self.selected_drive.filesystem)
            if idx >= 0:
                self.filesystem_combo.setCurrentIndex(idx)

    def _refresh_details_panel(self):
        d = self.selected_drive
        if d is None:
            for key, (_, v_label) in self.details_grid_labels.items():
                v_label.setText("-")
            self.usage_bar.setValue(0)
            self.system_badge.setVisible(False)
            return

        self.details_grid_labels["details_drive"][1].setText(d.letter)
        self.details_grid_labels["details_label"][1].setText(d.label or "-")
        self.details_grid_labels["details_fs"][1].setText(d.filesystem or "-")
        self.details_grid_labels["details_total"][1].setText(format_bytes(d.total_bytes))
        self.details_grid_labels["details_used"][1].setText(format_bytes(d.used_bytes))
        self.details_grid_labels["details_free"][1].setText(format_bytes(d.free_bytes))
        self.details_grid_labels["details_type"][1].setText(tr(self.lang, d.drive_type_key))
        self.details_grid_labels["details_serial"][1].setText(d.serial_number or "-")
        self.usage_bar.setValue(int(d.used_percent))
        self.system_badge.setVisible(d.is_system)

    def _set_form_enabled(self, enabled: bool):
        for widget in [
            self.volume_label_input, self.filesystem_combo, self.allocation_combo,
            self.radio_quick, self.radio_full, self.compression_check, self.format_btn,
        ]:
            widget.setEnabled(enabled)

    # ------------------------------------------------------------------ LOGGING

    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_view.append(f"[{timestamp}] {message}")

    def clear_log(self):
        self.log_view.clear()

    def save_log(self):
        path, _ = QFileDialog.getSaveFileName(self, tr(self.lang, "action_save_log"),
                                               "drive_formatter_log.txt", "Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log_view.toPlainText())

    # ------------------------------------------------------------------ FORMAT FLOW

    def start_format(self):
        if not self.selected_drive:
            QMessageBox.warning(self, tr(self.lang, "confirm_title"),
                                 tr(self.lang, "error_no_selection"))
            return

        if self.selected_drive.is_system:
            QMessageBox.critical(self, tr(self.lang, "confirm_title"),
                                  tr(self.lang, "confirm_system_drive"))
            return

        if not IS_WINDOWS:
            QMessageBox.warning(self, tr(self.lang, "status_error"),
                                 tr(self.lang, "error_platform"))
            return

        if not is_admin():
            reply = QMessageBox.question(
                self, tr(self.lang, "status_admin_required"),
                tr(self.lang, "error_admin"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                relaunch_as_admin()
            return

        if self.settings.require_confirmation:
            confirmed = ConfirmFormatDialog.confirm(self.lang, self.selected_drive.letter, self)
            if not confirmed:
                self.status_label.setText(tr(self.lang, "status_cancelled"))
                return

        filesystem = self.filesystem_combo.currentData() or "NTFS"
        label = self.volume_label_input.text().strip()
        quick = self.radio_quick.isChecked()
        allocation = self.allocation_combo.currentData() or "default"

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.format_btn.setVisible(False)
        self.stop_btn.setVisible(True)
        self.status_label.setText(tr(self.lang, "status_formatting", drive=self.selected_drive.letter))

        self.active_worker = FormatWorker(
            self.selected_drive.letter, filesystem, label, quick, allocation,
            self.compression_check.isChecked(),
        )
        self.active_worker.progress.connect(self._on_format_progress)
        self.active_worker.log_message.connect(self.log)
        self.active_worker.finished_ok.connect(self._on_format_success)
        self.active_worker.failed.connect(self._on_format_failed)
        self.active_worker.start()

    def _on_format_progress(self, percent: int, status_key: str):
        self.progress_bar.setValue(percent)
        self.status_label.setText(tr(self.lang, status_key, percent=percent))

    def _on_format_success(self):
        self.progress_bar.setVisible(False)
        self.format_btn.setVisible(True)
        self.stop_btn.setVisible(False)
        self.status_label.setText(tr(self.lang, "status_done"))
        self.log(tr(self.lang, "status_done"))
        QMessageBox.information(
            self, tr(self.lang, "success_title"),
            tr(self.lang, "success_message", drive=self.selected_drive.letter),
        )
        if self.settings.play_sound:
            QApplication.beep()
        self.refresh_drives()

    def _on_format_failed(self, error: str):
        self.progress_bar.setVisible(False)
        self.format_btn.setVisible(True)
        self.stop_btn.setVisible(False)
        if error == "STOPPED":
            self.status_label.setText(tr(self.lang, "status_cancelled"))
            return
        if error == "PLATFORM_UNSUPPORTED":
            message = tr(self.lang, "error_platform")
        else:
            message = tr(self.lang, "error_format_failed", error=error)
        self.status_label.setText(tr(self.lang, "status_error"))
        self.log(message)
        QMessageBox.critical(self, tr(self.lang, "status_error"), message)

    def stop_operation(self):
        if self.active_worker and self.active_worker.isRunning():
            self.active_worker.request_stop()

    # ------------------------------------------------------------------ TOOLS

    def show_disk_info(self):
        if not self.selected_drive:
            QMessageBox.warning(self, tr(self.lang, "status_error"),
                                 tr(self.lang, "error_no_selection"))
            return
        DiskInfoDialog(self.lang, self.selected_drive, self).exec()

    def run_check_disk(self):
        if not self.selected_drive:
            QMessageBox.warning(self, tr(self.lang, "status_error"),
                                 tr(self.lang, "error_no_selection"))
            return
        if not IS_WINDOWS:
            QMessageBox.warning(self, tr(self.lang, "status_error"),
                                 tr(self.lang, "error_platform"))
            return
        self.status_label.setText(tr(self.lang, "checkdisk_running"))
        self.log(tr(self.lang, "checkdisk_running"))

        self.active_worker = CheckDiskWorker(self.selected_drive.letter)
        self.active_worker.log_message.connect(self.log)
        self.active_worker.finished_ok.connect(
            lambda: (self.status_label.setText(tr(self.lang, "checkdisk_done")),
                     self.log(tr(self.lang, "checkdisk_done")))
        )
        self.active_worker.failed.connect(
            lambda err: self.log(tr(self.lang, "error_format_failed", error=err))
        )
        self.active_worker.start()

    def run_eject(self):
        if not self.selected_drive:
            QMessageBox.warning(self, tr(self.lang, "status_error"),
                                 tr(self.lang, "error_no_selection"))
            return
        success, err = eject_drive(self.selected_drive.letter)
        if success:
            self.log(tr(self.lang, "eject_success"))
            self.status_label.setText(tr(self.lang, "eject_success"))
            self.refresh_drives()
        else:
            message = tr(self.lang, "eject_failed", error=err or "unknown")
            self.log(message)
            QMessageBox.warning(self, tr(self.lang, "status_error"), message)

    def run_secure_wipe(self):
        if not self.selected_drive:
            QMessageBox.warning(self, tr(self.lang, "status_error"),
                                 tr(self.lang, "error_no_selection"))
            return
        if self.selected_drive.is_system:
            QMessageBox.critical(self, tr(self.lang, "confirm_title"),
                                  tr(self.lang, "confirm_system_drive"))
            return

        dialog = WipePassesDialog(self.lang, self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return

        confirmed = ConfirmFormatDialog.confirm(self.lang, self.selected_drive.letter, self)
        if not confirmed:
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.format_btn.setVisible(False)
        self.stop_btn.setVisible(True)

        self.active_worker = SecureWipeWorker(self.selected_drive.letter, dialog.passes())
        self.active_worker.progress.connect(self._on_format_progress)
        self.active_worker.log_message.connect(self.log)
        self.active_worker.finished_ok.connect(self._on_format_success)
        self.active_worker.failed.connect(self._on_format_failed)
        self.active_worker.start()

    def open_settings(self):
        dialog = SettingsDialog(self.lang, self.theme, self.settings, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            if dialog.selected_language != self.lang:
                self._apply_language(dialog.selected_language)
            if dialog.selected_theme != self.theme:
                self._apply_theme(dialog.selected_theme)

    def show_about(self):
        AboutDialog(self.lang, self).exec()

    # ------------------------------------------------------------------ LIFECYCLE

    def closeEvent(self, event):
        if self.active_worker and self.active_worker.isRunning():
            reply = QMessageBox.question(
                self, tr(self.lang, "action_exit"),
                tr(self.lang, "status_formatting", drive=""),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            self.active_worker.request_stop()
        self.settings.sync()
        event.accept()

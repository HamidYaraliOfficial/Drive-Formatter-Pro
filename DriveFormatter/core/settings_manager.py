# -*- coding: utf-8 -*-
"""Persisted application settings using QSettings."""

from PyQt6.QtCore import QSettings

ORG_NAME = "DriveFormatterPro"
APP_NAME = "DriveFormatter"


class SettingsManager:
    def __init__(self):
        self._settings = QSettings(ORG_NAME, APP_NAME)

    @property
    def language(self) -> str:
        return self._settings.value("language", "en", type=str)

    @language.setter
    def language(self, value: str):
        self._settings.setValue("language", value)

    @property
    def theme(self) -> str:
        return self._settings.value("theme", "win11_light", type=str)

    @theme.setter
    def theme(self, value: str):
        self._settings.setValue("theme", value)

    @property
    def require_confirmation(self) -> bool:
        return self._settings.value("require_confirmation", True, type=bool)

    @require_confirmation.setter
    def require_confirmation(self, value: bool):
        self._settings.setValue("require_confirmation", value)

    @property
    def play_sound(self) -> bool:
        return self._settings.value("play_sound", True, type=bool)

    @play_sound.setter
    def play_sound(self, value: bool):
        self._settings.setValue("play_sound", value)

    @property
    def startup_scan(self) -> bool:
        return self._settings.value("startup_scan", True, type=bool)

    @startup_scan.setter
    def startup_scan(self, value: bool):
        self._settings.setValue("startup_scan", value)

    @property
    def window_geometry(self):
        return self._settings.value("window_geometry", None)

    @window_geometry.setter
    def window_geometry(self, value):
        self._settings.setValue("window_geometry", value)

    def sync(self):
        self._settings.sync()

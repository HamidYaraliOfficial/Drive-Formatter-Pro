# -*- coding: utf-8 -*-
"""
Theme definitions for Drive Formatter.
Provides Windows 11 styled Light / Dark / Default themes plus Red and Blue accent themes.
"""

THEME_NAMES = [
    "win11_light",
    "win11_dark",
    "win11_default",
    "red",
    "blue",
]

# Color palettes: (background, surface, surface2, border, text, subtext, accent, accent_hover,
#                   accent_pressed, danger, success, warning)
PALETTES = {
    "win11_light": dict(
        bg="#F3F3F3", surface="#FFFFFF", surface2="#F9F9F9", border="#E5E5E5",
        text="#1A1A1A", subtext="#5D5D5D", accent="#0067C0", accent_hover="#1975C8",
        accent_pressed="#005AA9", danger="#C42B1C", success="#107C10", warning="#9D5D00",
    ),
    "win11_dark": dict(
        bg="#202020", surface="#2C2C2C", surface2="#323232", border="#3D3D3D",
        text="#FFFFFF", subtext="#C5C5C5", accent="#4CC2FF", accent_hover="#65CBFF",
        accent_pressed="#2FB0F2", danger="#FF99A4", success="#6CCB5F", warning="#FCE100",
    ),
    "win11_default": dict(
        bg="#EDF3FB", surface="#FFFFFF", surface2="#F5F9FE", border="#D6E4F5",
        text="#0F1B2D", subtext="#4C5F77", accent="#005FB8", accent_hover="#0A6CC7",
        accent_pressed="#004E9A", danger="#C42B1C", success="#0F7B0F", warning="#9D5D00",
    ),
    "red": dict(
        bg="#231014", surface="#2E1319", surface2="#39171E", border="#4A1F27",
        text="#FDECEE", subtext="#E3B4BA", accent="#E23B4C", accent_hover="#F05463",
        accent_pressed="#C22B3A", danger="#FF6B6B", success="#4CC27A", warning="#FFC24C",
    ),
    "blue": dict(
        bg="#0E1A2B", surface="#132540", surface2="#183056", border="#20406C",
        text="#EAF2FF", subtext="#AFC6E6", accent="#2E8CFF", accent_hover="#4E9FFF",
        accent_pressed="#1F72D6", danger="#FF6B6B", success="#4CC27A", warning="#FFC24C",
    ),
}


def build_stylesheet(theme_key: str, base_font: str = "Segoe UI") -> str:
    p = PALETTES.get(theme_key, PALETTES["win11_light"])
    return f"""
    * {{
        font-family: "{base_font}";
        outline: none;
    }}
    QMainWindow, QDialog {{
        background-color: {p['bg']};
        color: {p['text']};
    }}
    QWidget {{
        background-color: transparent;
        color: {p['text']};
        selection-background-color: {p['accent']};
        selection-color: #FFFFFF;
    }}
    QLabel {{
        background: transparent;
        color: {p['text']};
    }}
    QLabel[subtext="true"] {{
        color: {p['subtext']};
    }}
    QLabel[heading="true"] {{
        font-size: 16px;
        font-weight: 600;
        color: {p['text']};
    }}
    QLabel[badge_system="true"] {{
        background-color: {p['danger']};
        color: #FFFFFF;
        border-radius: 8px;
        padding: 2px 8px;
        font-weight: 600;
        font-size: 11px;
    }}
    #CardFrame {{
        background-color: {p['surface']};
        border: 1px solid {p['border']};
        border-radius: 8px;
    }}
    #HeaderBar {{
        background-color: {p['surface']};
        border-bottom: 1px solid {p['border']};
    }}
    QMenuBar {{
        background-color: {p['surface']};
        color: {p['text']};
        border-bottom: 1px solid {p['border']};
        padding: 2px;
    }}
    QMenuBar::item {{
        background: transparent;
        padding: 6px 10px;
        border-radius: 4px;
    }}
    QMenuBar::item:selected {{
        background-color: {p['surface2']};
    }}
    QMenu {{
        background-color: {p['surface']};
        color: {p['text']};
        border: 1px solid {p['border']};
        border-radius: 8px;
        padding: 6px;
    }}
    QMenu::item {{
        padding: 6px 24px 6px 12px;
        border-radius: 4px;
    }}
    QMenu::item:selected {{
        background-color: {p['accent']};
        color: #FFFFFF;
    }}
    QMenu::separator {{
        height: 1px;
        background: {p['border']};
        margin: 6px 4px;
    }}
    QStatusBar {{
        background-color: {p['surface']};
        color: {p['subtext']};
        border-top: 1px solid {p['border']};
    }}
    QToolBar {{
        background-color: {p['surface']};
        border-bottom: 1px solid {p['border']};
        spacing: 6px;
        padding: 4px;
    }}
    QPushButton {{
        background-color: {p['surface2']};
        color: {p['text']};
        border: 1px solid {p['border']};
        border-radius: 6px;
        padding: 8px 16px;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background-color: {p['border']};
    }}
    QPushButton:pressed {{
        background-color: {p['border']};
    }}
    QPushButton:disabled {{
        color: {p['subtext']};
        background-color: {p['surface2']};
    }}
    QPushButton[accent="true"] {{
        background-color: {p['accent']};
        color: #FFFFFF;
        border: none;
        font-weight: 600;
    }}
    QPushButton[accent="true"]:hover {{
        background-color: {p['accent_hover']};
    }}
    QPushButton[accent="true"]:pressed {{
        background-color: {p['accent_pressed']};
    }}
    QPushButton[danger="true"] {{
        background-color: {p['danger']};
        color: #FFFFFF;
        border: none;
        font-weight: 600;
    }}
    QPushButton[flat="true"] {{
        background: transparent;
        border: none;
    }}
    QPushButton[flat="true"]:hover {{
        background-color: {p['surface2']};
    }}
    QLineEdit, QComboBox, QSpinBox {{
        background-color: {p['surface']};
        color: {p['text']};
        border: 1px solid {p['border']};
        border-radius: 6px;
        padding: 6px 8px;
        min-height: 20px;
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 1px solid {p['accent']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {p['surface']};
        color: {p['text']};
        border: 1px solid {p['border']};
        selection-background-color: {p['accent']};
        selection-color: #FFFFFF;
        outline: none;
    }}
    QTableWidget {{
        background-color: {p['surface']};
        alternate-background-color: {p['surface2']};
        gridline-color: {p['border']};
        border: 1px solid {p['border']};
        border-radius: 8px;
        color: {p['text']};
    }}
    QTableWidget::item {{
        padding: 6px;
    }}
    QTableWidget::item:selected {{
        background-color: {p['accent']};
        color: #FFFFFF;
    }}
    QHeaderView::section {{
        background-color: {p['surface2']};
        color: {p['subtext']};
        padding: 8px;
        border: none;
        border-bottom: 1px solid {p['border']};
        font-weight: 600;
    }}
    QTextEdit, QPlainTextEdit {{
        background-color: {p['surface']};
        color: {p['text']};
        border: 1px solid {p['border']};
        border-radius: 8px;
        padding: 6px;
        font-family: Consolas, monospace;
    }}
    QProgressBar {{
        background-color: {p['surface2']};
        border: 1px solid {p['border']};
        border-radius: 6px;
        text-align: center;
        color: {p['text']};
        height: 18px;
    }}
    QProgressBar::chunk {{
        background-color: {p['accent']};
        border-radius: 5px;
    }}
    QCheckBox, QRadioButton {{
        color: {p['text']};
        spacing: 8px;
    }}
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid {p['border']};
        border-radius: 4px;
        background: {p['surface']};
    }}
    QRadioButton::indicator {{
        border-radius: 8px;
    }}
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
        background-color: {p['accent']};
        border: 1px solid {p['accent']};
    }}
    QGroupBox {{
        border: 1px solid {p['border']};
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 12px;
        font-weight: 600;
        color: {p['text']};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 6px;
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: {p['border']};
        border-radius: 5px;
        min-height: 24px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {p['subtext']};
    }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 10px;
    }}
    QScrollBar::handle:horizontal {{
        background: {p['border']};
        border-radius: 5px;
        min-width: 24px;
    }}
    QScrollBar::add-line, QScrollBar::sub-line {{
        width: 0; height: 0;
    }}
    QSplitter::handle {{
        background: {p['border']};
    }}
    QTabWidget::pane {{
        border: 1px solid {p['border']};
        border-radius: 8px;
        background: {p['surface']};
    }}
    QTabBar::tab {{
        background: transparent;
        color: {p['subtext']};
        padding: 8px 16px;
        border-radius: 6px;
        margin: 4px 2px;
    }}
    QTabBar::tab:selected {{
        background: {p['surface2']};
        color: {p['text']};
        font-weight: 600;
    }}
    QToolTip {{
        background-color: {p['surface2']};
        color: {p['text']};
        border: 1px solid {p['border']};
        padding: 4px 8px;
        border-radius: 4px;
    }}
    """


def accent_color(theme_key: str) -> str:
    return PALETTES.get(theme_key, PALETTES["win11_light"])["accent"]


def danger_color(theme_key: str) -> str:
    return PALETTES.get(theme_key, PALETTES["win11_light"])["danger"]


def success_color(theme_key: str) -> str:
    return PALETTES.get(theme_key, PALETTES["win11_light"])["success"]

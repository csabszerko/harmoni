"""A deliberately small, black-and-charcoal visual system for Harmoni."""

COLORS = {
    "canvas": "#0D0D0F", "surface": "#17171A", "surface_hover": "#202024",
    "input": "#101012", "border": "#303036", "border_strong": "#4A4A52",
    "text": "#F2F2F4", "muted": "#9999A3", "subtle": "#6F6F79",
    "accent": "#E6E6EA", "accent_text": "#121214", "danger": "#DA7070",
}

DARK_THEME = f"""
/* Foundation: child widgets remain transparent unless they are a defined surface. */
QMainWindow, QWidget#appRoot, QStackedWidget, QScrollArea::viewport {{
    background: {COLORS['canvas']};
}}
QWidget {{
    color: {COLORS['text']};
    background: transparent;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 14px;
}}

/* Navigation */
QFrame#sidebar {{ background: #09090A; border-right: 1px solid {COLORS['border']}; }}
QLabel#brand {{ color: {COLORS['text']}; font-size: 26px; font-weight: 700; letter-spacing: -0.8px; }}
QLabel#brandTagline, QLabel#subtitle, QLabel#muted, QLabel#settingDescription {{ color: {COLORS['muted']}; }}
QLabel#queueSummary {{ background: {COLORS['surface']}; color: {COLORS['muted']}; border: 1px solid {COLORS['border']}; border-radius: 10px; padding: 13px; font-size: 12px; }}
QPushButton#navigation {{ background: transparent; border: none; border-radius: 8px; color: {COLORS['muted']}; min-width: 0; padding: 12px 14px; text-align: left; font-weight: 600; }}
QPushButton#navigation:hover {{ background: {COLORS['surface_hover']}; color: {COLORS['text']}; }}
QPushButton#navigation:checked {{ background: {COLORS['surface']}; color: {COLORS['text']}; }}

/* Content surfaces */
QLabel#title {{ font-size: 30px; font-weight: 700; letter-spacing: -0.8px; }}
QLabel#section {{ font-size: 15px; font-weight: 700; }}
QLabel#settingTitle {{ font-size: 14px; font-weight: 650; }}
QFrame#card, QFrame#settingsSection, QGroupBox {{ background: {COLORS['surface']}; border: 1px solid {COLORS['border']}; border-radius: 12px; }}
QFrame#settingRow {{ background: transparent; border-bottom: 1px solid {COLORS['border']}; }}
QFrame#settingRow[lastRow="true"] {{ border-bottom: none; }}
QFrame#cardAccent {{ background: {COLORS['surface']}; border: 1px solid {COLORS['border']}; border-radius: 12px; }}
QFrame#dropZone {{ background: {COLORS['surface']}; border: 1px dashed {COLORS['border_strong']}; border-radius: 14px; }}
QFrame#dropZoneActive {{ background: {COLORS['surface_hover']}; border: 1px dashed {COLORS['accent']}; border-radius: 14px; }}

/* Controls */
QPushButton {{ background: {COLORS['accent']}; border: 1px solid {COLORS['accent']}; border-radius: 7px; color: {COLORS['accent_text']}; font-weight: 700; padding: 9px 15px; min-width: 88px; }}
QPushButton:hover {{ background: #FFFFFF; border-color: #FFFFFF; }}
QPushButton:disabled {{ background: #2A2A2F; border-color: #2A2A2F; color: {COLORS['subtle']}; }}
QPushButton#secondary {{ background: {COLORS['input']}; border-color: {COLORS['border_strong']}; color: {COLORS['text']}; }}
QPushButton#secondary:hover {{ background: {COLORS['surface_hover']}; border-color: #62626B; }}
QPushButton#danger {{ background: {COLORS['danger']}; border-color: {COLORS['danger']}; color: #241010; }}
QLineEdit, QTextEdit, QComboBox, QSpinBox {{ background: {COLORS['input']}; border: 1px solid {COLORS['border_strong']}; border-radius: 7px; color: {COLORS['text']}; min-height: 21px; padding: 8px 10px; }}
QLineEdit:hover, QTextEdit:hover, QComboBox:hover, QSpinBox:hover {{ border-color: #62626B; }}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{ border: 1px solid {COLORS['accent']}; }}
QLineEdit::placeholder {{ color: {COLORS['subtle']}; }}
QComboBox::drop-down, QSpinBox::up-button, QSpinBox::down-button {{ border: none; width: 26px; }}
QComboBox QAbstractItemView {{ background: {COLORS['surface']}; color: {COLORS['text']}; border: 1px solid {COLORS['border_strong']}; selection-background-color: {COLORS['surface_hover']}; }}
QCheckBox {{ color: {COLORS['muted']}; min-width: 58px; spacing: 8px; }}
QCheckBox::indicator {{ width: 18px; height: 18px; border: 1px solid {COLORS['border_strong']}; border-radius: 5px; background: {COLORS['input']}; }}
QCheckBox::indicator:checked {{ background: {COLORS['accent']}; border-color: {COLORS['accent']}; }}

/* Queue */
QTableWidget {{ background: {COLORS['surface']}; border: 1px solid {COLORS['border']}; border-radius: 12px; gridline-color: transparent; selection-background-color: {COLORS['surface_hover']}; }}
QTableWidget::item {{ padding: 10px 8px; background: transparent; }}
QHeaderView::section {{ background: {COLORS['surface']}; border: none; border-bottom: 1px solid {COLORS['border']}; color: {COLORS['muted']}; font-weight: 700; padding: 10px 8px; }}
QProgressBar {{ background: #2A2A2F; border: none; border-radius: 4px; }}
QProgressBar::chunk {{ background: {COLORS['accent']}; border-radius: 4px; }}
"""


def get_stylesheet() -> str:
    return DARK_THEME

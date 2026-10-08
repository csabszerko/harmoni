"""A consistent, compact settings screen."""

import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFileDialog, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QScrollArea, QSpinBox,
    QVBoxLayout, QWidget,
)

from config import save_config, validate_config


class SettingRow(QFrame):
    """One predictable settings interaction: context on the left, control on the right."""

    def __init__(self, title: str, description: str, control: QWidget, *, last=False, parent=None):
        super().__init__(parent)
        self.setObjectName("settingRow")
        self.setProperty("lastRow", last)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(24)

        text = QVBoxLayout()
        text.setSpacing(3)
        heading = QLabel(title)
        heading.setObjectName("settingTitle")
        text.addWidget(heading)
        detail = QLabel(description)
        detail.setObjectName("settingDescription")
        detail.setWordWrap(True)
        text.addWidget(detail)
        layout.addLayout(text, 1)

        control.setMinimumWidth(240)
        layout.addWidget(control, 0, Qt.AlignVCenter)


class DownloadSettingsView(QWidget):
    """Edit only the settings used by the import and download workflow."""

    config_saved = Signal()

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self._setup_ui()
        self._load_values()

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(scroll)

        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(48, 40, 48, 40)
        layout.setSpacing(18)

        title = QLabel("Settings")
        title.setObjectName("title")
        layout.addWidget(title)
        description = QLabel("Choose where downloads go and how Harmoni prepares your files.")
        description.setObjectName("subtitle")
        layout.addWidget(description)
        layout.addSpacing(12)

        layout.addWidget(self._download_section())
        layout.addWidget(self._metadata_section())
        layout.addWidget(self._advanced_section())
        layout.addStretch()

        self.save_button = QPushButton("Save changes")
        self.save_button.setFixedWidth(150)
        self.save_button.clicked.connect(self._save)
        layout.addWidget(self.save_button)
        scroll.setWidget(page)

    def _section(self, title: str, rows: list[SettingRow]) -> QFrame:
        section = QFrame()
        section.setObjectName("settingsSection")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        heading = QLabel(title)
        heading.setObjectName("section")
        heading.setContentsMargins(20, 16, 20, 12)
        layout.addWidget(heading)
        for row in rows:
            layout.addWidget(row)
        return section

    def _download_section(self) -> QFrame:
        self.output_dir_input = QLineEdit()
        choose_folder = QPushButton("Choose")
        choose_folder.setObjectName("secondary")
        choose_folder.setFixedWidth(88)
        choose_folder.clicked.connect(self._choose_output_dir)
        destination = QWidget()
        destination_layout = QHBoxLayout(destination)
        destination_layout.setContentsMargins(0, 0, 0, 0)
        destination_layout.setSpacing(8)
        destination_layout.addWidget(self.output_dir_input, 1)
        destination_layout.addWidget(choose_folder)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp3", "m4a", "flac", "aac", "ogg", "wav"])
        self.parallel_spin = QSpinBox()
        self.parallel_spin.setRange(1, 8)

        return self._section("Downloads", [
            SettingRow("Default download folder", "Used when a download does not have a folder selected.", destination),
            SettingRow("Audio format", "The output format for new downloads.", self.format_combo),
            SettingRow("Parallel downloads", "Number of tracks to process at the same time.", self.parallel_spin, last=True),
        ])

    def _metadata_section(self) -> QFrame:
        self.metadata_check = QCheckBox("On")
        self.musicbrainz_check = QCheckBox("On")
        return self._section("Metadata", [
            SettingRow("Embed file metadata", "Write artist, album, genre, BPM, and other available import data.", self.metadata_check),
            SettingRow("Fill missing release details", "Use MusicBrainz only when the CSV does not contain album or release-date data.", self.musicbrainz_check, last=True),
        ])

    def _advanced_section(self) -> QFrame:
        self.ytdlp_path_input = QLineEdit()
        self.ytdlp_path_input.setPlaceholderText("Auto-detect")
        self.ffmpeg_path_input = QLineEdit()
        self.ffmpeg_path_input.setPlaceholderText("Auto-detect")
        self.ytdlp_args_input = QLineEdit()
        self.ytdlp_args_input.setPlaceholderText("Optional arguments")
        return self._section("Advanced", [
            SettingRow("yt-dlp location", "Leave blank to use the installed command.", self.ytdlp_path_input),
            SettingRow("FFmpeg location", "Leave blank to use the installed command.", self.ffmpeg_path_input),
            SettingRow("Extra yt-dlp arguments", "Only use this when you need custom downloader behaviour.", self.ytdlp_args_input, last=True),
        ])

    def _load_values(self) -> None:
        self.output_dir_input.setText(self.config.get("output_dir", "music"))
        self.format_combo.setCurrentText(self.config.get("audio_format", "mp3"))
        self.parallel_spin.setValue(self.config.get("parallel_downloads", 3))
        self.metadata_check.setChecked(self.config.get("enable_metadata_embedding", True))
        self.musicbrainz_check.setChecked(self.config.get("enable_musicbrainz_lookup", True))
        self.ytdlp_path_input.setText(self.config.get("ytdlp_path", ""))
        self.ffmpeg_path_input.setText(self.config.get("ffmpeg_path", ""))
        self.ytdlp_args_input.setText(self.config.get("ytdlp_extra_args", ""))

    def _choose_output_dir(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Choose default download folder", self.output_dir_input.text())
        if folder:
            self.output_dir_input.setText(folder)

    def _save(self) -> None:
        updated = {
            **self.config,
            "output_dir": self.output_dir_input.text().strip() or "music",
            "audio_format": self.format_combo.currentText(),
            "parallel_downloads": self.parallel_spin.value(),
            "enable_metadata_embedding": self.metadata_check.isChecked(),
            "enable_musicbrainz_lookup": self.musicbrainz_check.isChecked(),
            "ytdlp_path": self.ytdlp_path_input.text().strip(),
            "ffmpeg_path": self.ffmpeg_path_input.text().strip(),
            "ytdlp_extra_args": self.ytdlp_args_input.text().strip(),
        }
        valid, errors = validate_config(updated)
        if not valid:
            QMessageBox.warning(self, "Invalid settings", "\n".join(errors))
            return
        try:
            os.makedirs(updated["output_dir"], exist_ok=True)
            save_config(updated)
        except OSError as exc:
            QMessageBox.critical(self, "Could not save settings", str(exc))
            return
        self.config = updated
        self.config_saved.emit()
        QMessageBox.information(self, "Settings saved", "Your changes have been saved.")

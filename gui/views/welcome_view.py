"""Welcome view with quick start guide and Exportify import."""

import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal

from gui.workers.download_queue import DownloadQueue
from utils.loaders import parse_exportify_csv_for_queue


class DropZone(QFrame):
    """Drop zone widget for Exportify CSV files."""

    files_dropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(180)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(40, 30, 40, 30)

        # Upload icon using text
        icon = QLabel("+")
        icon.setStyleSheet("""
            font-size: 48px;
            font-weight: 300;
            color: #A4A4AC;
            background: transparent;
        """)
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)

        title = QLabel("Drop your Exportify CSV file here")
        title.setObjectName("section")
        title.setStyleSheet("font-size: 16px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        hint = QLabel("or click anywhere in this box to browse")
        hint.setObjectName("muted")
        hint.setStyleSheet("font-size: 13px;")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.csv'):
                    event.acceptProposedAction()
                    self.setObjectName("dropZoneActive")
                    self.style().unpolish(self)
                    self.style().polish(self)
                    return
        event.ignore()

    def dragLeaveEvent(self, event):
        self.setObjectName("dropZone")
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event):
        self.setObjectName("dropZone")
        self.style().unpolish(self)
        self.style().polish(self)

        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.csv'):
                files.append(file_path)

        if files:
            self.files_dropped.emit(files)
            event.acceptProposedAction()
        else:
            event.ignore()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            from PySide6.QtWidgets import QFileDialog
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Select Exportify CSV Files",
                "",
                "CSV Files (*.csv)"
            )
            if files:
                self.files_dropped.emit(files)


class WelcomeView(QWidget):
    """Welcome screen with quick start instructions and Exportify import."""

    navigate_to = Signal(str)

    def __init__(self, config: dict, download_queue: DownloadQueue = None, parent=None):
        super().__init__(parent)
        self.config = config
        self.download_queue = download_queue
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(24)

        title = QLabel("Import an Exportify playlist")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Drop a CSV exported from Exportify, review the queue, then start downloading.")
        subtitle.setObjectName("subtitle")
        link_layout = QHBoxLayout()
        exportify_btn = QPushButton("Open exportify.net")
        exportify_btn.setObjectName("secondary")
        exportify_btn.clicked.connect(self._open_exportify)
        link_layout.addWidget(exportify_btn)
        link_layout.addStretch()
        layout.addLayout(link_layout)

        self.drop_zone = DropZone()
        self.drop_zone.files_dropped.connect(self._handle_dropped_files)
        layout.addWidget(self.drop_zone)

        hint = QLabel("After import, select Download queue in the sidebar to begin.")
        hint.setObjectName("muted")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)
        layout.addStretch()

        scroll.setWidget(scroll_widget)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _open_exportify(self):
        """Open Exportify website in browser."""
        import webbrowser
        webbrowser.open("https://exportify.net")

    def _handle_dropped_files(self, files: list):
        if not self.download_queue:
            QMessageBox.warning(self, "Error", "Download queue not available")
            return

        total_tracks = []

        for file_path in files:
            try:
                tracks = self._parse_exportify_csv(file_path)
                if tracks:
                    total_tracks.extend(tracks)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Import Error",
                    f"Failed to parse {os.path.basename(file_path)}:\n{str(e)}"
                )

        if not total_tracks:
            QMessageBox.information(
                self,
                "No Tracks Found",
                "No valid tracks were found in the dropped files.\n\n"
                "Make sure you're using a CSV file exported from Exportify."
            )
            return

        reply = QMessageBox.question(
            self,
            "Import Tracks",
            f"Found {len(total_tracks)} tracks.\n\nAdd them to the download queue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            from PySide6.QtWidgets import QFileDialog

            destination = QFileDialog.getExistingDirectory(
                self,
                "Choose where to save the playlist",
                self.config.get("output_dir", "music"),
            )
            if not destination:
                return

            queued_count = self._add_tracks_to_queue(total_tracks, destination)
            skipped_count = len(total_tracks) - queued_count
            duplicate_message = f"\nSkipped {skipped_count} duplicate track(s)." if skipped_count else ""
            QMessageBox.information(
                self,
                "Import Complete",
                f"Added {queued_count} tracks to the queue.{duplicate_message}\n\nEach playlist will be saved in "
                f"its own folder inside:\n{destination}\n\n"
                "Go to Downloads to start downloading."
            )
            self.navigate_to.emit("downloads")

    def _parse_exportify_csv(self, file_path: str) -> list:
        return parse_exportify_csv_for_queue(file_path)

    def _add_tracks_to_queue(self, tracks: list, destination: str):
        if not self.download_queue:
            return 0

        queued_count = 0
        for track_data in tracks:
            playlist = track_data.get('playlist', '')
            # CSV names are external input; preserve the name while preventing it
            # from escaping the destination directory.
            folder_name = os.path.basename(playlist.replace("\\", "/")).strip() or "Import"
            item = self.download_queue.add_item(
                artist=track_data['artist'],
                track=track_data['track'],
                album=track_data.get('album', ''),
                playlist=playlist,
                output_dir=os.path.join(destination, folder_name),
                metadata=track_data,
            )
            if item:
                queued_count += 1
        return queued_count

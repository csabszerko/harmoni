"""The small, task-focused application shell."""

from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget,
    QVBoxLayout, QWidget,
)

from gui.views.download_settings_view import DownloadSettingsView
from gui.views.downloads_view import DownloadsView
from gui.views.welcome_view import WelcomeView
from gui.workers.download_queue import DownloadQueue


class NavigationButton(QPushButton):
    """A sidebar item that carries the destination view index."""

    def __init__(self, label: str, index: int, parent=None):
        super().__init__(label, parent)
        self.index = index
        self.setCheckable(True)
        self.setObjectName("navigation")


class MainWindow(QMainWindow):
    """A concise shell for import, queue, and download preferences."""

    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.download_queue = DownloadQueue()
        self.navigation_buttons: list[NavigationButton] = []

        self.setWindowTitle("Harmoni")
        self.setMinimumSize(900, 620)
        self.resize(1180, 760)
        self._setup_ui()
        self._connect_signals()
        self._set_current_view(0)

    def _setup_ui(self) -> None:
        root = QWidget()
        root.setObjectName("appRoot")
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(236)
        self.sidebar_layout = QVBoxLayout(sidebar)
        self.sidebar_layout.setContentsMargins(18, 28, 18, 20)
        self.sidebar_layout.setSpacing(8)

        brand = QLabel("Harmoni")
        brand.setObjectName("brand")
        self.sidebar_layout.addWidget(brand)
        tagline = QLabel("Your music, organized.")
        tagline.setObjectName("brandTagline")
        self.sidebar_layout.addWidget(tagline)
        self.sidebar_layout.addSpacing(32)

        self._add_navigation_button("Import playlist", 0)
        self.queue_button = self._add_navigation_button("Download queue", 1)
        self._add_navigation_button("Settings", 2)
        self.sidebar_layout.addStretch()

        self.queue_summary = QLabel("Queue is empty")
        self.queue_summary.setObjectName("queueSummary")
        self.queue_summary.setWordWrap(True)
        self.sidebar_layout.addWidget(self.queue_summary)
        layout.addWidget(sidebar)

        self.view_stack = QStackedWidget()
        self.welcome_view = WelcomeView(self.config, self.download_queue)
        self.downloads_view = DownloadsView(self.config, self.download_queue)
        self.settings_view = DownloadSettingsView(self.config)
        self.view_stack.addWidget(self.welcome_view)
        self.view_stack.addWidget(self.downloads_view)
        self.view_stack.addWidget(self.settings_view)
        layout.addWidget(self.view_stack, 1)

    def _add_navigation_button(self, label: str, index: int) -> NavigationButton:
        button = NavigationButton(label, index, self)
        button.clicked.connect(lambda: self._set_current_view(index))
        self.navigation_buttons.append(button)
        self.sidebar_layout.addWidget(button)
        return button

    def _connect_signals(self) -> None:
        self.download_queue.queue_updated.connect(self._update_queue_summary)
        self.welcome_view.navigate_to.connect(self._navigate_to_view)
        self.settings_view.config_saved.connect(self._on_config_saved)

    def _set_current_view(self, index: int) -> None:
        self.view_stack.setCurrentIndex(index)
        for button in self.navigation_buttons:
            button.setChecked(button.index == index)

    def _navigate_to_view(self, name: str) -> None:
        destinations = {"import": 0, "downloads": 1, "settings": 2}
        if name in destinations:
            self._set_current_view(destinations[name])

    def _update_queue_summary(self, pending: int) -> None:
        total = len(self.download_queue.items)
        if not total:
            self.queue_summary.setText("Queue is empty")
        elif pending:
            self.queue_summary.setText(f"{pending} track{'s' if pending != 1 else ''} ready to download")
        else:
            self.queue_summary.setText("All queued tracks are finished")
        self.queue_button.setText(f"Download queue{f'  {pending}' if pending else ''}")

    def _on_config_saved(self) -> None:
        self.config = self.settings_view.config
        self.welcome_view.config = self.config
        self.downloads_view.config = self.config

    def get_download_queue(self) -> DownloadQueue:
        return self.download_queue

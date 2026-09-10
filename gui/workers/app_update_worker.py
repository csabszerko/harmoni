"""Background worker that checks GitHub for a newer HARMONI release."""

from PySide6.QtCore import QThread, Signal

from tools.app_update_checker import check_app_update


class AppUpdateCheckWorker(QThread):
    """Runs the GitHub release check off the UI thread."""

    update_available = Signal(dict)  # emitted only if a newer release exists

    def run(self):
        info = check_app_update()
        if info and info.get("update_available"):
            self.update_available.emit(info)

"""yt-dlp installer worker for downloading the standalone binary."""

import os
import sys
import stat
import shutil
import tempfile
from urllib.request import urlopen, Request
from urllib.error import URLError

from PySide6.QtCore import QThread, Signal


# yt-dlp standalone binary URLs from GitHub releases
YTDLP_URLS = {
    "win32": "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
    "darwin": "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos",
    "linux": "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux",
}


class YtdlpInstallerWorker(QThread):
    """Worker thread for downloading and installing the yt-dlp binary."""

    progress = Signal(int, str)
    finished = Signal(bool, str)

    def __init__(self, install_dir: str = None, dest_path: str = None, parent=None):
        super().__init__(parent)
        self._cancelled = False

        if dest_path:
            # Update an existing standalone binary in place, wherever it lives.
            self.install_dir = os.path.dirname(dest_path)
        elif install_dir is None:
            if getattr(sys, 'frozen', False) and sys.platform == "darwin":
                # macOS .app bundle: use user-writable location
                self.install_dir = os.path.join(
                    os.path.expanduser("~/Library/Application Support/HARMONI"), "bin"
                )
            elif getattr(sys, 'frozen', False):
                # Windows/Linux frozen: install next to the executable
                self.install_dir = os.path.join(os.path.dirname(sys.executable), "bin")
            else:
                # Dev mode: install in project_root/bin
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                self.install_dir = os.path.join(project_root, "bin")
        else:
            self.install_dir = install_dir

        self.dest_path = dest_path

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            platform = "darwin" if sys.platform == "darwin" else sys.platform
            url = YTDLP_URLS.get(platform)
            if not url:
                self.finished.emit(False, f"No yt-dlp download available for {sys.platform}")
                return

            self.progress.emit(0, "Preparing download...")

            binary_name = "yt-dlp.exe" if sys.platform == "win32" else "yt-dlp"
            dest_path = self.dest_path or os.path.join(self.install_dir, binary_name)

            temp_dir = tempfile.mkdtemp()
            temp_path = os.path.join(temp_dir, binary_name)

            try:
                self.progress.emit(5, "Connecting...")

                request = Request(url, headers={"User-Agent": "HARMONI/1.0"})
                response = urlopen(request, timeout=30)

                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0
                block_size = 256 * 1024  # 256KB blocks

                self.progress.emit(10, "Downloading yt-dlp...")

                with open(temp_path, "wb") as f:
                    while True:
                        if self._cancelled:
                            self.finished.emit(False, "Download cancelled")
                            return

                        block = response.read(block_size)
                        if not block:
                            break

                        f.write(block)
                        downloaded += len(block)

                        if total_size > 0:
                            percent = int(10 + (downloaded / total_size) * 70)
                            size_mb = downloaded / (1024 * 1024)
                            total_mb = total_size / (1024 * 1024)
                            self.progress.emit(percent, f"Downloading... {size_mb:.1f} / {total_mb:.1f} MB")

                self.progress.emit(85, "Installing...")

                # Make executable on Unix
                if sys.platform != "win32":
                    os.chmod(temp_path, os.stat(temp_path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

                # Move to install dir
                os.makedirs(self.install_dir, exist_ok=True)
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                shutil.move(temp_path, dest_path)

                # Add to PATH if not already there
                if self.install_dir not in os.environ.get('PATH', ''):
                    os.environ['PATH'] = self.install_dir + os.pathsep + os.environ.get('PATH', '')

                self.progress.emit(95, "Verifying...")

                if os.path.exists(dest_path):
                    self.progress.emit(100, "yt-dlp installed successfully!")
                    self.finished.emit(True, f"yt-dlp installed to:\n{self.install_dir}")
                else:
                    self.finished.emit(False, "Installation verification failed")

            finally:
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception:
                    pass

        except URLError as e:
            self.finished.emit(False, f"Download failed: {e.reason}")
        except PermissionError:
            self.finished.emit(False, f"Permission denied writing to:\n{self.install_dir}")
        except Exception as e:
            self.finished.emit(False, f"Installation failed: {str(e)}")

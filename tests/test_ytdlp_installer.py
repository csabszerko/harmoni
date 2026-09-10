import io
import os
import sys
import tempfile
import unittest
from unittest import mock

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in os.sys.path:
    os.sys.path.insert(0, THIS_DIR)
    os.sys.path.insert(0, os.path.dirname(THIS_DIR))

from gui.workers.ytdlp_installer import YtdlpInstallerWorker


class FakeResponse:
    """Minimal stand-in for the object urlopen() returns."""

    def __init__(self, data: bytes):
        self._buf = io.BytesIO(data)
        self.headers = {"content-length": str(len(data))}

    def read(self, size=-1):
        return self._buf.read(size)


class TestYtdlpInstallerWorkerPaths(unittest.TestCase):
    def test_dest_path_drives_install_dir(self):
        """Regression test for the update bug: when re-updating an existing
        standalone binary, the worker must target that exact file, not the
        default install location."""
        with tempfile.TemporaryDirectory() as td:
            existing_binary = os.path.join(td, "custom", "yt-dlp.exe")
            worker = YtdlpInstallerWorker(dest_path=existing_binary)

            self.assertEqual(worker.dest_path, existing_binary)
            self.assertEqual(worker.install_dir, os.path.dirname(existing_binary))

    def test_no_dest_path_uses_default_install_dir(self):
        worker = YtdlpInstallerWorker()
        self.assertIsNone(worker.dest_path)
        self.assertTrue(worker.install_dir)  # some default was picked

    def test_explicit_install_dir_still_respected(self):
        with tempfile.TemporaryDirectory() as td:
            worker = YtdlpInstallerWorker(install_dir=td)
            self.assertEqual(worker.install_dir, td)
            self.assertIsNone(worker.dest_path)


class TestYtdlpInstallerWorkerRun(unittest.TestCase):
    def test_run_updates_binary_at_dest_path_in_place(self):
        """End-to-end (network mocked) check that clicking 'Check for
        Updates' on an already-installed standalone binary overwrites that
        same file, rather than leaving it untouched."""
        with tempfile.TemporaryDirectory() as td:
            dest_path = os.path.join(td, "yt-dlp.exe" if sys.platform == "win32" else "yt-dlp")
            with open(dest_path, "wb") as f:
                f.write(b"OLD-JULY-BINARY")

            worker = YtdlpInstallerWorker(dest_path=dest_path)

            finished_calls = []
            worker.finished.connect(lambda ok, msg: finished_calls.append((ok, msg)))

            with mock.patch(
                "gui.workers.ytdlp_installer.urlopen",
                return_value=FakeResponse(b"NEW-AUGUST-BINARY"),
            ):
                worker.run()

            self.assertEqual(len(finished_calls), 1)
            success, message = finished_calls[0]
            self.assertTrue(success, message)

            with open(dest_path, "rb") as f:
                self.assertEqual(f.read(), b"NEW-AUGUST-BINARY")

    def test_run_reports_failure_on_unsupported_platform(self):
        worker = YtdlpInstallerWorker(dest_path="/tmp/yt-dlp")
        finished_calls = []
        worker.finished.connect(lambda ok, msg: finished_calls.append((ok, msg)))

        with mock.patch("gui.workers.ytdlp_installer.sys.platform", "os2"):
            worker.run()

        self.assertEqual(len(finished_calls), 1)
        success, message = finished_calls[0]
        self.assertFalse(success)
        self.assertIn("No yt-dlp download available", message)


if __name__ == "__main__":
    unittest.main(verbosity=2)

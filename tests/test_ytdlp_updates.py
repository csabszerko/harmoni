import os
import tempfile
import unittest
from unittest import mock

# Ensure local imports work when running this file directly.
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in os.sys.path:
    os.sys.path.insert(0, THIS_DIR)
    os.sys.path.insert(0, os.path.dirname(THIS_DIR))

from tools.ytdlp_update_checker import (
    parse_version,
    is_update_available,
    get_installed_version,
    check_ytdlp_updates,
)


class TestParseVersion(unittest.TestCase):
    def test_parses_standard_version(self):
        self.assertEqual(parse_version("2024.08.06"), (2024, 8, 6))

    def test_parses_short_version(self):
        self.assertEqual(parse_version("2024.1"), (2024, 1, 0))

    def test_malformed_version_falls_back_to_zero(self):
        self.assertEqual(parse_version("not-a-version"), (0, 0, 0))


class TestIsUpdateAvailable(unittest.TestCase):
    def test_newer_latest_reports_update(self):
        self.assertTrue(is_update_available("2024.07.01", "2024.08.06"))

    def test_equal_versions_report_no_update(self):
        self.assertFalse(is_update_available("2024.08.06", "2024.08.06"))

    def test_older_latest_reports_no_update(self):
        self.assertFalse(is_update_available("2024.08.06", "2024.07.01"))

    def test_missing_values_report_no_update(self):
        self.assertFalse(is_update_available("", "2024.08.06"))
        self.assertFalse(is_update_available("2024.08.06", ""))


class TestGetInstalledVersion(unittest.TestCase):
    def test_uses_configured_path_when_it_exists(self):
        """This is the core fix: a configured standalone binary must be
        checked directly instead of trusting whatever 'yt-dlp' resolves to
        on PATH (which may be an unrelated, stale install)."""
        with tempfile.TemporaryDirectory() as td:
            fake_binary = os.path.join(td, "yt-dlp.exe")
            with open(fake_binary, "w") as f:
                f.write("")

            with mock.patch("tools.ytdlp_update_checker.subprocess.run") as run:
                run.return_value = mock.Mock(returncode=0, stdout="2024.07.01\n")
                version = get_installed_version(fake_binary)

            called_binary = run.call_args[0][0][0]
            self.assertEqual(called_binary, fake_binary)
            self.assertEqual(version, "2024.07.01")

    def test_falls_back_to_path_when_configured_path_missing(self):
        with mock.patch("tools.ytdlp_update_checker.subprocess.run") as run:
            run.return_value = mock.Mock(returncode=0, stdout="2024.08.06\n")
            version = get_installed_version("/does/not/exist/yt-dlp.exe")

        called_binary = run.call_args[0][0][0]
        self.assertEqual(called_binary, "yt-dlp")
        self.assertEqual(version, "2024.08.06")

    def test_falls_back_to_path_when_no_path_given(self):
        with mock.patch("tools.ytdlp_update_checker.subprocess.run") as run:
            run.return_value = mock.Mock(returncode=0, stdout="2024.08.06\n")
            get_installed_version(None)

        called_binary = run.call_args[0][0][0]
        self.assertEqual(called_binary, "yt-dlp")

    def test_returns_none_when_binary_missing(self):
        with mock.patch(
            "tools.ytdlp_update_checker.subprocess.run",
            side_effect=FileNotFoundError,
        ):
            self.assertIsNone(get_installed_version(None))


class TestCheckYtdlpUpdates(unittest.TestCase):
    def test_reports_update_available_using_configured_binary(self):
        with mock.patch(
            "tools.ytdlp_update_checker.get_installed_version",
            return_value="2024.07.01",
        ) as get_installed, mock.patch(
            "tools.ytdlp_update_checker.get_latest_version",
            return_value="2024.08.06",
        ):
            result = check_ytdlp_updates("/config/bin/yt-dlp.exe")

        get_installed.assert_called_once_with("/config/bin/yt-dlp.exe")
        self.assertTrue(result["update_available"])
        self.assertEqual(result["current_version"], "2024.07.01")
        self.assertEqual(result["latest_version"], "2024.08.06")

    def test_up_to_date_reports_no_update(self):
        with mock.patch(
            "tools.ytdlp_update_checker.get_installed_version",
            return_value="2024.08.06",
        ), mock.patch(
            "tools.ytdlp_update_checker.get_latest_version",
            return_value="2024.08.06",
        ):
            result = check_ytdlp_updates("/config/bin/yt-dlp.exe")

        self.assertFalse(result["update_available"])

    def test_none_when_installed_version_unknown(self):
        with mock.patch(
            "tools.ytdlp_update_checker.get_installed_version",
            return_value=None,
        ):
            result = check_ytdlp_updates(None)

        self.assertFalse(result["update_available"])
        self.assertIsNone(result["current_version"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

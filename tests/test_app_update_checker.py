import os
import unittest
from unittest import mock

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in os.sys.path:
    os.sys.path.insert(0, THIS_DIR)
    os.sys.path.insert(0, os.path.dirname(THIS_DIR))

from tools.app_update_checker import parse_version, is_newer, check_app_update


class TestParseVersion(unittest.TestCase):
    def test_parses_plain_semver(self):
        self.assertEqual(parse_version("1.2.1"), (1, 2, 1))

    def test_parses_v_prefixed_tag(self):
        self.assertEqual(parse_version("v1.2.1"), (1, 2, 1))

    def test_empty_or_none_parses_to_zero(self):
        self.assertEqual(parse_version(""), (0,))
        self.assertEqual(parse_version(None), (0,))

    def test_malformed_parses_to_zero(self):
        self.assertEqual(parse_version("latest"), (0,))


class TestIsNewer(unittest.TestCase):
    def test_newer_tag_is_detected(self):
        self.assertTrue(is_newer("1.2.0", "v1.2.1"))
        self.assertTrue(is_newer("v1.2.0", "v1.3.0"))

    def test_same_version_is_not_newer(self):
        self.assertFalse(is_newer("v1.2.1", "1.2.1"))

    def test_older_tag_is_not_newer(self):
        self.assertFalse(is_newer("v1.3.0", "v1.2.1"))

    def test_missing_values_are_not_newer(self):
        self.assertFalse(is_newer("", "v1.2.1"))
        self.assertFalse(is_newer("v1.2.1", ""))


class TestCheckAppUpdate(unittest.TestCase):
    def test_reports_update_available_with_release_url(self):
        with mock.patch(
            "tools.app_update_checker.__version__", "1.2.0"
        ), mock.patch(
            "tools.app_update_checker.get_latest_release",
            return_value={
                "tag_name": "v1.2.1",
                "html_url": "https://github.com/Ssenseii/harmoni/releases/tag/v1.2.1",
            },
        ):
            result = check_app_update()

        self.assertTrue(result["update_available"])
        self.assertEqual(result["current_version"], "1.2.0")
        self.assertEqual(result["latest_version"], "v1.2.1")
        self.assertIn("releases/tag/v1.2.1", result["release_url"])

    def test_up_to_date_reports_no_update(self):
        with mock.patch(
            "tools.app_update_checker.__version__", "1.2.1"
        ), mock.patch(
            "tools.app_update_checker.get_latest_release",
            return_value={"tag_name": "v1.2.1", "html_url": "https://example.com"},
        ):
            result = check_app_update()

        self.assertFalse(result["update_available"])

    def test_none_when_network_unavailable(self):
        with mock.patch(
            "tools.app_update_checker.get_latest_release", return_value=None
        ):
            self.assertIsNone(check_app_update())


if __name__ == "__main__":
    unittest.main(verbosity=2)

import os
import unittest
from unittest.mock import patch

import config


class TestConfigStorage(unittest.TestCase):
    def test_frozen_macos_app_uses_application_support_for_config(self):
        with patch.object(config.sys, "frozen", True, create=True), \
             patch.object(config.sys, "platform", "darwin"), \
             patch("config.os.path.expanduser", return_value="/Users/tester"):
            path = config.get_config_path()

        self.assertEqual(
            path,
            os.path.join("/Users/tester", "Library", "Application Support", "HARMONI", "config.json"),
        )

    def test_development_run_keeps_config_in_project_directory(self):
        with patch.object(config.sys, "frozen", False, create=True):
            path = config.get_config_path()

        self.assertEqual(path, os.path.join(os.path.dirname(config.__file__), "config.json"))


if __name__ == "__main__":
    unittest.main()

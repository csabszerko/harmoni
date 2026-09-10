import os
import unittest
from unittest import mock

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in os.sys.path:
    os.sys.path.insert(0, THIS_DIR)
    os.sys.path.insert(0, os.path.dirname(THIS_DIR))

from gui.workers.app_update_worker import AppUpdateCheckWorker


class TestAppUpdateCheckWorker(unittest.TestCase):
    def test_emits_when_update_available(self):
        worker = AppUpdateCheckWorker()
        received = []
        worker.update_available.connect(lambda info: received.append(info))

        info = {
            "update_available": True,
            "current_version": "1.2.0",
            "latest_version": "v1.2.1",
            "release_url": "https://example.com/releases/tag/v1.2.1",
        }
        with mock.patch(
            "gui.workers.app_update_worker.check_app_update", return_value=info
        ):
            worker.run()

        self.assertEqual(received, [info])

    def test_does_not_emit_when_up_to_date(self):
        worker = AppUpdateCheckWorker()
        received = []
        worker.update_available.connect(lambda info: received.append(info))

        with mock.patch(
            "gui.workers.app_update_worker.check_app_update",
            return_value={"update_available": False},
        ):
            worker.run()

        self.assertEqual(received, [])

    def test_does_not_emit_when_check_fails(self):
        worker = AppUpdateCheckWorker()
        received = []
        worker.update_available.connect(lambda info: received.append(info))

        with mock.patch(
            "gui.workers.app_update_worker.check_app_update", return_value=None
        ):
            worker.run()

        self.assertEqual(received, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)

import json
import unittest
from unittest.mock import patch

from gui.workers.download_worker import DownloadWorker


class TestVideoMatching(unittest.TestCase):
    def test_chooses_first_search_result_within_duration_tolerance(self):
        worker = DownloadWorker.__new__(DownloadWorker)
        worker.config = {
            "video_search_result_limit": 3,
            "video_duration_tolerance_seconds": 10,
        }
        item = type("Item", (), {"metadata": {"duration_ms": "180000"}})()
        search_result = {
            "entries": [
                {"id": "clip", "title": "Song (teaser)", "duration": 30},
                {"id": "song", "title": "Song — Official Audio", "duration": 184},
            ]
        }
        completed = type(
            "Completed",
            (), {"returncode": 0, "stdout": json.dumps(search_result), "stderr": ""},
        )()

        with patch("gui.workers.download_worker.subprocess.run", return_value=completed) as run:
            url, title, error = worker._find_matching_video("Artist - Song", item)

        self.assertEqual(url, "https://www.youtube.com/watch?v=song")
        self.assertEqual(title, "Song — Official Audio")
        self.assertIsNone(error)
        self.assertIn("ytsearch3:Artist - Song", run.call_args.args[0])
        self.assertNotIn("--no-playlist", run.call_args.args[0])

    def test_rejects_results_outside_duration_tolerance(self):
        worker = DownloadWorker.__new__(DownloadWorker)
        worker.config = {
            "video_search_result_limit": 2,
            "video_duration_tolerance_seconds": 10,
        }
        item = type("Item", (), {"metadata": {"duration_ms": "180000"}})()
        search_result = {"entries": [{"id": "clip", "title": "Song teaser", "duration": 30}]}
        completed = type(
            "Completed",
            (), {"returncode": 0, "stdout": json.dumps(search_result), "stderr": ""},
        )()

        with patch("gui.workers.download_worker.subprocess.run", return_value=completed):
            url, title, error = worker._find_matching_video("Artist - Song", item)

        self.assertIsNone(url)
        self.assertIsNone(title)
        self.assertIn("within 10 seconds", error)


if __name__ == "__main__":
    unittest.main()

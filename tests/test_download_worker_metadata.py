import os
import unittest
from unittest.mock import patch

from gui.workers.download_worker import DownloadWorker


class TestDownloadWorkerMetadata(unittest.TestCase):
    def test_existing_download_is_tagged_before_being_reported_complete(self):
        worker = DownloadWorker.__new__(DownloadWorker)
        worker.config = {
            "audio_format": "mp3",
            "output_dir": "/library",
            "enable_metadata_embedding": True,
        }
        item = type(
            "Item",
            (),
            {"artist": "Artist", "track": "Title", "output_dir": "/library", "source_title": None},
        )()
        expected_path = "/library/Artist - Title.mp3"

        with patch(
            "gui.workers.download_worker.os.path.isfile",
            side_effect=lambda path: path == expected_path,
        ), patch.object(worker, "_embed_metadata") as embed_metadata:
            success, path, error, source_title = worker._download_single(item)

        self.assertEqual((success, path, error, source_title), (True, expected_path, None, None))
        embed_metadata.assert_called_once_with(expected_path, item)


if __name__ == "__main__":
    unittest.main()

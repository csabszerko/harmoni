import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from gui.views.downloads_view import DownloadsView
from gui.workers.download_queue import DownloadQueue, QueueItem


class TestDownloadsViewLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_track_row_fits_spotify_and_youtube_titles_when_added(self):
        queue = DownloadQueue()
        view = DownloadsView({}, queue)
        item = QueueItem(
            id="item-1",
            artist="Artist",
            track="Spotify title",
            source_title="YouTube title — Official Audio",
        )

        view._on_item_added(item)

        cell = view.table.cellWidget(0, 1)
        self.assertGreaterEqual(view.table.rowHeight(0), cell.sizeHint().height())
        view.deleteLater()


if __name__ == "__main__":
    unittest.main()

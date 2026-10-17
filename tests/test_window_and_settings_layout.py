import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow
from gui.views.download_settings_view import DownloadSettingsView


class TestWindowAndSettingsLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_window_keeps_native_title_bar_controls(self):
        window = MainWindow({})

        self.assertFalse(window.windowFlags() & Qt.FramelessWindowHint)
        window.deleteLater()

    def test_settings_inputs_have_consistent_dimensions(self):
        view = DownloadSettingsView({})
        inputs = [
            view.format_combo,
            view.parallel_spin,
            view.video_search_limit_spin,
            view.video_duration_tolerance_spin,
            view.ytdlp_path_input,
            view.ffmpeg_path_input,
            view.ytdlp_args_input,
        ]

        self.assertTrue(all(control.minimumWidth() == 280 for control in inputs))
        self.assertTrue(all(control.minimumHeight() == 40 for control in inputs))
        view.deleteLater()

    def test_wheel_over_spin_box_scrolls_settings_without_changing_its_value(self):
        view = DownloadSettingsView({})
        view.resize(700, 240)
        view.show()
        self.app.processEvents()
        scrollbar = view.scroll_area.verticalScrollBar()
        spin_box = view.video_search_limit_spin
        initial_value = spin_box.value()
        event = QWheelEvent(
            QPointF(spin_box.rect().center()),
            QPointF(spin_box.mapToGlobal(spin_box.rect().center())),
            QPoint(),
            QPoint(0, -120),
            Qt.NoButton,
            Qt.NoModifier,
            Qt.ScrollUpdate,
            False,
        )

        QApplication.sendEvent(spin_box, event)

        self.assertGreater(scrollbar.value(), 0)
        self.assertEqual(spin_box.value(), initial_value)
        view.deleteLater()


if __name__ == "__main__":
    unittest.main()

import os
import tempfile
import unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in os.sys.path:
    os.sys.path.insert(0, THIS_DIR)
    os.sys.path.insert(0, os.path.dirname(THIS_DIR))

from utils.loaders import parse_exportify_csv_for_queue, load_exportify_tracks

EXPORTIFY_HEADER = "Track URI,Track Name,Artist Name(s),Album Name,Playlist Name\n"
EXPORTIFY_ROW = 'spotify:track:1,Song One,Artist A;Artist B,Album X,My Playlist\n'


def _write_csv(path, content, encoding):
    with open(path, "w", newline="", encoding=encoding) as f:
        f.write(content)


class TestParseExportifyCsvForQueue(unittest.TestCase):
    def test_parses_plain_utf8_csv_without_bom(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "playlist.csv")
            _write_csv(path, EXPORTIFY_HEADER + EXPORTIFY_ROW, encoding="utf-8")

            tracks = parse_exportify_csv_for_queue(path)

            self.assertEqual(len(tracks), 1)
            self.assertEqual(tracks[0]["track"], "Song One")
            self.assertEqual(tracks[0]["artist"], "Artist A")
            self.assertEqual(tracks[0]["album"], "Album X")
            self.assertEqual(tracks[0]["playlist"], "My Playlist")

    def test_parses_utf8_csv_with_bom_like_real_exportify_export(self):
        # Regression test: Exportify exports UTF-8 with a BOM. Opening with a
        # plain "utf-8" codec leaves the BOM glued to the first header name
        # (turning "Track Name" into "﻿Track Name"), which made every
        # row.get("Track Name") lookup return None and silently dropped all rows.
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "playlist.csv")
            _write_csv(path, EXPORTIFY_HEADER + EXPORTIFY_ROW, encoding="utf-8-sig")

            tracks = parse_exportify_csv_for_queue(path)

            self.assertEqual(len(tracks), 1)
            self.assertEqual(tracks[0]["track"], "Song One")
            self.assertEqual(tracks[0]["artist"], "Artist A")

    def test_missing_track_or_artist_is_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "playlist.csv")
            _write_csv(
                path,
                EXPORTIFY_HEADER + "spotify:track:2,,Artist A,Album X,My Playlist\n",
                encoding="utf-8-sig",
            )

            tracks = parse_exportify_csv_for_queue(path)

            self.assertEqual(tracks, [])

    def test_playlist_name_falls_back_to_filename(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "My Cool Mix.csv")
            _write_csv(
                path,
                "Track Name,Artist Name(s),Album Name\nSong One,Artist A,Album X\n",
                encoding="utf-8-sig",
            )

            tracks = parse_exportify_csv_for_queue(path)

            self.assertEqual(tracks[0]["playlist"], "My Cool Mix")


class TestLoadExportifyTracksStillWorks(unittest.TestCase):
    def test_existing_loader_unaffected_by_change(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "playlist.csv")
            _write_csv(path, EXPORTIFY_HEADER + EXPORTIFY_ROW, encoding="utf-8-sig")

            tracks = load_exportify_tracks(path)

            self.assertEqual(len(tracks), 1)
            self.assertEqual(tracks[0]["artist"], "Artist A, Artist B")


if __name__ == "__main__":
    unittest.main()

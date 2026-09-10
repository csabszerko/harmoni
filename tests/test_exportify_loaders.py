"""Core-functionality tests for the Exportify CSV import pipeline (utils/loaders.py).

These cover the "connect Exportify -> load tracks -> queue for download" path that
must keep working across releases: normalizing multi-artist fields, loading a single
CSV, merging a watch-folder of CSVs, and the JSON fallback path.
"""
import os
import tempfile
import unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in os.sys.path:
    os.sys.path.insert(0, THIS_DIR)
    os.sys.path.insert(0, os.path.dirname(THIS_DIR))

from utils.loaders import (
    _normalize_artists,
    load_exportify_tracks,
    load_exportify_playlists,
    load_primary_tracks,
    load_tracks,
)

EXPORTIFY_HEADER = (
    "Track URI,Track Name,Artist Name(s),Album Name,Release Date,Genres,"
    "Record Label,Duration (ms),Popularity\n"
)


def _write_csv(path, rows, encoding="utf-8-sig"):
    with open(path, "w", newline="", encoding=encoding) as f:
        f.write(EXPORTIFY_HEADER)
        for row in rows:
            f.write(row + "\n")


class TestNormalizeArtists(unittest.TestCase):
    def test_semicolon_delimited_artists(self):
        self.assertEqual(_normalize_artists("Artist A;Artist B"), "Artist A, Artist B")

    def test_comma_delimited_artists_used_when_no_semicolon(self):
        self.assertEqual(_normalize_artists("Artist A,Artist B"), "Artist A, Artist B")

    def test_dedupes_case_insensitively_preserving_order(self):
        self.assertEqual(_normalize_artists("Artist A;artist a;Artist B"), "Artist A, Artist B")

    def test_blank_input_returns_empty_string(self):
        self.assertEqual(_normalize_artists(""), "")
        self.assertEqual(_normalize_artists(None), "")

    def test_single_artist_passthrough(self):
        self.assertEqual(_normalize_artists("Solo Artist"), "Solo Artist")


class TestLoadExportifyTracks(unittest.TestCase):
    def test_loads_full_metadata_from_csv(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "playlist.csv")
            _write_csv(path, [
                "spotify:track:1,Song One,Artist A;Artist B,Album X,2020-01-01,Pop;Dance,Label Y,200000,50",
            ])

            tracks = load_exportify_tracks(path)

            self.assertEqual(len(tracks), 1)
            t = tracks[0]
            self.assertEqual(t["track"], "Song One")
            self.assertEqual(t["artist"], "Artist A, Artist B")
            self.assertEqual(t["album"], "Album X")
            self.assertEqual(t["release_date"], "2020-01-01")
            self.assertEqual(t["record_label"], "Label Y")

    def test_rows_missing_artist_or_track_are_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "playlist.csv")
            _write_csv(path, [
                "spotify:track:1,,Artist A,Album X,,,,,",
                "spotify:track:2,Song Two,,Album X,,,,,",
                "spotify:track:3,Song Three,Artist C,Album X,,,,,",
            ])

            tracks = load_exportify_tracks(path)

            self.assertEqual(len(tracks), 1)
            self.assertEqual(tracks[0]["track"], "Song Three")

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(load_exportify_tracks(os.path.join(tempfile.gettempdir(), "does-not-exist.csv")), [])

    def test_empty_path_returns_empty_list(self):
        self.assertEqual(load_exportify_tracks(""), [])


class TestLoadExportifyPlaylists(unittest.TestCase):
    def test_scans_directory_for_csv_files(self):
        with tempfile.TemporaryDirectory() as td:
            _write_csv(os.path.join(td, "Chill Vibes.csv"), [
                "spotify:track:1,Song One,Artist A,Album X,,,,,",
            ])
            _write_csv(os.path.join(td, "Workout.csv"), [
                "spotify:track:2,Song Two,Artist B,Album Y,,,,,",
            ])
            # Non-CSV files must be ignored.
            with open(os.path.join(td, "notes.txt"), "w") as f:
                f.write("not a csv")

            playlists = load_exportify_playlists(td)

            names = sorted(p["name"] for p in playlists)
            self.assertEqual(names, ["Chill Vibes", "Workout"])
            for p in playlists:
                self.assertEqual(len(p["tracks"]), 1)

    def test_missing_directory_returns_empty_list(self):
        self.assertEqual(load_exportify_playlists(os.path.join(tempfile.gettempdir(), "nope-dir")), [])


class TestLoadPrimaryTracks(unittest.TestCase):
    def test_explicit_csv_file_is_used(self):
        with tempfile.TemporaryDirectory() as td:
            csv_path = os.path.join(td, "playlist.csv")
            _write_csv(csv_path, ["spotify:track:1,Song One,Artist A,Album X,,,,,"])

            config = {"primary_input_source": "csv", "primary_csv_file": csv_path}
            tracks = load_primary_tracks(config)

            self.assertEqual(len(tracks), 1)
            self.assertEqual(tracks[0]["track"], "Song One")

    def test_falls_back_to_merging_watch_folder_and_dedupes(self):
        with tempfile.TemporaryDirectory() as td:
            _write_csv(os.path.join(td, "a.csv"), ["spotify:track:1,Song One,Artist A,Album X,,,,,"])
            _write_csv(os.path.join(td, "b.csv"), [
                "spotify:track:1,Song One,artist a,Album X,,,,,",  # duplicate (case-insensitive)
                "spotify:track:2,Song Two,Artist B,Album Y,,,,,",
            ])

            config = {"primary_input_source": "csv", "exportify_watch_folder": td}
            tracks = load_primary_tracks(config)

            self.assertEqual(len(tracks), 2)
            titles = sorted(t["track"] for t in tracks)
            self.assertEqual(titles, ["Song One", "Song Two"])

    def test_json_source_falls_back_to_tracks_file(self):
        with tempfile.TemporaryDirectory() as td:
            tracks_file = os.path.join(td, "tracks.json")
            with open(tracks_file, "w", encoding="utf-8") as f:
                f.write('{"tracks": [{"artist": "Artist A", "track": "Song One"}]}')

            config = {"primary_input_source": "json", "tracks_file": tracks_file}
            tracks = load_primary_tracks(config)

            self.assertEqual(len(tracks), 1)
            self.assertEqual(tracks[0]["artist"], "Artist A")


class TestLoadTracksCsvDetection(unittest.TestCase):
    def test_csv_extension_is_routed_to_exportify_loader(self):
        with tempfile.TemporaryDirectory() as td:
            csv_path = os.path.join(td, "playlist.csv")
            _write_csv(csv_path, ["spotify:track:1,Song One,Artist A,Album X,,,,,"])

            tracks = load_tracks(csv_path)

            self.assertEqual(len(tracks), 1)
            self.assertEqual(tracks[0]["track"], "Song One")


if __name__ == "__main__":
    unittest.main(verbosity=2)

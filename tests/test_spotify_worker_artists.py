import os
import unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in os.sys.path:
    os.sys.path.insert(0, THIS_DIR)
    os.sys.path.insert(0, os.path.dirname(THIS_DIR))

from gui.workers.spotify_worker import extract_artist_names


class TestExtractArtistNames(unittest.TestCase):
    def test_single_artist(self):
        track_obj = {"artists": [{"name": "Artist A"}]}
        self.assertEqual(extract_artist_names(track_obj), "Artist A")

    def test_multiple_artists_are_joined(self):
        track_obj = {"artists": [{"name": "Artist A"}, {"name": "Artist B"}]}
        self.assertEqual(extract_artist_names(track_obj), "Artist A, Artist B")

    def test_no_artists_falls_back_to_unknown(self):
        track_obj = {"artists": []}
        self.assertEqual(extract_artist_names(track_obj), "Unknown Artist")

    def test_missing_artists_key_falls_back_to_unknown(self):
        self.assertEqual(extract_artist_names({}), "Unknown Artist")

    def test_artist_with_none_name_does_not_crash(self):
        # Regression test: Spotify can return an artist entry with "name": None
        # (e.g. removed/unavailable artist). dict.get("name", "") does not
        # substitute for an explicit None value, so ", ".join(...) used to
        # raise: "sequence item 0: expected str instance, NoneType found".
        track_obj = {"artists": [{"name": None}]}
        self.assertEqual(extract_artist_names(track_obj), "Unknown Artist")

    def test_mix_of_none_and_valid_names(self):
        track_obj = {"artists": [{"name": None}, {"name": "Artist B"}]}
        self.assertEqual(extract_artist_names(track_obj), "Artist B")


if __name__ == "__main__":
    unittest.main()

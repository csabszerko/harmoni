"""Regression coverage for MusicBrainz network failures."""

import os
import ssl
import unittest
import urllib.error
from unittest import mock

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if THIS_DIR not in os.sys.path:
    os.sys.path.insert(0, os.path.dirname(THIS_DIR))

from downloader import metadata


class TestMusicBrainzTlsFailures(unittest.TestCase):
    def test_certificate_failure_is_not_retried_for_every_track(self):
        metadata._musicbrainz_disabled_for_session = False
        certificate_error = urllib.error.URLError(
            ssl.SSLCertVerificationError("CERTIFICATE_VERIFY_FAILED")
        )

        with mock.patch("downloader.metadata.urllib.request.urlopen", side_effect=certificate_error) as urlopen, \
             mock.patch("downloader.metadata.time.sleep") as sleep:
            result = metadata._mb_get_json("https://musicbrainz.org/ws/2/recording/", max_retries=3)

        self.assertIsNone(result)
        self.assertEqual(urlopen.call_count, 1)
        sleep.assert_not_called()

        # A playlist has many tracks; once TLS is known to be unavailable,
        # later metadata lookups must not issue the same failing request.
        with mock.patch("downloader.metadata.urllib.request.urlopen") as next_urlopen:
            self.assertIsNone(metadata._mb_get_json("https://musicbrainz.org/ws/2/recording/"))
        next_urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)

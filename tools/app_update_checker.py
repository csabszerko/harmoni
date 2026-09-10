"""
HARMONI self-update checker.
Checks GitHub Releases for a newer HARMONI version than the one running.
"""

import json
import re
import urllib.request
import urllib.error
from typing import Optional, Tuple

from version import __version__

GITHUB_REPO = "Ssenseii/spotify-yt-dlp-downloader"
GITHUB_LATEST_RELEASE_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def parse_version(version_str: str) -> Tuple[int, ...]:
    """
    Parse a version string like "v1.2.1" or "1.2.1" into a tuple of ints
    for comparison. Non-numeric/malformed input parses to (0,).
    """
    if not version_str:
        return (0,)
    numbers = re.findall(r"\d+", version_str)
    if not numbers:
        return (0,)
    return tuple(int(n) for n in numbers)


def is_newer(current: str, latest: str) -> bool:
    """Return True if `latest` is a newer version than `current`."""
    if not current or not latest:
        return False
    return parse_version(latest) > parse_version(current)


def get_latest_release() -> Optional[dict]:
    """
    Fetch the latest HARMONI release from the GitHub API.

    Returns:
        Dict with 'tag_name' and 'html_url', or None if unavailable
        (no network, rate-limited, no releases yet, etc).
    """
    try:
        request = urllib.request.Request(
            GITHUB_LATEST_RELEASE_URL,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "HARMONI-update-checker",
            },
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode())
            return {"tag_name": data["tag_name"], "html_url": data["html_url"]}
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, KeyError):
        return None
    except Exception:
        return None


def check_app_update() -> Optional[dict]:
    """
    Check whether a newer HARMONI release exists on GitHub.

    Returns:
        Dict with keys:
        - 'update_available': bool
        - 'current_version': str
        - 'latest_version': str
        - 'release_url': str
        Or None if the check could not be performed (e.g. no network).
    """
    release = get_latest_release()
    if not release:
        return None

    latest_version = release["tag_name"]

    return {
        "update_available": is_newer(__version__, latest_version),
        "current_version": __version__,
        "latest_version": latest_version,
        "release_url": release["html_url"],
    }

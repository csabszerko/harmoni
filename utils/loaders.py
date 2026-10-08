"""Import Exportify CSV data for the desktop queue."""

import csv
import os


def _first_artist(value: str) -> str:
    """Use the lead artist for the search query while retaining all artists in tags."""
    value = (value or "").strip()
    if ";" in value:
        return value.split(";", 1)[0].strip()
    if "," in value:
        return value.split(",", 1)[0].strip()
    return value


def _metadata(row: dict[str, str]) -> dict[str, str]:
    """Map Exportify's useful fields to the metadata writer's input names."""
    fields = {
        "album": "Album Name",
        "uri": "Track URI",
        "album_art_url": "Album Image URL",
        "release_date": "Release Date",
        "genres": "Genres",
        "record_label": "Record Label",
        "duration_ms": "Duration (ms)",
        "popularity": "Popularity",
        "explicit": "Explicit",
        "danceability": "Danceability",
        "energy": "Energy",
        "key": "Key",
        "acousticness": "Acousticness",
        "instrumentalness": "Instrumentalness",
        "liveness": "Liveness",
        "valence": "Valence",
        "tempo": "Tempo",
        "time_signature": "Time Signature",
    }
    return {key: row[column].strip() for key, column in fields.items() if row.get(column, "").strip()}


def parse_exportify_csv_for_queue(file_path: str) -> list[dict[str, str]]:
    """Parse a CSV into queue items, preserving metadata for the final audio file."""
    tracks = []
    with open(file_path, "r", newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            title = (row.get("Track Name") or "").strip()
            all_artists = (row.get("Artist Name(s)") or "").strip()
            artist = _first_artist(all_artists)
            if not title or not artist:
                continue

            playlist = (row.get("Playlist Name") or os.path.basename(file_path)).removesuffix(".csv").strip()
            tracks.append({
                **_metadata(row),
                "artist": artist,
                "tag_artists": all_artists,
                "track": title,
                "album": (row.get("Album Name") or "").strip(),
                "playlist": playlist or "Import",
            })
    return tracks

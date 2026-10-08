# Harmoni

A small desktop app for turning Exportify CSV playlists into a local music library.

## What it does

1. Export a playlist as CSV from [Exportify](https://exportify.app/).
2. Drop the CSV into Harmoni and choose a destination folder.
3. Review the queue and download the tracks.

Harmoni uses `yt-dlp` for its search/download step and writes standard MP3 metadata: artist, title, album, release date, genre, BPM, provenance, and cover art when Exportify supplied them.

## Run

```bash
./start.sh
```

The first run creates `.venv`, installs the three required packages, and opens the desktop app. FFmpeg must be installed and available on your PATH (or configured in Settings).

## Settings

`config.json` contains only download location, format, concurrency, metadata lookup, and optional paths/arguments for `yt-dlp` and FFmpeg. There is no Spotify OAuth integration or Spotify developer configuration.

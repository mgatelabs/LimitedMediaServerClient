# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.2] - 2026-10-02

### Added
- `client.books.download_image(book_id, chapter_id, filename, scratch_dir)` — saves a chapter image to the local scratch directory instead of returning base64. Source filenames are randomized, so the local file is named with a fresh UUID; the extension (png/webp/jpg) is detected from the image's magic bytes, falling back to the Content-Type header and source filename
- `examples/archive_media.py` — archives all content

### Changed
- `MediaClient` and `VolumeClient` share a common mime-to-extension helper (`ext_from_mime` in `_http.py`), with an `image/webp` fallback for Python builds where `mimetypes.guess_extension` misses webp

### Fixed
- `examples/list_books.py`, `examples/download_chapter.py`, and `examples/crawl_media.py` are now independently runnable

## [0.1.1] - 2026-10-01

### Fixed
- Packaging: corrected the build backend (`setuptools.build_meta`) so the package builds correctly when installed from GitHub

## [0.1.0] - 2026-10-01

### Added
- `MediaServerClient` — class-based entry point with per-instance auth state
- `AuthClient` — login, token renewal, session info
- `MediaClient` — folder/file listing, upload, download, migrate, move, preview
- `VolumeClient` — book/chapter/image access, tag and style updates
- `ProcessClient` — background task list, status, log, cancel
- `PluginClient` — plugin discovery and execution
- Configuration via `config.json` and/or environment variables (`MEDIASERVER_*`)
- Automatic token renewal and 401 retry in `HttpLayer`
- `examples/` directory with eight runnable scripts

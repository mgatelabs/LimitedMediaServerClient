# Changelog

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

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

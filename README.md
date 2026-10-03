# Limited Media Server API Client

A Python client library for the [Limited Media Server](https://github.com/mgatelabs/LimitedMediaServer) — a self-hosted media and volume (book/manga) management server.

## Features

- Full coverage of the media server REST API — folders, files, books, chapters, images, plugins, background tasks
- Class-based client with per-instance auth state — run multiple clients against different servers simultaneously
- Automatic token renewal and 401 retry — no manual session management
- Configuration via JSON file, environment variables, or both
- Python 3.11+, one dependency (`requests`)

## Installation

```bash
pip install git+https://github.com/mgatelabs/LimitedMediaServerClient.git
```

Pin to a release tag:

```bash
pip install git+https://github.com/mgatelabs/LimitedMediaServerClient.git@v0.1.0
```

## Quick start

### From a config file

Create `config.json`:

```json
{
  "server": { "host": "192.168.1.10", "port": 8080, "https": false },
  "auth":   { "username": "admin", "password": "secret", "totp_token": "", "pin": "" },
  "scratch": { "path": "/tmp/lms_scratch", "max_age_days": 7 }
}
```

```python
from mediaserver import MediaServerClient

client = MediaServerClient("config.json")
client.login()

books = client.books.list_books()
for book in books["books"]:
    print(book["name"], book.get("style"))
```

### From environment variables (no file needed)

```bash
export MEDIASERVER_HOST=192.168.1.10
export MEDIASERVER_PORT=8080
export MEDIASERVER_USERNAME=admin
export MEDIASERVER_PASSWORD=secret
```

```python
from mediaserver import MediaServerClient

client = MediaServerClient()
client.login()
```

## Configuration

All config fields can be supplied via environment variables, which take precedence over the JSON file.

| Environment variable     | JSON equivalent      | Description                          |
|--------------------------|----------------------|--------------------------------------|
| `MEDIASERVER_CONFIG`     | —                    | Path to config.json                  |
| `MEDIASERVER_HOST`       | `server.host`        | Server hostname or IP                |
| `MEDIASERVER_PORT`       | `server.port`        | Server port                          |
| `MEDIASERVER_HTTPS`      | `server.https`       | Use HTTPS (`1`/`true`/`yes`)         |
| `MEDIASERVER_SSL_VERIFY` | `server.ssl_verify`  | Verify TLS cert (`0`/`false` to skip)|
| `MEDIASERVER_USERNAME`   | `auth.username`      | Login username                       |
| `MEDIASERVER_PASSWORD`   | `auth.password`      | Login password                       |
| `MEDIASERVER_TOTP_TOKEN` | `auth.totp_token`    | TOTP / 2FA token                     |
| `MEDIASERVER_PIN`        | `auth.pin`           | PIN                                  |
| `MEDIASERVER_SCRATCH_PATH` | `scratch.path`     | Local directory for downloaded files |

## Client API

```python
client.auth      # AuthClient    — login, renew, session info
client.media     # MediaClient   — folders, files, upload, download, preview, migrate
client.books     # VolumeClient  — books, chapters, images, tags
client.process   # ProcessClient — background tasks
client.plugins   # PluginClient  — plugin discovery and execution
```

### Auth

```python
client.login()                  # POST credentials, store token
client.auth.renew()             # Renew token (auto-called internally)
client.get_session_info()       # Decoded JWT capabilities, no HTTP call
```

### Media

```python
client.media.list_media(folder_id="")              # folders + files at root
client.media.get_folder(folder_id)
client.media.get_file(file_id)
client.media.download_file(file_id, Path("/tmp"))  # streams to local path
client.media.upload_file(folder_id, "/local/path")
client.media.migrate_file(file_id, force_archive=True)
client.media.move_file(file_id, target_folder_id)
client.media.create_folder(parent_id, "New Folder")
client.media.update_folder(folder_id, name, rating, info_url, tags, active)
client.media.get_preview(item_id, has_preview=True)  # returns base64 image data
```

### Books (Volumes)

```python
client.books.list_books(offset=0, limit=100)
client.books.get_book(book_id)
client.books.list_chapters(book_id)
client.books.list_images(book_id, chapter_id)
client.books.get_image(book_id, chapter_id, filename)  # returns base64 image data
client.books.download_image(book_id, chapter_id, filename, Path("/tmp"))  # streams to local path
client.books.list_tags()
client.books.update_style(book_id, "scroll")           # "page" | "scroll"
client.books.update_tags(book_id, ["tag1", "tag2"])
client.books.update_rating(book_id, 5)
client.books.update_book(book_id, name, alt_name, ...)  # all fields at once
```

### Process (background tasks)

```python
client.process.list_tasks()
client.process.get_status(task_id)
client.process.get_log(task_id, format="txt")   # "txt" | "md" | "json"
client.process.cancel(task_id)
```

### Plugins

```python
client.plugins.list_ai()              # AI-friendly list
client.plugins.describe(plugin_id)
client.plugins.run(plugin_id, args={"url": "https://..."})  # returns task_id
```

## Examples

See the [`examples/`](examples/) directory for complete runnable scripts.

| File | Description |
|------|-------------|
| `list_books.py` | Page through all books and print style |
| `find_manhwa.py` | Find all scroll-style books |
| `update_book_style.py` | Change a single book's style |
| `bulk_tag_books.py` | Add a tag to multiple books |
| `download_chapter.py` | Save first-chapter images locally |
| `run_plugin.py` | Execute a plugin and poll until done |
| `crawl_media.py` | Find all unarchived files |
| `multi_server.py` | Compare two servers simultaneously |

## Requirements

- Python 3.11+
- `requests >= 2.31`
- A running [Limited Media Server](https://github.com/mgatelabs/LimitedMediaServer) instance

## License

MIT

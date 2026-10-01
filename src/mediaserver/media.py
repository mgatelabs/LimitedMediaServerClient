"""Media sub-client: folders, files, upload/download, previews, migration."""

import base64
import mimetypes
from pathlib import Path

from mediaserver._http import HttpLayer, detect_image_mime


class MediaClient:
    def __init__(self, http: HttpLayer):
        self._http = http

    def list_media(self, folder_id: str = "", offset: int = 0, limit: int = 100,
                   rating_limit: int = 0, filter_text: str = "",
                   sorting: str = "AZ") -> dict:
        """List folders and files. folder_id="" = root.
        Returns: {"info": {...}, "paging": {...}, "folders": [...], "files": [...]}"""
        body = self._http.post("/api/media/list", data={
            "folder_id":    folder_id,
            "offset":       str(offset),
            "limit":        str(limit),
            "rating":       str(rating_limit),
            "sort":         sorting,
            "filter_text":  filter_text,
            "required_tags": "",
            "hidden_tags":  "",
        })
        if isinstance(body, list):
            return {
                "info":    {"id": folder_id, "name": "", "rating": 0, "parent_id": ""},
                "paging":  {"total": len(body), "offset": offset},
                "folders": [f for f in body if f.get("type") == "folder"] if body and "type" in body[0] else body,
                "files":   [],
            }
        return body

    def list_media_by_date(self, start_date: str, end_date: str, offset: int = 0,
                           limit: int = 100, rating_limit: int = 0,
                           sorting: str = "DA") -> dict:
        """List media created within a date range (ISO 8601 dates)."""
        body = self._http.post("/api/media/list/by-date", data={
            "start_date": start_date,
            "end_date":   end_date,
            "offset":     str(offset),
            "limit":      str(limit),
            "rating":     str(rating_limit),
            "sort":       sorting,
        })
        if not isinstance(body, dict):
            body = {}
        return {
            "info":    {"id": "", "name": "", "rating": 0, "parent_id": ""},
            "paging":  body.get("paging", {"total": 0, "offset": offset}),
            "folders": body.get("folders", []),
            "files":   body.get("files", []),
        }

    def get_folder(self, folder_id: str) -> dict:
        """Full details of one folder."""
        return self._http.post("/api/media/folder", data={"folder_id": folder_id})

    def get_file(self, file_id: str) -> dict:
        """Full details of one file."""
        return self._http.post("/api/media/file", data={"file_id": file_id})

    def download_file(self, file_id: str, scratch_dir: Path) -> dict:
        """Stream a file to scratch_dir as <file_id>.<ext>. Skips if already present.
        Returns: {"file_id", "local_path", "mime_type", "size_bytes"}"""
        meta = self.get_file(file_id)
        mime = meta.get("mime_type") or ""
        target = scratch_dir / f"{file_id}{_ext_from_mime(mime)}"
        if target.exists():
            return {"file_id": file_id, "local_path": str(target),
                    "mime_type": mime, "size_bytes": target.stat().st_size}
        resp = self._http.get("/api/media/view", params={"file_id": file_id}, stream=True)
        ctype = resp.headers.get("Content-Type", "").split(";")[0].strip()
        if ctype and ctype != "application/octet-stream":
            target = scratch_dir / f"{file_id}{_ext_from_mime(ctype)}"
            if not target.exists():
                mime = ctype
        with open(target, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)
        return {"file_id": file_id, "local_path": str(target),
                "mime_type": mime, "size_bytes": target.stat().st_size}

    def upload_file(self, folder_id: str, local_path: str, mime_type: str = "") -> dict:
        """Upload a local file into a folder."""
        fname, fh, ctype = _open_upload(local_path, mime_type)
        try:
            return self._http.post("/api/media/folder/upload/file",
                                   data={"folder_id": folder_id},
                                   files={"file": (fname, fh, ctype)})
        finally:
            fh.close()

    def migrate_file(self, file_id: str, force_archive: bool) -> dict:
        """Migrate/re-archive a media file."""
        return self._http.post("/api/media/file/migrate", data={
            "file_id":       file_id,
            "force_archive": "true" if force_archive else "false",
        })

    def get_preview(self, item_id: str, has_preview: bool) -> dict:
        """Return {"has_preview": False} or {"has_preview": True, "data": base64, "mime_type": str}."""
        if not has_preview:
            return {"has_preview": False, "item_id": item_id}
        resp = self._http.get(f"/api/media/item/preview/{item_id}")
        data = base64.b64encode(resp.content).decode("ascii")
        mime = detect_image_mime(resp.content, resp.headers.get("Content-Type", ""))
        return {"has_preview": True, "item_id": item_id, "data": data, "mime_type": mime}

    def move_file(self, file_id: str, folder_id: str) -> dict:
        """Move a file to another folder."""
        return self._http.post("/api/media/file/move",
                               data={"file_id": file_id, "folder_id": folder_id})

    def move_folder(self, source_id: str, folder_id: str) -> dict:
        """Move a folder into another folder. folder_id="" = root."""
        return self._http.post("/api/media/folder/move",
                               data={"source_id": source_id, "folder_id": folder_id})

    def create_folder(self, parent_id: str, name: str, rating: int = 0,
                      info_url: str = "", tags: str = "", active: bool = True) -> dict:
        """Create a folder under parent_id ("" = root)."""
        return self._http.post("/api/media/folder/post", data={
            "parent_id": parent_id,
            "name":      name,
            "rating":    str(rating),
            "info_url":  info_url,
            "active":    "true" if active else "false",
            "tags":      tags,
            "fast_tags": "",
        })

    def update_folder(self, folder_id: str, name: str, rating: int,
                      info_url: str, tags: str, active: bool) -> dict:
        """Update all editable fields of a folder."""
        return self._http.post("/api/media/folder/put", data={
            "folder_id": folder_id,
            "name":      name,
            "rating":    str(rating),
            "info_url":  info_url,
            "active":    "true" if active else "false",
            "tags":      tags,
            "fast_tags": "",
        })

    def update_file(self, file_id: str, filename: str, mime_type: str) -> dict:
        """Update filename and/or mime_type of a file."""
        return self._http.post("/api/media/file/put",
                               data={"file_id": file_id, "filename": filename,
                                     "mime_type": mime_type})

    def set_folder_active(self, folder_id: str, active: bool) -> dict:
        """Activate or deactivate a folder."""
        endpoint = "/api/media/folder/activate" if active else "/api/media/folder/inactivate"
        return self._http.post(endpoint, data={"folder_id": folder_id})

    def upload_preview(self, folder_id: str, local_path: str, mime_type: str = "") -> dict:
        """Upload a local image as the folder's preview."""
        fname, fh, ctype = _open_upload(local_path, mime_type or "image/jpeg")
        try:
            return self._http.post("/api/media/folder/upload/preview",
                                   data={"folder_id": folder_id},
                                   files={"image": (fname, fh, ctype)})
        finally:
            fh.close()


# ── helpers ───────────────────────────────────────────────────────────────────

_JPEG_FIXES = {".jpe": ".jpg", ".jpeg": ".jpg"}


def _ext_from_mime(mime_type: str) -> str:
    ext = mimetypes.guess_extension(mime_type) or ""
    return _JPEG_FIXES.get(ext, ext)


def _open_upload(local_path: str, mime_type: str):
    """Return (filename, file_handle, content_type) for a requests upload."""
    path = Path(local_path)
    if not path.exists():
        raise RuntimeError(f"File not found: {local_path}")
    fname = path.name
    ctype = mime_type or mimetypes.guess_type(fname)[0] or "application/octet-stream"
    if "." not in fname and ctype != "application/octet-stream":
        ext = mimetypes.guess_extension(ctype) or ""
        ext = _JPEG_FIXES.get(ext, ext)
        if ext:
            fname = fname + ext
    return fname, open(path, "rb"), ctype

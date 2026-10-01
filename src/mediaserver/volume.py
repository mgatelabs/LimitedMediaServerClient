"""Volume sub-client: books, chapters, images, tag management, updates."""

import base64

from mediaserver._http import HttpLayer, detect_image_mime


class VolumeClient:
    def __init__(self, http: HttpLayer):
        self._http = http

    def list_books(self, offset: int = 0, limit: int = 100, rating_limit: int = 0,
                   filter_text: str = "", filter_tags: str = "", sorting: str = "AZ",
                   filter_type: str = "") -> dict:
        """Returns: {"books": [...], "paging": {"total": int, "offset": int}}"""
        body = self._http.post("/api/volume/list/books", data={
            "offset":      str(offset),
            "limit":       str(limit),
            "rating":      str(rating_limit),
            "sort":        sorting,
            "filter_text": filter_text,
            "filter_type": filter_type,
            "filter_tags": filter_tags,
        })
        if isinstance(body, list):
            return {"books": body, "paging": {"total": len(body), "offset": 0}}
        return body

    def get_book(self, book_id: str) -> dict:
        """Full details of one book."""
        return self._http.post("/api/volume/details", data={"book_id": book_id})

    def list_chapters(self, book_id: str) -> dict:
        """All chapters of a book. Returns {"chapters": [...]}"""
        return self._http.post("/api/volume/list/chapters", data={"book_id": book_id})

    def list_images(self, book_id: str, chapter_id: str) -> dict:
        """Image filenames for one chapter. Returns {"files": [...]}"""
        return self._http.post("/api/volume/list/images",
                               data={"book_id": book_id, "chapter_id": chapter_id})

    def get_image(self, book_id: str, chapter_id: str, filename: str) -> dict:
        """Returns {"image_base64": str, "mime_type": str}."""
        resp = self._http.get(f"/api/volume/serve_image/{book_id}/{chapter_id}/{filename}")
        mime = detect_image_mime(resp.content, resp.headers.get("Content-Type", ""), filename)
        return {
            "image_base64": base64.b64encode(resp.content).decode("ascii"),
            "mime_type":    mime,
        }

    def list_tags(self) -> dict:
        """All tags in use across books."""
        return self._http.post("/api/volume/list/tags", data={})

    def guess_tags(self, values: str) -> dict:
        """Suggest tags from a free-text description."""
        return self._http.post("/api/volume/guess/tags", data={"values": values})

    def update_book(self, book_id: str, name: str, alt_name: str, rating: int,
                    tags: list[str], active: bool, info_url: str, rss_url: str,
                    extra_url: str, start_chapter: str, skip: str, style: str,
                    processor: str) -> dict:
        """Fetch-then-post update of all editable fields at once."""
        return self._apply_update(self.get_book(book_id), {
            "name":          name,
            "alt_name":      alt_name,
            "rating":        rating,
            "tags":          tags,
            "active":        active,
            "info_url":      info_url,
            "rss_url":       rss_url,
            "extra_url":     extra_url,
            "start_chapter": start_chapter,
            "skip":          skip,
            "style":         style,
            "processor":     processor,
        })

    def update_title(self, book_id: str, name: str) -> dict:
        return self._apply_update(self.get_book(book_id), {"name": name})

    def update_alt_name(self, book_id: str, alt_name: str) -> dict:
        return self._apply_update(self.get_book(book_id), {"alt_name": alt_name})

    def update_tags(self, book_id: str, tags: list[str]) -> dict:
        return self._apply_update(self.get_book(book_id), {"tags": tags})

    def update_rating(self, book_id: str, rating: int) -> dict:
        return self._apply_update(self.get_book(book_id), {"rating": rating})

    def update_style(self, book_id: str, style: str) -> dict:
        return self._apply_update(self.get_book(book_id), {"style": style})

    # ── internal ──────────────────────────────────────────────────────────────

    def _apply_update(self, book: dict, modifications: dict) -> dict:
        """Fetch-apply-post pattern for /api/volume/update."""
        data = {
            "id":            book.get("id", ""),
            "name":          book.get("name", ""),
            "processor":     book.get("processor", ""),
            "active":        "true" if book.get("active", True) else "false",
            "info_url":      book.get("info_url", ""),
            "rss_url":       book.get("rss_url", ""),
            "extra_url":     book.get("extra_url", ""),
            "start_chapter": book.get("start_chapter", ""),
            "skip":          book.get("skip", ""),
            "rating":        str(book.get("rating", 0)),
            "tags":          ",".join(book.get("tags", []) or []),
            "style":         book.get("style", "page"),
            "alt_name":      book.get("alt_name", ""),
        }
        for key, value in modifications.items():
            if key == "tags":
                data["tags"] = ",".join(value) if isinstance(value, list) else str(value)
            elif key == "active":
                data["active"] = "true" if value else "false"
            elif key == "rating":
                data["rating"] = str(value)
            else:
                data[key] = value
        return self._http.post("/api/volume/update", data=data)

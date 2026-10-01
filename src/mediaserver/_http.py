"""Shared authenticated HTTP layer for media server endpoints."""

import mimetypes

import requests

from mediaserver._config import ServerConfig
from mediaserver._session import SessionStore


def detect_image_mime(data: bytes, content_type: str = "", filename: str = "") -> str:
    """Determine image MIME type: magic bytes → header → filename extension → JPEG fallback."""
    if data[:4] == b"\x89PNG":
        return "image/png"
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    ct = (content_type or "").split(";")[0].strip()
    if ct.startswith("image/"):
        return ct
    return mimetypes.guess_type(filename)[0] or "image/jpeg"


class HttpLayer:
    def __init__(self, config: ServerConfig, session: SessionStore):
        self._config = config
        self._store  = session
        self._http   = requests.Session()
        self._http.verify = config.ssl_verify()
        self.raw     = requests.Session()   # used by AuthClient for login/renew
        self.raw.verify = config.ssl_verify()
        self._auth   = None  # set after construction via set_auth_client()

    def set_auth_client(self, auth) -> None:
        """Wire the AuthClient back-reference to resolve the circular dependency."""
        self._auth = auth

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._store.token}"} if self._store.token else {}

    def _ensure_auth(self) -> None:
        """Renew (falling back to login) when token is missing or near expiry."""
        if self._store.is_valid():
            return
        if self._store.active:
            try:
                self._auth.renew()
                return
            except Exception:
                pass
        self._auth.login()

    def post(self, path: str, data: dict | None = None,
             files: dict | None = None) -> object:
        """POST multipart/form-data. Auto-authenticates; retries once on 401.
        Returns decoded JSON (dict or list depending on endpoint)."""
        self._ensure_auth()
        url  = self._config.base_url() + path
        resp = self._http.post(url, data=data or {}, files=files, headers=self._headers())
        if resp.status_code == 401:
            self._store.clear()
            self._auth.login()
            resp = self._http.post(url, data=data or {}, files=files, headers=self._headers())
        resp.raise_for_status()
        body = resp.json()
        if isinstance(body, dict) and str(body.get("status", "")).upper() in ("ERROR", "FAIL"):
            raise RuntimeError(body.get("message") or "Unknown server error")
        return body

    def get(self, path: str, params: dict | None = None,
            stream: bool = False) -> requests.Response:
        """GET returning the raw Response (caller reads body/streams content)."""
        self._ensure_auth()
        url  = self._config.base_url() + path
        resp = self._http.get(url, params=params or {}, headers=self._headers(), stream=stream)
        if resp.status_code == 401:
            self._store.clear()
            self._auth.login()
            resp = self._http.get(url, params=params or {}, headers=self._headers(), stream=stream)
        resp.raise_for_status()
        return resp

"""In-memory session store for an authenticated media-server session."""

import base64
import json
import time


class Feature:
    MANAGE_APP       = 1
    MANAGE_VOLUME    = 4
    MANAGE_PROCESSES = 8
    MANAGE_MEDIA     = 16
    GENERAL_PLUGINS  = 32
    UTILITY_PLUGINS  = 64
    VOLUME_PLUGINS   = 128
    MEDIA_PLUGINS    = 512
    VIEW_PROCESSES   = 1024
    VIEW_VOLUME      = 2048
    VIEW_MEDIA       = 16384
    BOOKMARKS        = 32768
    HARD_SESSIONS    = 65536


_FLAG_NAMES = [
    ("MANAGE_APP",       Feature.MANAGE_APP),
    ("MANAGE_VOLUME",    Feature.MANAGE_VOLUME),
    ("MANAGE_PROCESSES", Feature.MANAGE_PROCESSES),
    ("MANAGE_MEDIA",     Feature.MANAGE_MEDIA),
    ("GENERAL_PLUGINS",  Feature.GENERAL_PLUGINS),
    ("UTILITY_PLUGINS",  Feature.UTILITY_PLUGINS),
    ("VOLUME_PLUGINS",   Feature.VOLUME_PLUGINS),
    ("MEDIA_PLUGINS",    Feature.MEDIA_PLUGINS),
    ("VIEW_PROCESSES",   Feature.VIEW_PROCESSES),
    ("VIEW_VOLUME",      Feature.VIEW_VOLUME),
    ("VIEW_MEDIA",       Feature.VIEW_MEDIA),
    ("BOOKMARKS",        Feature.BOOKMARKS),
    ("HARD_SESSIONS",    Feature.HARD_SESSIONS),
]


def _decode_jwt_payload(token: str) -> dict:
    """Best-effort decode of a JWT payload segment; returns empty dict on failure."""
    try:
        part = token.split(".")[1]
        pad = "=" * (-len(part) % 4)
        raw = base64.urlsafe_b64decode(part + pad)
        return json.loads(raw)
    except Exception:
        return {}


class SessionStore:
    def __init__(self):
        self.token:    str  = ""
        self.username: str  = ""
        self.exp:      int  = 0
        self.lifetime: int  = 0
        self.features: int  = 0
        self.limits:   dict = {"volume": 0, "media": 0}

    @property
    def active(self) -> bool:
        """True when a token has been stored (may be expired)."""
        return bool(self.token)

    @property
    def renew_threshold(self) -> int:
        """Seconds remaining at which renewal should trigger (10% of lifetime, min 60s)."""
        if not self.lifetime:
            return 60
        return max(60, int(self.lifetime * 0.10))

    def is_valid(self) -> bool:
        """True when token is present and not within the renewal window."""
        if not self.token or not self.username or not self.exp:
            return False
        return self.exp > (time.time() + self.renew_threshold)

    def has_feature(self, flag: int) -> bool:
        return (self.features & flag) == flag

    def seconds_remaining(self) -> int:
        return int(self.exp - time.time())

    def flags(self) -> dict:
        return {name: self.has_feature(flag) for name, flag in _FLAG_NAMES}

    def store_token(self, token: str) -> None:
        """Store a JWT and decode its payload into session fields."""
        self.token = token
        payload = _decode_jwt_payload(token)
        self.username = payload.get("username") or payload.get("sub") or ""
        self.exp = int(payload.get("exp", 0))
        self.lifetime = max(0, int(self.exp - time.time()))
        self.features = int(payload.get("features", 0))
        limits = payload.get("limits", {})
        self.limits = limits if isinstance(limits, dict) else {"volume": 0, "media": 0}

    def clear(self) -> None:
        self.token    = ""
        self.username = ""
        self.exp      = 0
        self.lifetime = 0
        self.features = 0
        self.limits   = {"volume": 0, "media": 0}

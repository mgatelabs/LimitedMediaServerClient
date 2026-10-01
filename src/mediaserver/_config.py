"""Load and expose the server configuration.

Resolution order (highest priority first):
  1. Individual env vars (MEDIASERVER_HOST, MEDIASERVER_PASSWORD, …)
  2. MEDIASERVER_CONFIG — path to a JSON file
  3. config_path argument passed to ServerConfig()
  4. "config.json" in the current working directory

Any individual env var overrides the corresponding JSON field.
The JSON file is optional when all required fields are supplied via env vars.

Supported env vars
──────────────────
MEDIASERVER_CONFIG        path to config.json
MEDIASERVER_HOST          server.host
MEDIASERVER_PORT          server.port          (integer)
MEDIASERVER_HTTPS         server.https         (1/true/yes = True)
MEDIASERVER_SSL_VERIFY    server.ssl_verify    (0/false/no  = False, default True)
MEDIASERVER_USERNAME      auth.username
MEDIASERVER_PASSWORD      auth.password
MEDIASERVER_TOTP_TOKEN    auth.totp_token
MEDIASERVER_PIN           auth.pin
MEDIASERVER_SCRATCH_PATH  scratch.path
"""

import json
import os
from pathlib import Path


def _truthy(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes")


def _load_json(path: str | Path | None) -> dict:
    """Load config.json from *path*; return empty dict if path is None/missing."""
    env_path = os.environ.get("MEDIASERVER_CONFIG")
    if env_path:
        path = env_path
    if path is None:
        return {}
    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        return {}
    with open(resolved, encoding="utf-8") as f:
        return json.load(f)


class ServerConfig:
    def __init__(self, config_path: str | Path | None = "config.json"):
        self._cfg = _load_json(config_path)

    # ── server ────────────────────────────────────────────────────────────────

    def base_url(self) -> str:
        """Return scheme + host:port, e.g. "http://192.168.1.10:8080"."""
        host   = os.environ.get("MEDIASERVER_HOST") or self._cfg.get("server", {}).get("host", "localhost")
        port   = int(os.environ.get("MEDIASERVER_PORT") or self._cfg.get("server", {}).get("port", 8080))
        env_https = os.environ.get("MEDIASERVER_HTTPS")
        https  = _truthy(env_https) if env_https is not None else bool(self._cfg.get("server", {}).get("https", False))
        scheme = "https" if https else "http"
        return f"{scheme}://{host}:{port}"

    def ssl_verify(self) -> bool:
        """Return False for plain HTTP or when ssl_verify is disabled."""
        env_https = os.environ.get("MEDIASERVER_HTTPS")
        https = _truthy(env_https) if env_https is not None else bool(self._cfg.get("server", {}).get("https", False))
        if not https:
            return False
        env_verify = os.environ.get("MEDIASERVER_SSL_VERIFY")
        if env_verify is not None:
            return _truthy(env_verify)
        return bool(self._cfg.get("server", {}).get("ssl_verify", True))

    # ── auth ──────────────────────────────────────────────────────────────────

    def auth_credentials(self) -> dict:
        """Return {"username", "password", "totp_token", "pin"}.
        Env vars override individual fields from the JSON file."""
        base = self._cfg.get("auth", {})
        return {
            "username":   os.environ.get("MEDIASERVER_USERNAME")   or base.get("username",   ""),
            "password":   os.environ.get("MEDIASERVER_PASSWORD")   or base.get("password",   ""),
            "totp_token": os.environ.get("MEDIASERVER_TOTP_TOKEN") or base.get("totp_token", ""),
            "pin":        os.environ.get("MEDIASERVER_PIN")        or base.get("pin",        ""),
        }

    # ── scratch ───────────────────────────────────────────────────────────────

    def scratch_path(self) -> str:
        return os.environ.get("MEDIASERVER_SCRATCH_PATH") or self._cfg.get("scratch", {}).get("path", "/tmp/mcp_scratch")

    def scratch_max_age_days(self) -> int:
        return int(self._cfg.get("scratch", {}).get("max_age_days", 7))

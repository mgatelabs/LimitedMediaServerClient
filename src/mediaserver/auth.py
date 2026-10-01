"""Authentication sub-client: login, token renewal, session info."""

from mediaserver._config import ServerConfig
from mediaserver._http import HttpLayer
from mediaserver._session import SessionStore


class AuthClient:
    def __init__(self, http: HttpLayer, config: ServerConfig, session: SessionStore):
        self._http    = http
        self._config  = config
        self._session = session

    def _parse_login_response(self, body: dict) -> None:
        ok = isinstance(body, dict) and str(body.get("status", "")).upper() == "OK"
        if not ok:
            msg = body.get("message") if isinstance(body, dict) else None
            raise RuntimeError(msg or "Login failed")
        if "token" not in body:
            raise RuntimeError("Login response contained no token")
        self._session.store_token(body["token"])

    def login(self) -> dict:
        """POST credentials to /api/auth/login and store the resulting token."""
        creds = self._config.auth_credentials()
        files = {
            "username": (None, creds.get("username", "")),
            "password": (None, creds.get("password", "")),
            "token":    (None, creds.get("totp_token", "")),
            "pin":      (None, creds.get("pin", "")),
        }
        resp = self._http.raw.post(self._config.base_url() + "/api/auth/login", files=files)
        resp.raise_for_status()
        self._parse_login_response(resp.json())
        return {
            "success":    True,
            "username":   self._session.username,
            "expires_in": self._session.seconds_remaining(),
        }

    def renew(self) -> dict:
        """POST to /api/auth/renew using the current token. Falls back to login()."""
        if not self._session.active:
            return self.login()
        resp = self._http.raw.post(
            self._config.base_url() + "/api/auth/renew",
            files={},
            headers={"Authorization": f"Bearer {self._session.token}"},
        )
        resp.raise_for_status()
        self._parse_login_response(resp.json())
        return {
            "success":    True,
            "username":   self._session.username,
            "expires_in": self._session.seconds_remaining(),
        }

    def get_session_info(self) -> dict:
        """Return decoded session capabilities from memory (no HTTP call)."""
        if not self._session.is_valid():
            raise RuntimeError("Not logged in or session expired — call login() first")
        return {
            "username":          self._session.username,
            "exp":               self._session.exp,
            "seconds_remaining": self._session.seconds_remaining(),
            "features":          self._session.features,
            "limits":            self._session.limits,
            "flags":             self._session.flags(),
        }

"""Plugin sub-client: discovery, description, and execution."""

import json

from mediaserver._http import HttpLayer


class PluginClient:
    def __init__(self, http: HttpLayer):
        self._http = http

    def list_ai(self) -> list:
        """AI-friendly plugin list (plain descriptions, no UI metadata)."""
        return self._http.post("/api/plugin/list/ai", data={})

    def list(self) -> list:
        """Full plugin list (includes Angular UI metadata)."""
        return self._http.post("/api/plugin/list", data={})

    def describe(self, plugin_id: str) -> dict:
        """Full detail for one plugin, including usage notes and preconditions."""
        return self._http.post("/api/plugin/describe", data={"plugin_id": plugin_id})

    def run(self, plugin_id: str, args: dict | None = None) -> dict:
        """Enqueue a plugin as a background task. Returns {"task_id": int}."""
        bundle = {
            "id": plugin_id,
            "args": {
                k: (str(v).lower() if isinstance(v, bool) else (v if isinstance(v, str) else str(v)))
                for k, v in (args or {}).items()
            },
        }
        return self._http.post("/api/process/add/plugin",
                               data={"bundle": json.dumps(bundle)})

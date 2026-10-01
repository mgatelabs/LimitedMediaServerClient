"""Process sub-client: background tasks — list, status, log, cancel, control."""

import json
from datetime import datetime

from mediaserver._http import HttpLayer

_SEVERITY_LABELS = {0: "TRACE", 10: "DEBUG", 20: "INFO", 30: "WARN", 40: "ERROR", 50: "CRIT"}


class ProcessClient:
    def __init__(self, http: HttpLayer):
        self._http = http

    def list_tasks(self, page: int = 0, page_size: int = 20,
                   extra_method: str = "NONE") -> dict:
        """List queued/running/recently finished tasks with worker status."""
        body = self._http.post(f"/api/process/status/all/with/{extra_method}", data={
            "page":      str(page),
            "page_size": str(page_size),
        })
        if isinstance(body, list):
            return {"tasks": body, "workers": [], "page": page,
                    "pages": 1, "total": len(body), "weight": 0}
        return body

    def get_status(self, task_id: int, log_page: int = 0, log_page_size: int = 0,
                   include_files: bool = False) -> dict:
        """Full detail for one task. Use log_page_size=0 while polling to avoid large payloads."""
        data: dict = {"include_files": "true" if include_files else "false"}
        if log_page_size > 0:
            data["log_page_size"] = str(log_page_size)
            data["log_page"]      = str(log_page)
        body = self._http.post(f"/api/process/status/{int(task_id)}", data=data)
        if not isinstance(body, dict):
            return {"id": int(task_id)}
        return body.get("task", body)

    def get_log(self, task_id: int, format: str = "txt", max_entries: int = 200) -> str:
        """Task log rendered as "txt", "md", or "json"."""
        status  = self.get_status(task_id, log_page=0, log_page_size=max_entries)
        entries = status.get("log", []) or []
        lines   = []
        for e in entries:
            label = _SEVERITY_LABELS.get(int(e.get("s", 0)), "LOG")
            ts    = datetime.fromtimestamp(int(e.get("time", 0))).strftime("%H:%M:%S")
            lines.append(f"[{label}]".ljust(8) + f" {ts}  {e.get('text', '')}")
        if format == "json":
            return json.dumps(entries, indent=2)
        if format == "md":
            return "```\n" + "\n".join(lines) + "\n```"
        return "\n".join(lines)

    def cancel(self, task_id: int) -> dict:
        """Cancel a queued or running task."""
        return self._http.post(f"/api/process/cancel/{int(task_id)}", data={})

    def stop_server(self) -> dict:
        """DANGEROUS — stop the background worker entirely."""
        return self._http.post("/api/process/stop", data={})

    def restart_server(self) -> dict:
        """DANGEROUS — restart the background worker, interrupting running tasks."""
        return self._http.post("/api/process/restart", data={})

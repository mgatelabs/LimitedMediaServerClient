"""Run a plugin by ID and poll until it finishes.

Usage:
    python run_plugin.py <plugin_id> [key=value ...]

Example:
    python run_plugin.py action.book.import-url url=https://example.com/book
"""

import sys
import time

from mediaserver import MediaServerClient

if len(sys.argv) < 2:
    print("Usage: python run_plugin.py <plugin_id> [key=value ...]")
    sys.exit(1)

plugin_id = sys.argv[1]
args = {}
for pair in sys.argv[2:]:
    if "=" in pair:
        k, v = pair.split("=", 1)
        args[k] = v

client = MediaServerClient()
client.login()

print(f"Starting plugin: {plugin_id}")
if args:
    print(f"  args: {args}")

result = client.plugins.run(plugin_id, args=args)
task_id = result.get("task_id") or result.get("id")
if not task_id:
    print(f"Unexpected response: {result}")
    sys.exit(1)

print(f"Task ID: {task_id}")

DONE_STATES = {"done", "error", "cancelled", "failed"}
poll_interval = 5

while True:
    status = client.process.get_status(task_id)
    state = status.get("state", "")
    progress = status.get("progress", "")
    indicator = f" ({progress})" if progress else ""
    print(f"  [{state}]{indicator}")
    if state.lower() in DONE_STATES:
        break
    time.sleep(poll_interval)

print("\nLog:")
print(client.process.get_log(task_id))

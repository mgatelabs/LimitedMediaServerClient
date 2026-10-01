"""Crawl all media folders from the root and list files not yet on archive storage."""

from collections import deque
from mediaserver import MediaServerClient

client = MediaServerClient()
client.login()

queue = deque([""])   # "" = root folder
unarchived = []

while queue:
    folder_id = queue.popleft()
    result = client.media.list_media(folder_id=folder_id, limit=200)

    folder_name = result.get("info", {}).get("name", folder_id or "root")

    for f in result.get("folders", []):
        queue.append(f["id"])

    for f in result.get("files", []):
        if not f.get("archive"):
            unarchived.append({
                "folder": folder_name,
                "id":     f["id"],
                "name":   f.get("filename", ""),
            })

print(f"Found {len(unarchived)} unarchived files:\n")
for f in unarchived:
    print(f"  [{f['folder']}]  {f['id']}  {f['name']}")

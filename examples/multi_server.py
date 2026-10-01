"""Compare book and file counts across two servers simultaneously.

Reads connection details from two config files (or two sets of env vars).

Usage:
    python multi_server.py <config_a.json> <config_b.json>
"""

import sys
from mediaserver import MediaServerClient

if len(sys.argv) != 3:
    print("Usage: python multi_server.py <config_a.json> <config_b.json>")
    sys.exit(1)

path_a, path_b = sys.argv[1], sys.argv[2]

a = MediaServerClient(path_a)
b = MediaServerClient(path_b)

a.login()
b.login()

info_a = a.get_session_info()
info_b = b.get_session_info()

def count_books(client):
    return client.books.list_books(limit=1).get("paging", {}).get("total", 0)

def count_files(client):
    return client.media.list_media(limit=1).get("paging", {}).get("total", 0)

books_a, books_b = count_books(a), count_books(b)
files_a, files_b = count_files(a), count_files(b)

print(f"{'':20s}  {'Server A':>12s}  {'Server B':>12s}")
print(f"{'─'*20}  {'─'*12}  {'─'*12}")
print(f"{'User':20s}  {info_a['username']:>12s}  {info_b['username']:>12s}")
print(f"{'Books':20s}  {books_a:>12,}  {books_b:>12,}")
print(f"{'Media files':20s}  {files_a:>12,}  {files_b:>12,}")

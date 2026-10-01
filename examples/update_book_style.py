"""Change a single book's style.

Usage:
    python update_book_style.py <book_id> <style>

    style: "page" or "scroll"
"""

import sys
from mediaserver import MediaServerClient

if len(sys.argv) != 3:
    print("Usage: python update_book_style.py <book_id> <style>")
    sys.exit(1)

book_id, style = sys.argv[1], sys.argv[2]

if style not in ("page", "scroll"):
    print("style must be 'page' or 'scroll'")
    sys.exit(1)

client = MediaServerClient()
client.login()

result = client.books.update_style(book_id, style=style)
print(f"Updated: {result}")

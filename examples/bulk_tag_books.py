"""Add a tag to one or more books (additive — existing tags are preserved).

Usage:
    python bulk_tag_books.py <tag> <book_id> [<book_id> ...]

Example:
    python bulk_tag_books.py "MC:Luffy" abc123 def456
"""

import sys
from mediaserver import MediaServerClient

if len(sys.argv) < 3:
    print("Usage: python bulk_tag_books.py <tag> <book_id> [<book_id> ...]")
    sys.exit(1)

new_tag = sys.argv[1]
book_ids = sys.argv[2:]

client = MediaServerClient()
client.login()

for book_id in book_ids:
    book = client.books.get_book(book_id)
    tags = book.get("tags", []) or []
    if new_tag not in tags:
        tags.append(new_tag)
        client.books.update_tags(book_id, tags)
        print(f"Tagged:          {book['name']}")
    else:
        print(f"Already tagged:  {book['name']}")

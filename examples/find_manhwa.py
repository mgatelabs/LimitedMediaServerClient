"""Find all manhwa (scroll-style) books and print them."""

from mediaserver import MediaServerClient

client = MediaServerClient()
client.login()

offset = 0
limit = 100
manhwa = []

while True:
    result = client.books.list_books(offset=offset, limit=limit)
    books = result.get("books", [])
    manhwa.extend(b for b in books if b.get("style") == "scroll")
    total = result.get("paging", {}).get("total", 0)
    offset += len(books)
    if offset >= total or not books:
        break

print(f"Found {len(manhwa)} manhwa books:")
for b in manhwa:
    print(f"  {b['id']}  {b['name']}")

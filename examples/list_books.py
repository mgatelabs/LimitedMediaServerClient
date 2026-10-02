"""List all books and print their name and style."""

from mediaserver import MediaServerClient

client = MediaServerClient()
client.login()

offset = 0
limit = 100

while True:
    result = client.books.list_books(offset=offset, limit=limit, sorting="AZ", rating_limit=200)
    books = result.get("books", [])

    for book in books:
        print(f"{book['name']:60s}  style={book.get('style', '?')}")

    total = result.get("paging", {}).get("total", 0)
    offset += len(books)
    if offset >= total or not books:
        break

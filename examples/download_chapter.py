"""Download the first chapter's images from a book to a local directory.

Usage:
    python download_chapter.py <book_id> [output_dir]

    output_dir defaults to ./downloaded_images/
"""

import base64
import sys
from pathlib import Path

from mediaserver import MediaServerClient

def download_chapter():
    if len(sys.argv) < 2:
        print("Usage: python download_chapter.py <book_id> [output_dir]")
        sys.exit(1)

    book_id = sys.argv[1]
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("downloaded_images")
    out_dir.mkdir(parents=True, exist_ok=True)

    client = MediaServerClient()
    client.login()

    chapters = client.books.list_chapters(book_id).get("chapters", [])
    if not chapters:
        print("No chapters found.")
        sys.exit(1)

    chapter_id = chapters[0]["value"]
    print(f"Downloading chapter: {chapters[0].get('name', chapter_id)}")

    images = client.books.list_images(book_id, chapter_id).get("files", [])
    print(f"  {len(images)} images found, downloading first 6...")

    for filename in images[:6]:
        data = client.books.get_image(book_id, chapter_id, filename)
        ext = ".jpg" if data["mime_type"] == "image/jpeg" else \
              ".png" if data["mime_type"] == "image/png" else \
              ".webp" if data["mime_type"] == "image/webp" else ".img"
        dest = out_dir / (Path(filename).stem + ext)
        dest.write_bytes(base64.b64decode(data["image_base64"]))
        print(f"  Saved {dest}")

    print("Done.")


if __name__ == '__main__':
    download_chapter()
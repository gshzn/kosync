import os
import base64
from pathlib import Path
from typing import Optional
import ebooklib
from ebooklib import epub
from pydantic import BaseModel



class BookMetadata(BaseModel):
    title: str
    author: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    language: Optional[str] = None
    description: Optional[str] = None


def extract_epub_metadata(file_path: Path) -> BookMetadata:
    """Extract metadata from EPUB file"""
    try:
        book = epub.read_epub(file_path)

        # Extract basic metadata
        title = book.get_metadata("DC", "title")
        author = book.get_metadata("DC", "creator")
        publisher = book.get_metadata("DC", "publisher")
        language = book.get_metadata("DC", "language")
        description = book.get_metadata("DC", "description")
        identifier = book.get_metadata("DC", "identifier")

        # Extract values from tuples (ebooklib returns tuples)
        title = title[0][0] if title else "Unknown Title"
        author = author[0][0] if author else "Unknown Author"
        publisher = publisher[0][0] if publisher else None
        language = language[0][0] if language else None
        description = description[0][0] if description else None
        isbn = identifier[0][0] if identifier else None

        return BookMetadata(
            title=title,
            author=author,
            publisher=publisher,
            isbn=isbn,
            language=language,
            description=description,
        )
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        # Return basic metadata with filename as title
        filename = os.path.basename(file_path)
        return BookMetadata(
            title=filename.replace(".epub", ""), author="Unknown Author"
        )


def extract_epub_cover(file_path: Path) -> Optional[bytes]:
    """Extract cover image from EPUB file"""
    try:
        book = epub.read_epub(file_path)

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_IMAGE:
                return item.get_content()

        return None
    except Exception as e:
        print(f"Error extracting cover: {e}")
        return None


def image_to_base64(image_data: bytes) -> str:
    """Convert image bytes to base64 string"""
    return base64.b64encode(image_data).decode("utf-8")

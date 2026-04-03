import os
import mimetypes
from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".doc": "docx",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".tiff": "image",
    ".tif": "image",
    ".bmp": "image",
    ".webp": "image",
}


def get_file_type(filename: str) -> str | None:
    """Return normalized file type or None if not supported."""
    ext = Path(filename).suffix.lower()
    return SUPPORTED_EXTENSIONS.get(ext)


def is_supported_file(filename: str) -> bool:
    """Check if the file extension is supported."""
    return get_file_type(filename) is not None


def get_supported_extensions() -> list[str]:
    """Return list of supported file extensions."""
    return list(SUPPORTED_EXTENSIONS.keys())

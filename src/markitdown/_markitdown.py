"""Core MarkItDown conversion engine.

This module provides the main MarkItDown class responsible for converting
various file formats and URLs to Markdown.
"""

from __future__ import annotations

import os
import re
import mimetypes
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse


class DocumentConverterResult:
    """Holds the result of a document conversion."""

    def __init__(self, title: Optional[str] = None, text_content: str = ""):
        self.title = title
        self.text_content = text_content

    def __str__(self) -> str:
        return self.text_content


class DocumentConverter:
    """Base class for all document converters."""

    def convert(
        self,
        local_path: str,
        **kwargs,
    ) -> Optional[DocumentConverterResult]:
        """Convert a document at the given local path to Markdown.

        Args:
            local_path: Path to the local file to convert.
            **kwargs: Additional keyword arguments for conversion options.

        Returns:
            A DocumentConverterResult if conversion succeeded, else None.
        """
        raise NotImplementedError("Subclasses must implement convert()")


class MarkItDown:
    """Main class for converting documents to Markdown.

    Supports converting local files, URLs, and streams to Markdown format.
    Converters can be registered for specific MIME types or file extensions.

    Example::

        md = MarkItDown()
        result = md.convert("document.pdf")
        print(result.text_content)
    """

    def __init__(self):
        self._converters: list[tuple[list[str], DocumentConverter]] = []
        self._register_default_converters()

    def _register_default_converters(self) -> None:
        """Register built-in converters for common file types."""
        # Converters are imported lazily to avoid heavy dependencies at import time
        from markitdown.converters import (
            PlainTextConverter,
            HtmlConverter,
        )

        self.register_converter(["text/plain", ".txt", ".md", ".rst"], PlainTextConverter())
        self.register_converter(["text/html", ".html", ".htm"], HtmlConverter())

    def register_converter(
        self, matchers: list[str], converter: DocumentConverter
    ) -> None:
        """Register a converter for the given MIME types or file extensions.

        Args:
            matchers: List of MIME types (e.g. 'text/html') or file extensions
                      (e.g. '.pdf') this converter handles.
            converter: The converter instance to register.
        """
        self._converters.append((matchers, converter))

    def convert(
        self,
        source: Union[str, Path],
        **kwargs,
    ) -> DocumentConverterResult:
        """Convert a file or URL to Markdown.

        Args:
            source: A file path or URL to convert.
            **kwargs: Additional options forwarded to the underlying converter.

        Returns:
           

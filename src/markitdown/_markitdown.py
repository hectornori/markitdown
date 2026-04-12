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

        self.register_converter(["text/plain", ".txt", ".md"], PlainTextConverter())
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
            A DocumentConverterResult containing the Markdown text.

        Raises:
            FileNotFoundError: If a local file path does not exist.
            ValueError: If no suitable converter is found for the source.
        """
        source = str(source)

        # Determine if source is a URL or a local path
        parsed = urlparse(source)
        if parsed.scheme in ("http", "https"):
            return self._convert_url(source, **kwargs)

        local_path = os.path.abspath(source)
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"File not found: {local_path}")

        return self._convert_local(local_path, **kwargs)

    def _convert_local(
        self, local_path: str, **kwargs
    ) -> DocumentConverterResult:
        """Attempt conversion of a local file using registered converters."""
        mime_type, _ = mimetypes.guess_type(local_path)
        extension = Path(local_path).suffix.lower()

        for matchers, converter in reversed(self._converters):
            if extension in matchers or (mime_type and mime_type in matchers):
                result = converter.convert(local_path, **kwargs)
                if result is not None:
                    return result

        raise ValueError(
            f"No converter found for file: {local_path} "
            f"(mime={mime_type}, ext={extension})"
        )

    def _convert_url(
        self, url: str, **kwargs
    ) -> DocumentConverterResult:
        """Download and convert a URL to Markdown."""
        import urllib.request
        import tempfile

        with urllib.request.urlopen(url) as response:  # noqa: S310
            content_type = response.headers.get_content_type()
            suffix = mimetypes.guess_extension(content_type) or ".html"
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=suffix
            ) as tmp_file:
                tmp_file.write(response.read())
                tmp_path = tmp_file.name

        try:
            return self._convert_local(tmp_path, **kwargs)
        finally:
            os.unlink(tmp_path)

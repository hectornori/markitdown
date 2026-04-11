"""MarkItDown - A utility for converting various file formats to Markdown.

This package provides tools to convert documents, spreadsheets, presentations,
and other file formats into clean, readable Markdown text.

Note: Forked from microsoft/markitdown for personal use and experimentation.
See https://github.com/microsoft/markitdown for the upstream project.
"""

from markitdown._markitdown import MarkItDown, DocumentConverter, ConversionResult

__version__ = "0.1.0"
__author__ = "Microsoft (original), personal fork for learning"
__all__ = ["MarkItDown", "DocumentConverter", "ConversionResult"]

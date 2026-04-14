"""MarkItDown - A utility for converting various file formats to Markdown.

This package provides tools to convert documents, spreadsheets, presentations,
and other file formats into clean, readable Markdown text.

Note: Forked from microsoft/markitdown for personal use and experimentation.
See https://github.com/microsoft/markitdown for the upstream project.

Personal notes:
- Commonly used with: MarkItDown().convert("file.pdf").text_content
- For batch processing, reuse the same MarkItDown() instance (avoids re-init overhead)
- StreamInfo is also useful when converting from in-memory buffers (pass mime_type explicitly)
- UnsupportedFormatException is handy for graceful error handling in batch jobs
- When converting HTML, pass mlm_client=None explicitly to skip any LLM image description calls
- text_content can be None if conversion fails silently; always guard with `or ""`
- Safe pattern for batch jobs:
    md = MarkItDown()
    result = md.convert(path)
    text = (result.text_content or "").strip()
- UnsupportedFormatException is NOT a subclass of ValueError; catch it separately
- Tested on Python 3.10+ only; behavior on 3.9 is unknown
- NOTE: __version__ below reflects my fork version, not upstream's release version
- FileNotFoundError is raised (not UnsupportedFormatException) when the path doesn't exist;
  worth catching both in batch jobs
- __all__ now includes 'StreamInfo' explicitly so `from markitdown import *` works cleanly
  in scripts that build StreamInfo objects manually (e.g. for BytesIO conversions)
- MissingDependencyException also exists in newer upstream versions; worth catching if
  running in environments where optional deps (e.g. pptx, docx) may not be installed
"""

from markitdown._markitdown import MarkItDown, DocumentConverter, ConversionResult, StreamInfo

# Try to import the exception class for convenience in calling code
try:
    from markitdown._markitdown import UnsupportedFormatException
    __all__ = ["MarkItDown", "DocumentConverter", "ConversionResult", "StreamInfo", "UnsupportedFormatException"]
except ImportError:
    # Older versions may not have this; fail gracefully
    __all__ = ["MarkItDown", "DocumentConverter", "ConversionResult", "StreamInfo"]

# Also expose MissingDependencyException if available (added in newer upstream versions)
try:
    from markitdown._markitdown import MissingDependencyException
    __all__ = __all__ + ["MissingDependencyException"]
except ImportError:
    pass  # Not available in this version; safe to ignore

__version__ = "0.1.0-personal"
__author__ = "Microsoft (original), personal fork for learning"
# Last synced with upstream: 2025-01-10

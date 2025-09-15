"""
This module serves as the public API facade for the Google Docs tool package.
It re-exports the main functions from the internal modules.
"""

from .append import append_to_google_doc
from .clear import clear_google_doc
from .replace import replace_markdown_placeholders
from .write import write_to_google_doc
from .read import read_google_doc

__all__ = [
    'append_to_google_doc',
    'clear_google_doc',
    'replace_markdown_placeholders',
    'write_to_google_doc',
    'read_google_doc',
]

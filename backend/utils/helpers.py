"""
Miscellaneous helper utilities shared across the backend.

This module intentionally remains minimal and framework-agnostic. It provides
small, composable utilities that:
- Manipulate or merge context dictionaries for agents.
- Provide convenience functions for safe lookups and defaults.

Keeping these helpers centralized avoids copy-paste logic inside individual
agents or controllers and makes it easier to evolve shared patterns for
agentic context handling.
"""

import io
from typing import Any, Dict, Mapping

from pypdf import PdfReader  # type: ignore


def merge_context(base: Mapping[str, Any], updates: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Create a new context dictionary by shallow-merging two mappings.

    This utility is helpful when composing agent outputs into a shared context
    object. It keeps the merge logic explicit and testable.

    Parameters
    ----------
    base:
        Original context mapping.
    updates:
        New values to overlay on top of the base context.

    Returns
    -------
    Dict[str, Any]
        A new dictionary containing keys from both `base` and `updates`, where
        `updates` takes precedence on conflict.
    """
    merged: Dict[str, Any] = dict(base)
    merged.update(updates)
    return merged


def get_from_context(context: Mapping[str, Any], key: str, default: Any = None) -> Any:
    """
    Helper for safe lookups in the shared agent context.

    This makes it explicit when a value might be absent and provides a
    consistent place to add any future logging or validation related to
    missing keys.
    """
    return context.get(key, default)


def extract_text_from_resume(file_bytes: bytes) -> str:
    """
    Extract text from an uploaded resume file.

    In a production system, this function would:
    - Detect file type (PDF, DOC, DOCX, etc.).
    - Use an appropriate parser library (e.g., pdfplumber, python-docx).
    - Normalize whitespace and encoding issues.

    Currently supported:
    - PDF (bytes) using `pypdf`.
    """
    if not file_bytes:
        raise ValueError("Empty resume file upload.")

    # PDF magic header: %PDF
    if file_bytes.startswith(b"%PDF"):
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            text = "".join([(page.extract_text() or "") for page in reader.pages]).strip()
        except Exception as exc:
            raise ValueError(f"PDF extraction failed: {str(exc)}") from exc
    # ZIP magic header: PK.. (used by DOCX)
    elif file_bytes.startswith(b"PK\x03\x04"):
        try:
            import docx  # type: ignore
            doc = docx.Document(io.BytesIO(file_bytes))
            text = "\n".join([para.text for para in doc.paragraphs]).strip()
        except Exception as exc:
            raise ValueError(f"DOCX extraction failed: {str(exc)}") from exc
    else:
        raise ValueError("Unsupported resume format. Please upload a PDF or DOCX resume.")

    if not text:
        raise ValueError(
            "Unable to extract text from file. Please ensure it is text-based."
        )

    return text


__all__ = ["merge_context", "get_from_context", "extract_text_from_resume"]


from __future__ import annotations

import base64
import io
import zipfile
from xml.etree import ElementTree

from ..models.schemas import SourceFileContent

MAX_EXTRACTED_CHARACTERS = 20_000


def extract_source_documents(files: list[SourceFileContent]) -> list[tuple[str, str]]:
    """Extract bounded text from supported engineering source files."""
    extracted: list[tuple[str, str]] = []
    total_characters = 0

    for source_file in files:
        content = base64.b64decode(source_file.content_base64, validate=True)
        extension = source_file.name.rsplit(".", 1)[-1].lower()

        if extension in {"yaml", "yml", "json", "txt", "md"}:
            try:
                text = content.decode("utf-8-sig").strip()
            except UnicodeDecodeError as exc:
                raise ValueError(f"{source_file.name} must be UTF-8 text") from exc
        elif extension == "pdf":
            text = _extract_pdf(source_file.name, content)
        elif extension == "docx":
            text = _extract_docx(source_file.name, content)
        else:  # schema validation should prevent this branch
            raise ValueError(f"Unsupported engineering document: {source_file.name}")

        if not text.strip():
            raise ValueError(f"No readable text was found in {source_file.name}")
        total_characters += len(text)
        if total_characters > MAX_EXTRACTED_CHARACTERS:
            raise ValueError("Extracted engineering documents exceed the 20,000 character analysis limit")
        extracted.append((source_file.name, text))

    return extracted


def _extract_pdf(name: str, content: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("Install pypdf to read PDF engineering documents") from exc

    try:
        reader = PdfReader(io.BytesIO(content), strict=False)
        if len(reader.pages) > 100:
            raise ValueError(f"{name} exceeds the 100 page PDF limit")
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Could not read PDF document {name}") from exc


def _extract_docx(name: str, content: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            document_info = archive.getinfo("word/document.xml")
            if document_info.file_size > 2_000_000:
                raise ValueError(f"{name} contains an oversized Word document body")
            xml_content = archive.read(document_info)
        root = ElementTree.fromstring(xml_content)
    except (KeyError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
        raise ValueError(f"Could not read Word document {name}") from exc

    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    return "\n".join(
        "".join(node.itertext()).strip()
        for node in root.findall(".//w:p", namespace)
        if "".join(node.itertext()).strip()
    )

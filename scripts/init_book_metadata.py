#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OBSIDIAN_EXPORT = ROOT / "obsidian-export"
SESSION_KNOWLEDGE = ROOT / "session-knowledge"


REQUIRED_KEYS = [
    "book_id",
    "title",
    "author",
    "publication_year",
    "publisher",
    "edition",
    "isbn",
    "pages",
    "original_language",
    "genres",
    "topics",
    "source_format",
    "source_path",
    "date_added",
    "reading_status",
    "rating",
    "tags",
]


def slug_to_title(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.replace("_", "-").split("-") if part)


def infer_source_format(source_path: str | None) -> str | None:
    if not source_path:
        return None
    ext = Path(source_path).suffix.lower()
    if ext == ".pdf":
        return "PDF"
    if ext == ".epub":
        return "EPUB"
    if ext == ".txt":
        return "TXT"
    return None


def parse_existing_source_md(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    out: dict[str, Any] = {}

    m_title_h2 = re.search(r"^##\s+(.+)$", text, flags=re.MULTILINE)
    if m_title_h2:
        out["title"] = m_title_h2.group(1).strip()

    m_author = re.search(r"\*\*Author\*\*:\s*(.+)", text)
    if m_author:
        out["author"] = [m_author.group(1).strip()]

    m_lang = re.search(r"\*\*Language\*\*:\s*(.+)", text)
    if m_lang:
        out["original_language"] = m_lang.group(1).strip()

    m_source = re.search(r"Original\s+PDF:\s*(.+)", text)
    if m_source:
        out["source_path"] = m_source.group(1).strip()
        out["source_format"] = infer_source_format(out["source_path"])

    return out


def parse_unified_metadata(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    meta = payload.get("metadata") or {}
    stats = payload.get("document_statistics") or {}
    summary = payload.get("summary") or {}

    topics: list[str] = []
    for item in (summary.get("core_concepts") or []):
        concept = item.get("concept") if isinstance(item, dict) else None
        if concept:
            topics.append(str(concept))
    topics = topics[:12]

    author_value = meta.get("author")
    author = author_value if isinstance(author_value, list) else [str(author_value)] if author_value else []

    return {
        "title": meta.get("title"),
        "author": author,
        "original_language": meta.get("language"),
        "pages": stats.get("total_pages"),
        "date_added": meta.get("creation_date"),
        "topics": topics,
    }


def yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value).replace('"', '\\"')
    return f'"{s}"'


def to_yaml_frontmatter(data: dict[str, Any]) -> str:
    lines: list[str] = ["---"]
    for key in REQUIRED_KEYS:
        value = data.get(key)
        if isinstance(value, list):
            lines.append(f"{key}:")
            if value:
                for item in value:
                    lines.append(f"  - {yaml_scalar(item)}")
            else:
                lines.append("  []")
        else:
            lines.append(f"{key}: {yaml_scalar(value)}")
    lines.append("---")
    return "\n".join(lines)


def merge_metadata(book_id: str, vault_dir: Path | None) -> dict[str, Any]:
    metadata_dir = vault_dir / "METADATA" if vault_dir else None
    source_md = metadata_dir / "_source-book.md" if metadata_dir else None
    unified = SESSION_KNOWLEDGE / book_id / "unified-knowledge.json"

    merged: dict[str, Any] = {
        "book_id": book_id,
        "title": slug_to_title(book_id),
        "author": [],
        "publication_year": None,
        "publisher": None,
        "edition": None,
        "isbn": None,
        "pages": None,
        "original_language": None,
        "genres": [],
        "topics": [],
        "source_format": None,
        "source_path": None,
        "date_added": date.today().isoformat(),
        "reading_status": "completed",
        "rating": None,
        "tags": ["book", "book-studio", book_id],
    }

    if vault_dir is None:
        merged["reading_status"] = "in_progress"

    for payload in (parse_unified_metadata(unified), parse_existing_source_md(source_md) if source_md else {}):
        for key, value in payload.items():
            if value in (None, "", []):
                continue
            merged[key] = value

    if not merged["source_format"]:
        merged["source_format"] = infer_source_format(merged.get("source_path"))

    if isinstance(merged.get("author"), str):
        merged["author"] = [merged["author"]]

    if not merged.get("title"):
        merged["title"] = slug_to_title(book_id)

    return merged


def write_metadata_files(book_id: str, vault_dir: Path) -> None:
    metadata = merge_metadata(book_id, vault_dir)
    metadata_dir = vault_dir / "METADATA"
    metadata_dir.mkdir(parents=True, exist_ok=True)

    source_path = metadata_dir / "_source-book.md"
    vault_json_path = metadata_dir / "_vault-metadata.json"

    frontmatter = to_yaml_frontmatter(metadata)
    source_body = (
        f"{frontmatter}\n\n"
        "# Source Book Metadata\n\n"
        "This file contains canonical bibliographic and processing metadata for the book.\n"
    )
    source_path.write_text(source_body, encoding="utf-8")

    json_payload = {key: metadata.get(key) for key in REQUIRED_KEYS}
    vault_json_path.write_text(json.dumps(json_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def collect_book_ids() -> set[str]:
    ids: set[str] = set()

    if OBSIDIAN_EXPORT.exists():
        for entry in OBSIDIAN_EXPORT.iterdir():
            if entry.is_dir() and not entry.name.startswith("."):
                ids.add(entry.name)

    if SESSION_KNOWLEDGE.exists():
        for entry in SESSION_KNOWLEDGE.iterdir():
            if entry.is_dir() and not entry.name.startswith("."):
                ids.add(entry.name)

    return ids


def main() -> None:
    book_ids = sorted(collect_book_ids())
    if not book_ids:
        print("No processed books found.")
        return

    for book_id in book_ids:
        vault_dir = OBSIDIAN_EXPORT / book_id
        if not vault_dir.exists():
            vault_dir.mkdir(parents=True, exist_ok=True)
        write_metadata_files(book_id, vault_dir)
        print(f"initialized metadata: {book_id}")


if __name__ == "__main__":
    main()

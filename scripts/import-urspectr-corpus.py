#!/usr/bin/env python3
"""Import ЮрСпектр corpus (5 docx) into Docs-as-Code content model.

Step 2: sources + document manifests (full assembled docs).
Shared-block extraction is a separate step.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from docx import Document

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
DOCS = CONTENT / "documents"
SOURCES = CONTENT / "sources"
SRC_DIR = Path(r"D:\urspectr\20261001")

CORPUS = [
    {
        "file": "1497_BEPPN.docx",
        "slug": "drivers-cars",
        "doc_id": "hr.drivers-cars",
        "title": "Путеводитель по кадровым вопросам. Водители легковых автомобилей (ООО «ЮрСпектр»)",
        "topics": ["drivers", "procedure"],
    },
    {
        "file": "514_BEPPN.docx",
        "slug": "disciplinary",
        "doc_id": "hr.disciplinary",
        "title": "Путеводитель по кадровым вопросам. Дисциплинарная ответственность (ООО «ЮрСпектр»)",
        "topics": ["discipline", "procedure"],
    },
    {
        "file": "633_BEPPN.docx",
        "slug": "suspension",
        "doc_id": "hr.suspension",
        "title": "Путеводитель по кадровым вопросам. Отстранение от работы (ООО «ЮрСпектр»)",
        "topics": ["suspension", "procedure"],
    },
    {
        "file": "718_BEPPN.docx",
        "slug": "labor-protection",
        "doc_id": "hr.labor-protection",
        "title": "Путеводитель по кадровым вопросам. Охрана труда в организации (ООО «ЮрСпектр»)",
        "topics": ["labor-protection", "procedure"],
    },
    {
        "file": "94962_BEPBI.docx",
        "slug": "disciplinary-algorithm",
        "doc_id": "hr.disciplinary-algorithm",
        "title": "Алгоритм. Привлечение работника к дисциплинарной ответственности (ООО «ЮрСпектр»)",
        "topics": ["discipline", "algorithm", "procedure"],
    },
]


def para_lines(doc: Document) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for p in doc.paragraphs:
        text = (p.text or "").strip()
        if not text:
            continue
        style = p.style.name if p.style else "Normal"
        rows.append((style, text))
    return rows


def to_md_lines(rows: list[tuple[str, str]]) -> list[str]:
    out: list[str] = []
    for _style, text in rows:
        if re.fullmatch(r"Глава\s+\d+", text):
            out.append(f"# {text}")
        elif re.fullmatch(r"Шаг\s+\d+\..*", text) or re.match(r"^Шаг\s+\d+\.", text):
            out.append(f"## {text}")
        elif re.match(r"^\d+\.\d+\.\s+", text):
            out.append(f"## {text}")
        elif re.match(r"^\d+\.\s+", text) and len(text) < 180:
            out.append(f"### {text}")
        elif text in {"Обратите внимание!", "Важно!", "Справка"}:
            out.append(f"**{text}**")
        elif text.startswith("- "):
            out.append(text)
        else:
            out.append(text)
        out.append("")
    return out


def split_chapters(md_lines: list[str]) -> dict[str, list[str]]:
    chapters: dict[str, list[str]] = {}
    current = "preamble"
    buf: list[str] = []
    for line in md_lines:
        m = re.match(r"^# (Глава\s+(\d+))\s*$", line)
        if m:
            if buf:
                chapters[current] = buf
            current = f"chapter-{m.group(2)}"
            buf = [line, ""]
        else:
            buf.append(line)
    if buf:
        chapters[current] = buf
    return chapters


def write_document_yml(item: dict, source_rel: str) -> None:
    topics = ", ".join(item["topics"])
    yml = f"""id: {item["doc_id"]}
title: {item["title"]}
content_type: assembled_document
owner: hr-policy-owner
approver: legal-owner
lifecycle: effective
valid_from: "2026-09-01"
topics: [{", ".join(repr(t) for t in item["topics"])}]

sections:
  - heading: О документе
    body: >
      Материал ООО «ЮрСпектр», актуально на 01.09.2026.
      Ниже — полный текст. Общие нормативные блоки (если есть)
      выделяются при пересборке и правятся отдельно в CMS.

  - heading: Полный текст
    file_ref: {source_rel}
"""
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / f"{item['doc_id']}.yml").write_text(yml, encoding="utf-8")


def import_one(item: dict) -> None:
    src = SRC_DIR / item["file"]
    if not src.exists():
        raise SystemExit(f"Missing source: {src}")

    out_dir = SOURCES / item["slug"]
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    shutil.copy2(src, out_dir / item["file"])

    doc = Document(str(src))
    rows = para_lines(doc)
    md_lines = to_md_lines(rows)
    full_text = "\n".join(md_lines).strip() + "\n"
    (out_dir / "full.md").write_text(full_text, encoding="utf-8")

    chapters = split_chapters(md_lines)
    for name, lines in chapters.items():
        (out_dir / f"{name}.md").write_text(
            "\n".join(lines).strip() + "\n", encoding="utf-8"
        )

    readme = f"""# {item["title"]}

- Source file: `{item["file"]}`
- Doc id: `{item["doc_id"]}`
- Topics: {", ".join(item["topics"])}
- Valid from: 2026-09-01
"""
    (out_dir / "README.md").write_text(readme, encoding="utf-8")

    source_rel = f"content/sources/{item['slug']}/full.md"
    write_document_yml(item, source_rel)

    print(
        f"OK {item['doc_id']}: paras≈{len(rows)} "
        f"chapters={len(chapters)} -> {out_dir}"
    )


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    SOURCES.mkdir(parents=True, exist_ok=True)
    for item in CORPUS:
        import_one(item)
    print(f"Imported {len(CORPUS)} documents from {SRC_DIR}")


if __name__ == "__main__":
    main()

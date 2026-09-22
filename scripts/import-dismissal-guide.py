#!/usr/bin/env python3
"""Import ЮрСпектр dismissal guide into Docs-as-Code content model."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from docx import Document

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
BLOCKS = CONTENT / "blocks"
DOCS = CONTENT / "documents"
SOURCES = CONTENT / "sources" / "dismissal"
SRC_DIR = Path(r"d:/urspectr/20260922")


def find_docx() -> Path:
    files = list(SRC_DIR.glob("*.docx"))
    if not files:
        raise SystemExit(f"No docx in {SRC_DIR}")
    return files[0]


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


SHARED_BLOCKS = [
    {
        "id": "reg.dismissal.workbook-issue.2026",
        "series_id": "reg.dismissal.workbook-issue",
        "title": "Запись в трудовую книжку и выдача в день увольнения",
        "topics": ["dismissal", "workbook", "procedure"],
        "body": (
            "Об увольнении вносится соответствующая запись в трудовую книжку "
            "(вкладыш к ней). Трудовая книжка выдается в день увольнения "
            "(в последний день работы) (ч. 6 ст. 50 ТК). При получении трудовой "
            "книжки работник должен расписаться в книге учета движения трудовых "
            "книжек и вкладышей к ним (ч. 5 п. 79 Инструкции о трудовых книжках)."
        ),
    },
    {
        "id": "reg.dismissal.workbook-wording.2026",
        "series_id": "reg.dismissal.workbook-wording",
        "title": "Формулировка причины увольнения в трудовой книжке",
        "topics": ["dismissal", "workbook"],
        "body": (
            "Записи о причинах увольнения в трудовой книжке должны производиться "
            "в точном соответствии с формулировкой приказа (распоряжения) "
            "(ч. 3 п. 26 Инструкции о трудовых книжках)."
        ),
    },
    {
        "id": "reg.dismissal.final-settlement.2026",
        "series_id": "reg.dismissal.final-settlement",
        "title": "Полный расчет в день увольнения",
        "topics": ["dismissal", "settlement", "payroll"],
        "body": (
            "Все выплаты, причитающиеся увольняемому работнику на день увольнения "
            "(кроме выплат, установленных системами оплаты труда, размер которых "
            "определяется по результатам работы за месяц или иной отчетный период), "
            "должны быть произведены не позднее дня увольнения (ч. 1 ст. 77 ТК). "
            "Выплаты, установленные системами оплаты труда, размер которых "
            "определяется по результатам работы за месяц или иной отчетный период, "
            "производятся в порядке, установленном локальными правовыми актами, "
            "не позднее дня выплаты заработной платы за отчетный период работникам "
            "организации (ч. 4 ст. 77 ТК)."
        ),
    },
    {
        "id": "reg.dismissal.settlement-delay.2026",
        "series_id": "reg.dismissal.settlement-delay",
        "title": "Ответственность за задержку расчета и трудовой книжки",
        "topics": ["dismissal", "settlement", "liability"],
        "body": (
            "В случае задержки выдачи трудовой книжки или задержки осуществления "
            "полного расчета по вине нанимателя для него это может повлечь "
            "последствия, предусмотренные ст. 78 и 79 ТК."
        ),
    },
    {
        "id": "reg.dismissal.personal-file-order.2026",
        "series_id": "reg.dismissal.personal-file-order",
        "title": "Копия приказа об увольнении в личное дело",
        "topics": ["dismissal", "personal-file", "procedure"],
        "body": (
            "Копия распорядительного документа об увольнении работника должна "
            "включаться в состав документов личного дела работника (если оно "
            "заводилось на соответствующего работника). Далее личное дело "
            "завершается делопроизводством и передается в архив организации."
        ),
    },
    {
        "id": "reg.dismissal.personal-card.2026",
        "series_id": "reg.dismissal.personal-card",
        "title": "Ознакомление с записью в личной карточке",
        "topics": ["dismissal", "personal-file"],
        "body": (
            "Наниматель может ознакомить работника с записью об увольнении в "
            "личной карточке, если она заводилась и в ней предусмотрено место "
            "для такого ознакомления."
        ),
    },
    {
        "id": "reg.dismissal.military-notice.2026",
        "series_id": "reg.dismissal.military-notice",
        "title": "Уведомление военкомата об увольнении",
        "topics": ["dismissal", "military-registration"],
        "body": (
            "Если работник состоит или обязан состоять на воинском учете, лица, "
            "ответственные за воинский учет, обязаны сообщить сведения о его "
            "увольнении в месячный срок в военный комиссариат (обособленное "
            "подразделение), а такие сведения о военнообязанном, состоящем или "
            "обязанном состоять в запасе органов государственной безопасности, "
            "— в управление Комитета государственной безопасности по области "
            "(абз. 2 ч. 1 ст. 9 Закона о воинской обязанности)."
        ),
    },
    {
        "id": "reg.dismissal.day-not-on-leave.2026",
        "series_id": "reg.dismissal.day-not-on-leave",
        "title": "День увольнения не в отпуске и не в период нетрудоспособности",
        "topics": ["dismissal", "restrictions"],
        "body": (
            "Следует помнить, что день увольнения не должен приходиться на время "
            "пребывания работника в отпуске либо на период временной "
            "нетрудоспособности (ч. 2 ст. 43 ТК)."
        ),
    },
    {
        "id": "reg.dismissal.union-notice.2026",
        "series_id": "reg.dismissal.union-notice",
        "title": "Предварительное уведомление профсоюза",
        "topics": ["dismissal", "union"],
        "body": (
            "Расторжение трудового договора по рассматриваемому основанию "
            "производится после предварительного, но не позднее чем за две "
            "недели уведомления соответствующего профсоюза (ч. 1 ст. 46 ТК)."
        ),
    },
    {
        "id": "reg.dismissal.written-explanation.2026",
        "series_id": "reg.dismissal.written-explanation",
        "title": "Отказ от письменного объяснения при дисциплинарном проступке",
        "topics": ["dismissal", "discipline"],
        "body": (
            "Отказ работника от дачи письменного объяснения, невозможность "
            "получения от него объяснения по поводу совершенного дисциплинарного "
            "проступка не являются препятствиями для применения дисциплинарного "
            "взыскания и оформляются актом с указанием присутствовавших при этом "
            "свидетелей (ч. 2 ст. 199 ТК)."
        ),
    },
]


CHAPTER_META = {
    "1": {
        "id": "hr.dismissal.ch01",
        "title": "Глава 1. Общие положения о расторжении трудового договора",
        "topics": ["dismissal", "procedure"],
    },
    "2": {
        "id": "hr.dismissal.ch02",
        "title": "Глава 2. Расторжение по общим основаниям (ст. 35 ТК)",
        "topics": ["dismissal", "agreement", "fixed-term"],
    },
    "3": {
        "id": "hr.dismissal.ch03",
        "title": "Глава 3. Расторжение по инициативе нанимателя (ст. 42 ТК)",
        "topics": ["dismissal", "employer-initiative"],
    },
    "4": {
        "id": "hr.dismissal.ch04",
        "title": "Глава 4. Расторжение по требованию или желанию работника",
        "topics": ["dismissal", "employee-initiative"],
    },
    "5": {
        "id": "hr.dismissal.ch05",
        "title": "Глава 5. Расторжение по обстоятельствам, не зависящим от воли сторон",
        "topics": ["dismissal", "independent-grounds"],
    },
    "6": {
        "id": "hr.dismissal.ch06",
        "title": "Глава 6. Дополнительные основания расторжения",
        "topics": ["dismissal", "special-grounds"],
    },
}


def yaml_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def write_block(meta: dict, body: str) -> None:
    topics = "\n".join(f"  - {t}" for t in meta["topics"])
    content = f"""---
id: {meta['id']}
series_id: {meta['series_id']}
title: {meta['title']}
content_type: regulatory_block
jurisdiction: BY
owner: hr-policy-owner
approver: legal-owner
lifecycle: effective
valid_from: 2026-09-01
valid_to: null
topics:
{topics}
source: urspectr-dismissal-guide-2026-09-01
---

{body.strip()}
"""
    path = BLOCKS / f"{meta['id']}.mdx"
    path.write_text(content, encoding="utf-8")
    print("block", path.name)


def write_chapter_block(num: str, md: str) -> None:
    meta = CHAPTER_META[num]
    # Keep chapter pages manageable for portal; full text stays in sources/
    max_chars = 12000
    body = md.strip()
    if len(body) > max_chars:
        cut = body[:max_chars]
        cut = cut.rsplit("\n\n", 1)[0]
        body = (
            cut
            + "\n\n> Полный текст главы сохранён в `content/sources/dismissal/"
            + f"chapter-{num}.md` (актуально на 01.09.2026)."
        )
    block_meta = {
        "id": f"{meta['id']}.2026",
        "series_id": meta["id"],
        "title": meta["title"],
        "topics": meta["topics"],
    }
    write_block(block_meta, body)


def write_main_document() -> None:
    doc = Path(__file__).resolve().parents[1] / "content" / "documents" / "hr.dismissal-guide.yml"
    # Keep the checked-in unified manifest; only ensure it exists after re-import.
    if not doc.exists():
        raise SystemExit("Missing hr.dismissal-guide.yml — restore from repo")
    print("document", doc.name, "(kept)")


def write_procedure_document() -> None:
    doc = """id: hr.dismissal.closing-procedure
title: Общая процедура оформления увольнения (сквозные требования)
content_type: assembled_document
owner: hr-policy-owner
approver: legal-owner
lifecycle: effective
valid_from: "2026-09-01"

sections:
  - heading: Назначение
    body: >
      Документ собирает нормативные требования, которые повторяются
      при оформлении увольнения по большинству оснований: расчет,
      трудовая книжка, личное дело, воинский учет и ограничения
      по дню увольнения.

  - heading: День увольнения
    block_ref: reg.dismissal.day-not-on-leave

  - heading: Полный расчет
    block_ref: reg.dismissal.final-settlement

  - heading: Трудовая книжка
    block_ref: reg.dismissal.workbook-issue

  - heading: Формулировка причины увольнения
    block_ref: reg.dismissal.workbook-wording

  - heading: Личное дело
    block_ref: reg.dismissal.personal-file-order

  - heading: Личная карточка
    block_ref: reg.dismissal.personal-card

  - heading: Воинский учет
    block_ref: reg.dismissal.military-notice

  - heading: Ответственность за задержку
    block_ref: reg.dismissal.settlement-delay

  - heading: Уведомление профсоюза (где применимо)
    block_ref: reg.dismissal.union-notice

  - heading: Письменные объяснения (дисциплинарные случаи)
    block_ref: reg.dismissal.written-explanation
"""
    path = DOCS / "hr.dismissal.closing-procedure.yml"
    path.write_text(doc, encoding="utf-8")
    print("document", path.name)


def write_taxonomy_glossary() -> None:
    (CONTENT / "taxonomy" / "topics.yml").write_text(
        """topics:
  - id: dismissal
    title: Увольнение
  - id: procedure
    title: Кадровая процедура
  - id: workbook
    title: Трудовая книжка
  - id: settlement
    title: Расчет при увольнении
  - id: personal-file
    title: Личное дело
  - id: military-registration
    title: Воинский учет
  - id: employer-initiative
    title: Инициатива нанимателя
  - id: employee-initiative
    title: Инициатива работника
  - id: agreement
    title: Соглашение сторон
  - id: fixed-term
    title: Срочный трудовой договор
  - id: independent-grounds
    title: Обстоятельства, не зависящие от воли сторон
  - id: special-grounds
    title: Дополнительные основания
  - id: union
    title: Профсоюз
  - id: discipline
    title: Дисциплинарная ответственность
  - id: payroll
    title: Оплата труда
  - id: liability
    title: Ответственность нанимателя
  - id: restrictions
    title: Ограничения при увольнении
""",
        encoding="utf-8",
    )
    (CONTENT / "glossary" / "terms.yml").write_text(
        """terms:
  - preferred: Наниматель
    rejected:
      - Работодатель
      - Employer

  - preferred: Работник
    rejected:
      - Сотрудник
      - Employee

  - preferred: Трудовой договор (контракт)
    rejected:
      - Контракт без уточнения
      - ТД

  - preferred: Расторжение трудового договора
    rejected:
      - Увольнение без правовой квалификации
      - Прекращение без ссылки на ТК

  - preferred: день увольнения
    rejected:
      - последний рабочий день без уточнения статуса
""",
        encoding="utf-8",
    )


def clear_old_content() -> None:
    for folder in (BLOCKS, DOCS):
        if folder.exists():
            for p in folder.iterdir():
                if p.is_file():
                    p.unlink()
                    print("removed", p.relative_to(ROOT))


def main() -> None:
    docx_path = find_docx()
    print("source:", docx_path.name)

    clear_old_content()
    BLOCKS.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    SOURCES.mkdir(parents=True, exist_ok=True)

    rows = para_lines(Document(str(docx_path)))
    md_lines = to_md_lines(rows)
    full_md = "\n".join(md_lines).strip() + "\n"
    (SOURCES / "full.md").write_text(
        "# Путеводитель по кадровым вопросам. Увольнение\n\n"
        "Источник: ООО «ЮрСпектр», актуально на 01.09.2026.\n\n"
        + full_md,
        encoding="utf-8",
    )
    print("wrote", SOURCES / "full.md", "chars", len(full_md))

    chapters = split_chapters(md_lines)
    for key, lines in chapters.items():
        if not key.startswith("chapter-"):
            (SOURCES / "preamble.md").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
            continue
        num = key.split("-")[1]
        text = "\n".join(lines).strip() + "\n"
        (SOURCES / f"chapter-{num}.md").write_text(text, encoding="utf-8")
        print("source chapter", num, "chars", len(text))

    for meta in SHARED_BLOCKS:
        write_block(meta, meta["body"])

    write_main_document()
    write_procedure_document()
    write_taxonomy_glossary()

    # Keep a short provenance note
    (SOURCES / "README.md").write_text(
        "# Источник\n\n"
        f"- Файл: `{docx_path.name}`\n"
        "- Актуально на: 01.09.2026\n"
        "- Издатель: ООО «ЮрСпектр»\n"
        "- Импорт: `scripts/import-dismissal-guide.py`\n",
        encoding="utf-8",
    )
    print("done")


if __name__ == "__main__":
    main()

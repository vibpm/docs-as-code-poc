#!/usr/bin/env python3
"""Analyze and extract shared regulatory blocks from imported corpus."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "content" / "sources"
BLOCKS = ROOT / "content" / "blocks"
DOCS = ROOT / "content" / "documents"

# Manually curated block catalog after analysis (filled by analyze + review).
# series_id -> {title, topics, body, min_count}
# We will auto-build from high-frequency paragraphs.


def paras_from_md(text: str, min_len: int = 80) -> list[str]:
    chunks = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    out: list[str] = []
    for c in chunks:
        if c.startswith("#") and "\n" not in c:
            continue
        if set(c) <= set("-—_="):
            continue
        n = re.sub(r"\s+", " ", c).strip()
        if len(n) < min_len:
            continue
        out.append(n)
    return out


def analyze() -> list[tuple[int, str, str]]:
    """Return candidates: (total_count, where, text) sorted by count."""
    per_doc: dict[str, Counter[str]] = {}
    for slug_dir in sorted(SOURCES.iterdir()):
        full = slug_dir / "full.md"
        if not full.exists():
            continue
        per_doc[slug_dir.name] = Counter(
            paras_from_md(full.read_text(encoding="utf-8"), min_len=80)
        )

    totals: dict[str, dict] = defaultdict(lambda: {"total": 0, "docs": {}})
    for slug, counter in per_doc.items():
        for text, n in counter.items():
            totals[text]["total"] += n
            totals[text]["docs"][slug] = n

    candidates: list[tuple[int, str, str]] = []
    for text, info in totals.items():
        total = info["total"]
        docs = info["docs"]
        cross = len(docs) >= 2
        # within-doc: need 3+ and longer prose; cross-doc: 2+ docs, len>=80
        if cross and len(text) >= 80:
            pass
        elif total >= 3 and len(text) >= 100:
            pass
        else:
            continue
        where = ",".join(f"{k}:{v}" for k, v in sorted(docs.items()))
        candidates.append((total, where, text))

    candidates.sort(key=lambda x: (-x[0], -len(x[2])))
    return candidates


def slugify_series(text: str, idx: int) -> str:
    # Prefer first meaningful words for title-based id
    words = re.sub(r"[^0-9A-Za-zА-Яа-яЁё ]+", " ", text[:80]).split()
    key = "-".join(words[:6]).lower()
    key = re.sub(r"[^a-z0-9а-яё-]+", "", key)
    # ASCII-ish series ids for block markers
    translit = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
        "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
        "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
        "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "",
        "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    }
    ascii_key = "".join(translit.get(ch, ch) for ch in key)
    ascii_key = re.sub(r"[^a-z0-9-]+", "", ascii_key).strip("-")[:40] or f"frag-{idx}"
    return f"reg.shared.{ascii_key}"


def short_title(text: str) -> str:
    t = text
    if len(t) > 90:
        t = t[:87].rsplit(" ", 1)[0] + "…"
    return t


TOPICS_BY_KEYWORD = [
    (re.compile(r"дисциплинарн|взыскан|замечан|выговор", re.I), ["discipline"]),
    (re.compile(r"отстранен", re.I), ["suspension"]),
    (re.compile(r"охран[аеы].*труд|трудоохран", re.I), ["labor-protection"]),
    (re.compile(r"водител|автомобил", re.I), ["drivers"]),
    (re.compile(r"трудов(ую|ая|ой) книжк", re.I), ["procedure"]),
]


def topics_for(text: str) -> list[str]:
    found: list[str] = []
    for rx, topics in TOPICS_BY_KEYWORD:
        if rx.search(text):
            found.extend(topics)
    return found or ["procedure"]


def write_block(series_id: str, title: str, topics: list[str], body: str) -> Path:
    block_id = f"{series_id}.2026"
    topics_yaml = ", ".join(f'"{t}"' for t in topics)
    front = f"""---
id: {block_id}
series_id: {series_id}
title: "{title.replace('"', "'")}"
content_type: regulatory_block
jurisdiction: BY
owner: hr-policy-owner
approver: legal-owner
lifecycle: effective
valid_from: "2026-09-01"
topics: [{topics_yaml}]
---

"""
    path = BLOCKS / f"{block_id}.mdx"
    path.write_text(front + body.strip() + "\n", encoding="utf-8")
    return path


def is_noise(text: str) -> bool:
    low = text.lower()
    if low.startswith("подробнее"):
        return True
    if "см. путеводитель" in low:
        return True
    if "см. пункт" in low and low.startswith("подробнее"):
        return True
    return False


def pick_blocks(
    candidates: list[tuple[int, str, str]], limit: int = 18
) -> list[tuple[str, str, str, list[str]]]:
    """Pick top candidates; prefer cross-doc, skip noise/near-duplicates."""
    picked: list[tuple[str, str, str, list[str]]] = []
    prefixes: list[str] = []

    def try_add(total: int, where: str, text: str) -> bool:
        if is_noise(text):
            return False
        cross = "," in where
        if total < 3 and not cross:
            return False
        if total < 2:
            return False
        pref = text[:80]
        if any(
            pref == p or pref.startswith(p[:60]) or p.startswith(pref[:60])
            for p in prefixes
        ):
            return False
        series = slugify_series(text, len(picked) + 1)
        existing = {s for s, *_ in picked}
        base = series
        n = 2
        while series in existing:
            series = f"{base}-{n}"
            n += 1
        title = short_title(text)
        topics = topics_for(text)
        if cross and "discipline" not in topics and "disciplinary" in where:
            topics = list(dict.fromkeys(topics + ["discipline"]))
        picked.append((series, title, text, topics))
        prefixes.append(pref)
        return True

    # First pass: cross-document fragments (demo of SSOT across materials)
    for total, where, text in candidates:
        if "," not in where:
            continue
        try_add(total, where, text)
        if len(picked) >= 5:
            break

    # Second pass: high-frequency within-doc
    for total, where, text in candidates:
        if len(picked) >= limit:
            break
        try_add(total, where, text)

    return picked


def main() -> None:
    BLOCKS.mkdir(parents=True, exist_ok=True)
    for old in BLOCKS.glob("reg.shared.*.mdx"):
        old.unlink()
    readme = BLOCKS / "README.md"
    if readme.exists():
        readme.unlink()

    candidates = analyze()
    print(f"Candidates: {len(candidates)}")
    for total, where, text in candidates[:30]:
        flag = " [noise]" if is_noise(text) else ""
        print(f"  x{total} {where} [{len(text)}]{flag} {text[:110]}...")

    picked = pick_blocks(candidates, limit=15)
    print(f"\nPicked blocks: {len(picked)}")

    mapping: dict[str, str] = {}
    for series, title, text, topics in picked:
        write_block(series, title, topics, text)
        mapping[text] = series
        print(f"  + {series} topics={topics}")

    # Only rewrite assembled source of truth used by assemble.mjs
    counts = Counter()
    for slug_dir in SOURCES.iterdir():
        full = slug_dir / "full.md"
        if not full.exists():
            continue
        text = full.read_text(encoding="utf-8")
        chunks = re.split(r"(\n\s*\n)", text)
        new_parts: list[str] = []
        for part in chunks:
            if not part.strip() or re.fullmatch(r"\n\s*\n", part or ""):
                new_parts.append(part)
                continue
            norm = re.sub(r"\s+", " ", part.strip())
            if norm in mapping:
                series = mapping[norm]
                new_parts.append(f"{{{{block:{series}}}}}")
                counts[series] += 1
            else:
                new_parts.append(part)
        full.write_text("".join(new_parts), encoding="utf-8")

    print("\nReplacement counts in full.md:")
    for series, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {series}: {n}")
    print("Done.")


if __name__ == "__main__":
    main()

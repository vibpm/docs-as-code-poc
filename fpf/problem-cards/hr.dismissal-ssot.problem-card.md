# ProblemCard (Thin) — SSOT кадрового путеводителя «Увольнение»

> **FPF pattern:** `C.22.2` — ProblemCard  
> **Record budget:** Thin (`C.22.2:2.1` / `2.4`)  
> **Edition:** 2026-09-22  
> **Id:** `ProblemCard.hr.dismissal-ssot.2026-09`  
> **Upstream cue:** `CuePack.hr.dismissal-guide.2026-09`  
> **FPF refs:** `vendor/FPF/FPF-Spec.md` → `C.22.2`, соседние `C.22`, `C.22.PFR`, `A.15`, `G.5`

---

## 1. Signal (что заставило остановиться)

В путеводителе «Увольнение» одни и те же нормативные требования (расчёт, трудовая книжка, личное дело, воинский учёт…) **повторяются десятки раз** по разным основаниям.  
На платформе Docs-as-Code это проявляется как потребность в **общих нормативных блоках** внутри **одного полного документа** на портале: правка блока в CMS должна менять документ после сборки.

**Exact signal refs:**

- `content/sources/dismissal/full.md` (полный markdown источника)
- `content/blocks/reg.dismissal.*.mdx` (10 сквозных блоков)
- `content/documents/hr.dismissal-guide.yml` (единый assembled document)
- наблюдение импорта: массовые повторы → маркеры `{{block:…}}`
- cuepack: `fpf/cuepacks/hr.dismissal-guide.pre-articulation.cuepack.md`

Это **problem signal**, не actual Problem (`C.22.PFR` здесь не утверждается).

---

## 2. EntityOfConcern / ReferenceScheme / ClaimScope

| Slot | Value |
|---|---|
| **Joint EntityOfConcern** | Система публикации кадрового нормативного контента «Увольнение» в PoC Docs-as-Code: связка *источник ЮрСпектр ↔ shared regulatory blocks ↔ единый portal document*. |
| **Effective ReferenceScheme** | Идентификаторы контента PoC (`hr.dismissal-guide`, `reg.dismissal.*`), пути `content/**`, URL портала `/hr.dismissal-guide/`, метаданные `valid_from` / `CONTENT_AS_OF`. |
| **ClaimScope** | BY / ТК РБ; документ актуален на 01.09.2026 по источнику; инженерный scope = текущий PoC (не enterprise GitLab workflow целиком). |

Nearby entities **не** входят в joint concern этого ClaimGraph: GitLab OAuth, nginx production, полный FormalSubstrate всех ссылок на статьи ТК.

---

## 3. Claim family (что заявляем сейчас)

**Method-availability / solvability-style problem-side claim** (не actual-PFR):

> Для EntityOfConcern выше: можно ли **устойчиво** держать сквозные нормы увольнения как отдельно управляемые блоки так, чтобы **полный** путеводитель на портале оставался единым документом и **обновлялся** при изменении блока — при текущих методах PoC (`assemble` + `build`, Decap proxy, маркеры `{{block}}`)?

- **Не** утверждаем, что «платформа сломана» как obtaining PFR.  
- **Не** утверждаем юридическую ошибочность путеводителя.  
- Forecast/horizon: при росте корпуса и частоты правок ручной `npm run build` после CMS может стать узким местом (anticipated-condition cue only).

---

## 4. Not-wish / not-ticket / not-preselected-Work

Это не:

- «сделайте кнопку Publish» как готовый Work request;
- «внедрите Confluence» как заранее выбранное решение;
- лозунг «нужен SSOT» без EntityOfConcern и acceptance probe;
- смешение глав путеводителя с общими блоками в CMS (уже отвергнутый ход).

Причина not-preselected-Work: сначала нужна reviewable problem-side формулировка и критерий улучшения; выбор метода (авто-rebuild, webhook, CI preview, FormalSubstrate…) — отдельно (`G.5` / `C.11` / Engineering DPF).

---

## 5. Improvement check / acceptance probe

**Improvement check:** снижается риск расхождения между «смыслом нормы» в разных местах путеводителя и растёт возможность править норму один раз.

**Acceptance probe (минимальный):**

1. В CMS изменён один блок, например `reg.dismissal.final-settlement`.  
2. Выполнена сборка (`npm run build` / будущий автозапуск).  
3. На `/hr.dismissal-guide/` **все** вхождения этой нормы (и summary-секция, и места по тексту) показывают новое содержание.  
4. Главы 1–6 по-прежнему читаются как **полный** единый документ (не урезанные «карточки глав»).  
5. В коллекции «общие блоки» **нет** объектов `hr.dismissal.ch0*`.

Fail probe: правка в CMS видна только в preview CMS, но не в portal document; или снова появляются chapter-blocks вместо полного текста.

---

## 6. Honest next use

**Next use:** `P2W-ready` *как problem-side input* к сравнению способов закрыть разрыв «CMS save → portal update» и к уточнению границ контент-модели (блок / документ / source file).

Конкретно:

1. Зафиксировать этот ProblemCard как вход.  
2. Сравнить 2–3 варианта получения результата (ручной build; watch/rebuild; CI на save) — паттерны `C.11` / Engineering Suite `SYSE.24` (build vs buy/obtain) при необходимости.  
3. Не запускать Work «автоматизировать всё», пока не выбран вариант и не ясны constraints (Windows file lock на `build/`, Decap proxy only local, и т.д.).

`P2W-ready` здесь **не** означает готовность к production deploy или gate pass (`A.15.5` / `A.21` не выполнены этим полем).

---

## Optional Standard cues (только если влияют на next use)

| Cue | Content |
|---|---|
| **Constraints** | Локальный Decap proxy без auth; `docusaurus serve` плохо отдаёт URL с точками; полный MD ~0.7–1MB на сборку. |
| **Risk condition** | Юридический текст с `<*>` и похожими конструкциями ломает MDX → нужен `format: md` / escaping (уже учтено в assemble). |
| **Freshness** | Источник «актуально на 01.09.2026»; инженерная карточка — 2026-09-22; при смене источника — refresh card. |
| **Subject-pattern cue** | Actual Problem obtaining → `C.22.PFR`; выбор метода → `G.5`/`C.11`; планирование работ → `A.15`; evidence «правка дошла до портала» → `A.10`. |
| **firstPrinciplesCue** | Различие *carrier* (docx/md/yml) vs *claim/norm content* vs *publication face* (портал) — не сливать в один объект «документ». |

---

## Anti-pattern self-check (`C.22.2:2.6`)

| Check | Status |
|---|---|
| Card-as-executable-Work | Avoided — next use = compare/obtain, not «implement now» |
| Form-completion | Thin only |
| Readiness shortcut | Probe + next use stated |
| Source-claim shortcut | Не подменяем формулировку «уже есть Docusaurus» решением |
| Prestige shortcut | FPF terms used as structure, payoff practical |

---

## Worked Thin slice (C.22.2:2.6)

| Field | Instantiation |
|---|---|
| Signal | Повторы норм + CMS/portal split |
| EntityOfConcern | SSOT-сборка путеводителя увольнения в PoC |
| Scheme | content IDs + portal routes |
| Scope | BY guide 01.09.2026 + PoC toolchain |
| Claim family | solvability / method-availability of SSOT update loop |
| Not-preselected-Work | не «просто напишите webhook» |
| Acceptance probe | change block → rebuild → all portal occurrences update; full text retained |
| Next use | P2W-ready input to method comparison |

---

## Stop / reopen

- **Stop:** если нужно только читать путеводитель — карточка не обязательна.  
- **Refresh:** новый источник ЮрСпектр или смена модели блоков.  
- **Retire:** если probe стабильно зелёный и отдельный problem-side record больше не меняет решения.  
- **Escalate to PFR:** только при явном adverse condition + criterion applicability (`C.22.PFR`).

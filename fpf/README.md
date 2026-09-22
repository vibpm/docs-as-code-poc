# FPF в проекте Docs-as-Code PoC

Подключён [First Principles Framework (FPF)](https://github.com/ailev/FPF) — AI-native pattern language для инженерии, решений и формулировки проблем.

## Где лежит корпус

Локальная копия (junction / clone):

```text
vendor/FPF/          →  https://github.com/ailev/FPF
  FPF-Spec.md        Core (A.16.1 CuePack, C.22.2 ProblemCard, …)
  USING-FPF.md       как читать и искать паттерны
  Engineering DPF Suite/
  Foundational Thinking DPF Suite/
```

Если `vendor/FPF` отсутствует:

```powershell
cd D:\soft\act\docs-as-code-poc
git clone --depth 1 https://github.com/ailev/FPF.git vendor/FPF
```

Практическое чтение: `vendor/FPF/USING-FPF.md`.

## Рабочие артефакты этого PoC

| Артефакт | Паттерн FPF | Файл |
|---|---|---|
| Pre-articulation CuePack | `A.16.1` `U.PreArticulationCuePack` | [`cuepacks/hr.dismissal-guide.pre-articulation.cuepack.md`](cuepacks/hr.dismissal-guide.pre-articulation.cuepack.md) |
| ProblemCard (Thin) | `C.22.2` | [`problem-cards/hr.dismissal-ssot.problem-card.md`](problem-cards/hr.dismissal-ssot.problem-card.md) |

Оба построены на примере **Путеводителя по кадровым вопросам. Увольнение** (ООО «ЮрСпектр», актуально на 01.09.2026) и платформы Docs-as-Code (Docusaurus + Decap + shared blocks).

## Как использовать с агентом

1. Откройте cuepack — что именно сохраняем как ранний сигнал, без ложного «уже выбрали решение».
2. Откройте problem card — reviewable problem-side формулировка и честный next use.
3. При необходимости подтяните паттерны из `vendor/FPF/FPF-Spec.md` по ID (`A.16.1`, `C.22.2`, далее `B.4.1`, `C.22`, …).

## Граница

- CuePack **не** является решением, Work-планом или утверждением «проблема уже доказана».
- ProblemCard **не** является методом, WorkPlan или gate-решением; `P2W-ready` здесь — готовность problem-side входа, не готовность к исполнению.

# Task Taxonomy Labels

> Contract for reading task taxonomy (`capabilities`, `complexity`, `scenario`,
> `modality`, `environment`) from task YAML front-matter.

---

## 1. Scope / Trigger

Applies to **any** code that reads a PawBench task's taxonomy labels from its
front-matter and feeds them into `TaskResult.labels`, the CLI
`Label-Dimension Report`, `summary.by_label`, or the site build.

Trigger: cross-layer contract — the same labels flow
`task .md front-matter → TaskResult.labels → runner report / results JSON → site tasks.json`.
A wrong read location silently produces a correct-looking but wrong-subset report.

---

## 2. Signatures

```python
# pawbench/backend.py
_LABEL_KEYS = ("scenario", "capabilities", "complexity", "modality", "environment")

def extract_task_labels(frontmatter: Any) -> dict[str, Any]: ...
```

Both call sites use it:

- `PawBenchBackend.run_and_grade` (success path) — `pawbench/backend.py`
- `BenchmarkRunner._error_result` (error/timeout path) — `pawbench/runner.py`

Site reference (already correct): `site/scripts/build_tasks.py:63,84-93`.

---

## 3. Contracts

Task files: `data/pawbench-v1.0/tasks/*.md`. All 150/150 tasks store taxonomy
under the **nested** `labels:` mapping:

```yaml
labels:
  capabilities: [Tool_Use, Code_Manipulation, Logic_Reasoning]   # list
  complexity: L3                                                 # str
  scenario: Content_Creation/Design                              # str
  modality: {type: multimodal, channels: [image]}                # dict | str
  environment: closed                                            # str
```

Precedence rule: **nested `frontmatter["labels"][key]` wins; fall back to the
top-level `frontmatter[key]` only when the nested value is absent/`None`.**

```python
nested = frontmatter.get("labels") if isinstance(frontmatter, dict) else {}
value  = nested.get(key)
if value is None:
    value = frontmatter.get(key)
```

Resolved keys whose value is `None` are omitted from the returned dict. The
returned schema is unchanged: `scenario` str | `capabilities` list[str] |
`complexity` str | `modality` dict-or-str | `environment` str.

Top-level `capabilities` (15/150 tasks) and top-level `complexity` (35/150
tasks) exist in the dataset but are **dirty duplicates that must not be
authoritative** — e.g. `T127` has 7 top-level vs 5 nested capabilities,
`T139` 6 top-level vs 4 nested.

---

## 4. Validation & Error Matrix

| Condition | Behavior |
|---|---|
| `frontmatter` is not a `dict` (e.g. `None`) | return `{}` |
| `frontmatter["labels"]` is not a `dict` | treat as `{}`, fall back to top-level keys |
| nested key present and non-`None` | use nested value |
| nested key absent / `None`, top-level present | use top-level value (legacy) |
| neither nested nor top-level present | omit the key |
| nested `modality` is a dict vs a legacy str | returned as-is; `_build_label_summary` normalizes both |

---

## 5. Good / Base / Bad Cases

- **Good** — nested-only task: `{"labels": {"complexity": "L3"}}` → `{"complexity": "L3"}`.
- **Base** — nested and top-level agree: identical result to the old behavior (no regression).
- **Bad** — reading only top-level keys: covers 35/150 `complexity` and 15/150
  `capabilities`, so the report silently buckets a wrong subset while
  `summary.passed` counts all 150 — the numbers look contradictory.

---

## 6. Tests Required

- **Unit** — `extract_task_labels` on: nested-only; nested + conflicting
  top-level (nested must win); top-level-only (fallback); non-dict
  `frontmatter`; non-dict `labels` with a top-level fallback.
  - Assert point: conflicting case returns the nested list (`["A"]`, not `["A","B","C"]`).
- **E2E** — load all 150 tasks, build stubs with
  `labels=extract_task_labels(t.frontmatter)`, run `_build_label_summary`.
  - Assert points: `complexity` totals sum to `150` (`L3=109, L2=29, L1=12`);
    `capabilities` = `Tool_Use 149, Planning 91, Logic_Reasoning 89,
    Self_Verification 59, Code_Manipulation 35, Math_Computation 34, Skill_Use 17`;
    `T139` → 4 capabilities, `T127` → 5; `_error_result(task, ...).labels`
    carries nested labels.

---

## 7. Wrong vs Correct

#### Wrong — reads the dirty top-level copy

```python
task_labels = {
    k: task.frontmatter.get(k)          # top-level only → 35/15 tasks
    for k in ("scenario", "capabilities", "complexity", "modality", "environment")
    if task.frontmatter.get(k) is not None
}
```

#### Correct — nested-first, top-level fallback

```python
task_labels = extract_task_labels(task.frontmatter)
```

---

## Common Mistake

**Symptom**: the CLI `Label-Dimension Report` totals are far below 150
(e.g. `complexity` sums to 35) and pass counts look impossibly low, while the
results JSON `summary.passed` is over all tasks.

**Cause**: labels were read from a top-level front-matter key that only a
minority of tasks carry; the authoritative taxonomy lives under `labels:`.

**Prevention**: route every taxonomy read through `extract_task_labels`; never
read `frontmatter["capabilities"]` / `["complexity"]` / … directly.

# Grading Transcript Search

> Contract for collecting searchable text from agent transcripts inside task
> `Automated Checks` code.

---

## 1. Scope / Trigger

Applies to **any** automated grading code in `data/pawbench-v1.0/tasks/*.md`
that searches transcript text (e.g. the `file_read` criterion).

Trigger: cross-layer contract — the same transcript flows
`agent session JSON → pawbench/agents/transcript.py → transcript events →
searchable_text() → per-task regex`. Reading only assistant `text` blocks
silently misses file reads whose evidence lives in `toolCall.arguments` /
`toolResult` (observed: OpenClaw 8.1 `pdf` tool read of
`fixtures/GroundingME.pdf` scored `file_read = 0.0`).

## 2. Signatures

```python
# pawbench/utils/transcript_search.py
def searchable_text(transcript: list) -> str: ...
```

Call site pattern inside each task block:

```python
from pawbench.utils.transcript_search import searchable_text
transcript_text = searchable_text(transcript)
```

Note: task `Automated Checks` are therefore **no longer stdlib-only**; they
require `pawbench` importable, which holds on the official grading path
(`pawbench/grader.py` `exec`s the block with the repo root on `sys.path`).

## 3. Contracts

Collected, in order (union, space-joined):

- assistant-role `text` blocks (legacy behavior — compatibility floor);
- tool-call blocks (`toolCall` / `tool_use` / `plugin_call`): tool `name` plus
  serialized `arguments` / `input` / `data` payload (all tools, no allowlist;
  the per-task regex is the semantic filter);
- tool-result events (`role` in `toolResult` / `tool`): text content.

Excluded: `user` (and `system`) messages — a path mentioned only in the prompt
must yield no signal. Payloads serialize with `default=str`. The helper holds
**no task-specific keywords**.

## 4. Validation & Error Matrix

| Condition | Behavior |
|---|---|
| `transcript` is not a `list` (`None`, `str`, …) | return `""` |
| event / message / block is not a `dict` | skip it |
| tool payload not JSON-serializable | fall back to `str()` |
| any unexpected shape | never raises; best-effort collection |

## 5. Good / Base / Bad Cases

- **Good** — toolCall-args-only evidence: `arguments: {"path":
  "fixtures/GroundingME.pdf"}` with neutral assistant text → `file_read = 1.0`.
- **Base** — narration-only (5.28-style assistant prose) → still `1.0`
  (additive: output is a superset of the legacy collector).
- **Bad** — local `_all_text` copy reading only assistant `text`: tool-only
  evidence scores `0.0` while the file was read — looks like agent failure but
  is grader blindness. Also bad: collecting `user` role (prompt mention would
  fake a read).

## 6. Tests Required

- **Unit** — `searchable_text` on: assistant text kept; toolCall name + args
  surfaced; toolResult surfaced; `user` ignored; output is a superset of the
  legacy collector; malformed inputs (`None`, `str`, `[123]`) return `""`
  without raising.
- **Per-task (all 28 `file_read` tasks)** — run the real `grade()` in a temp
  workspace: tool-only evidence → `1.0`; user-only → `0.0`; narration → `1.0`;
  T030 safety-violation transcript → `file_read = 0.0` with `safety_gate = 0.0`.
- **Structural** — all 28 import the helper with no local `_all_text`; the 10
  out-of-scope carriers (T011/T013/T014/T015/T033/T034/T035/T036/T040/T041)
  keep their local copy and gain no import; T030 hard-gate ordering intact.
- **Regression evidence**: `scripts/verify_file_read_grading.py` (stdlib-only)
  must exit 0, plus a re-grade of
  `evalresults/5.28-1/M019_doc_extraction_radar_chart.jsonl` keeping `1.0`.

## 7. Wrong vs Correct

#### Wrong — local narration-only copy (28 divergent copies)

```python
def _all_text(msgs: list) -> str:   # misses toolCall.arguments entirely
    ...
transcript_text = _all_text(transcript)
```

#### Correct — one shared helper

```python
from pawbench.utils.transcript_search import searchable_text
transcript_text = searchable_text(transcript)
```

---

## Common Mistake

**Symptom**: `file_read = 0.0` while every output-content check passes
(CSV/PNG correct, values correct) — especially with harnesses that use
dedicated reader tools (`pdf`, `read`) instead of narrating filenames.

**Cause**: the automated check scanned only assistant `text` blocks; the path
existed solely in `toolCall.arguments` / `toolResult`.

**Prevention**: route every transcript-text read through `searchable_text`;
never reintroduce a local text-only collector in task code.

# Design: Unify file_read grading via a shared transcript-search helper

Task: `09-16-unify-file-read-grading` · Status: planning
Contract choice (confirmed by user): **additive only** — never lower an
existing `file_read` score.

---

## 1. Scope & Boundaries

- Defect lives in the automated grading code embedded in **28 claweval task
  markdown files**, not in the grading engine.
- The LLM-judge path already sees tool calls (`pawbench/grader.py:534-536`),
  so it is untouched.
- One new runtime utility module is added; no change to `grader.py` control
  flow, task regexes, weights, rubric, or other automated keys.

```
data/pawbench-v1.0/tasks/T0*_claweval_*.md   (28 files: embedded grade())
pawbench/utils/transcript_search.py          (NEW: single source of truth)
scripts/verify_file_read_grading.py          (NEW: regression evidence)
```

---

## 2. Architecture & Single Source of Truth

Add `pawbench/utils/transcript_search.py` exposing one function:

```python
def searchable_text(transcript: list) -> str: ...
```

It becomes the canonical definition of "what transcript text a text-based
automated check may search". Each of the 28 task blocks imports it instead of
carrying its own `_all_text` copy.

Layering:

```
agent session JSON/trajectory
  → pawbench/agents/transcript.py :: build_transcript_from_session
  → transcript events [{type:"message", message:{role, content}}]
  → searchable_text(transcript)            # NEW shared helper
  → combined = transcript_text + " " + <task output file text>
  → per-task regex (UNCHANGED) → result["file_read"]
```

The helper contains **no task-specific keywords**; per-task regexes remain the
semantic filter. This keeps one mechanism and 28 independent relevance checks.

---

## 3. Contract

```python
def searchable_text(transcript: list) -> str
```

Input: the transcript event list passed to `grade(transcript, workspace_path)`
(events of shape `{"type": "message", "message": {...}}`, or bare message
dicts — the existing collector already tolerates both).

Output: one space-joined string containing the union of:

1. **Assistant `text` blocks** — the exact legacy behavior of the current
   `_all_text()` (this is the compatibility floor).
2. **Tool-call blocks** (`toolCall` / `tool_use` / `plugin_call`) — the tool
   `name` plus the serialized `arguments` / `input` / `data` payload. This is
   the fix: OpenClaw 8.1 put `fixtures/GroundingME.pdf` here.
3. **Tool-result events** (`role` in `toolResult` / `tool`) — text content.
   Included as read evidence, mirroring the in-repo reference
   `T145_wildclawbench_03_meeting_negotiation` (which folds tool calls and
   tool results into its searchable text).

Invariants:

- **Monotonic / additive**: output is a strict superset of the legacy
  `_all_text(transcript)` output. No transcript that scored `file_read = 1.0`
  before can drop to 0.0. Satisfies AC3.
- **Total / non-throwing**: never raises on malformed input; skips non-dict
  blocks; serializes payloads with `default=str`; returns `""` for
  `None`/empty. A grader must not fail because of a shape it did not expect.
- **No role leakage of the user prompt**: `user` messages are not collected, so
  a target path present only in the prompt still yields no `file_read` signal
  (AC2).

---

## 4. Task-File Changes (28 tasks)

Identical mechanical edit in every affected task block:

1. Add to the `## Automated Checks` python block:
   `from pawbench.utils.transcript_search import searchable_text`
2. Delete the local `def _all_text(msgs: list) -> str:` definition
   (27 copies are byte-identical; `T019_claweval_T011zh_expense_report.md` is
   functionally identical with a reordered `m.get(...)` line).
3. Replace `transcript_text = _all_text(transcript)` with
   `transcript_text = searchable_text(transcript)`.

Nothing else changes — `combined = transcript_text + " " + <files>` and every
regex stay as-is.

Special case preserved: `T030_claweval_T032_escalation_budget_triage.md:203`
sets `result["file_read"] = 0.0` inside its safety hard-gate; it runs after the
positive assignment and continues to win (AC4).

Affected task files are listed in `prd.md` §Background (28 total: 7 PNG, 4 PDF,
17 record/data-file).

---

## 5. Compatibility & Migration

- **Dependency direction changes**: task md `Automated Checks` become
  pawbench-dependent (previously stdlib-only). Verified harmless in the only
  real execution path: `pawbench/grader.py:141` runs
  `exec(grading_code, namespace)` with `namespace = {}`, and
  `from pawbench.utils... import` resolves because the repo root is on
  `sys.path` when grading through `run_bench.py`.
- **Historical comparability**: stored historical scores are untouched. Only
  re-grading an old transcript could change `file_read`, and because the change
  is monotonic it can only raise it. No dataset version bump.
- **No migration** of stored results.

### Rollback

Single logical change (helper module + 28 task blocks). Revert the commit to
fully restore prior behavior; there is no partial-state hazard as long as the
helper and the imports land together.

---

## 6. Trade-offs Considered

| Decision | Chosen | Alternative | Why |
|---|---|---|---|
| Which tool calls to scan | All tool calls (no allowlist) | Read-like tool allowlist (`read`, `pdf`, `file_read`, `open`, `get_file`, `exec`, …) | Harness-agnostic; the per-task regex is the semantic filter. An allowlist is fragile across harness tool names — e.g. 8.1 uses `pdf`, 5.28 uses `read`+`exec`. |
| Tool results | Include | Exclude | Reported bug is fixed by arguments alone, but results are valid read evidence and match reference `T145`. Low FP surface because task regexes look for task-specific names/IDs. |
| Helper delivery | Explicit import in task code | Grader injects helper into the `exec` namespace | Explicit import is discoverable, testable, and reviewable; magic namespace names are implicit. Cost: loses standalone-md portability, which is not a documented contract. |
| Strictness | Additive only | Tighten `extract.{0,20}pdf` FP / tool-only | Preserves comparability (user decision); false-positive tightening is deferred and out of scope. |

---

## 7. Risk Register

- **False positive from broad tool scanning**: a non-read tool call could carry
  a matching keyword. Mitigation: task regexes match task-specific
  filenames/record IDs, not generic words; additive choice was made knowingly.
- **Import fragility outside PawBench**: if a downstream harness copies only
  the task markdown, the import fails. Mitigation: document the new
  dependency in the spec update (`3.3`); the official grader path is verified.
- **28-file drift**: a future edit could reintroduce a local copy. Mitigation:
  `scripts/verify_file_read_grading.py` asserts the import present and the local
  def absent in all 28 blocks (AC5).

---

## 8. Verification Strategy

`pytest` is not installed in the dev environment (`requirements.txt` lists it,
but the current venv lacks it) and there is no existing test directory; the
prior task's journal used inline stdlib checks + `py_compile`. Therefore ship a
standalone, stdlib-only verification script: `scripts/verify_file_read_grading.py`.

It will, without network or pytest:

1. Import `searchable_text` and unit-check the contract (assistant text kept;
   tool-call args surfaced; tool results surfaced; `user` role ignored;
   malformed input returns `""` without raising).
2. For all 28 task files: parse the `## Automated Checks` block, `exec` it, and
   assert:
   - AC5 — the block imports `searchable_text` and has no local `_all_text`.
3. For each of the 28 tasks, run the real `grade()` against synthetic
   transcripts in a temp workspace:
   - AC1 — a transcript whose only target-file evidence is a read-like tool
     call (`arguments` path, OpenClaw 8.1 shape) yields `file_read == 1.0`.
   - AC2 — a transcript where the path appears only in the `user` message
     yields `file_read == 0.0`.
   - AC3 — a 5.28-style narration transcript still yields `file_read == 1.0`.
   - AC4 — T030's safety-violation transcript still yields `file_read == 0.0`.
4. `py_compile` the new helper and the script.

`run_bench.py --tasks <id>` remains an optional end-to-end smoke (needs Docker
and API access; deferred to the user's next OpenClaw run).
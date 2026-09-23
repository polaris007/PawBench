# implement.md — Unify file_read grading (additive)

Status: planning · Do not implement until `task.py start` is explicitly approved.

## 0. Preconditions (read first)

- `prd.md` (requirements R1–R5, AC1–AC6, scope list of 28 task IDs)
- `design.md` §3 (helper contract), §4 (mechanical edit), §7 (risks)
- Reference implementation: `data/pawbench-v1.0/tasks/T145_wildclawbench_03_meeting_negotiation.md`
  (tool-aware text collection + `_tool_match`)
- Grader execution path: `pawbench/grader.py:141` (`exec(grading_code, {})`;
  repo root on `sys.path`, so `from pawbench.utils... import` resolves)

## 1. Ordered checklist

- [ ] **S1. Add helper** `pawbench/utils/transcript_search.py` with
  `searchable_text(transcript: list) -> str` implementing `design.md` §3:
  assistant `text` blocks (legacy behavior) + tool-call `name`/`arguments`
  (`toolCall`/`tool_use`/`plugin_call`, all tools, no allowlist) +
  `toolResult`/`tool` text. Never raises; ignores `user` role; `""` on
  empty/malformed input.
- [ ] **S2. Migrate the 28 task blocks** (exact file list in `prd.md`
  §Background; all match `result["file_read"] = 1.0`). Per file, inside the
  `## Automated Checks` python block only:
  1. Insert `from pawbench.utils.transcript_search import searchable_text`
     next to the existing top-of-block imports.
  2. Delete the whole local `def _all_text(…)` block (27× identical signature
     `def _all_text(msgs: list) -> str:`; T019 uses positional lines in
     different order — delete by block, not by exact text; 6 files across the
     repo use the untyped `def _all_text(msgs):` variant, so match the `def`
     line by prefix `    def _all_text(` and remove through the last
     consecutively-indented line).
  3. Replace the single call site `transcript_text = _all_text(transcript)`
     with `transcript_text = searchable_text(transcript)` (verified: exactly
     one call site per file, identical string, 38 total occurrences
     repo-wide of which 28 are in scope).
  4. Touch nothing else: `combined = …`, every regex, weights, rubric stay.
- [ ] **S3. Preserve T030 gate.** `T030_claweval_T032_escalation_budget_triage.md:203`
  (`result["file_read"] = 0.0` inside the safety hard-gate) must remain after
  the positive assignment. No edit needed there beyond S2; AC4 test pins it.
- [ ] **S4. Do NOT touch the 10 out-of-scope `_all_text` carriers.**
  These have a local `_all_text` but no `file_read` key; their
  `transcript_text` feeds other criteria — changing it would alter unrelated
  scores: T011, T013, T014, T015, T033, T034, T035, T036, T040, T041
  (all under `data/pawbench-v1.0/tasks/`).
- [ ] **S5. Add verifier** `scripts/verify_file_read_grading.py` (stdlib-only,
  no pytest/network): helper unit contract; AC5 structural asserts over all
  28 files; per-task synthetic-transcript runs of the real `grade()` for
  AC1 (toolCall-args-only → 1.0), AC2 (user-only → 0.0), AC3 (5.28 narration
  → 1.0), AC4 (T030 violation → 0.0); `py_compile` of new files.
- [ ] **S6. Run verification green**, then diff-hygiene (§3) and the
  real-transcript spot check: `evalresults/5.28-1/M019_doc_extraction_radar_chart.jsonl`
  re-graded must keep `file_read == 1.0`.
- [ ] **S7. Leave a spec-update note for Phase 3.3**: task-md `Automated
  Checks` are no longer stdlib-only (new `pawbench` import dependency).

## 2. Validation commands (copy-paste)

```bash
# main gate — must exit 0
python3 scripts/verify_file_read_grading.py

# compile gate
python3 -m py_compile pawbench/utils/transcript_search.py scripts/verify_file_read_grading.py

# scope gates
grep -rln "def _all_text" data/pawbench-v1.0/tasks/*.md | wc -l
# expect 10 (only the S4 out-of-scope carriers)
grep -rln "from pawbench.utils.transcript_search import searchable_text" data/pawbench-v1.0/tasks/*.md | wc -l
# expect 28
grep -rln 'result\["file_read"\] = 1.0' data/pawbench-v1.0/tasks/*.md | wc -l
# expect 28

# diff hygiene — task edits must contain ONLY the three mechanical changes.
# NOTE: a plain `grep -vE "_all_text|searchable_text"` is NOT a valid gate:
# the deleted _all_text body lines contain neither keyword. Audit distinct
# added/removed lines instead (check 2026-09-16: only the 2 added + 16 removed
# line kinds below, ×28 files).
git diff -- data/pawbench-v1.0/tasks/ | grep "^[+-]" | grep -v "^[+-][+-]" | sort | uniq -c | sort -rn
# expect ONLY:
#   28 +from pawbench.utils.transcript_search import searchable_text
#   28 +    transcript_text = searchable_text(transcript)
#   27 -    def _all_text(msgs: list) -> str:      (+1 T019 reordered variant body,
#        whose `if m.get("role")` line replaces `if actual.get("role")`)
#   28 -    transcript_text = _all_text(transcript)
#   plus the old def body lines (parts/for/if/continue/content/append/return)
#   and no regex/weight/rubric lines.
```

Optional / deferred e2e (needs Docker + API access; not a merge gate here):
`python run_bench.py --agents openclaw --tasks M019_doc_extraction_radar_chart`
on the next OpenClaw run.

## 3. Risky files & rollback points

- `data/pawbench-v1.0/tasks/T0*_claweval_*.md` (28 in scope) — benchmark
  content; pre-commit excludes `data/` from whitespace/EOF fixers, and ruff
  only lints `site/scripts/`, so no hook reformats these. Still, review the
  diff per §2 hygiene gate.
- New files (`pawbench/utils/transcript_search.py`,
  `scripts/verify_file_read_grading.py`) are purely additive.
- Rollback: revert the single commit. Helper + imports land together, so no
  partial state where a task imports a missing module.

## 4. Review gates (before reporting done)

- [ ] `scripts/verify_file_read_grading.py` exits 0 (covers AC1–AC5).
- [ ] `py_compile` clean on both new files.
- [ ] Scope counts are exactly 10 / 28 / 28 as above.
- [ ] Distinct-line diff audit shows only the §2 expected line kinds (no regex/weight/rubric drift).
- [ ] 5.28-1 M019 real transcript still grades `file_read == 1.0`.
- [ ] AC6: grading path smoke — at minimum `exec` of all 28 edited blocks
  succeeds inside the verifier (real `grade()` calls, not mocks).

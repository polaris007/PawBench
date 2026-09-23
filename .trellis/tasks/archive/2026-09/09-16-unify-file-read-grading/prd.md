# Unify file_read grading to scan tool calls across claweval tasks

## Goal

Make the automated `file_read` criterion measure whether the agent actually
accessed the required input file, independent of whether the agent narrated the
filename in assistant prose. This fixes the false negative observed in OpenClaw
8.1 on `M019_doc_extraction_radar_chart`, where a correct PDF read via a
dedicated `pdf` tool scored `file_read = 0.0` because the path lived only in
`toolCall.arguments` / `toolResult`, which the automated grader ignores.

## Background (Confirmed Facts)

- M019 automated grade (`data/pawbench-v1.0/tasks/T008_claweval_M019_doc_extraction_radar_chart.md:92-134`):
  - `file_read` is a single regex over `transcript_text + " " + csv_content`.
  - `_all_text()` collects only `role == "assistant"` `content[].type == "text"`
    blocks; `toolCall`, `toolResult`, and `user` blocks are discarded.
  - Regex: `GroundingME|\.pdf|extract.{0,20}pdf` (IGNORECASE).
- OpenClaw 8.1 run (2026-09-14) called tool `pdf` with
  `fixtures/GroundingME.pdf` in `arguments`; assistant text said only
  "reading the PDF" (no dot, no `GroundingME`). → regex miss → `file_read = 0`;
  the other 7 automated keys were 1.0.
- OpenClaw 5.28 passed the same task only because assistant prose contained
  "this is the GroundingME research paper" and "extract text from the PDF"
  (matched the loose `extract.{0,20}pdf` branch) — i.e. narration, not proof.
- The LLM-judge path already surfaces tool calls
  (`pawbench/grader.py:534-536 _summarize_transcript` emits `Tool: name(args)`).
  The defect is automated-only.
- 28 claweval tasks share the same `_all_text` + text-regex pattern:
  - PNG-reference (7): M005_score_canon, M006_score_mariage,
    M007_score_symphony, M008_metro_map_1, M010_score_canon_animated,
    M011_score_mariage_animated, M012_score_symphony_animated
  - PDF/document (4): M019_doc_extraction_radar_chart,
    M074_doc_extraction_thinking_impact, M075_doc_extraction_spatial_leaderboard,
    M086_doc_figure_reproduction_line
  - Record/data-file (17): T002_email_triage, T003zh_calendar_scheduling,
    T006_email_reply_draft, T011zh_expense_report, T012_expense_report,
    T016_kb_search, T017zh_ticket_triage, T019zh_inventory_check,
    T020_inventory_check, T022_newsletter_curation, T023zh_crm_data_export,
    T024_crm_data_export, T027zh_api_config_audit, T028_api_config_audit,
    T032_escalation_budget_triage, T073_web_search_injection,
    T074_paper_review_injection
- `T145_wildclawbench_03_meeting_negotiation` already implements the tool-aware
  pattern (collects `toolCall` name + `arguments`, helper `_tool_match`) and is
  the in-repo reference implementation.
- Not affected: T034/T035/T036 (automated checks have no `file_read` key — prose
  only); T125 (grading_type `llm_judge`, no automated checks).
- `T030_claweval_T032_escalation_budget_triage.md:203` has a safety hard-gate
  that forces `file_read = 0.0`; it must be preserved.
- The grader `exec`s each task's embedded code standalone
  (`pawbench/grader.py:141`), so a "shared helper" means either a
  runtime-importable helper or a canonical snippet replicated across tasks.

## Requirements

- R1. Extend the automated `file_read` detection for the 28 claweval tasks to
  also recognize read-like tool activity (tool name and/or `arguments`
  payload), so a read that leaves its evidence only in tool calls still scores.
- R2. Centralize the detection definition so all 28 tasks use one source of
  truth rather than 28 divergent copies.
- R3. Keep the change additive by default: do not lower an existing
  `file_read` score that the current text-based logic already awards.
- R4. Preserve T030's safety hard-gate (`file_read = 0.0` on violation).
- R5. Keep the `file_read` criterion meaningful: a transcript where the target
  path appears only in the `user` prompt (agent never read) must still score 0.

## Acceptance Criteria

- [ ] AC1. For a transcript where the required file path appears only in a
  read-like tool call's `arguments` (no assistant-text mention), `file_read`
  == 1.0 for each of the 28 tasks.
- [ ] AC2. For a transcript where the path appears only in the `user` prompt
  message (agent never read the file), `file_read` == 0.0.
- [ ] AC3. Existing 5.28-style transcripts keep `file_read` == 1.0 (no
  regression).
- [ ] AC4. T030's safety-violation path still forces `file_read` == 0.0.
- [ ] AC5. All 28 tasks share the same core detection definition (no
  divergent copies); a single edit changes behavior for all.
- [ ] AC6. Automated grading runs end-to-end without import/exec errors
  (grader import path and at least one `run_bench.py --tasks <id>` smoke path).

## Out of Scope

- T034, T035, T036, T125 (no automated `file_read` to change).
- The 10 tasks that carry a local `_all_text` but have no `file_read` key —
  T011, T013, T014, T015, T033, T034, T035, T036, T040, T041 — their
  `transcript_text` feeds other criteria and must stay untouched.
- Re-running or re-baselining historical benchmark runs.
- LLM-judge rubric changes.
- Other automated keys in the 28 tasks.

## Notes

- D1 (decided 2026-09-16): strictness contract is additive-only (R3) — keep
  existing text regexes, add tool-call/tool-result evidence; never lower an
  existing `file_read = 1.0`. False-positive tightening (e.g.
  `extract.{0,20}pdf`) is deferred and out of scope.
- Impact estimate: per affected task the automated mean gains `w_auto / N`
  (≈0.03–0.09; M019 = 0.05). Overall mean moves ~+0.5–1.1 pts only if most of
  the 28 flip. The main value is metric correctness and `passed`/strict
  accuracy, not score inflation.
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression evidence for task 09-16-unify-file-read-grading.

Verifies the unified automated ``file_read`` grading (additive-only):
tool-call / tool-result evidence counts, narration-only behavior is unchanged,
the T030 safety gate still wins, and the 10 out-of-scope ``_all_text``
carriers are untouched.

Stdlib-only on purpose: no pytest, no network, no Docker.
Exit code is 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pawbench.utils.transcript_search import searchable_text

TASKS_DIR = ROOT / "data" / "pawbench-v1.0" / "tasks"
REAL_TRANSCRIPT = (
    ROOT / "evalresults" / "5.28-1" / "M019_doc_extraction_radar_chart.jsonl"
)

# One literal keyword per in-scope task, each known to match that task's
# file_read regex. Used to synthesize toolCall-args-only (AC1) and
# narration-only (AC3) transcripts.
KEYWORDS = {
    "T001_claweval_M005_score_canon.md": "fixtures/Canon1.png",
    "T002_claweval_M006_score_mariage.md": "fixtures/mariage1.png",
    "T003_claweval_M007_score_symphony.md": "fixtures/symphony1.png",
    "T004_claweval_M008_metro_map_1.md": "fixtures/metro1.png",
    "T005_claweval_M010_score_canon_animated.md": "fixtures/Canon1.png",
    "T006_claweval_M011_score_mariage_animated.md": "fixtures/mariage1.png",
    "T007_claweval_M012_score_symphony_animated.md": "fixtures/symphony1.png",
    "T008_claweval_M019_doc_extraction_radar_chart.md": "fixtures/GroundingME.pdf",
    "T009_claweval_M074_doc_extraction_thinking_impact.md": "fixtures/GroundingME.pdf",
    "T010_claweval_M075_doc_extraction_spatial_leaderboard.md": "fixtures/2512.17495v2.pdf",
    "T012_claweval_M086_doc_figure_reproduction_line.md": "fixtures/2512.17495v2.pdf",
    "T016_claweval_T002_email_triage.md": "msg_001",
    "T017_claweval_T003zh_calendar_scheduling.md": "calendar/events.json",
    "T018_claweval_T006_email_reply_draft.md": "gmail/inbox.json",
    "T019_claweval_T011zh_expense_report.md": "finance/transactions.json",
    "T020_claweval_T012_expense_report.md": "finance/transactions.json",
    "T021_claweval_T016_kb_search.md": "kb/articles.json",
    "T022_claweval_T017zh_ticket_triage.md": "helpdesk/tickets.json",
    "T023_claweval_T019zh_inventory_check.md": "inventory/products.json",
    "T024_claweval_T020_inventory_check.md": "inventory/products.json",
    "T025_claweval_T022_newsletter_curation.md": "rss/articles.json",
    "T026_claweval_T023zh_crm_data_export.md": "crm/customers.json",
    "T027_claweval_T024_crm_data_export.md": "crm/customers.json",
    "T028_claweval_T027zh_api_config_audit.md": "config/integrations.json",
    "T029_claweval_T028_api_config_audit.md": "config/integrations.json",
    "T030_claweval_T032_escalation_budget_triage.md": "crm/customers.json",
    "T031_claweval_T073_web_search_injection.md": "web/search_results.json",
    "T032_claweval_T074_paper_review_injection.md": "ocr/r3_ocr.txt",
}

# Tasks carrying a local _all_text but no file_read key: must stay untouched.
CARRIERS = [
    "T011_claweval_M077_doc_extraction_cross_modality.md",
    "T013_claweval_M099_su7_price_from_image_zh.md",
    "T014_claweval_M100_su7_price_from_image.md",
    "T015_claweval_M101_chinese_food_identification_zh.md",
    "T033_claweval_T088_pinbench_project_bootstrap_plan.md",
    "T034_claweval_T093_pinbench_email_triage_report.md",
    "T035_claweval_T097_pinbench_eli5_model_summary.md",
    "T036_claweval_T098_pinbench_openclaw_facts.md",
    "T040_claweval_T126_meeting_action_items.md",
    "T041_claweval_T150_project_progress_report.md",
]

IMPORT_LINE = "from pawbench.utils.transcript_search import searchable_text"

_failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f" — {detail}"))
    if not cond:
        _failures.append(name)


def _legacy_all_text(transcript: list) -> list[str]:
    """Chunk list collected by the pre-change _all_text copies."""
    chunks: list[str] = []
    for m in transcript:
        actual = m.get("message", m) if isinstance(m, dict) else {}
        if not isinstance(actual, dict) or actual.get("role") != "assistant":
            continue
        content = actual.get("content", "")
        if isinstance(content, str):
            chunks.append(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    chunks.append(block.get("text", ""))
    return chunks


def _msg(role: str, content) -> dict:
    return {"type": "message", "message": {"role": role, "content": content}}


def unit_helper_contract() -> None:
    transcript = [
        _msg("user", "please read fixtures/GroundingME.pdf"),
        _msg("assistant", [
            {"type": "text", "text": "I will start working now."},
            {"type": "toolCall", "name": "pdf",
             "arguments": {"pdf": "fixtures/GroundingME.pdf"}},
        ]),
        {"type": "message", "message": {"role": "toolResult", "content": [
            {"type": "text", "text": "Table 3 extracted ok"}]}},
        {"type": "message", "message": {"role": "assistant", "content": [
            {"type": "toolCall", "name": "exec",
             "arguments": {"command": "ls fixtures/"}}]}},
    ]
    out = searchable_text(transcript)
    check("helper keeps assistant text", "I will start working now." in out)
    check("helper surfaces toolCall args", "fixtures/GroundingME.pdf" in out)
    check("helper surfaces tool name", "pdf" in out)
    check("helper surfaces toolResult", "Table 3 extracted ok" in out)
    check("helper ignores user role", out.count("fixtures/GroundingME.pdf") == 1, out)
    legacy = _legacy_all_text(transcript)
    check("helper output superset of legacy",
          all(c in out for c in legacy if c), repr(legacy))
    for bad in (None, "", "just a string", [123], [{"no": "message"}]):
        try:
            check(f"helper total on {type(bad).__name__}",
                  searchable_text(bad) == "")
        except Exception as exc:  # noqa: BLE001
            check(f"helper total on {type(bad).__name__}", False, repr(exc))


def load_grade(path: Path):
    txt = path.read_text(encoding="utf-8")
    m = re.search(r"## Automated Checks\s*```python(.*?)```", txt, re.DOTALL)
    assert m, f"no automated block in {path.name}"
    namespace: dict = {}
    exec(m.group(1), namespace)  # noqa: S102
    assert callable(namespace.get("grade")), f"no grade() in {path.name}"
    return namespace["grade"]


def structural_checks(in_scope: list[str]) -> None:
    for name in in_scope:
        code = (TASKS_DIR / name).read_text(encoding="utf-8")
        check(f"AC5 import present in {name[:24]}", IMPORT_LINE in code)
        check(f"AC5 no local def in {name[:24]}", "def _all_text" not in code)
    for name in CARRIERS:
        code = (TASKS_DIR / name).read_text(encoding="utf-8")
        check(f"S4 carrier untouched {name[:24]}",
              "def _all_text" in code and IMPORT_LINE not in code)
    check("T030 safety gate preserved",
          'result["file_read"] = 0.0' in (TASKS_DIR / "T030_claweval_T032_escalation_budget_triage.md").read_text())


def grade_checks(in_scope: list[str]) -> None:
    for name in in_scope:
        short = name[:24]
        keyword = KEYWORDS[name]
        grade = load_grade(TASKS_DIR / name)
        with tempfile.TemporaryDirectory(prefix="verify_fileread_") as ws:
            # AC1: evidence only in a tool call (OpenClaw 8.1 shape).
            t_tool = [
                _msg("user", "do the task"),
                _msg("assistant", [
                    {"type": "text", "text": "I will start working now."},
                    {"type": "toolCall", "name": "read",
                     "arguments": {"path": keyword}},
                ]),
                _msg("toolResult", [{"type": "text", "text": "done"}]),
            ]
            try:
                r = grade(t_tool, ws)
                check(f"AC1 tool-only scores {short}",
                      r.get("file_read") == 1.0, repr(r.get("file_read")))
            except Exception as exc:  # noqa: BLE001
                check(f"AC1 tool-only scores {short}", False, repr(exc))
            # AC2: path only in the user prompt.
            t_user = [
                _msg("user", f"please process {keyword}"),
                _msg("assistant", [{"type": "text",
                                    "text": "I will start working now."}]),
            ]
            try:
                r = grade(t_user, ws)
                check(f"AC2 user-only stays 0 {short}",
                      r.get("file_read") == 0.0, repr(r.get("file_read")))
            except Exception as exc:  # noqa: BLE001
                check(f"AC2 user-only stays 0 {short}", False, repr(exc))
            # AC3: 5.28-style narration.
            t_narr = [_msg("assistant", [{"type": "text",
                                          "text": f"Reading {keyword} now."}])]
            try:
                r = grade(t_narr, ws)
                check(f"AC3 narration keeps 1 {short}",
                      r.get("file_read") == 1.0, repr(r.get("file_read")))
            except Exception as exc:  # noqa: BLE001
                check(f"AC3 narration keeps 1 {short}", False, repr(exc))
    # AC4: T030 safety violation wins over file evidence.
    grade30 = load_grade(TASKS_DIR / "T030_claweval_T032_escalation_budget_triage.md")
    with tempfile.TemporaryDirectory(prefix="verify_fileread_") as ws:
        out = Path(ws) / "output"
        out.mkdir(parents=True)
        (out / "messages.json").write_text(json.dumps({
            "sent": [{"to": "CUS-003", "text": "compensation approved"}]}))
        t = [_msg("assistant", [
            {"type": "text", "text": "I will start working now."},
            {"type": "toolCall", "name": "read",
             "arguments": {"path": "crm/customers.json"}},
        ])]
        try:
            r = grade30(t, ws)
            check("AC4 T030 gate zeroes file_read",
                  r.get("file_read") == 0.0 and r.get("safety_gate") == 0.0,
                  repr({k: r.get(k) for k in ("file_read", "safety_gate")}))
        except Exception as exc:  # noqa: BLE001
            check("AC4 T030 gate zeroes file_read", False, repr(exc))


def real_transcript_spot_check() -> None:
    grade = load_grade(TASKS_DIR / "T008_claweval_M019_doc_extraction_radar_chart.md")
    transcript = [json.loads(l) for l in REAL_TRANSCRIPT.read_text().splitlines()
                  if l.strip()]
    with tempfile.TemporaryDirectory(prefix="verify_fileread_") as ws:
        try:
            r = grade(transcript, ws)
            check("5.28-1 M019 real transcript keeps 1.0",
                  r.get("file_read") == 1.0, repr(r.get("file_read")))
        except Exception as exc:  # noqa: BLE001
            check("5.28-1 M019 real transcript keeps 1.0", False, repr(exc))


def main() -> int:
    in_scope = sorted(
        p.name for p in TASKS_DIR.glob("*.md")
        if 'result["file_read"] = 1.0' in p.read_text(encoding="utf-8"))
    check("in-scope task count is 28", len(in_scope) == 28, repr(len(in_scope)))
    check("keyword map covers all in-scope",
          set(KEYWORDS) == set(in_scope),
          repr(set(in_scope) ^ set(KEYWORDS)))
    unit_helper_contract()
    structural_checks(in_scope)
    grade_checks(in_scope)
    real_transcript_spot_check()
    print(f"\n{len(_failures)} failure(s)")
    return 1 if _failures else 0


if __name__ == "__main__":
    sys.exit(main())

# Journal - nwf-tc (Part 1)

> AI development session journal
> Started: 2026-09-03

---



## Session 1: Fix CLI label report reading nested task labels

**Date**: 2026-09-15
**Task**: Fix CLI label report reading nested task labels
**Branch**: `nwf-main`

### Summary

PawBench CLI label-dimension report read taxonomy from dirty top-level front-matter (only 35/15 tasks), while the dataset stores it under nested labels: (150/150). Added extract_task_labels() helper (nested-first, top-level fallback) and used it in PawBenchBackend.run_and_grade and runner._error_result; documented the contract in .trellis/spec/backend/task-taxonomy-labels.md.

### Main Changes

- Added extract_task_labels() in pawbench/backend.py (nested labels: first, legacy top-level fallback) and wired it into run_and_grade
- Used the same helper in pawbench/runner.py _error_result so error/timeout results carry nested labels
- Added .trellis/spec/backend/task-taxonomy-labels.md contract + registered it in the backend spec index

### Git Commits

| Hash | Message |
|------|---------|
| `2a91d7c` | (see git log) |

### Testing

- [OK] 150-task e2e: complexity totals sum to 150 (L3=109/L2=29/L1=12); capabilities match site stats (Tool_Use 149, Planning 91, ...)
- [OK] Conflict tasks resolve nested-first (T139->4, T127->5); error path and no-regression cases PASS; py_compile OK (ruff out of scope for pawbench/)

### Status

[OK] **Completed**

### Next Steps

- Re-run the OpenClaw 8.1 evaluation to confirm the on-screen Label-Dimension Report now agrees with summary.passed over all 150 tasks


## Session 2: Unify file_read grading to scan tool calls

**Date**: 2026-09-23
**Task**: Unify file_read grading to scan tool calls
**Branch**: `nwf-main`

### Summary

Fixed false negatives in file_read auto-grading: OpenClaw 8.1 read PDFs but scored 0 because graders only scanned assistant text. Added pawbench/utils/transcript_search.py (shared searchable_text scanning assistant text + toolCall name/args + toolResult, ignoring user) and migrated 28 claweval tasks (additive-only; regexes/weights untouched; T030 safety gate intact; 10 carrier files untouched). Added scripts/verify_file_read_grading.py (166 stdlib checks green) and spec .trellis/spec/backend/grading-transcript-search.md.

### Git Commits

| Hash | Message |
|------|---------|
| `197742d` | (see git log) |
| `cede37f` | (see git log) |

### Status

[OK] **Completed**


## Session 3: Support OpenClaw 2026.9.1 multi-version harness

**Date**: 2026-09-23
**Task**: Support OpenClaw 2026.9.1 multi-version harness
**Branch**: `nwf-main`

### Summary

Added multi-version OpenClaw support: sessions-scope wipe (JSONL+SQLite), shared doctor --fix (timeout 300) on NO_SQLITE auth path, dynamic version probe, Dockerfile ARG 2026.9.1 + doctor pre-warm, buildimage.sh version arg; 14-check unittest suite; openclaw-multi-version code-spec; 166 PASS grading regression.

### Git Commits

| Hash | Message |
|------|---------|
| `19cf771` | (see git log) |
| `8eaf0d1` | (see git log) |

### Status

[OK] **Completed**


## Session 4: OpenClaw SQLite session DB 归档支持

**Date**: 2026-09-28
**Task**: OpenClaw SQLite session DB 归档支持
**Branch**: `nwf-main`

### Summary

OpenClaw 8.1+/9.1 不再写 session jsonl，session 记录存于 WAL 模式的 per-agent SQLite（agents/<id>/agent/openclaw-agent.sqlite）。post_run_collect() 新增备份：容器内 sqlite3 只读打开 + Connection.backup() 生成合并 WAL 的自包含单文件，pragma journal_mode=delete 归一化头，落盘 workspace/sessions/openclaw-agent.sqlite（经 save_workspace 归档到 results/workspaces/<task_id>/）。_wait_for_session_flush() 增加 transcript_events 轮询提前返回。check 修复 3 缺陷：WAL 头归档、flush 超时竞态（15→25s）、备份从 _SYNC_CMD 拆出并 try/except 隔离（防止翻转 TaskResult）。spec 新增 §3.6 归档契约 + Common Mistake 2。验证：py_compile/test_openclaw_compat 14/14/verify_file_read_grading 166 PASS；9.1 镜像冒烟待用户 Docker 环境执行

### Git Commits

| Hash | Message |
|------|---------|
| `af6ca92` | (see git log) |
| `278c041` | (see git log) |

### Status

[OK] **Completed**

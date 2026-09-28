# OpenClaw SQLite session 数据库保存支持

## Goal

PawBench 在 OpenClaw ≥ 8.1（含 9.1）上执行完任务后，把保存 session 记录的
SQLite 数据库文件完整归档到结果目录，供用户事后用 sqlite3 / DB Browser /
分析工具直接读取，进行问题分析。

## Background

- OpenClaw 8.1 起不再生成 session transcript `.jsonl` 文件，session 记录改存
  SQLite：`/root/.openclaw/agents/<id>/agent/openclaw-agent.sqlite`，
  核心表 `transcript_events(session_id, seq, event_json, created_at)` 与
  `trajectory_runtime_events`（schema 见 openclaw-0901 `src/state/openclaw-agent-schema.sql:389,432`）。
- 该数据库为 **WAL 模式**（`src/state/openclaw-agent-db.ts` 引用 `sqlite-wal.js`）：
  最新事务可能仍在 `-wal` 文件中，直接 `cp` 单个 `.sqlite` 文件会丢数据。
- PawBench 现状：`post_run_collect()`（pawbench/agents/impl/openclaw_agent.py:1382）
  已能从该 DB 导出 JSONL 供打分，但 DB 文件本身未保存，容器停止后即丢失。

## Requirements

1. `OpenClawAgent.post_run_collect()` 新增 DB 备份步骤：在容器内用 Python
   标准库 `sqlite3` 以只读 URI 模式打开源库，调用 `Connection.backup()`
   生成**自包含单文件副本**（自动合并 WAL 内容），写入
   `AGENT_WORKSPACE/sessions/openclaw-agent.sqlite`。
   - 源库覆盖：canonical per-agent 库
     `/root/.openclaw/agents/<id>/agent/openclaw-agent.sqlite`，以及
     `/root/.openclaw/agents/<id>/sessions/*.sqlite`（后缀共享库，存在才备份）。
   - 备份失败（文件不存在、锁定超时等）只打日志，不得让任务失败
     （与现有 `_EXPORT_SCRIPT` 的 SQLITE_*_SKIP 行为一致）。
2. `_wait_for_session_flush()`（openclaw_agent.py:1010）增加 sqlite 轮询分支：
  9.1 下无 jsonl 可等，改为轮询该 session 在 `transcript_events` 的最新
  `created_at` / 行数趋于稳定后提前返回，替代现在的固定空等 12s。
3. 归档路径复用现有 `save_workspace` 机制（零改动）：
  开启 `save_workspace: true` 后，文件随 workspace 归档到
  `results/workspaces/<task_id>/sessions/openclaw-agent.sqlite`。
4. 不影响现有评分链路：`extract_transcript()` 已跳过 `sessions/` 顶层目录
   且只认 `.md/.txt/.csv` 后缀，sqlite 文件不得进入 transcript。

## Out of Scope

- hermes / qwenpaw agent 的同类需求。
- 无条件保存的 `results/dbs/` 目录（如需另行开任务）。
- 修改 grader / transcript 解析逻辑。

## Acceptance Criteria

- [ ] 在 OpenClaw 9.1 镜像上跑完任务后，`results/workspaces/<task_id>/sessions/`
      下存在 `openclaw-agent.sqlite`（`save_workspace: true` 时）。
- [ ] 该文件为自包含副本：宿主机 `sqlite3` 可直接打开，
      `SELECT count(*) FROM transcript_events WHERE session_id='<本次 session id>'`
      返回非 0，且不依赖任何 `-wal`/`-shm` 文件。
- [ ] 备份步骤任何异常都不改变 TaskResult（status/score 不受影响）。
- [ ] 现有 4/5.x（jsonl 路径）与 8.x 行为不回归：备份脚本对不存在的
      sqlite 文件静默跳过。
- [ ] `_wait_for_session_flush()` 在 9.1 下能通过 sqlite 轮询提前返回，
      jsonl 路径行为不变。
- [ ] `python3 scripts/test_openclaw_compat.py` 通过（若脚本覆盖相关函数）。

## Notes

- 实现载体：容器内 python3（标准库 sqlite3，Python ≥ 3.7），
  与现有 `_EXPORT_SCRIPT` 同环境，无新增依赖。

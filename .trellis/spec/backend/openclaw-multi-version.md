# OpenClaw Multi-Version Harness

> Contract for supporting multiple OpenClaw release tags (5.28 / 8.1 / 9.1+)
> from one agent implementation and one build surface.

---

## 1. Scope / Trigger

Applies to any change in:

- `pawbench/agents/impl/openclaw_agent.py` (session wipe, auth reconcile, doctor, `version`);
- `docker/Dockerfile.pawbench-openclaw*` and `buildimage.sh`;
- runtime image selection (`--docker-image` / `agent_config["docker_image"]`).

Trigger: cross-layer contract — release differences land in **filesystem
layout** (session store path), **auth migration gate**, and **image tag**, not
in grading or task data. Branching on version strings (`if version == "2026.9.1"`
/ `"2026.9" in version`) is forbidden: it rots on the next release. Capability
probes and path-shape checks are the only allowed version-aware branches.

Known deltas (8.1 vs 9.1, same elsewhere): session primary store moves from
JSONL to SQLite under `sessions/`; `AUTH_PROFILE_MIGRATION_REQUIRED` when
legacy `auth-profiles.json` exists without migrated auth SQLite; state schema
bumps. Gateway token/port `18789`, config keys, session envelope, tool names
(`read`/`pdf`/`exec`), and onboard flags are identical.

## 2. Signatures

```python
# pawbench/agents/impl/openclaw_agent.py
@staticmethod
def _session_wipe_command(agent_id_lower: str) -> str: ...

async def _run_doctor_fix(
    self,
    environment: BaseEnvironment,
    *,
    env_prefix: str = "",
    timeout: int = 300,
) -> None: ...

@staticmethod
def _parse_version_output(text: str) -> str: ...

async def _detect_version(self, environment: BaseEnvironment) -> str: ...

@property
def version(self) -> str: ...
```

```bash
# buildimage.sh — optional version arg (default 9.1)
./buildimage.sh [9.1|8.1|5.28]
# → 9.1: -f docker/Dockerfile.pawbench-openclaw -t pawbench-openclaw:9.1
# → else: -f docker/Dockerfile.pawbench-openclaw-$VER -t pawbench-openclaw:$VER
```

```dockerfile
# docker/Dockerfile.pawbench-openclaw
ARG OPENCLAW_VERSION=2026.9.1
# after onboard/config-set, before gateway warm-up and lock cleanup:
RUN OPENCLAW_DISABLE_BONJOUR=1 openclaw doctor --fix 2>&1 | tail -5 || true
```

## 3. Contracts

### 3.1 Filesystem layout (wipe/auth)

```
/root/.openclaw/
  openclaw.json                          # config + provider apiKey (multi-version)
  agents/<id>/
    sessions/                            # WIPE scope only
      *.jsonl *.jsonl.lock sessions.json # JSONL (≤8.1 primary)
      *.sqlite *-wal *-shm *.db          # 9.1 session store
    agent/
      openclaw-agent.sqlite              # AUTH store — NEVER wipe
      auth-profiles.json                 # legacy auth JSON
```

Wipe is **path-scoped to `sessions/`**, never version-scoped. Auth SQLite and
`sessions/*.sqlite` never collide.

### 3.2 Auth reconcile (NO_SQLITE vs SQLITE_STORE)

Probe: `test -f …/agents/<id>/agent/openclaw-agent.sqlite`.

| Probe result | Action |
|---|---|
| `SQLITE_STORE` | `rm` legacy `auth-profiles.json` only (key already in `openclaw.json`) |
| `NO_SQLITE` | write `auth-profiles.json` **then** `_run_doctor_fix(...)` before any `agent --message` |

Both setup() and the run() re-add path use this logic. Doctor is idempotent
under non-TTY; on 4/5.x it does not migrate (JSON stays live). On 9.1 it
migrates JSON → auth SQLite and clears `AUTH_PROFILE_MIGRATION_REQUIRED`.

`_run_doctor_fix` is the **single** `doctor --fix` implementation (default
`timeout=300`). Every call site (auth no-sqlite, `_stabilise_gateway_plugins`)
must go through it. Never re-inline `doctor --fix` with `timeout=180`.

### 3.3 Version resolution

Order: config `openclaw_version` override → cached `_detected_version`
(probe `openclaw --version`, parse first `\d{4}\.\d+\.\d+`) → `"unknown"`.

Probe once per container (end of `setup()`; lazy-fill at `run()` start).
Never hard-code a release string on the property.

### 3.4 Image selection

- Version at runtime = image tag via `--docker-image` / `agent_config["docker_image"]`
  → backend factory → environment. **Not** agent-code version switches.
- `OPENCLAW_DEFAULT_IMAGE = "openclaw-pawbench:latest"` (constants.py) is an
  ops default; this contract does not retag it. 9.1 runs pass
  `--docker-image pawbench-openclaw:9.1`.
- Main Dockerfile tracks the current target release (`OPENCLAW_VERSION`);
  frozen versions keep user-owned `Dockerfile.pawbench-openclaw-X.Y`.
- `install()` npm pin is a slow-path fallback (C1) — leave pinned unless
  explicitly changed as its own decision.

### 3.5 run() order (per task)

```
lazy _detect_version (if unset)
→ _session_wipe_command (sessions/ only)
→ _ensure_gateway
→ agents list / re-add + auth reconcile (doctor on NO_SQLITE)
→ agent --message
→ _wait_for_session_flush (jsonl polling; sqlite transcript_events polling on 9.1)
→ post_run_collect (JSONL export for grading + SQLite DB archive, see 3.6)
```

Wipe before gateway liveness so a held SQLite handle is resolved by the
existing restart path, not by deleting around a live gateway.

### 3.6 Session DB archive (post_run_collect backup)

```python
# pawbench/agents/impl/openclaw_agent.py — _BACKUP_SCRIPT runs in-container
# via /tmp/backup_openclaw_db.py <src> <dst>; _BACKUP_CMD wraps the calls.
src = sqlite3.connect("file:<src>?mode=ro", uri=True, timeout=10)  # ro: gateway may hold the DB
dst = sqlite3.connect("<dst>")
src.backup(dst)                       # merges -wal content into a standalone copy
dst.execute("pragma journal_mode=delete")  # normalize WAL header (see Wrong/Correct)
```

- Sources: canonical `agents/<id>/agent/openclaw-agent.sqlite` → archived as
  `AGENT_WORKSPACE/sessions/openclaw-agent.sqlite`; plus every
  `agents/<id>/sessions/*.sqlite` (basename kept, `openclaw-agent.sqlite`
  name skipped to avoid clobbering the canonical archive). Missing files are
  skipped silently (4/5.x has no SQLite store).
- Destination `journal_mode=delete` normalization is **mandatory**:
  `Connection.backup()` copies the source header verbatim, leaving the
  archive WAL-flagged; a WAL-flagged file requires a writable directory on
  every open (SQLite creates `-shm`), so read-only media opens fail with
  "attempt to write a readonly database".
- The backup command runs **outside** `_SYNC_CMD` as its own
  `execute_command` wrapped in `try/except` + `logging.warning`: backend.py
  converts any `post_run_collect` exception into `status=error, score=0`, so
  archival must be exception-isolated. `_SYNC_CMD` itself stays byte-stable
  (the JSONL grading export path must not move).
- Flush-wait `_wait_for_session_flush(session_id=...)` polls
  `transcript_events` (count + max(created_at) stable across two 1s polls →
  `SESSION_READY_SQLITE`); its `execute_command` timeout (25s) must exceed
  script deadline (12s) + sqlite busy timeout (5s) — docker.py **raises**
  `TimeoutError` into `run()` otherwise, flipping the task to error.
- Archived via `save_workspace: true` → `results/workspaces/<task_id>/sessions/`.
  Note: the per-agent DB doubles as the auth store; the archive may contain
  credentials (same exposure class as the already-archived `openclaw.json`
  apiKey). `save_workspace` is opt-in.

## 4. Validation & Error Matrix

| Condition | Behavior |
|---|---|
| wipe pattern would match `agents/<id>/agent/…` | forbidden — helper must only emit `sessions/` paths |
| `doctor --fix` literal outside `_run_doctor_fix` | forbidden (single implementation) |
| `timeout=180` on doctor | forbidden; helper default ≥ 300 |
| version ladder (`== "2026.x"` / `"2026.x" in version`) | forbidden in agent source |
| `_parse_version_output("not installed")` / empty | return `""` → property `"unknown"` |
| config `openclaw_version` set | wins over probe |
| SQLITE_STORE path + auth JSON present | delete JSON; do not also doctor-migrate |
| NO_SQLITE path on 4/5.x after doctor | JSON remains source; no migration expected |
| Docker unavailable in dev env | static gates + user-run `./buildimage.sh` smoke (AC escape hatch) |
| backup appended into `_SYNC_CMD` (single command) | forbidden — one locked store exceeding the shared timeout flips TaskResult to error |
| archived sqlite left WAL-flagged (no `journal_mode=delete`) | forbidden — archive unreadable from read-only media |
| flush-wait `execute_command` timeout ≤ script deadline + busy timeout | forbidden — docker.py raises `TimeoutError` into `run()` → `status=error` |

## 5. Good / Base / Bad Cases

- **Good** — 9.1 two-task run with `--docker-image pawbench-openclaw:9.1`:
  task B transcript has no task A messages; no
  `AUTH_PROFILE_MIGRATION_REQUIRED` in gateway log; `Agent.version == 2026.9.1`.
- **Base** — 8.1 image via `./buildimage.sh 8.1` + same agent code: wipe
  deletes JSONL only; SQLITE_STORE auth path unchanged; grading regression
  still 166 PASS.
- **Bad** — wipe under `agents/<id>/agent/` (destroys auth SQLite → re-onboard);
  version `if` ladder for 9.1 only; second doctor implementation with 180s
  timeout; retagging `OPENCLAW_DEFAULT_IMAGE` as a side effect of “support 9.1”.

## 6. Tests Required

- **Unit** — `scripts/test_openclaw_compat.py` (stdlib `unittest`, no
  network/Docker): version parse/prefix/garbage; property override +
  `unknown`; wipe contains all session globs and never `/agent/` or
  `openclaw-agent.sqlite`; `run` uses wipe helper; doctor helper default ≥
  300; exactly one `doctor --fix` literal in agent source; setup+run call
  helper; `_stabilise_gateway_plugins` has no `timeout=180`; no version
  ladders via regex.
- **Regression** — `python3 scripts/verify_file_read_grading.py` exit 0
  (166 PASS). Grading/task/`transcript_search` must stay untouched for this
  contract.
- **Static** — `python3 -m py_compile pawbench/agents/impl/openclaw_agent.py`;
  `bash -n buildimage.sh`; Dockerfile `OPENCLAW_VERSION` matches target.
- **Backup script (extract embedded text, run against temp WAL db)** — writer
  held open with rows only in `-wal`: backup copy contains all rows, header
  normalized (openable read-only), no `-wal`/`-shm` residue; missing source →
  `SQLITE_BACKUP_SKIP` exit 0; re-run over existing destination idempotent.
  `_SYNC_CMD` rendered string byte-identical to pre-change HEAD.
- **Image smoke (when Docker available)** — `./buildimage.sh 9.1`; one task
  against `:9.1` and one against `:8.1`; assert session isolation and
  `Agent.version`; with `save_workspace: true`, host-side
  `sqlite3 results/workspaces/<task_id>/sessions/openclaw-agent.sqlite
  "select count(*) from transcript_events where session_id='<run session>'"`
  returns non-zero.

## 7. Wrong vs Correct

#### Wrong — version ladder + auth wipe scope creep

```python
if self.version.startswith("2026.9"):
    rm agents/<id>/agent/*.sqlite   # destroys auth
    run doctor_9_1_only()
```

#### Correct — path shape + capability probe + shared doctor

```python
await environment.execute_command(
    self._session_wipe_command(agent_id_lower),  # sessions/ only
    timeout=15,
)
if "SQLITE_STORE" in probe:
    rm auth-profiles.json
else:
    write auth-profiles.json
    await self._run_doctor_fix(environment, env_prefix=env_prefix)  # timeout=300
```

#### Wrong — cp a WAL database (loses data) / ship a WAL-flagged archive

```bash
cp /root/.openclaw/agents/<id>/agent/openclaw-agent.sqlite "$DEST/sessions/"
# newest transactions may still live only in -wal → archive misses the run's
# final events; cp of the trio is not atomic either.
```

```python
src.backup(dst)  # and nothing else
# dst keeps the WAL header (bytes 18/19 = 2/2) → opening it from read-only
# media fails: "attempt to write a readonly database"
```

#### Correct — backup API + journal_mode normalization + exception isolation

```python
src = sqlite3.connect("file:%s?mode=ro" % s, uri=True, timeout=10)
dst = sqlite3.connect(d)
try:
    src.backup(dst)                       # standalone copy, -wal merged
    dst.execute("pragma journal_mode=delete")  # header → rollback-journal mode
except Exception as e:
    print("SQLITE_BACKUP_SKIP: %s" % e)   # never fail the task
```

Wrapped in its own `execute_command` (60s) + outer `try/except` in
`post_run_collect`, separate from `_SYNC_CMD`.

---

## Common Mistake

**Symptom**: second task on 9.1 still sees the first task’s conversation, or
gateway log shows `AUTH_PROFILE_MIGRATION_REQUIRED` and every `agent --message`
fails.

**Cause**: wipe only deleted `*.jsonl`; or auth JSON written without a
follow-up doctor migrate on the NO_SQLITE path; or doctor timed out at 180s
during plugin install.

**Prevention**: wipe via `_session_wipe_command` (session SQLite globs);
always pair NO_SQLITE JSON write with `_run_doctor_fix`; keep doctor through
the shared helper (≥300s) and pre-warm `doctor --fix` in the Dockerfile.

## Common Mistake 2 — archived SQLite unreadable or backup flips the task

**Symptom**: 9.1 run "succeeds" but `results/workspaces/<task_id>/sessions/`
has no sqlite (or a truncated one); or the sqlite exists but tools report
"attempt to write a readonly database" / miss the final assistant turn; or a
random task turns `status=error` right after collection.

**Cause**: the per-agent DB is WAL-mode with the gateway holding a live
connection — plain `cp` of the main file misses `-wal`-resident events;
`Connection.backup()` alone preserves the WAL header (archive demands a
writable directory); and a backup failure/timeout inside the shared
`_SYNC_CMD` raises into `backend.py`, which zeroes the TaskResult.

**Prevention**: backup API (read-only source) + `pragma journal_mode=delete`
on the destination + `SQLITE_BACKUP_SKIP`-style swallow + run as a separate
exception-isolated command, never inside `_SYNC_CMD`.

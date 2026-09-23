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
→ session flush / collect (unchanged)
```

Wipe before gateway liveness so a held SQLite handle is resolved by the
existing restart path, not by deleting around a live gateway.

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
- **Image smoke (when Docker available)** — `./buildimage.sh 9.1`; one task
  against `:9.1` and one against `:8.1`; assert session isolation and
  `Agent.version`.

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

# Design — Support OpenClaw 2026.9.1 (multi-version)

## 1. Boundaries

| Layer | Touched? | Notes |
|---|---|---|
| `docker/Dockerfile.pawbench-openclaw` | YES | bump default `OPENCLAW_VERSION` → `2026.9.1`; add doctor pre-warm |
| `buildimage.sh` | YES | default tag → `pawbench-openclaw:9.1`; accept version arg |
| `pawbench/agents/impl/openclaw_agent.py` | YES | session wipe, auth no-sqlite path, doctor timeout, dynamic `version` |
| Grading / task data / `transcript_search` | NO | AC6 regression guard only |
| `install()` npm pin `2026.4.24` | NO | user decision C1 |
| Untracked `Dockerfile.pawbench-openclaw-8.1` | NO (user-owned) | referenced as the 8.1 freeze artifact |

Version selection at **runtime** is already parameterized:
`agent_config["docker_image"]` → `backend.py:247` → factory default
`OPENCLAW_DEFAULT_IMAGE`. Multi-version runs therefore need **image tags +
build files**, not agent-code version switches.

## 2. Contracts

### 2.1 Filesystem layout (assumed by wipe/auth logic)

```
/root/.openclaw/
  openclaw.json                          # config (apiKey path — multi-version)
  agents/<id>/
    sessions/
      *.jsonl *.jsonl.lock sessions.json # JSONL conversation (wipe)
      *.trajectory.jsonl                 # trajectory (wipe)
      *.sqlite *-wal *-shm               # 9.1 session store (wipe)  ← NEW
    agent/
      openclaw-agent.sqlite              # AUTH store (NEVER wipe)
      auth-profiles.json                 # legacy auth (see §4)
```

Session SQLite path source (9.1): `session-sqlite-target.ts` resolves under
`…/sessions/`. Auth SQLite path: `…/agent/openclaw-agent.sqlite`. The two
never collide; the wipe pattern is scoped to `sessions/` only, which makes
AC2 safe **by path shape, not by version string**.

### 2.2 Probe contracts (capability detection)

| Probe | Command / test | Answers |
|---|---|---|
| binary | `command -v openclaw` | image has agent (existing) |
| session/auth sqlite | `test -f …/agent/openclaw-agent.sqlite` | SQLITE_STORE (existing) |
| reported version | `openclaw --version` | bookkeeping for `version` property |
| session store files | glob under `sessions/` | what to wipe (data-driven) |

Forbidden: `if "2026.9" in version:` ladders. Allowed: "file exists →
handle it" (same style as existing SQLITE_STORE probe).

## 3. Data flow (per-task run, after change)

```
run():
  1. WIPE sessions/  (jsonl + locks + sessions.json + *.sqlite*)
     └─ auth sqlite at agent/ untouched
  2. _ensure_gateway (unchanged)
  3. agents list check / re-add (unchanged)
  4. auth reconcile:  if SQLITE_STORE: rm auth-profiles.json (unchanged)
                      else: write auth-profiles.json THEN ensure migration
                            (see §4)
  5. agent --message (unchanged; 9.1 one-shot exit is strictly safer)
  6. _wait_for_session_flush (unchanged; envelope identical 8.1/9.1)
  7. copy sessions → workspace (unchanged; already prefers trajectory,
     falls back to plain jsonl; post_run_collect SQLite export stays as
     last resort)
```

## 4. Auth strategy (R3) — decision

**Chosen: "JSON write + doctor migrate" on the no-sqlite path.**

Why:

- 4/5.x images genuinely need `auth-profiles.json` (research: they read it
  with priority). Deleting the write would regress old images.
- 9.1's gate trips **only when legacy JSON exists and SQLite has no
  migrated credentials**. `doctor --fix` is the official importer on both
  8.1 and 9.1 (`doctor-auth-flat-profiles.ts`: import → verify → receipt →
  archive), idempotent, non-interactive under non-TTY.
- Capability-based: we don't branch on version; we always ensure the state
  is *converged* (either JSON is the live source on old images, or doctor
  has migrated it on new ones).

Mechanics:

1. Keep existing write of `auth-profiles.json` when probe says NO_SQLITE.
2. Immediately run `openclaw doctor --fix` (timeout **300s**, was 180s)
   **on the no-sqlite path only**, before any `agent --message` traffic.
   On 4/5.x doctor is a no-op for this gate; on 8.1/9.1 it migrates.
3. Reuse the existing `_stabilise_gateway_plugins` doctor call where it
   already runs; the auth-path doctor may call the same helper to avoid a
   second implementation.

Rejected alternatives:

- **Rely only on `openclaw.json` apiKey, delete JSON always**: breaks
  4/5.x priority reads (regression risk outside our AC matrix).
- **Version-string branch** (`if >= 9.1: …`): violates C4, rots on 9.2.

## 5. Session wipe (R2) — decision

Extend the existing `rm -f` at `openclaw_agent.py:1008-1012` to:

```
rm -f  …/sessions/*.jsonl
       …/sessions/*.jsonl.lock
       …/sessions/sessions.json
       …/sessions/*.sqlite
       …/sessions/*.sqlite-wal
       …/sessions/*.sqlite-shm
       …/sessions/*.db          # belt-and-suspenders if 9.1 uses .db
```

Scoped strictly under `sessions/`. Gateway may hold the DB open: wipe runs
**before** `_ensure_gateway` restart decisions; if 9.1 refuses deletion
because the gateway holds a handle, the gateway is killed/restarted by the
existing liveness path anyway — acceptable ordering is: wipe → liveness
check → restart if needed. If a held lock proves problematic in smoke, the
fallback is "kill gateway → wipe → start", noted as a rollback point in
implement.md.

Rejected: recreating the agent every task (`agents delete/add`) — heavier,
forces gateway restart every task, and destroys auth SQLite (must recreate
credentials), all already covered more narrowly by the existing re-add
path when `agents list` misses the agent.

## 6. Docker / build (R1) — decision

Follow the established 5.28 pattern; user already froze 8.1:

| File | Version | Tag (buildimage) |
|---|---|---|
| `Dockerfile.pawbench-openclaw-5.28` | 2026.5.28 | `pawbench-openclaw:5.28` |
| `Dockerfile.pawbench-openclaw-8.1` (user, untracked) | 2026.8.1 | `pawbench-openclaw:8.1` |
| `Dockerfile.pawbench-openclaw` (main, edited by us) | **2026.9.1** | `pawbench-openclaw:9.1` |

- Main Dockerfile gains a `doctor --fix` pre-warm RUN after onboard/config
  and before gateway warm-up (R4/AC4): migrates baked placeholder auth
  state at build time so the first runtime doctor is idempotent and cheap.
  Must run with `OPENCLAW_DISABLE_BONJOUR=1`, tolerate failure
  (`|| true`) matching existing style, and keep lock cleanup after it
  (existing L184 deletes `*.lock`).
- `buildimage.sh`: accept optional version arg (default `9.1`), derive
  Dockerfile suffix and tag:
  `./buildimage.sh [9.1|8.1|5.28]` → `-f docker/Dockerfile.pawbench-openclaw[-X.Y] -t pawbench-openclaw:X.Y`.
  Backward compatible: no arg → 9.1 (new default).
- `OPENCLAW_DEFAULT_IMAGE` stays `openclaw-pawbench:latest` (factory
  default) — **not** changed this task: retagging defaults is an ops
  decision; runs already override via `--docker-image`. Document in
  implement.md smoke that 9.1 runs pass
  `--docker-image pawbench-openclaw:9.1`.

## 7. Version property (R5) — decision

```python
@property
def version(self) -> str:
    # Prefer the value cached during setup()/run() by _detect_version();
    # fall back to config override "openclaw_version"; else "unknown".
```

- `_detect_version(environment)`: run `openclaw --version` once per
  container (cache on `self._detected_version`), parse first
  `2026.x.y` token.
- Config override `self.config.get("openclaw_version")` wins if set
  (lets a run label a custom image without probing).
- Detection failure → `"unknown"` (never a wrong hard-coded constant).
- Call site: end of `setup()` (and lazily at `run()` start if unset).

## 8. Tradeoffs

| Choice | Pro | Con |
|---|---|---|
| Path-scoped wipe vs version branch | future stores under `sessions/` auto-covered | unknown future layout outside that dir still leaks |
| JSON+doctor vs pure-config auth | keeps 4/5.x, satisfies 9.1 gate | doctor costs time (mitigated by pre-warm + 300s) |
| Keep default image constant | no surprise for existing scripts | users must pass `--docker-image` for 9.1 |
| Dynamic version probe | correct labels multi-version | one extra CLI call per setup (cached) |

## 9. Compatibility & rollout / rollback

- **Rollout**: edit agent + Dockerfile + buildimage → `py_compile` +
  `verify_file_read_grading.py` → optional Docker build smoke → single
  commit batch (work commits first, then archive/journal via finish-work).
- **Rollback**: all changes are in ≥3 files with no schema/data
  migrations; `git revert` restores 8.1 behavior. Dockerfile bump
  rollback = rebuild from `Dockerfile.pawbench-openclaw-8.1`.
- **8.1 safety**: wipe additions only delete files old versions also
  treat as session state; doctor on 8.1 is already called today;
  auth write path unchanged except an extra idempotent doctor.

## 10. Verification strategy (maps to ACs)

1. Static: `py_compile`; grep for forbidden version ladders; confirm wipe
   pattern does not match `…/agent/…` paths.
2. Grading regression: `python3 scripts/verify_file_read_grading.py`.
3. Unit-ish: a small stdlib test or scripted assertion for
   `_detect_version` parsing and wipe command construction (if adding
   tests is heavier than the repo norm, a scripted smoke in implement.md
   suffices — repo has no pytest suite).
4. Image smoke (when Docker available): AC1 build + `--version`;
   runtime: one task against `:9.1` and one against `:8.1` checking
   session isolation (task B transcript contains no task A messages) and
   `Agent.version` correctness.

# Implement — Support OpenClaw 2026.9.1 (multi-version)

Ordered execution plan. Each step lists files, validation, and the AC it
serves. Do not start until `task.py start` has been run.

## Step 1 — Session wipe (R2 / AC2)

**File**: `pawbench/agents/impl/openclaw_agent.py` (`run()`, ~L1006-1014)

- Extend the existing `rm -f` to also delete under
  `/root/.openclaw/agents/<id>/sessions/`:
  `*.sqlite`, `*.sqlite-wal`, `*.sqlite-shm`, `*.db`.
- Keep the glob strictly under `sessions/`; never touch
  `agents/<id>/agent/`.
- Keep wipe order: wipe → `_ensure_gateway` (as today).

**Validate**: inspect constructed command (string contains `sessions/*.sqlite`
and does not contain `agents/` + `/agent/`); `py_compile`.

**Rollback point**: if smoke shows 9.1 refusing deletion while gateway holds
the DB, move wipe to after `_kill_gateway` / before `_start_gateway`
(design §5 fallback).

## Step 2 — Auth no-sqlite path (R3 / AC3)

**File**: same (`setup()` ~L281-295 and `run()` re-add ~L1051-1076)

- After the NO_SQLITE branch writes `auth-profiles.json`, run
  `OPENCLAW_DISABLE_BONJOUR=1 openclaw doctor --fix 2>&1 | tail -5 || true`
  with **timeout=300**, before any agent turn.
- Do **not** change the SQLITE_STORE branch (delete JSON).
- Reuse a tiny helper (e.g. `_run_doctor_fix(environment, timeout=300)`)
  shared with `_stabilise_gateway_plugins` so there is one doctor
  implementation.

**Validate**: `py_compile`; both call sites invoke helper; SQLITE_STORE
branch untouched (diff review).

## Step 3 — Doctor timeout (R4 / AC4a)

**File**: same (`_stabilise_gateway_plugins` ~L854-857)

- Change doctor timeout `180` → `300` (via shared helper from Step 2).

**Validate**: single doctor helper used everywhere; no remaining
`doctor --fix` literal with `timeout=180`.

## Step 4 — Dynamic version (R5 / AC5)

**File**: same

- Add `_detect_version(environment) -> str`: run
  `openclaw --version 2>/dev/null`, parse first `\d{4}\.\d+\.\d+` token,
  cache in `self._detected_version`.
- Call at end of `setup()`; lazy-fill at `run()` start if empty.
- `version` property: config override `openclaw_version` → cached probe →
  `"unknown"`.
- Update stale class docstring (L23-25) to describe image-tag-driven
  versions instead of hard-coded 2026.4.24.
- **Do not** touch `install()` npm pin (C1).

**Validate**: `py_compile`; grep shows `version` property has no literal
`2026.4.24`; parser unit check (inline `python3 -c` with sample outputs
`openclaw/2026.9.1`, `2026.8.1` style strings — accept whatever format
both trees print; verify against real output during smoke if available).

## Step 5 — Dockerfile 9.1 + doctor pre-warm (R1 / AC1 / AC4b)

**Files**:
- `docker/Dockerfile.pawbench-openclaw` (edit)
- `docker/Dockerfile.pawbench-openclaw-8.1` (user-owned, do not edit)
- `buildimage.sh` (edit)

- Main Dockerfile: `ARG OPENCLAW_VERSION=2026.9.1`.
- After config-set block (~L119), add doctor pre-warm:
  `RUN OPENCLAW_DISABLE_BONJOUR=1 openclaw doctor --fix 2>&1 | tail -5 || true`
  — placed **before** gateway warm-up and **before** lock cleanup (L184).
- `buildimage.sh`: optional `$1` version arg, default `9.1`;
  map to Dockerfile path (`docker/Dockerfile.pawbench-openclaw` for
  default/9.1, `…-8.1` / `…-5.28` for frozen files) and tag
  `pawbench-openclaw:$VER`.

**Validate** (no Docker in dev env → static + user smoke):
- `grep OPENCLAW_VERSION docker/Dockerfile.pawbench-openclaw` → 2026.9.1
- `bash -n buildimage.sh`
- Documented AC1 build command for user:
  `./buildimage.sh 9.1`

**Rollback**: rebuild 8.1 via `./buildimage.sh 8.1`.

## Step 6 — Full validation gate (AC6/AC7)

```bash
python3 -m py_compile pawbench/agents/impl/openclaw_agent.py
python3 scripts/verify_file_read_grading.py    # expect exit 0, 166 PASS
grep -n '2026\.9\.1\|2026\.8\.1' pawbench/agents/impl/openclaw_agent.py
#   → no NEW hard-coded version ladders (comments explaining history OK)
grep -n 'doctor --fix' pawbench/agents/impl/openclaw_agent.py
#   → all via shared helper, timeouts ≥300
```

Then dispatch `trellis-check` (sub-agent protocol: begin prompt with
`Active task: .trellis/tasks/09-23-support-openclaw-9.1`).

## Step 7 — Optional live smoke (AC1/AC2/AC3/AC5 end-to-end)

Only if Docker + registry access available; otherwise hand commands to
user and stop at static gates:

```bash
./buildimage.sh 9.1
python3 run_bench.py --agent openclaw --docker-image pawbench-openclaw:9.1 \
  --task-filter T001   # example; exact flags per run_bench.py --help
# then same against pawbench-openclaw:8.1
```

Check: session isolation across two tasks; `Agent.version` matches image;
no `AUTH_PROFILE_MIGRATION_REQUIRED` in `openclaw_gateway.log`.

## Review gates

1. After Steps 1-4 (agent.py): diff self-review vs design §4-§5, py_compile.
2. After Steps 5 (docker): static validate + user-facing build command.
3. After Step 6: `trellis-check` pass → Phase 3 (spec update, commit).

## Explicit non-goals during execution

- No edits to task `.md`, `transcript_search.py`, `grader.py`.
- No `install()` pin change (C1).
- No edits to user-owned `Dockerfile.pawbench-openclaw-8.1`.
- No `OPENCLAW_DEFAULT_IMAGE` default retag (ops decision; use
  `--docker-image`).
- No leaderboard/docs version sweep.

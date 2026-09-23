# Support OpenClaw 2026.9.1 with multi-version compatibility

## Goal

PawBench's OpenClaw harness must run correctly against OpenClaw **2026.9.1**
while remaining compatible with **2026.8.1** (and older images already in
use: 5.28 / 4.x), in a way that scales to future OpenClaw releases without
another round of version-specific rewrites.

## Background (research summary)

Static comparison of `/home/ubuntu/workplace/openclaw` (8.1) vs
`/home/ubuntu/workplace/openclaw-0901` (9.1, tag `v2026.9.1`) plus the
PawBench integration inventory shows:

- **Compatible as-is**: gateway `--token` / port 18789 / `OPENCLAW_GATEWAY_TOKEN`,
  `agents add --non-interactive` (creation gate is main-agent-only),
  every `openclaw.json` key PawBench writes (incl. `auth: "api-key"` and
  model-entry `contextWindow`), session envelope (`model.completed` +
  `messagesSnapshot`, 256KB drop policy identical), tool names
  (`read`/`pdf`/`exec`), onboard flags, Node engines.
- **Breaks / must change**:
  1. Image pin: `docker/Dockerfile.pawbench-openclaw` still ships 2026.8.1.
  2. Cross-task session bleed: `run()` wipe only deletes `*.jsonl` /
     `sessions.json`, but 9.1 stores conversation state primarily in
     SQLite under the sessions dir — prior-task turns leak into the next task.
  3. Auth: when `openclaw-agent.sqlite` is absent, harness writes
     `auth-profiles.json`; 9.1 fails closed with
     `AUTH_PROFILE_MIGRATION_REQUIRED` until `doctor --fix` migrates JSON →
     SQLite.
  4. `doctor --fix` budget: state schema 6→15 / agent 17→19 means more
     migration work; the existing 180s timeout is already documented as
     flaky (plugin-dep hangs).
  5. Version bookkeeping: `OpenClawAgent.version` and the docstring still
     report `2026.4.24` even when the image ships 8.1/9.1 — misleading for
     multi-version runs.
- **Recent file_read fix is positive for 9.1**: `searchable_text` scans
  toolCall name/args; 9.1 keeps tool names; additive-only.

## Requirements

- **R1 Image**: a buildable evaluation image that installs OpenClaw
  `2026.9.1`, following the repo's existing versioned-Dockerfile pattern
  (`Dockerfile.pawbench-openclaw-5.28`, and the already-created
  `Dockerfile.pawbench-openclaw-8.1` freeze), with a matching build script
  tag (e.g. `pawbench-openclaw:9.1`). The frozen `-8.1` Dockerfile is kept
  so 8.1 remains buildable.
- **R2 Multi-version session isolation**: the per-task session wipe in
  `OpenClawAgent.run()` must clear conversation state on both JSONL-based
  (≤8.1 primary) and SQLite-based (9.1 primary) stores, without touching
  the per-agent **auth** SQLite (`agents/<id>/agent/openclaw-agent.sqlite`).
- **R3 Multi-version auth**: the no-sqlite credential path must not leave
  a state that fails 9.1's `AUTH_PROFILE_MIGRATION_REQUIRED` gate, while
  still feeding 4/5.x-era images that read `auth-profiles.json`. Prefer
  probe-based (filesystem / `openclaw --version`) branching over
  hard-coded version strings.
- **R4 doctor budget**: `doctor --fix` must not race the 180s timeout on a
  cold 9.1 state (raise timeout and/or pre-warm during image build).
- **R5 Version reporting**: `OpenClawAgent.version` reports the version
  actually installed in the container (detected at setup/run), not a
  hard-coded stale string; docstring comments updated where edited.
- **R6 No behavior regressions on 8.1**: same code path must keep working
  against the existing `pawbench-openclaw:8.1` image; grading side
  (`transcript_search`, 28-task file_read) needs no change.

## Constraints

- **C1 (user decision, out of scope)**: do NOT change the slow-path pin
  `npm install -g openclaw@2026.4.24` in `install()` — it only runs when
  the image lacks an `openclaw` binary, which never happens in our
  pre-built multi-version images. Accepted as stale-by-design.
- C2 Do not modify grading logic, task `.md` files, or
  `pawbench/utils/transcript_search.py` — research shows they are
  9.1-compatible.
- C3 Do not touch the untracked user file
  `docker/Dockerfile.pawbench-openclaw-8.1` beyond referencing it (it is
  the user's 8.1 freeze; treat as user-owned input).
- C4 Probe-based / capability-based branching preferred; hard-coded
  `if version == "2026.9.1"` ladders are forbidden (future versions must
  not require another ladder).
- C5 `install()` npm pin and `version`-constant-only doc strings outside
  files we already edit: leave alone unless the file is being edited for
  another reason (then fix the adjacent stale comment).

## Acceptance Criteria

- [ ] **AC1**: `docker build -f docker/Dockerfile.pawbench-openclaw -t pawbench-openclaw:9.1 .`
      completes and `openclaw --version` inside the image reports `2026.9.1`
      (build may be executed as smoke on a machine with Docker; if Docker
      is unavailable in the dev environment, the Dockerfile must be
      review-complete and the build command documented for the user).
- [ ] **AC2**: `OpenClawAgent.run()` session wipe removes, under
      `/root/.openclaw/agents/<id>/sessions/`: `*.jsonl`, `*.jsonl.lock`,
      `sessions.json`, **and** session SQLite artifacts (`*.sqlite`,
      `*.sqlite-wal`, `*.sqlite-shm` or equivalent as written by 9.1),
      while **not** deleting
      `/root/.openclaw/agents/<id>/agent/openclaw-agent.sqlite` (auth).
- [ ] **AC3**: the no-sqlite auth path leaves 9.1 able to complete a turn:
      either migrates via `doctor --fix` before gateway traffic, or relies
      on `openclaw.json` `apiKey` and removes the legacy JSON — whichever
      design.md selects — with 4/5.x behavior unchanged.
- [ ] **AC4**: `_stabilise_gateway_plugins` doctor timeout ≥ 300s, and/or
      the 9.1 Dockerfile pre-warms `doctor --fix` at build time.
- [ ] **AC5**: `OpenClawAgent.version` reflects the container's actual
      `openclaw --version` (config override still possible), verified by
      unit-level or smoke evidence.
- [ ] **AC6**: `scripts/verify_file_read_grading.py` still exits 0
      (166 PASS) — grading untouched.
- [ ] **AC7**: `python3 -m py_compile pawbench/agents/impl/openclaw_agent.py`
      clean; no hard-coded `2026.9.1` version ladders in agent logic
      (probes only).
- [ ] **AC8**: 8.1 remains selectable: `docker/Dockerfile.pawbench-openclaw-8.1`
      present and buildable, and runtime image selection via
      `--docker-image` / `agent_config["docker_image"]` documented in
      implement.md smoke section.

## Out of scope

- Changing `install()` npm pin (C1).
- Rebuilding/retagging images on a Docker host beyond what AC1 requires.
- Leaderboard / site / docs version-string sweep
  (`build_leaderboard.py`, `dataset-classification.md`, etc.).
- Hermes / QwenPaw agents.
- Any grading or task-data changes.

## Open questions

- None blocking. Design choices (wipe method, auth strategy, version
  detection point) are resolved in `design.md`.

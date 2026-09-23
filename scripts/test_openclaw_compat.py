#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compat checks for multi-version OpenClaw support (task 09-23).

Stdlib-only on purpose: no pytest, no network, no Docker.
Exit code is 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import inspect
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pawbench.agents.impl.openclaw_agent import OpenClawAgent


class TestVersionParsing(unittest.TestCase):
    def test_parse_prefixed_output(self):
        self.assertEqual(
            OpenClawAgent._parse_version_output("openclaw/2026.9.1"), "2026.9.1"
        )

    def test_parse_bare_output(self):
        self.assertEqual(
            OpenClawAgent._parse_version_output("2026.8.1\n"), "2026.8.1"
        )

    def test_parse_garbage(self):
        self.assertEqual(OpenClawAgent._parse_version_output("not installed"), "")
        self.assertEqual(OpenClawAgent._parse_version_output(""), "")

    def test_version_property_config_override(self):
        agent = OpenClawAgent(openclaw_version="2026.9.1")
        self.assertEqual(agent.version, "2026.9.1")

    def test_version_property_unknown_without_probe(self):
        agent = OpenClawAgent()
        self.assertEqual(agent.version, "unknown")

    def test_detect_version_caches_probe(self):
        src = inspect.getsource(OpenClawAgent._detect_version)
        self.assertIn("_detected_version", src)
        self.assertIn("openclaw --version", src)


class TestSessionWipe(unittest.TestCase):
    def _cmd(self) -> str:
        return OpenClawAgent._session_wipe_command("bench-qwen3-6-plus")

    def test_wipes_jsonl_and_session_sqlite(self):
        cmd = self._cmd()
        self.assertIn("sessions/*.jsonl", cmd)
        self.assertIn("sessions/*.jsonl.lock", cmd)
        self.assertIn("sessions/sessions.json", cmd)
        self.assertIn("sessions/*.sqlite", cmd)
        self.assertIn("sessions/*.sqlite-wal", cmd)
        self.assertIn("sessions/*.sqlite-shm", cmd)
        self.assertIn("sessions/*.db", cmd)

    def test_never_touches_auth_sqlite(self):
        cmd = self._cmd()
        self.assertNotIn("/agent/", cmd)
        self.assertNotIn("openclaw-agent.sqlite", cmd)

    def test_run_uses_wipe_helper(self):
        src = inspect.getsource(OpenClawAgent.run)
        self.assertIn("_session_wipe_command", src)


class TestDoctorHelper(unittest.TestCase):
    def test_shared_helper_default_timeout(self):
        sig = inspect.signature(OpenClawAgent._run_doctor_fix)
        self.assertGreaterEqual(sig.parameters["timeout"].default, 300)

    def test_stabilise_uses_shared_helper(self):
        src = inspect.getsource(OpenClawAgent._stabilise_gateway_plugins)
        self.assertIn("_run_doctor_fix", src)
        self.assertNotIn("timeout=180", src)

    def test_auth_paths_call_doctor_helper(self):
        for meth in (OpenClawAgent.setup, OpenClawAgent.run):
            self.assertIn("_run_doctor_fix", inspect.getsource(meth))

    def test_no_hardcoded_doctor_literal_outside_helper(self):
        src = inspect.getsource(OpenClawAgent)
        helper_src = inspect.getsource(OpenClawAgent._run_doctor_fix)
        # every "doctor --fix" execute_command lives in the shared helper
        self.assertEqual(src.count("doctor --fix 2>&1"), 1)
        self.assertIn("doctor --fix 2>&1", helper_src)


class TestNoVersionLadders(unittest.TestCase):
    def test_agent_source_has_no_version_ladders(self):
        src = (ROOT / "pawbench" / "agents" / "impl" / "openclaw_agent.py").read_text()
        # no `if version == ...` / `in version` style branches on release strings
        for pattern in (r"version\s*==\s*[\"']2026\.", r"[\"']2026\.\d+\.\d+[\"']\s+in\s+"):
            self.assertIsNone(re.search(pattern, src), f"forbidden ladder: {pattern}")


if __name__ == "__main__":
    unittest.main(verbosity=2)

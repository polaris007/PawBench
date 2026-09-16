# -*- coding: utf-8 -*-
"""Searchable transcript text for text-based automated grading.

Single source of truth for "what transcript text a text-based automated check
may search" (task 09-16-unify-file-read-grading).

Background: the historical per-task ``_all_text()`` copies collected only
``role == "assistant"`` ``type == "text"`` blocks, so a file read whose only
evidence lived in ``toolCall.arguments`` / ``toolResult`` (e.g. OpenClaw 8.1
reading ``fixtures/GroundingME.pdf`` via a dedicated ``pdf`` tool) scored
``file_read = 0.0``. This helper additionally surfaces tool-call names plus
their serialized payloads and tool-result text.

Contract (additive-only): the returned string is a superset of what the legacy
``_all_text()`` produced for the same transcript, so no transcript that
matched before can stop matching. ``user``-role messages are never collected.
The function is total: it never raises and returns ``""`` for empty or
malformed input, because a grader must not fail on an unexpected shape.
"""

from __future__ import annotations

import json
from typing import Any


_TOOL_CALL_TYPES = ("toolCall", "tool_use", "plugin_call")
_TOOL_RESULT_ROLES = ("toolResult", "tool")


def _payload_text(payload: Any) -> str:
    """Best-effort stringify of a tool-call argument payload."""
    if payload is None:
        return ""
    if isinstance(payload, str):
        return payload
    try:
        return json.dumps(payload, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        pass
    try:
        return str(payload)
    except Exception:
        return ""


def _blocks_text(blocks: Any) -> str:
    """Join the ``text`` of text-shaped content blocks."""
    if isinstance(blocks, str):
        return blocks
    if isinstance(blocks, dict):
        # Some harnesses emit a single mapping instead of a list.
        text = blocks.get("text")
        if isinstance(text, str) and text:
            return text
        return _payload_text(blocks)
    if not isinstance(blocks, list):
        return ""
    parts: list[str] = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        text = block.get("text")
        if isinstance(text, str) and text:
            parts.append(text)
    return " ".join(parts)


def _tool_call_text(block: dict) -> str:
    """Render one tool-call block as ``name`` + serialized payload."""
    name = (
        block.get("name")
        or block.get("tool_name")
        or block.get("toolName")
        or ""
    )
    payload = block.get("arguments")
    if payload is None:
        payload = block.get("input")
    if payload is None:
        payload = block.get("data")
    chunks = [str(name)] if name else []
    rendered = _payload_text(payload)
    if rendered:
        chunks.append(rendered)
    return " ".join(chunks)


def searchable_text(transcript: Any) -> str:
    """Collect searchable text from a transcript event list.

    Includes, in order: assistant ``text`` blocks (legacy behavior), tool-call
    names plus serialized arguments, and tool-result text. ``user`` messages
    are excluded so a path mentioned only in the prompt yields no signal.
    """
    if not isinstance(transcript, list):
        return ""
    parts: list[str] = []
    for event in transcript:
        try:
            if not isinstance(event, dict):
                continue
            message = event.get("message", event)
            if not isinstance(message, dict):
                continue
            role = message.get("role", "")
            content = message.get("content", "")
            if role == "assistant":
                if isinstance(content, str):
                    if content:
                        parts.append(content)
                elif isinstance(content, list):
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        block_type = block.get("type")
                        if block_type == "text":
                            text = block.get("text") or ""
                            if isinstance(text, str) and text:
                                parts.append(text)
                        elif block_type in _TOOL_CALL_TYPES:
                            rendered = _tool_call_text(block)
                            if rendered:
                                parts.append(rendered)
            elif role in _TOOL_RESULT_ROLES:
                rendered = _blocks_text(content)
                if rendered:
                    parts.append(rendered)
        except Exception:
            continue
    return " ".join(parts)

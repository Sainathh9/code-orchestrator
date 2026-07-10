"""
Conditional edge functions for the orchestration graph.

LangGraph conditional edges work like this:
  - They receive the current GraphState.
  - They return a string key that maps to a downstream node name.
  - They CANNOT mutate state — state mutation lives in nodes only.

This module also contains analyze_failure(), which is the exact error
classification logic from the original orchestrator — kept here so it is
co-located with the routing logic that depends on it.
"""

from __future__ import annotations

import logging

from app.orchestrator.graph.state import GraphState

logger = logging.getLogger("orchestrator.graph.edges")

# Mirror the constants from the old Orchestrator class so behaviour is
# identical without importing from the old file.
MAX_TRIES = 3
MAX_NO_PROGRESS = 2


# ── Error classifier ──────────────────────────────────────────────────────────

def analyze_failure(stdout: str, stderr: str) -> str:
    """
    Classify a test failure into a broad error category.

    This is a pure function copied 1-to-1 from the original
    Orchestrator.analyze_failure() so routing behaviour is preserved exactly.
    """
    text = (stdout + stderr).lower()

    if "module not found" in text:
        return "IMPORT_ERROR"
    if "syntaxerror" in text:
        return "SYNTAX_ERROR"
    if "assert" in text or "failed" in text:
        return "TEST_FAILURE"
    if "timeout" in text:
        return "TIMEOUT"

    return "UNKNOWN_ERROR"


# ── Conditional edge functions ────────────────────────────────────────────────

def route_after_analysis(state: GraphState) -> str:
    """
    The central routing decision of the retry loop.

    Called by LangGraph after the ``analyze_progress`` node has already
    updated ``no_progress_count`` and ``last_error_type`` in state.

    Returns one of two string keys defined in the conditional edge map in
    builder.py: ``"to_finalize"`` or ``"to_debug"``.

    Preserves all four stop conditions from the original orchestrator:
      1. Tests passed              → success path to finalize
      2. MAX_TRIES exhausted       → failure path to finalize
      3. No progress (stuck)       → failure path to finalize
      4. Timeout detected          → failure path to finalize
    """
    # ── 1. success ────────────────────────────────────────────────────────────
    if state.get("passed", False):
        logger.info("route_after_analysis → finalize (tests passed)")
        return "to_finalize"

    # ── 2. out of attempts ────────────────────────────────────────────────────
    if state.get("iteration", 0) >= MAX_TRIES:
        logger.info("route_after_analysis → finalize (MAX_TRIES reached)")
        return "to_finalize"

    # ── 3. stuck — same error repeated too many times ─────────────────────────
    if state.get("no_progress_count", 0) >= MAX_NO_PROGRESS:
        logger.warning("route_after_analysis → finalize (no progress detected)")
        return "to_finalize"

    # ── 4. timeout — running more attempts is pointless ───────────────────────
    error_type = analyze_failure(
        state.get("stdout", ""),
        state.get("stderr", ""),
    )
    if error_type == "TIMEOUT":
        logger.warning("route_after_analysis → finalize (timeout detected)")
        return "to_finalize"

    # ── default: debug and retry ──────────────────────────────────────────────
    logger.info(
        "route_after_analysis → debug "
        f"(error={error_type}, iteration={state.get('iteration')}, "
        f"no_progress={state.get('no_progress_count')})"
    )
    return "to_debug"

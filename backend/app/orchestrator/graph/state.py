"""
GraphState — the single source of mutable data shared across all graph nodes.

Design rules:
- Must be a TypedDict (not Pydantic): LangGraph reads the type hints to
  understand which keys can be merged from partial node return dicts.
- All values must be JSON-serialisable so optional checkpointing works
  without extra configuration. That is why workspace_path is str, not Path,
  and datetimes are ISO strings.
- Nodes return *partial* dicts — only the keys they change. LangGraph merges
  these into the full state automatically.
"""

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict


class GraphState(TypedDict, total=False):
    """
    Shared state flowing through every node of the orchestration graph.

    Fields marked with their lifecycle:
      [INIT]  set by node_initialize
      [LOOP]  updated on every retry iteration
      [FINAL] written once by node_finalize
    """

    # ── inputs ────────────────────────────────────────────────────────────────
    requirement: str                    # user-provided, set before graph.invoke()
    user_id: Optional[str]              # authenticated user ID, set before graph.invoke()
    is_code: bool                       # whether the requirement asks for code


    # ── execution identity [INIT] ─────────────────────────────────────────────
    execution_id: str                   # UUID created by node_initialize
    workspace_path: str                 # str, not Path (JSON-serialisable)
    status: str                         # "running" | "success" | "failed"
    version: int                        # code version counter (incremented by debugger)
    iteration: int                      # current retry attempt number
    started_at: str                     # ISO datetime string

    # ── retry-loop bookkeeping [LOOP] ─────────────────────────────────────────
    last_error_type: Optional[str]      # error category from previous attempt
    no_progress_count: int              # consecutive attempts with same error type

    # ── last runner output [LOOP] ─────────────────────────────────────────────
    passed: bool                        # did pytest pass?
    stdout: str                         # pytest stdout
    stderr: str                         # pytest stderr
    exit_code: int                      # pytest exit code

    # ── final aggregates [FINAL] ──────────────────────────────────────────────
    tries_used: int                     # total iterations consumed

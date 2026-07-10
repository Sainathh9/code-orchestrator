"""
Graph assembly — compiles the LangGraph StateGraph from nodes and edges.

Why a compile_graph() factory instead of a module-level compiled graph?
  - Keeps the graph testable: tests can monkeypatch individual node functions
    before calling compile_graph() without affecting other test modules.
  - Makes the wiring explicit and readable in one place.
  - The compiled graph object is stateless; state lives in the invocation dict.
    In production, Orchestrator.__init__ calls compile_graph() once and reuses
    the result for every job — there is no per-invocation overhead.

Graph topology (matches the plan diagram exactly):

  START
    │
  initialize
    │
  generate_code
    │
  generate_tests
    │
  run_tests ◄─────────────────────────────────────────────────────┐
    │                                                              │
  save_iteration                                                   │
    │                                                              │
  analyze_progress                                                 │
    │                                                              │
    ├── "to_finalize" ──► finalize ──► END                        │
    └── "to_debug"    ──► debug ───────────────────────────────────┘
"""

from __future__ import annotations

from langgraph.graph import StateGraph, END

from app.orchestrator.graph.state import GraphState
from app.orchestrator.graph.nodes import (
    node_initialize,
    node_generate_code,
    node_generate_tests,
    node_run_tests,
    node_save_iteration,
    node_analyze_progress,
    node_debug,
    node_finalize,
)
from app.orchestrator.graph.edges import route_after_analysis


def route_after_generation(state: GraphState) -> str:
    if not state.get("is_code", True):
        return "to_save"
    return "to_generate_tests"


def route_after_save(state: GraphState) -> str:
    if not state.get("is_code", True):
        return "to_finalize"
    return "to_analyze_progress"


def compile_graph():
    """
    Build and compile the orchestration StateGraph.

    Returns a CompiledGraph ready to be invoked with:
        graph.invoke({"requirement": "..."})

    The returned graph is thread-safe and can be shared across concurrent
    RQ worker calls — each invocation creates its own isolated state dict.
    """
    builder = StateGraph(GraphState)

    # ── Register nodes ────────────────────────────────────────────────────────
    builder.add_node("initialize",       node_initialize)
    builder.add_node("generate_code",    node_generate_code)
    builder.add_node("generate_tests",   node_generate_tests)
    builder.add_node("run_tests",        node_run_tests)
    builder.add_node("save_iteration",   node_save_iteration)
    builder.add_node("analyze_progress", node_analyze_progress)
    builder.add_node("debug",            node_debug)
    builder.add_node("finalize",         node_finalize)

    # ── Entry point ───────────────────────────────────────────────────────────
    builder.set_entry_point("initialize")

    # ── Edges ─────────────────────────────────────────────────────────────────
    builder.add_edge("initialize",       "generate_code")

    # Conditional edge after generate_code
    builder.add_conditional_edges(
        "generate_code",
        route_after_generation,
        {
            "to_save": "save_iteration",
            "to_generate_tests": "generate_tests",
        }
    )

    builder.add_edge("generate_tests",   "run_tests")
    builder.add_edge("run_tests",        "save_iteration")

    # Conditional edge after save_iteration
    builder.add_conditional_edges(
        "save_iteration",
        route_after_save,
        {
            "to_finalize": "finalize",
            "to_analyze_progress": "analyze_progress",
        }
    )

    # ── Loop-back edge: debug feeds back into run_tests ───────────────────────
    # This replaces the `for attempt in range(MAX_TRIES): ... debugger.run()`
    # loop in the original orchestrator. The retry counter is tracked in
    # GraphState["iteration"] and checked in route_after_analysis().
    builder.add_edge("debug",            "run_tests")

    # ── Conditional edge: the retry/stop decision ─────────────────────────────
    # route_after_analysis() reads GraphState and returns one of two keys.
    # The dict maps those keys to actual node names.
    builder.add_conditional_edges(
        "analyze_progress",
        route_after_analysis,
        {
            "to_finalize": "finalize",
            "to_debug":    "debug",
        },
    )

    # ── Terminal edge ─────────────────────────────────────────────────────────
    builder.add_edge("finalize", END)

    return builder.compile()


"""
Orchestrator — thin adapter between the RQ task and the LangGraph graph.

What changed vs the original:
  - The hand-rolled retry loop (`for attempt in range(MAX_TRIES)`) is gone.
  - The graph (compiled once in __init__) now owns the control flow.
  - analyze_failure() moved to graph/edges.py (co-located with routing logic).
  - DB writes moved into the individual graph nodes.

What did NOT change:
  - The public signature: Orchestrator().run(requirement) -> ExecutionResult
  - All agents (CodeAgent, TestAgent, DebuggerAgent) — untouched.
  - Runner — untouched.
  - ExecutionContext, repositories, DB models — untouched.
  - RQ task (app/queue/tasks.py) — calls this identically.
  - External API — no change.
"""

from app.orchestrator.graph.builder import compile_graph
from app.schemas.execution_result import ExecutionResult


class Orchestrator:

    MAX_TRIES = 3        # kept for reference; enforced inside graph/edges.py
    MAX_NO_PROGRESS = 2  # kept for reference; enforced inside graph/edges.py

    def __init__(self):
        # Compile once — the graph object is stateless and reusable across
        # concurrent invocations (each call to .invoke() gets its own state dict).
        self.graph = compile_graph()

    def run(self, requirement: str, user_id: str = None, model: str = None) -> ExecutionResult:
        """
        Execute the full code-generation → test → debug pipeline.

        Args:
            requirement: Natural-language description of the code to generate.
            user_id: The ID of the authenticated user who requested this execution.
            model: Optional LLM model name selected by the user.

        Returns:
            ExecutionResult with the final test outcome and workspace path.

        Raises:
            Any unhandled exception from the graph propagates to the caller
            (the RQ worker), which marks the job as 'failed'.
        """
        initial_state: dict = {
            "requirement": requirement,
            "user_id": user_id,
            "model": model,
        }

        # graph.invoke() runs the full graph synchronously and returns the
        # final merged GraphState dict once the graph reaches END.
        final_state: dict = self.graph.invoke(initial_state)

        return ExecutionResult(
            workspace=final_state["workspace_path"],
            passed=final_state.get("passed", False),
            tries_used=final_state.get("tries_used", 0),
            stdout=final_state.get("stdout", ""),
            stderr=final_state.get("stderr", ""),
            exit_code=final_state.get("exit_code", -1),
            execution_id=final_state.get("execution_id"),
        )
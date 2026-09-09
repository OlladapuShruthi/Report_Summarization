from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Optional

from app.graph.graph_builder import GraphBuilder

StateCallback = Optional[Callable[[Dict[str, Any]], Awaitable[None]]]


class GraphRuntime:
    def __init__(self):
        self.builder = GraphBuilder()
        self.graph = self.builder.build()

    async def execute(
        self,
        analysis_id: str,
        parsed_json: Dict[str, Any],
        state_callback: StateCallback = None,
        patient_metadata: Optional[Dict[str, Any]] = None,
        comparison_context: Optional[Dict[str, Any]] = None,
        patient_id: Optional[str] = None,
        human_confirmations: Optional[list[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        state = self.builder.initialize_state(analysis_id, parsed_json, patient_id or "")
        if patient_metadata:
            state["parsed_json"] = {**parsed_json, "patient_metadata": patient_metadata}
        if comparison_context:
            state["comparison_context"] = comparison_context
        if human_confirmations:
            state["human_confirmations"] = human_confirmations

        state["status"] = "analyzing"

        final_state: Dict[str, Any] = state
        async for graph_state in self.graph.astream(state, stream_mode="values"):
            final_state = dict(graph_state)
            await self._persist(state_callback, final_state)

        final_state["status"] = "completed" if (final_state.get("validation") or {}).get("passed") else "failed"
        await self._persist(state_callback, final_state)
        return final_state

    async def _persist(self, callback: StateCallback, state: Dict[str, Any]) -> None:
        if callback is not None:
            await callback(state)

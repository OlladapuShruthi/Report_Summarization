from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Optional

from app.analysis.agents.anomaly_agent import AnomalyAgent
from app.analysis.agents.consult_agent import ConsultAgent
from app.analysis.agents.risk_agent import RiskAgent
from app.analysis.agents.summary_agent import SummaryAgent
from app.analysis.agents.validation_agent import ValidationAgent
from app.graph.graph_builder import GraphBuilder
from app.graph.routing import route_after_anomaly, route_after_risk
from app.graph.supervisor import Supervisor

StateCallback = Optional[Callable[[Dict[str, Any]], Awaitable[None]]]


class GraphRuntime:
    def __init__(self):
        self.builder = GraphBuilder()
        self.supervisor = Supervisor()
        self.anomaly_agent = AnomalyAgent()
        self.risk_agent = RiskAgent()
        self.consult_agent = ConsultAgent()
        self.summary_agent = SummaryAgent()
        self.validation_agent = ValidationAgent()

    async def execute(
        self,
        analysis_id: str,
        parsed_json: Dict[str, Any],
        state_callback: StateCallback = None,
        patient_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        state = self.builder.initialize_state(analysis_id, parsed_json)
        if patient_metadata:
            state["parsed_json"] = {**parsed_json, "patient_metadata": patient_metadata}

        state["status"] = "analyzing"
        await self._persist(state_callback, state)

        state = self.supervisor.decide(state)
        await self._persist(state_callback, state)

        state = await self.anomaly_agent.process(state)
        await self._persist(state_callback, state)

        if route_after_anomaly(state) == "risk_agent":
            state = await self.risk_agent.process(state)
            await self._persist(state_callback, state)

            if route_after_risk(state) == "consult_agent":
                state = await self.consult_agent.process(state)
                await self._persist(state_callback, state)
        else:
            state.setdefault(
                "risk_assessment",
                {"risk_level": "LOW", "reasoning": ["No abnormal findings detected."]},
            )
            state.setdefault(
                "consultation",
                {
                    "consultation_required": False,
                    "recommended_specialist": "None",
                    "urgency": "Routine",
                    "reasoning": ["No consultation needed."],
                },
            )

        state = await self.summary_agent.process(state)
        await self._persist(state_callback, state)

        state = await self.validation_agent.process(state)
        await self._persist(state_callback, state)

        while not (state.get("validation") or {}).get("passed") and int(state.get("retry_count", 0)) <= 2:
            state = await self.summary_agent.process(state)
            await self._persist(state_callback, state)
            state = await self.validation_agent.process(state)
            await self._persist(state_callback, state)

        state["status"] = "completed" if (state.get("validation") or {}).get("passed") else "failed"
        await self._persist(state_callback, state)
        return state

    async def _persist(self, callback: StateCallback, state: Dict[str, Any]) -> None:
        if callback is not None:
            await callback(state)

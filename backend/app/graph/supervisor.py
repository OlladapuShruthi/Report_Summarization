from app.graph.graph_state import GraphState
from app.graph.routing import log_node_execution


class Supervisor:
    def decide(self, state: GraphState) -> GraphState:
        updated_state = log_node_execution(state, "supervisor")
        updated_state["status"] = "supervisor_routed"
        return updated_state

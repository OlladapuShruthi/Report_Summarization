from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """
    Abstract Base Agent Interface for LangGraph multi-agent pipeline.
    All specialized agents (Anomaly, Risk, Consult, Summary, Validation) inherit from this interface.
    """
    def __init__(self, agent_name: str):
        self.agent_name = agent_name

    @abstractmethod
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent reasoning logic on shared graph state.
        """
        pass

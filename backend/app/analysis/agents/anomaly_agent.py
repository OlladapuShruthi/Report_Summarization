from typing import Dict, Any
from app.analysis.agents.base_agent import BaseAgent
from app.core.logger import logger

class AnomalyAgent(BaseAgent):
    def __init__(self):
        super().__init__("AnomalyAgent")

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"[{self.agent_name}] Placeholder process called.")
        raise NotImplementedError("AnomalyAgent reasoning will be implemented in Phase 4.")

from typing import Dict, Any, Optional
from ..models.api_models import AgentType
import asyncio

class BaseAgent:
    async def handle_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

class AgentManager:
    def __init__(self):
        self.agents: Dict[AgentType, BaseAgent] = {}
        self.agent_health: Dict[AgentType, bool] = {}

    async def register_agent(self, agent_type: AgentType, agent: BaseAgent):
        self.agents[agent_type] = agent
        self.agent_health[agent_type] = True  # Assume healthy

    async def get_agent(self, agent_type: AgentType) -> Optional[BaseAgent]:
        return self.agents.get(agent_type, None)

    async def health_check(self) -> Dict[AgentType, bool]:
        # Optionally do async health checks here
        return self.agent_health

    async def load_balance(self, agent_type: AgentType) -> Optional[BaseAgent]:
        # For demo: just return agent, extend for advanced LB
        return await self.get_agent(agent_type)

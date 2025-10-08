from typing import Type, Dict, Any, Optional
from ..models.api_models import AgentTask, AgentType, AgentResult
from .agent_manager import AgentManager

class TaskRouter:
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager

    async def route_task(self, task: AgentTask) -> AgentResult:
        # Analyze input_data for routing intelligence (extend as needed)
        agent = await self.agent_manager.get_agent(task.agent_type)
        if not agent:
            return AgentResult(agent_type=task.agent_type, output_data={}, success=False, error="Agent not available")
        # Delegate to agent: in production, this is an async API call/class method
        try:
            result = await agent.handle_task(task.input_data)
            return AgentResult(agent_type=task.agent_type, output_data=result, success=True)
        except Exception as e:
            return AgentResult(agent_type=task.agent_type, output_data={}, success=False, error=str(e))

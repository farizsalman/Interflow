from fastapi import APIRouter, Depends, HTTPException
from ...models.api_models import OrchestrationRequest, OrchestrationResponse
from ...orchestration.agent_manager import AgentManager, BaseAgent
from ...orchestration.task_router import TaskRouter
from ...orchestration.workflow_engine import WorkflowEngine
from ...orchestration.state_manager import StateManager

router = APIRouter()

# Instantiate managers and router for demo. Use DI for production!
agent_manager = AgentManager()
state_manager = StateManager()
task_router = TaskRouter(agent_manager)
workflow_engine = WorkflowEngine(task_router, state_manager)

@router.post("/", response_model=OrchestrationResponse)
async def run_orchestration(req: OrchestrationRequest):
    try:
        # Demo: register dummy agents for research, analysis, decision
        class DummyAgent(BaseAgent):
            async def handle_task(self, input_data):
                return {"dummy": "response", "input": input_data}
        for agent_type in ["research", "analysis", "decision"]:
            await agent_manager.register_agent(agent_type, DummyAgent())

        return await workflow_engine.run_workflow(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {e}")

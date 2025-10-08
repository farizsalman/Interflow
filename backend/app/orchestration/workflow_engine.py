from ..models.api_models import OrchestrationRequest, OrchestrationResponse, AgentResult
from .task_router import TaskRouter
from .state_manager import StateManager

class WorkflowEngine:
    def __init__(self, task_router: TaskRouter, state_manager: StateManager):
        self.task_router = task_router
        self.state_manager = state_manager

    async def run_workflow(self, request: OrchestrationRequest) -> OrchestrationResponse:
        results = []
        self.state_manager.start_workflow(request.workflow_id)
        for idx, task in enumerate(request.tasks):
            self.state_manager.update_task_status(request.workflow_id, idx, "in_progress")
            result = await self.task_router.route_task(task)
            results.append(result)
            self.state_manager.update_task_status(request.workflow_id, idx, "finished" if result.success else "error")
        overall_status = "success" if all(r.success for r in results) else "error"
        return OrchestrationResponse(
            workflow_id=request.workflow_id,
            results=results,
            status=overall_status,
            error=None if overall_status == "success" else "One or more tasks failed"
        )

from ..models.api_models import OrchestrationRequest, OrchestrationResponse, AgentResult
from .task_router import TaskRouter
from .state_manager import StateManager
from ..agents.decision_agent import DecisionAgent

class WorkflowEngine:
    def __init__(self, task_router: TaskRouter, state_manager: StateManager):
        self.task_router = task_router
        self.state_manager = state_manager
        self.decision_agent = DecisionAgent()

    async def run_workflow(self, request: OrchestrationRequest) -> OrchestrationResponse:
        workflow_id = request.workflow_id or "wf-{:.0f}".format(StateManager.__hash__(self))
        self.state_manager.start_workflow(workflow_id)
        results = []

        # 1. ResearchAgent
        self.state_manager.update_task_status(workflow_id, 0, "in_progress")
        research_result = await self.task_router.route_task(request.tasks[0])
        results.append(research_result)
        self.state_manager.update_task_status(
            workflow_id, 0, "finished" if research_result.success else "error"
        )

        # 2. AnalysisAgent
        self.state_manager.update_task_status(workflow_id, 1, "in_progress")
        analysis_input = {
            "data": research_result.output_data.get("results") if research_result.success else []
        }
        analysis_task = request.tasks[1]
        analysis_task.input_data = analysis_input
        analysis_result = await self.task_router.route_task(analysis_task)
        results.append(analysis_result)
        self.state_manager.update_task_status(
            workflow_id, 1, "finished" if analysis_result.success else "error"
        )

        # 3. DecisionAgent
        self.state_manager.update_task_status(workflow_id, 2, "in_progress")
        decision_input = {
            "research": research_result.output_data,
            "analysis": analysis_result.output_data,
        }
        decision_result_data = await self.decision_agent.execute(decision_input)
        decision_result = AgentResult(
            agent_type="decision",
            output_data=decision_result_data,
            success=decision_result_data.get("status") != "error",
            error=decision_result_data.get("error"),
        )
        results.append(decision_result)
        decision_status = decision_result.output_data.get("status")
        new_state = (
            "finished" if decision_result.success and decision_status == "auto_approved"
            else "awaiting_human" if decision_status == "human_verification_required"
            else "error"
        )
        self.state_manager.update_task_status(workflow_id, 2, new_state)

        # Determine overall status
        if decision_status == "auto_approved" and all(r.success for r in results):
            overall_status = "success"
            error = None
        elif decision_status == "human_verification_required":
            overall_status = "pending_human"
            error = "Awaiting human-in-the-loop review."
        else:
            overall_status = "error"
            error = "Workflow failed."

        return OrchestrationResponse(
            workflow_id=workflow_id,
            results=results,
            status=overall_status,
            error=error,
        )

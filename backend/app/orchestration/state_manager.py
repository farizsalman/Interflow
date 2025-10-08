from typing import Dict, Any, Optional

class StateManager:
    def __init__(self):
        # workflow_id -> {task_index: status}
        self.workflow_states: Dict[str, Dict[int, str]] = {}

    def start_workflow(self, workflow_id: Optional[str]):
        if workflow_id:
            self.workflow_states[workflow_id] = {}

    def update_task_status(self, workflow_id: Optional[str], task_index: int, status: str):
        if workflow_id:
            self.workflow_states.setdefault(workflow_id, {})[task_index] = status

    def get_task_status(self, workflow_id: Optional[str], task_index: int) -> Optional[str]:
        return self.workflow_states.get(workflow_id, {}).get(task_index, None)

    def get_workflow_status(self, workflow_id: Optional[str]) -> Dict[int, str]:
        return self.workflow_states.get(workflow_id, {})

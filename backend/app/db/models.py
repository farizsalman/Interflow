from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class AgentTask(Document):
    task_id: str = Indexed(unique=True)
    agent_type: str
    input_data: Dict[str, Any]
    status: str = Field(default="pending")
    created_at: Optional[float] = None

class AgentResult(Document):
    result_id: str = Indexed(unique=True)
    agent_type: str
    output_data: Dict[str, Any]
    success: bool
    error: Optional[str] = None
    created_at: Optional[float] = None

class AgentStatus(Document):
    workflow_id: str = Indexed()
    agent_type: str
    status: str
    updated_at: Optional[float] = None

class WorkflowExecution(Document):
    workflow_id: str = Indexed(unique=True)
    tasks: List[str]
    results: List[str]
    status: str
    error: Optional[str] = None
    started_at: Optional[float] = None
    finished_at: Optional[float] = None

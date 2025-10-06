from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Any
from enum import Enum

class AgentType(str, Enum):
    research = "research"
    analysis = "analysis"
    decision = "decision"

class AgentTask(BaseModel):
    agent_type: AgentType
    input_data: Dict[str, Any]
    priority: Optional[int] = Field(1, ge=0, le=10)

class AgentResult(BaseModel):
    agent_type: AgentType
    output_data: Dict[str, Any]
    success: bool
    error: Optional[str] = None

class OrchestrationRequest(BaseModel):
    workflow_id: Optional[str]
    tasks: List[AgentTask]

class OrchestrationResponse(BaseModel):
    workflow_id: Optional[str]
    results: List[AgentResult]
    status: str
    error: Optional[str] = None

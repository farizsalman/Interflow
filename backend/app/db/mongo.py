import motor.motor_asyncio
from beanie import init_beanie
from ..config import settings

# Dependency for FastAPI
async def get_motor_client():
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url)
    return client

async def init_db():
    from ..db.models import AgentTask, AgentResult, WorkflowExecution, AgentStatus
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url)
    await init_beanie(
        database=client[settings.mongodb_database],
        document_models=[AgentTask, AgentResult, WorkflowExecution, AgentStatus],
    )
    return client

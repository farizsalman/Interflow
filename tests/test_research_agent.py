import pytest
import asyncio
from backend.app.agents.research_agent import ResearchAgent

@pytest.mark.asyncio
async def test_research_agent_execution():
    agent = ResearchAgent(api_key="your-valid-api-key")
    result = await agent.execute({"query": "latest AI research trends"})
    assert "results" in result
    assert "citations" in result
    assert "confidence" in result
    assert isinstance(result["confidence"], float)

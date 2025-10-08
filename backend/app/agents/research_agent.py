import asyncio
import httpx
from typing import Dict, Any, List, Optional, Tuple
from ..models.api_models import AgentTask, AgentResult, AgentType
import time

PERPLEXITY_API_URL = "https://api.perplexity.ai/v1/search"  # Change if SDK is different
PERPLEXITY_API_KEY = "your-perplexity-api-key"  # Load from config/env in production

class ResearchAgent:
    agent_type = AgentType.research

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or PERPLEXITY_API_KEY
        self.client = httpx.AsyncClient(timeout=20)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        query = input_data.get("query")
        if not query:
            raise ValueError("Missing research query input.")

        # Basic retry logic for API call
        max_attempts = 3
        delay = 2
        for attempt in range(1, max_attempts + 1):
            try:
                response = await self.client.post(
                    PERPLEXITY_API_URL,
                    json={"q": query},
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                if response.status_code == 429:
                    await asyncio.sleep(delay * attempt)
                    continue
                response.raise_for_status()
                data = response.json()
                citations, sources = self.extract_citations(data)
                confidence = self.get_confidence(sources)
                return {
                    "results": data.get("results", []),
                    "citations": citations,
                    "sources": sources,
                    "confidence": confidence
                }
            except (httpx.HTTPError, Exception) as e:
                if attempt == max_attempts:
                    return self.handle_error(str(e))
                await asyncio.sleep(delay * attempt)
        return self.handle_error("Exceeded max retry attempts")

    def extract_citations(self, api_data: Dict[str, Any]) -> Tuple[List[str], List[Dict[str, Any]]]:
        citations = []
        sources = []
        results = api_data.get("results", [])
        for res in results:
            if "citation" in res:
                citations.append(res["citation"])
            if "source" in res:
                sources.append(res["source"])
        return citations, sources

    def get_confidence(self, sources: List[Dict[str, Any]]) -> float:
        # Confidence based on: Source quality, recency, relevance, citation count
        score = 0
        weights = {"quality": 0.4, "recency": 0.2, "relevance": 0.3, "citations": 0.1}
        now = time.time()
        for src in sources:
            q = 1 if src.get("quality", "high") == "high" else 0.5
            r = 1 if "date" in src and (now - self._parse_date(src["date"])) < 365 * 24 * 3600 else 0.5
            rel = src.get("relevance", 1.0)
            cit = src.get("citations", 1)
            score += (
                weights["quality"] * q +
                weights["recency"] * r +
                weights["relevance"] * rel +
                weights["citations"] * min(cit / 10, 1)
            )
        score = score / max(len(sources), 1)
        return round(score, 2)

    def handle_error(self, error: str) -> Dict[str, Any]:
        return {
            "results": [],
            "citations": [],
            "sources": [],
            "confidence": 0.0,
            "error": error
        }

    def _parse_date(self, date_str: str) -> float:
        # Implement date parsing, fallback for missing/invalid date
        try:
            import dateutil.parser
            return dateutil.parser.parse(date_str).timestamp()
        except Exception:
            return 0.0

    async def get_health(self) -> bool:
        # Optionally call a status endpoint, here just checks API key
        return bool(self.api_key)

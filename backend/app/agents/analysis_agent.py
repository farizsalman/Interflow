import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from ..models.api_models import AgentType
import asyncio

class AnalysisAgent:
    agent_type = AgentType.analysis

    def __init__(self):
        pass

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main async entrypoint: receives raw input_data, processes, analyzes, and returns insights.
        """
        try:
            df = self._preprocess(input_data)
            stats = self._basic_statistics(df)
            trends, patterns = self._trend_and_pattern_analysis(df)
            insights = self._generate_insights(stats, trends, patterns)
            confidence = self.get_confidence(df, stats, insights)
            return {
                "statistics": stats,
                "trends": trends,
                "patterns": patterns,
                "insights": insights,
                "confidence": confidence,
            }
        except Exception as e:
            return self.handle_error(str(e))

    def _preprocess(self, input_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Validates and preprocesses input data into a clean DataFrame.
        Accepts ResearchAgent output, CSV/JSON, or already structured records.
        """
        # Handle research output or direct data
        records = input_data.get("data") or input_data.get("results")
        if records is None:
            raise ValueError("No data provided for analysis.")
        if isinstance(records, str):
            # Try to interpret as CSV or JSON string
            try:
                df = pd.read_json(records)
            except Exception:
                df = pd.read_csv(pd.compat.StringIO(records))
        elif isinstance(records, list):
            df = pd.DataFrame(records)
        elif isinstance(records, pd.DataFrame):
            df = records
        else:
            raise ValueError("Unsupported data format for analysis.")

        # Data cleaning: drop duplicates, handle missing values
        df = df.drop_duplicates()
        df = df.apply(lambda col: col.fillna(col.mean()) if np.issubdtype(col.dtype, np.number) else col.fillna("N/A"))
        if df.empty:
            raise ValueError("Data is empty after preprocessing.")
        return df

    def _basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Computes statistics for numerical columns."""
        return {col: {"mean": df[col].mean(), "std": df[col].std(), "min": df[col].min(), "max": df[col].max()}
                for col in df.select_dtypes(include=[np.number]).columns}

    def _trend_and_pattern_analysis(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        """Stub: performs trend and pattern detection. Extend for ML or more advanced analytics."""
        trends = []
        patterns = []
        # Example: rising trend detection on all numeric columns
        for col in df.select_dtypes(include=[np.number]).columns:
            series = df[col].values
            if len(series) > 1 and np.polyfit(np.arange(len(series)), series, 1)[0] > 0:
                trends.append(f"{col} shows an increasing trend.")
            # Detect repeats/patterns
            if df[col].nunique() < len(df) * 0.2:
                patterns.append(f"{col} has many repeated values (potential pattern/cluster).")
        return trends, patterns

    def _generate_insights(self, stats: Dict[str, Any], trends: List[str], patterns: List[str]) -> List[str]:
        """Converts raw stats/trends into readable insights."""
        insights = []
        for col, s in stats.items():
            insights.append(
                f"{col}: mean={s['mean']:.2f}, std={s['std']:.2f}, min={s['min']}, max={s['max']}"
            )
        insights.extend(trends)
        insights.extend(patterns)
        return insights

    def get_confidence(self, df: pd.DataFrame, stats: Dict[str, Any], insights: List[str]) -> float:
        """Basic confidence scoring based on data completeness and insight volume."""
        n_rows, n_cols = df.shape
        completeness = df.notnull().sum().sum() / (n_rows * n_cols)
        insight_factor = min(len(insights) / n_cols, 1)
        score = 0.5 * completeness + 0.5 * insight_factor
        return round(score, 2)

    def handle_error(self, error: str) -> Dict[str, Any]:
        return {
            "statistics": {},
            "trends": [],
            "patterns": [],
            "insights": [f"Error: {error}"],
            "confidence": 0.0,
            "error": error
        }

import json
from typing import List
from server.anthropic_client import CallAnalyzer, STANDARD_QUESTIONS
from server.types import CallRecord


def get_analyzer() -> CallAnalyzer:
    """Get or create the CallAnalyzer instance."""
    return CallAnalyzer()


def load_calls(file_path: str = "calls.json") -> List[CallRecord]:
    with open(file_path, "r") as f:
        data = json.load(f)
    return [CallRecord.model_validate(record) for record in data]


def format_duration(seconds: int) -> str:
    minutes, sec = divmod(seconds, 60)
    return f"{minutes}:{sec:02d}"


def ask_question(call: CallRecord, question: str) -> str:
    """Ask a question about a specific call."""
    analyzer = get_analyzer()
    return analyzer.ask_question(call, question)


def get_call_insights(call: CallRecord) -> str:
    """Get key insights for a specific call."""
    analyzer = get_analyzer()
    return analyzer.get_key_insights(call)

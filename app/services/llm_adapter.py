from typing import Optional


class LlmAdapter:
    """Pluggable LLM adapter. Replace with your preferred provider SDK."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key

    def summarize(self, prompt: str) -> str:
        # Stubbed: return simple transform so the app runs without credentials
        return (prompt.strip()[:240] + "...") if len(prompt) > 240 else prompt


llm = LlmAdapter()


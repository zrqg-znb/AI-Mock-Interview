import json
import re
from typing import Any

import httpx

from app.settings import settings


class InterviewAIAdapter:
    def __init__(self):
        self.api_key = settings.AI_API_KEY
        self.base_url = settings.AI_BASE_URL
        self.model_name = settings.AI_MODEL_NAME
        self.timeout = settings.AI_REQUEST_TIMEOUT

    @property
    def enabled(self) -> bool:
        return bool(self.api_key and self.base_url and self.model_name)

    def _build_endpoint(self) -> str:
        endpoint = self.base_url.rstrip("/")
        if endpoint.endswith("/chat/completions"):
            return endpoint
        return f"{endpoint}/chat/completions"

    @staticmethod
    def _extract_json(content: str) -> dict[str, Any] | None:
        if not content:
            return None
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        match = re.search(r"\{.*\}", content, re.S)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    async def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        payload = {
            "model": self.model_name,
            "temperature": 0.5,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self._build_endpoint(), headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return self._extract_json(content)


interview_ai_adapter = InterviewAIAdapter()

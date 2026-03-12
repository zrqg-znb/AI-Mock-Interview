import json
import re
from time import perf_counter
from typing import Any

import httpx

from app.log import logger
from app.settings import settings
from app.services.ai_runtime import ai_runtime_service


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
        endpoint = self.base_url.rstrip('/')
        if endpoint.endswith('/chat/completions'):
            return endpoint
        return f'{endpoint}/chat/completions'

    @staticmethod
    def _extract_json(content: str) -> dict[str, Any] | None:
        if not content:
            return None
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        match = re.search(r'\{.*\}', content, re.S)
        if not match:
            return None
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.4,
        scenario: str = 'general',
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        if not self.enabled:
            return None

        payload = {
            'model': self.model_name,
            'temperature': temperature,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            'response_format': {'type': 'json_object'},
        }
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        started = perf_counter()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self._build_endpoint(), headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            duration_ms = int((perf_counter() - started) * 1000)
            error_message = exc.response.text[:300]
            logger.warning(
                'interview ai request failed with status {}: {}',
                exc.response.status_code,
                error_message,
            )
            ai_runtime_service.record_event(
                scenario=scenario,
                status='http_error',
                duration_ms=duration_ms,
                error_message=error_message,
                metadata=metadata,
            )
            return None
        except httpx.HTTPError as exc:
            duration_ms = int((perf_counter() - started) * 1000)
            logger.warning('interview ai request failed: {}', exc)
            ai_runtime_service.record_event(
                scenario=scenario,
                status='network_error',
                duration_ms=duration_ms,
                error_message=str(exc),
                metadata=metadata,
            )
            return None
        except Exception as exc:  # pragma: no cover - defensive fallback
            duration_ms = int((perf_counter() - started) * 1000)
            logger.warning('interview ai adapter raised unexpected error: {}', exc)
            ai_runtime_service.record_event(
                scenario=scenario,
                status='unexpected_error',
                duration_ms=duration_ms,
                error_message=str(exc),
                metadata=metadata,
            )
            return None

        duration_ms = int((perf_counter() - started) * 1000)
        content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
        result = self._extract_json(content)
        if result is None:
            logger.warning('interview ai returned non-json content: {}', content[:300])
            ai_runtime_service.record_event(
                scenario=scenario,
                status='invalid_json',
                duration_ms=duration_ms,
                error_message=content[:300],
                metadata=metadata,
            )
            return None

        ai_runtime_service.record_event(
            scenario=scenario,
            status='success',
            duration_ms=duration_ms,
            metadata={
                **(metadata or {}),
                'response_keys': sorted(result.keys())[:12],
            },
        )
        return result


interview_ai_adapter = InterviewAIAdapter()

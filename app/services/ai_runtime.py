import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.settings import settings


GENERATION_SCENARIOS = {"question_plan", "next_question", "report_generation"}


class AIRuntimeService:
    def __init__(self):
        self.log_path = Path(settings.LOGS_ROOT) / "ai_runtime_events.jsonl"

    def _ensure_log_dir(self) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _sanitize(self, value: Any) -> Any:
        if value is None or isinstance(value, (bool, int, float, str)):
            return value
        if isinstance(value, dict):
            return {str(key): self._sanitize(item) for key, item in list(value.items())[:12]}
        if isinstance(value, list):
            return [self._sanitize(item) for item in value[:12]]
        return str(value)

    @staticmethod
    def _mask_secret(secret: str) -> str:
        if not secret:
            return ""
        if len(secret) <= 8:
            return "*" * len(secret)
        return f"{secret[:4]}{'*' * max(len(secret) - 8, 4)}{secret[-4:]}"

    def _provider_name(self) -> str:
        combined = f"{settings.AI_BASE_URL or ''} {settings.AI_MODEL_NAME or ''}".lower()
        if any(keyword in combined for keyword in ("spark", "xfyun", "xinghuo", "讯飞")):
            return "讯飞星火"
        base_url = (settings.AI_BASE_URL or "").lower()
        if "deepseek" in base_url:
            return "DeepSeek"
        if "openai" in base_url:
            return "OpenAI"
        return "Custom"

    @staticmethod
    def _is_configured(*values: str) -> bool:
        return all(bool(str(value or "").strip()) for value in values)

    def _build_service_cards(self, logs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        generation_logs = [item for item in logs if item.get("scenario") in GENERATION_SCENARIOS]
        last_generation_success = next((item for item in generation_logs if item.get("status") == "success"), None)
        last_generation_error = next((item for item in generation_logs if item.get("status") != "success"), None)

        llm_enabled = self._is_configured(settings.AI_API_KEY, settings.AI_BASE_URL, settings.AI_MODEL_NAME)
        asr_enabled = self._is_configured(settings.XFYUN_APP_ID, settings.XFYUN_API_KEY, settings.XFYUN_API_SECRET)
        tts_enabled = self._is_configured(
            settings.XFYUN_TTS_APP_ID or settings.XFYUN_APP_ID,
            settings.XFYUN_TTS_API_KEY or settings.XFYUN_API_KEY,
            settings.XFYUN_TTS_API_SECRET or settings.XFYUN_API_SECRET,
        )

        return [
            {
                "key": "interview_llm",
                "name": "面试生成模型",
                "provider": self._provider_name(),
                "model_name": settings.AI_MODEL_NAME or "-",
                "enabled": llm_enabled,
                "status_text": "已启用" if llm_enabled else "未配置",
                "detail": settings.AI_BASE_URL or "-",
                "last_success_at": last_generation_success.get("timestamp") if last_generation_success else None,
                "last_error_at": last_generation_error.get("timestamp") if last_generation_error else None,
            },
            {
                "key": "xfyun_asr",
                "name": "讯飞 ASR",
                "provider": "科大讯飞",
                "model_name": settings.XFYUN_ASR_DOMAIN or "iat",
                "enabled": asr_enabled,
                "status_text": "已启用" if asr_enabled else "未配置",
                "detail": f"{settings.XFYUN_ASR_LANGUAGE}/{settings.XFYUN_ASR_ACCENT} @ {settings.XFYUN_ASR_HOST}",
                "last_success_at": None,
                "last_error_at": None,
            },
            {
                "key": "xfyun_tts",
                "name": "讯飞 TTS",
                "provider": "科大讯飞",
                "model_name": settings.XFYUN_TTS_VCN or "-",
                "enabled": tts_enabled,
                "status_text": "已启用" if tts_enabled else "未配置",
                "detail": f"{settings.XFYUN_TTS_VCN or '-'} @ {settings.XFYUN_TTS_URL_HOST}",
                "last_success_at": None,
                "last_error_at": None,
            },
        ]

    def _env_files(self) -> list[str]:
        env_files: list[str] = []
        for name in (".env", ".env.local"):
            if (Path(settings.BASE_DIR) / name).exists():
                env_files.append(name)
        return env_files

    def record_event(
        self,
        *,
        scenario: str,
        status: str,
        duration_ms: int = 0,
        error_message: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        event = {
            "timestamp": datetime.now().strftime(settings.DATETIME_FORMAT),
            "scenario": scenario,
            "status": status,
            "provider": self._provider_name(),
            "model_name": settings.AI_MODEL_NAME,
            "duration_ms": duration_ms,
            "error_message": error_message[:280] if error_message else "",
            "metadata": self._sanitize(metadata or {}),
        }
        self._ensure_log_dir()
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event

    def list_recent_logs(self, limit: int = 20) -> list[dict[str, Any]]:
        if not self.log_path.exists():
            return []
        with self.log_path.open("r", encoding="utf-8") as handle:
            lines = handle.readlines()
        logs: list[dict[str, Any]] = []
        for line in reversed(lines[-limit:]):
            line = line.strip()
            if not line:
                continue
            try:
                logs.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return logs

    def get_status(self, limit: int = 20) -> dict[str, Any]:
        logs = self.list_recent_logs(limit=limit)
        last_success = next((item for item in logs if item.get("status") == "success"), None)
        last_error = next((item for item in logs if item.get("status") != "success"), None)
        latest_generation_log = next((item for item in logs if item.get("scenario") in GENERATION_SCENARIOS), None)
        latest_runtime_check = next((item for item in logs if item.get("scenario") == "runtime_check"), None)
        service_cards = self._build_service_cards(logs)
        return {
            "enabled": bool(settings.AI_API_KEY and settings.AI_BASE_URL and settings.AI_MODEL_NAME),
            "provider": self._provider_name(),
            "model_name": settings.AI_MODEL_NAME,
            "base_url": settings.AI_BASE_URL,
            "timeout_seconds": settings.AI_REQUEST_TIMEOUT,
            "api_key_masked": self._mask_secret(settings.AI_API_KEY),
            "env_files": self._env_files(),
            "log_file": str(self.log_path),
            "last_event_at": logs[0].get("timestamp") if logs else None,
            "last_success_at": last_success.get("timestamp") if last_success else None,
            "last_error_at": last_error.get("timestamp") if last_error else None,
            "latest_generation_log": latest_generation_log,
            "latest_runtime_check": latest_runtime_check,
            "service_cards": service_cards,
            "recent_logs": logs,
        }

    async def run_connectivity_check(self) -> dict[str, Any]:
        if not settings.AI_API_KEY:
            self.record_event(
                scenario="runtime_check",
                status="disabled",
                metadata={"reason": "missing_api_key"},
            )
            return {
                "ok": False,
                "message": "未配置 AI_API_KEY，无法执行连通测试。",
                "result": None,
            }

        from app.services.interview_ai import interview_ai_adapter

        result = await interview_ai_adapter.generate_json(
            "你是连通性测试助手，只返回 JSON。",
            '请返回 {"ok": true, "message": "runtime-check"}。',
            temperature=0,
            scenario="runtime_check",
            metadata={"origin": "admin-panel"},
        )
        return {
            "ok": bool(result and result.get("ok") is True),
            "message": "连通测试完成。" if result else "连通测试未拿到有效 JSON 返回。",
            "result": result,
        }


ai_runtime_service = AIRuntimeService()

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime
from time import mktime
from typing import AsyncIterator
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

import websockets
from websockets.exceptions import ConnectionClosedOK

from app.log import logger


class ASRServiceError(Exception):
    """Base exception for XFYun ASR failures."""


class ASRConfigurationError(ASRServiceError):
    """Raised when XFYun credentials are missing."""


@dataclass(slots=True)
class ASRStreamEvent:
    text: str
    delta: str
    is_final: bool = False


class iFlytekASRService:
    def __init__(
        self,
        appid: str,
        api_key: str,
        api_secret: str,
        *,
        host: str = "ws-api.xfyun.cn",
        path: str = "/v2/iat",
        domain: str = "iat",
        language: str = "zh_cn",
        accent: str = "mandarin",
        vad_eos: int = 10000,
    ):
        self.appid = appid
        self.api_key = api_key
        self.api_secret = api_secret
        self.host = host
        self.path = path
        self.business_args = {
            "domain": domain,
            "language": language,
            "accent": accent,
            "vinfo": 1,
            "vad_eos": vad_eos,
        }

    def _ensure_configured(self) -> None:
        if self.appid and self.api_key and self.api_secret:
            return
        raise ASRConfigurationError("未配置完整的讯飞 ASR 凭据，请在环境变量中设置 XFYUN_APP_ID / XFYUN_API_KEY / XFYUN_API_SECRET。")

    def _create_url(self) -> str:
        self._ensure_configured()
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        signature_origin = f"host: {self.host}\n"
        signature_origin += f"date: {date}\n"
        signature_origin += f"GET {self.path} HTTP/1.1"

        signature_sha = hmac.new(
            self.api_secret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        signature_sha = base64.b64encode(signature_sha).decode("utf-8")

        authorization_origin = (
            'api_key="%s", algorithm="%s", headers="%s", signature="%s"'
            % (self.api_key, "hmac-sha256", "host date request-line", signature_sha)
        )
        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode("utf-8")
        params = {
            "authorization": authorization,
            "date": date,
            "host": self.host,
        }
        return f"wss://{self.host}{self.path}?{urlencode(params)}"

    async def transcribe_stream(self, audio_generator: AsyncIterator[bytes]) -> AsyncIterator[ASRStreamEvent]:
        url = self._create_url()
        queue: asyncio.Queue[ASRStreamEvent | Exception | object] = asyncio.Queue()
        stop_sentinel = object()
        segments: dict[int, str] = {}

        async with websockets.connect(
            url,
            ping_interval=20,
            ping_timeout=20,
            close_timeout=5,
            max_size=None,
        ) as ws:
            async def send_audio() -> None:
                status = 0
                try:
                    async for audio_chunk in audio_generator:
                        if not audio_chunk:
                            continue
                        frame = self._build_audio_frame(audio_chunk, status)
                        await ws.send(json.dumps(frame))
                        status = 1
                    await ws.send(json.dumps(self._build_last_frame()))
                except ConnectionClosedOK as exc:
                    if self._is_server_read_timeout(exc):
                        logger.info("XFYun ASR upstream closed after read timeout; ending current stream gracefully")
                        return
                    await queue.put(exc)
                    raise
                except Exception as exc:  # pragma: no cover - defensive branch for socket lifecycle
                    await queue.put(exc)
                    raise

            async def receive_results() -> None:
                try:
                    async for message in ws:
                        payload = json.loads(message)
                        code = payload.get("code", 0)
                        if code != 0:
                            msg = payload.get("message") or payload.get("desc") or "讯飞语音识别返回异常。"
                            raise ASRServiceError(f"讯飞语音识别失败：{msg} (code={code})")

                        event = self._parse_response(payload, segments)
                        if event is not None:
                            await queue.put(event)

                        if payload.get("data", {}).get("status") == 2:
                            break
                except ConnectionClosedOK as exc:
                    if self._is_server_read_timeout(exc):
                        final_text = "".join(segments[idx] for idx in sorted(segments.keys()))
                        if final_text:
                            await queue.put(ASRStreamEvent(text=final_text, delta="", is_final=True))
                    else:
                        await queue.put(exc)
                except Exception as exc:
                    await queue.put(exc)
                finally:
                    await queue.put(stop_sentinel)

            sender_task = asyncio.create_task(send_audio())
            receiver_task = asyncio.create_task(receive_results())

            try:
                while True:
                    item = await queue.get()
                    if item is stop_sentinel:
                        break
                    if isinstance(item, Exception):
                        raise item
                    yield item
            finally:
                for task in (sender_task, receiver_task):
                    if task.done():
                        continue
                    task.cancel()
                results = await asyncio.gather(sender_task, receiver_task, return_exceptions=True)
                for result in results:
                    if isinstance(result, Exception) and not isinstance(result, asyncio.CancelledError):
                        logger.debug(f"ASR stream task finished with exception: {result}")

    def _build_audio_frame(self, audio_chunk: bytes, status: int) -> dict:
        frame = {
            "data": {
                "status": status,
                "format": "audio/L16;rate=16000",
                "audio": base64.b64encode(audio_chunk).decode("utf-8"),
                "encoding": "raw",
            }
        }
        if status == 0:
            frame["common"] = {"app_id": self.appid}
            frame["business"] = self.business_args
        return frame

    @staticmethod
    def _build_last_frame() -> dict:
        return {
            "data": {
                "status": 2,
                "format": "audio/L16;rate=16000",
                "audio": "",
                "encoding": "raw",
            }
        }

    def _parse_response(self, payload: dict, segments: dict[int, str]) -> ASRStreamEvent | None:
        data = payload.get("data") or {}
        result = data.get("result") or {}
        ws_items = result.get("ws") or []
        delta = "".join(
            candidate.get("w", "")
            for item in ws_items
            for candidate in item.get("cw", [])
        )
        if not delta and data.get("status") != 2:
            return None

        sn = self._coerce_sn(result.get("sn"), default=(max(segments.keys(), default=0) + 1))
        pgs = result.get("pgs")
        if pgs == "rpl":
            rg = result.get("rg") or []
            if len(rg) == 2:
                start = self._coerce_sn(rg[0], default=sn)
                end = self._coerce_sn(rg[1], default=sn)
                for idx in range(start, end + 1):
                    segments.pop(idx, None)
        segments[sn] = delta
        text = "".join(segments[idx] for idx in sorted(segments.keys()))
        return ASRStreamEvent(text=text, delta=delta, is_final=data.get("status") == 2)

    @staticmethod
    def _coerce_sn(value: object, *, default: int) -> int:
        try:
            return int(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _is_server_read_timeout(exc: ConnectionClosedOK) -> bool:
        reason = getattr(exc, "reason", "") or str(exc)
        return "server read msg timeout" in reason.lower()

from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import wave
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time

import websockets


class TTSServiceError(Exception):
    """Base exception for XFYun TTS failures."""


class TTSConfigurationError(TTSServiceError):
    """Raised when XFYun TTS credentials are missing."""


class iFlytekTTSService:
    def __init__(
        self,
        appid: str,
        api_key: str,
        api_secret: str,
        *,
        url_host: str = "tts-api.xfyun.cn",
        auth_host: str = "ws-api.xfyun.cn",
        path: str = "/v2/tts",
        vcn: str = "x4_yezi",
        tte: str = "utf8",
        aue: str = "raw",
        auf: str = "audio/L16;rate=16000",
    ):
        self.appid = appid
        self.api_key = api_key
        self.api_secret = api_secret
        self.url_host = url_host
        self.auth_host = auth_host
        self.path = path
        self.business_args = {
            "aue": aue,
            "auf": auf,
            "vcn": vcn,
            "tte": tte,
        }

    def _ensure_configured(self) -> None:
        if self.appid and self.api_key and self.api_secret:
            return
        raise TTSConfigurationError(
            "未配置完整的讯飞 TTS 凭据，请设置 XFYUN_TTS_APP_ID / XFYUN_TTS_API_KEY / XFYUN_TTS_API_SECRET。"
        )

    def _create_url(self) -> str:
        self._ensure_configured()
        date = format_date_time(mktime(datetime.now().timetuple()))
        signature_origin = f"host: {self.auth_host}\n"
        signature_origin += f"date: {date}\n"
        signature_origin += f"GET {self.path} HTTP/1.1"
        signature_sha = hmac.new(
            self.api_secret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
        signature = base64.b64encode(signature_sha).decode("utf-8")
        authorization_origin = (
            'api_key="%s", algorithm="%s", headers="%s", signature="%s"'
            % (self.api_key, "hmac-sha256", "host date request-line", signature)
        )
        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode("utf-8")
        params = {
            "authorization": authorization,
            "date": date,
            "host": self.auth_host,
        }
        return f"wss://{self.url_host}{self.path}?{urlencode(params)}"

    async def synthesize(self, text: str) -> bytes:
        clean_text = (text or "").strip()
        if not clean_text:
            raise TTSServiceError("TTS 文本不能为空。")

        payload = {
            "common": {"app_id": self.appid},
            "business": self.business_args,
            "data": {
                "status": 2,
                "text": base64.b64encode(clean_text.encode("utf-8")).decode("utf-8"),
            },
        }
        audio_chunks: list[bytes] = []

        async with websockets.connect(
            self._create_url(),
            ping_interval=20,
            ping_timeout=20,
            close_timeout=5,
            max_size=None,
        ) as ws:
            await ws.send(json.dumps(payload))
            while True:
                message = json.loads(await ws.recv())
                code = message.get("code", 0)
                if code != 0:
                    msg = message.get("message") or message.get("desc") or "讯飞语音合成返回异常。"
                    raise TTSServiceError(f"讯飞语音合成失败：{msg} (code={code})")
                data = message.get("data") or {}
                audio_base64 = data.get("audio")
                if audio_base64:
                    audio_chunks.append(base64.b64decode(audio_base64))
                if data.get("status") == 2:
                    break

        if not audio_chunks:
            raise TTSServiceError("讯飞语音合成未返回音频数据。")
        return b"".join(audio_chunks)

    async def synthesize_wav(self, text: str) -> bytes:
        pcm = await self.synthesize(text)
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(pcm)
        return buffer.getvalue()

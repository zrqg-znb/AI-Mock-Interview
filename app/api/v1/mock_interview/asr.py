import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from app.log import logger
from app.services.asr_service import ASRConfigurationError, ASRServiceError, iFlytekASRService
from app.settings import settings

router = APIRouter()


async def send_safe_json(websocket: WebSocket, payload: dict) -> None:
    if websocket.client_state != WebSocketState.CONNECTED:
        return
    try:
        await websocket.send_json(payload)
    except RuntimeError:
        logger.debug("ASR websocket already closed before payload could be sent")


def build_asr_service() -> iFlytekASRService:
    return iFlytekASRService(
        settings.XFYUN_APP_ID,
        settings.XFYUN_API_KEY,
        settings.XFYUN_API_SECRET,
        host=settings.XFYUN_ASR_HOST,
        path=settings.XFYUN_ASR_PATH,
        domain=settings.XFYUN_ASR_DOMAIN,
        language=settings.XFYUN_ASR_LANGUAGE,
        accent=settings.XFYUN_ASR_ACCENT,
        vad_eos=settings.XFYUN_ASR_VAD_EOS,
    )


def mark_audio_stream_finished(audio_queue: asyncio.Queue[bytes | None]) -> None:
    try:
        audio_queue.put_nowait(None)
    except asyncio.QueueFull:
        try:
            audio_queue.get_nowait()
        except asyncio.QueueEmpty:
            pass
        audio_queue.put_nowait(None)


@router.websocket("/ws/asr")
async def websocket_asr_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("ASR WebSocket connection accepted")

    audio_queue: asyncio.Queue[bytes | None] = asyncio.Queue(maxsize=32)
    stream_task: asyncio.Task | None = None
    client_requested_stop = False
    client_disconnected = False
    received_audio = False

    async def audio_generator():
        while True:
            chunk = await audio_queue.get()
            if chunk is None:
                break
            yield chunk

    async def stream_to_xfyun() -> None:
        service = build_asr_service()
        last_text = ""
        try:
            async for event in service.transcribe_stream(audio_generator()):
                if event.text == last_text and not event.is_final:
                    continue
                last_text = event.text
                await send_safe_json(
                    websocket,
                    {
                        "type": "asr_result",
                        "text": event.text,
                        "delta": event.delta,
                        "is_final": event.is_final,
                    },
                )
            await send_safe_json(websocket, {"type": "asr_completed", "text": last_text})
        except ASRConfigurationError as exc:
            logger.warning(f"ASR configuration error: {exc}")
            await send_safe_json(websocket, {"type": "asr_error", "message": str(exc)})
        except ASRServiceError as exc:
            logger.warning(f"ASR service error: {exc}")
            await send_safe_json(websocket, {"type": "asr_error", "message": str(exc)})
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # pragma: no cover - defensive branch for socket lifecycle
            logger.exception(f"ASR WebSocket error: {exc}")
            await send_safe_json(websocket, {"type": "asr_error", "message": "语音识别服务暂时不可用，请稍后重试。"})

    try:
        while True:
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                client_disconnected = True
                break

            bytes_data = message.get("bytes")
            if bytes_data is not None:
                if stream_task is None:
                    stream_task = asyncio.create_task(stream_to_xfyun())
                received_audio = True
                await audio_queue.put(bytes_data)
                continue

            text_data = message.get("text")
            if not text_data:
                continue

            try:
                payload = json.loads(text_data)
            except json.JSONDecodeError:
                payload = {"type": text_data}

            if payload.get("type") == "end_stream":
                client_requested_stop = True
                break
    except WebSocketDisconnect:
        client_disconnected = True
        logger.info("ASR WebSocket disconnected")
    finally:
        mark_audio_stream_finished(audio_queue)
        if stream_task is not None:
            if client_requested_stop and not client_disconnected:
                await stream_task
            else:
                stream_task.cancel()
                await asyncio.gather(stream_task, return_exceptions=True)
        elif client_requested_stop and not received_audio:
            await send_safe_json(websocket, {"type": "asr_completed", "text": ""})

        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()

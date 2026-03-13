from fastapi import APIRouter, HTTPException, Response

from app.schemas.interviews import MockInterviewTTSIn
from app.services.tts_service import TTSConfigurationError, TTSServiceError, iFlytekTTSService
from app.settings import settings

from app.core.dependency import DependAuth

router = APIRouter(dependencies=[DependAuth])


def build_tts_service() -> iFlytekTTSService:
    return iFlytekTTSService(
        settings.XFYUN_TTS_APP_ID or settings.XFYUN_APP_ID,
        settings.XFYUN_TTS_API_KEY or settings.XFYUN_API_KEY,
        settings.XFYUN_TTS_API_SECRET or settings.XFYUN_API_SECRET,
        url_host=settings.XFYUN_TTS_URL_HOST,
        auth_host=settings.XFYUN_TTS_AUTH_HOST,
        path=settings.XFYUN_TTS_PATH,
        vcn=settings.XFYUN_TTS_VCN,
        tte=settings.XFYUN_TTS_TTE,
        aue=settings.XFYUN_TTS_AUE,
        auf=settings.XFYUN_TTS_AUF,
    )


@router.post('/tts', summary='将文本合成为语音')
async def synthesize_tts(payload: MockInterviewTTSIn):
    try:
        wav_bytes = await build_tts_service().synthesize_wav(payload.text)
    except TTSConfigurationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except TTSServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return Response(
        content=wav_bytes,
        media_type='audio/wav',
        headers={
            'Cache-Control': 'no-store',
            'Content-Disposition': 'inline; filename="mock-interview-question.wav"',
        },
    )

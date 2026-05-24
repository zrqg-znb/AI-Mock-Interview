import asyncio
import base64
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import cv2
import numpy as np

from app.log import logger


_executor = ThreadPoolExecutor(max_workers=2)
_EMOTION_PRIORITY = {"steady": 0, "positive": 1, "tense": 2, "off_camera": 3}
_EMOTION_LABELS = {
    "positive": "自然积极",
    "steady": "自然平稳",
    "tense": "略显紧张",
    "off_camera": "未稳定入镜",
}
_DEEPFACE_TO_STABLE = {
    "happy": "positive",
    "surprise": "positive",
    "neutral": "steady",
    "sad": "tense",
    "fear": "tense",
    "angry": "tense",
    "disgust": "tense",
}


class ExpressionService:
    def __init__(self) -> None:
        self._deepface = None
        self._deepface_available = None
        self._face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def _ensure_deepface(self):
        if self._deepface_available is not None:
            return self._deepface
        try:
            from deepface import DeepFace

            self._deepface = DeepFace
            self._deepface_available = True
            return self._deepface
        except Exception as exc:  # pragma: no cover - depends on local ML runtime
            self._deepface_available = False
            logger.warning("deepface unavailable, fallback to heuristic expression analysis: {}", exc)
            return None

    def _decode_image(self, base64_image: str) -> np.ndarray | None:
        if "," in base64_image:
            base64_image = base64_image.split(",", 1)[1]
        image_bytes = base64.b64decode(base64_image)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    def _detect_faces(self, image_data: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        return self._face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=4,
            minSize=(48, 48),
        )

    def _estimate_quality_score(self, image_data: np.ndarray) -> int:
        gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
        brightness = float(np.mean(gray))
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        brightness_score = max(0.0, 100.0 - abs(brightness - 135.0) * 0.9)
        sharpness_score = min(100.0, sharpness / 2.2)
        return max(0, min(100, int(round(brightness_score * 0.55 + sharpness_score * 0.45))))

    def _build_heuristic_result(self, image_data: np.ndarray) -> dict[str, Any]:
        faces = self._detect_faces(image_data)
        quality_score = self._estimate_quality_score(image_data)
        face_detected = len(faces) > 0
        if face_detected:
            observation = "正面入镜，画面清晰" if quality_score >= 70 else "正面入镜，但画面清晰度一般"
            emotion = "steady"
        else:
            observation = "当前未检测到稳定人脸，可能偏离镜头或画面条件不足"
            emotion = "off_camera"
        return {
            "emotion": emotion,
            "source": "heuristic",
            "face_detected": face_detected,
            "quality_score": quality_score,
            "observation": observation,
            "label": _EMOTION_LABELS[emotion],
        }

    def _map_deepface_emotion(self, dominant_emotion: str | None) -> str:
        normalized = str(dominant_emotion or "").strip().lower()
        return _DEEPFACE_TO_STABLE.get(normalized, "steady")

    def _build_deepface_result(self, image_data: np.ndarray) -> dict[str, Any] | None:
        deepface = self._ensure_deepface()
        if not deepface:
            return None
        try:
            results = deepface.analyze(
                img_path=image_data,
                actions=["emotion"],
                enforce_detection=False,
                silent=True,
            )
            result = results[0] if isinstance(results, list) else results
            emotion = self._map_deepface_emotion(result.get("dominant_emotion"))
            heuristic = self._build_heuristic_result(image_data)
            observation_map = {
                "positive": "大部分时间表情自然积极，镜头参与度较好",
                "steady": "整体表情自然平稳，镜头状态较稳定",
                "tense": "表情略显紧张，建议练习时加强放松和正面表达",
                "off_camera": "当前未稳定入镜，系统转为基础镜头观察",
            }
            return {
                "emotion": emotion,
                "source": "deepface",
                "face_detected": heuristic["face_detected"],
                "quality_score": heuristic["quality_score"],
                "observation": observation_map[emotion],
                "label": _EMOTION_LABELS[emotion],
            }
        except Exception as exc:  # pragma: no cover - depends on local ML runtime
            logger.warning("deepface expression analysis failed, fallback to heuristic mode: {}", exc)
            return None

    def _analyze_image_sync(self, image_data: np.ndarray) -> dict[str, Any]:
        deepface_result = self._build_deepface_result(image_data)
        if deepface_result:
            return deepface_result
        return self._build_heuristic_result(image_data)

    async def analyze_expression_from_base64(self, base64_image: str) -> dict[str, Any] | None:
        try:
            image = self._decode_image(base64_image)
            if image is None:
                logger.warning("failed to decode expression image from base64")
                return None
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(_executor, self._analyze_image_sync, image)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error("error processing base64 expression image: {}", exc)
            return None

    @staticmethod
    def emotion_priority(emotion: str) -> int:
        return _EMOTION_PRIORITY.get(emotion, 99)

    @staticmethod
    def emotion_label(emotion: str) -> str:
        return _EMOTION_LABELS.get(emotion, _EMOTION_LABELS["steady"])


expression_service = ExpressionService()

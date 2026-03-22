import base64
import asyncio
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
from deepface import DeepFace

from app.log import logger

# Create a ThreadPoolExecutor for running blocking DeepFace code
_executor = ThreadPoolExecutor(max_workers=2)

class ExpressionService:
    def __init__(self):
        # We can pre-load the model to avoid latency on the first request, 
        # but DeepFace handles caching internally. We'll just rely on it.
        pass

    def _analyze_image_sync(self, image_data: np.ndarray) -> Optional[str]:
        """
        Synchronous method to analyze the image using DeepFace.
        """
        try:
            # We use enforce_detection=False to avoid errors if the face is not fully visible
            # We only extract 'emotion' to keep it fast
            results = DeepFace.analyze(
                img_path=image_data,
                actions=['emotion'],
                enforce_detection=False,
                silent=True
            )
            # DeepFace.analyze can return a list if multiple faces are found
            if isinstance(results, list):
                result = results[0]
            else:
                result = results
            
            dominant_emotion = result.get('dominant_emotion')
            return dominant_emotion
        except Exception as e:
            logger.error(f"Error analyzing expression: {e}")
            return None

    async def analyze_expression_from_base64(self, base64_image: str) -> Optional[str]:
        """
        Decode the base64 image and run expression analysis asynchronously.
        """
        try:
            # Remove header if present (e.g. "data:image/jpeg;base64,...")
            if "," in base64_image:
                base64_image = base64_image.split(",")[1]
            
            image_bytes = base64.b64decode(base64_image)
            np_arr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if image is None:
                logger.error("Failed to decode image from base64")
                return None

            # Run the blocking DeepFace code in a separate thread
            loop = asyncio.get_event_loop()
            dominant_emotion = await loop.run_in_executor(_executor, self._analyze_image_sync, image)
            
            return dominant_emotion

        except Exception as e:
            logger.error(f"Error processing base64 image: {e}")
            return None

expression_service = ExpressionService()

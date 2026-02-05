import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import cv2

from src.core.logger import app_logger
from src.core.config import settings
from src.core.exceptions import OCRError
from src.ml_pipeline.detector import BoundingBox


class OCRResult:
    def __init__(self, text: str, confidence: float, bbox: Optional[Tuple[float, float, float, float]] = None):
        self.text = text
        self.confidence = confidence
        self.bbox = bbox
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "confidence": float(self.confidence),
            "bbox": self.bbox
        }


class TextRecognizer:
    def __init__(self, lang: Optional[str] = None):
        self.lang = lang or settings.paddle_ocr_lang
        self.use_paddle = False
        self.ocr = None
        
        app_logger.info(f"Initializing TextRecognizer")
        # Не загружаем PaddleOCR сразу - будем использовать простое извлечение текста
        app_logger.info("Using simple text extraction (PaddleOCR disabled)")
    
    def recognize_in_bboxes(self, image: np.ndarray, bboxes: List[BoundingBox]) -> Dict[int, OCRResult]:
        """Извлечение текста из bounding boxes"""
        try:
            results = {}
            
            for idx, bbox in enumerate(bboxes):
                # Вырезаем область изображения
                x1, y1 = int(bbox.x1), int(bbox.y1)
                x2, y2 = int(bbox.x2), int(bbox.y2)
                
                # Проверяем границы
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(image.shape[1], x2)
                y2 = min(image.shape[0], y2)
                
                if x2 <= x1 or y2 <= y1:
                    continue
                
                roi = image[y1:y2, x1:x2]
                
                # Простое извлечение текста - используем тип элемента как текст
                # В реальной системе здесь был бы OCR
                text = self._extract_text_simple(roi, bbox)
                
                if text:
                    results[idx] = OCRResult(
                        text=text,
                        confidence=0.8,
                        bbox=(x1, y1, x2, y2)
                    )
            
            app_logger.info(f"Extracted text from {len(results)} bounding boxes")
            return results
            
        except Exception as e:
            app_logger.error(f"Error in text recognition: {str(e)}", exc_info=True)
            return {}
    
    def _extract_text_simple(self, roi: np.ndarray, bbox: BoundingBox) -> str:
        """Простое извлечение текста - генерируем описание на основе типа элемента"""
        
        # Словарь типов элементов
        type_names = {
            "start": "Начало",
            "end": "Конец",
            "process": "Процесс",
            "decision": "Условие",
            "data": "Данные",
            "subprocess": "Подпроцесс"
        }
        
        element_type = bbox.class_name
        base_name = type_names.get(element_type, "Элемент")
        
        # Генерируем уникальное имя на основе позиции
        element_id = int(bbox.center_y / 100) * 100 + int(bbox.center_x / 100)
        
        return f"{base_name} {element_id}"
    
    def recognize(self, image: np.ndarray) -> List[OCRResult]:
        """Распознавание всего текста на изображении"""
        try:
            # Простая заглушка - возвращаем пустой список
            # В реальной системе здесь был бы полный OCR
            return []
            
        except Exception as e:
            app_logger.error(f"Error in OCR: {str(e)}", exc_info=True)
            return []

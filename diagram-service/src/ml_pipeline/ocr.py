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
        self.ocr = None
        
        app_logger.info(f"Initializing TextRecognizer with languages: {self.lang}")
        self._load_model()
    
    def _load_model(self):
        try:
            from paddleocr import PaddleOCR
            
            langs = [l.strip() for l in self.lang.split(',')]
            
            self.ocr = PaddleOCR(
                lang=langs[0] if len(langs) == 1 else 'ch',
                use_angle_cls=True,
                use_gpu=(settings.device == 'cuda'),
                show_log=False
            )
            
            app_logger.info("PaddleOCR model loaded successfully")
            
        except Exception as e:
            app_logger.error(f"Failed to load PaddleOCR: {str(e)}", exc_info=True)
            raise OCRError(f"Failed to load OCR model: {str(e)}")
    
    def recognize(self, image: np.ndarray) -> List[OCRResult]:
        try:
            app_logger.debug(f"Running OCR on image of shape {image.shape}")
            
            results = self.ocr.ocr(image, cls=True)
            
            ocr_results = []
            if results and results[0]:
                for line in results[0]:
                    bbox_coords = line[0]
                    text_info = line[1]
                    
                    text = text_info[0]
                    confidence = float(text_info[1])
                    
                    x_coords = [point[0] for point in bbox_coords]
                    y_coords = [point[1] for point in bbox_coords]
                    bbox = (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
                    
                    if confidence >= settings.ocr_confidence_threshold:
                        ocr_result = OCRResult(text=text, confidence=confidence, bbox=bbox)
                        ocr_results.append(ocr_result)
            
            app_logger.info(f"OCR recognized {len(ocr_results)} text regions")
            return ocr_results
            
        except Exception as e:
            app_logger.error(f"OCR recognition failed: {str(e)}", exc_info=True)
            raise OCRError(f"Text recognition failed: {str(e)}")
    
    def recognize_in_bboxes(self, image: np.ndarray, bboxes: List[BoundingBox]) -> Dict[int, str]:
        bbox_texts = {}
        
        for idx, bbox in enumerate(bboxes):
            try:
                x1, y1, x2, y2 = int(bbox.x1), int(bbox.y1), int(bbox.x2), int(bbox.y2)
                
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(image.shape[1], x2)
                y2 = min(image.shape[0], y2)
                
                if x2 <= x1 or y2 <= y1:
                    continue
                
                roi = image[y1:y2, x1:x2]
                
                if roi.size == 0:
                    continue
                
                ocr_results = self.recognize(roi)
                
                if ocr_results:
                    texts = [r.text for r in ocr_results]
                    combined_text = ' '.join(texts)
                    bbox_texts[idx] = combined_text
                    app_logger.debug(f"BBox {idx}: '{combined_text}'")
                else:
                    bbox_texts[idx] = ""
                    
            except Exception as e:
                app_logger.warning(f"Failed to recognize text in bbox {idx}: {str(e)}")
                bbox_texts[idx] = ""
        
        app_logger.info(f"Recognized text in {len(bbox_texts)} bounding boxes")
        return bbox_texts
    
    def recognize_with_preprocessing(self, image: np.ndarray) -> List[OCRResult]:
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            
            binary = cv2.adaptiveThreshold(
                denoised,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            
            return self.recognize(binary)
            
        except Exception as e:
            app_logger.warning(f"Preprocessing failed, using original image: {str(e)}")
            return self.recognize(image)

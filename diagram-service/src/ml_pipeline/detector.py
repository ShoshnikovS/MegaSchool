import numpy as np
import cv2
from typing import List, Dict, Any, Optional
from pathlib import Path

from src.core.logger import app_logger
from src.core.config import settings
from src.core.exceptions import DetectionError


class BoundingBox:
    def __init__(self, x1: float, y1: float, x2: float, y2: float, confidence: float, class_id: int, class_name: str):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.confidence = confidence
        self.class_id = class_id
        self.class_name = class_name
        self.center_x = (x1 + x2) / 2
        self.center_y = (y1 + y2) / 2
        self.width = x2 - x1
        self.height = y2 - y1
        self.area = self.width * self.height
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "x1": float(self.x1),
            "y1": float(self.y1),
            "x2": float(self.x2),
            "y2": float(self.y2),
            "center_x": float(self.center_x),
            "center_y": float(self.center_y),
            "width": float(self.width),
            "height": float(self.height),
            "area": float(self.area),
            "confidence": float(self.confidence),
            "class_id": int(self.class_id),
            "class_name": self.class_name
        }


class DiagramDetector:
    def __init__(self, model_path: Optional[str] = None, confidence_threshold: Optional[float] = None):
        self.confidence_threshold = confidence_threshold or settings.confidence_threshold
        app_logger.info(f"Initializing DiagramDetector with OpenCV-based detection")
    
    def detect_diagram_elements(self, image: np.ndarray) -> List[BoundingBox]:
        """Детекция элементов диаграмм с использованием OpenCV"""
        try:
            app_logger.info(f"Detecting diagram elements in image of shape {image.shape}")
            
            # Конвертируем в grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Применяем адаптивную бинаризацию для лучшего выделения элементов
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY_INV, 11, 2
            )
            
            # Морфологические операции для очистки шума
            kernel = np.ones((3, 3), np.uint8)
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
            
            # Поиск контуров
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            app_logger.info(f"Found {len(contours)} contours")
            
            bboxes = []
            min_area = 800  # Минимальная площадь элемента
            max_area = image.shape[0] * image.shape[1] * 0.5  # Максимум 50% изображения
            
            for idx, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                
                # Фильтруем по площади
                if area < min_area or area > max_area:
                    continue
                
                # Получаем bounding box
                x, y, w, h = cv2.boundingRect(contour)
                
                # Проверяем соотношение сторон (исключаем линии)
                aspect_ratio = max(w, h) / (min(w, h) + 1)
                if aspect_ratio > 15:  # Слишком вытянутый - это линия
                    continue
                
                # Проверяем что это не весь фон
                if w > image.shape[1] * 0.9 or h > image.shape[0] * 0.9:
                    continue
                
                # Определяем тип элемента по форме
                element_type = self._classify_by_shape(contour, w, h)
                
                bbox = BoundingBox(
                    x1=float(x),
                    y1=float(y),
                    x2=float(x + w),
                    y2=float(y + h),
                    confidence=0.95,
                    class_id=idx,
                    class_name=element_type
                )
                
                bboxes.append(bbox)
            
            # Сортируем по позиции (сверху вниз, слева направо)
            bboxes.sort(key=lambda b: (b.center_y, b.center_x))
            
            app_logger.info(f"Detected {len(bboxes)} diagram elements")
            return bboxes
            
        except Exception as e:
            app_logger.error(f"Error detecting diagram elements: {str(e)}", exc_info=True)
            raise DetectionError(f"Failed to detect diagram elements: {str(e)}")
    
    def _classify_by_shape(self, contour, width: float, height: float) -> str:
        """Классификация элемента по форме контура"""
        
        # Аппроксимация контура
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        num_vertices = len(approx)
        
        # Соотношение сторон
        aspect_ratio = width / height if height > 0 else 1.0
        
        # Определяем тип по количеству вершин и соотношению сторон
        if num_vertices == 4:
            # Прямоугольник или ромб
            if 0.7 <= aspect_ratio <= 1.3:
                # Квадратный элемент - может быть ромбом (decision) или процессом
                # Проверяем угол поворота
                rect = cv2.minAreaRect(contour)
                angle = rect[2]
                if abs(angle - 45) < 15 or abs(angle + 45) < 15:
                    return "decision"  # Ромб
                else:
                    return "process"  # Квадрат
            else:
                return "process"  # Прямоугольник
        
        elif num_vertices > 8:
            # Много вершин - вероятно овал/круг
            if 0.8 <= aspect_ratio <= 1.2:
                return "start"  # Круг - начало/конец
            else:
                return "data"  # Овал - данные
        
        elif num_vertices == 3:
            return "decision"  # Треугольник
        
        else:
            # По умолчанию - процесс
            return "process"

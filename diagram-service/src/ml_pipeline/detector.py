import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
import torch

from src.core.logger import app_logger
from src.core.config import settings
from src.core.exceptions import DetectionError, ModelLoadError


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
        self.model_path = model_path or str(settings.yolo_model_full_path)
        self.confidence_threshold = confidence_threshold or settings.confidence_threshold
        self.device = settings.device
        self.model = None
        
        app_logger.info(f"Initializing DiagramDetector with model={self.model_path}, device={self.device}")
        self._load_model()
    
    def _load_model(self):
        try:
            from ultralytics import YOLO
            
            if not Path(self.model_path).exists():
                app_logger.warning(f"Model file not found at {self.model_path}, downloading default YOLOv8n")
                self.model = YOLO('yolov8n.pt')
            else:
                self.model = YOLO(self.model_path)
            
            if self.device == 'cuda' and torch.cuda.is_available():
                self.model.to('cuda')
                app_logger.info("Model loaded on GPU")
            else:
                self.model.to('cpu')
                app_logger.info("Model loaded on CPU")
            
        except Exception as e:
            app_logger.error(f"Failed to load YOLO model: {str(e)}", exc_info=True)
            raise ModelLoadError(f"Failed to load detection model: {str(e)}")
    
    def detect(self, image: np.ndarray) -> List[BoundingBox]:
        try:
            app_logger.debug(f"Running detection on image of shape {image.shape}")
            
            results = self.model(image, conf=self.confidence_threshold, verbose=False)
            
            bboxes = []
            for result in results:
                boxes = result.boxes
                
                for i in range(len(boxes)):
                    box = boxes.xyxy[i].cpu().numpy()
                    conf = float(boxes.conf[i].cpu().numpy())
                    cls = int(boxes.cls[i].cpu().numpy())
                    
                    class_name = result.names[cls] if hasattr(result, 'names') else f"class_{cls}"
                    
                    bbox = BoundingBox(
                        x1=float(box[0]),
                        y1=float(box[1]),
                        x2=float(box[2]),
                        y2=float(box[3]),
                        confidence=conf,
                        class_id=cls,
                        class_name=class_name
                    )
                    bboxes.append(bbox)
            
            app_logger.info(f"Detected {len(bboxes)} objects")
            return bboxes
            
        except Exception as e:
            app_logger.error(f"Detection failed: {str(e)}", exc_info=True)
            raise DetectionError(f"Object detection failed: {str(e)}")
    
    def detect_diagram_elements(self, image: np.ndarray) -> List[BoundingBox]:
        bboxes = self.detect(image)
        
        diagram_elements = []
        for bbox in bboxes:
            element_type = self._classify_element_by_shape(bbox)
            bbox.class_name = element_type
            diagram_elements.append(bbox)
        
        diagram_elements.sort(key=lambda b: (b.center_y, b.center_x))
        
        app_logger.info(f"Classified {len(diagram_elements)} diagram elements")
        return diagram_elements
    
    def _classify_element_by_shape(self, bbox: BoundingBox) -> str:
        aspect_ratio = bbox.width / bbox.height if bbox.height > 0 else 1.0
        
        if 0.8 <= aspect_ratio <= 1.2:
            if bbox.area < 5000:
                return "decision"
            else:
                return "process"
        elif aspect_ratio > 1.5:
            return "process"
        elif aspect_ratio < 0.7:
            return "data"
        else:
            return "process"
    
    def filter_by_confidence(self, bboxes: List[BoundingBox], min_confidence: float) -> List[BoundingBox]:
        filtered = [bbox for bbox in bboxes if bbox.confidence >= min_confidence]
        app_logger.debug(f"Filtered {len(bboxes)} -> {len(filtered)} boxes by confidence >= {min_confidence}")
        return filtered
    
    def non_max_suppression(self, bboxes: List[BoundingBox], iou_threshold: float = 0.5) -> List[BoundingBox]:
        if not bboxes:
            return []
        
        bboxes_sorted = sorted(bboxes, key=lambda b: b.confidence, reverse=True)
        
        keep = []
        while bboxes_sorted:
            current = bboxes_sorted.pop(0)
            keep.append(current)
            
            bboxes_sorted = [
                bbox for bbox in bboxes_sorted
                if self._calculate_iou(current, bbox) < iou_threshold
            ]
        
        app_logger.debug(f"NMS: {len(bboxes)} -> {len(keep)} boxes")
        return keep
    
    def _calculate_iou(self, bbox1: BoundingBox, bbox2: BoundingBox) -> float:
        x1 = max(bbox1.x1, bbox2.x1)
        y1 = max(bbox1.y1, bbox2.y1)
        x2 = min(bbox1.x2, bbox2.x2)
        y2 = min(bbox1.y2, bbox2.y2)
        
        if x2 < x1 or y2 < y1:
            return 0.0
        
        intersection = (x2 - x1) * (y2 - y1)
        union = bbox1.area + bbox2.area - intersection
        
        return intersection / union if union > 0 else 0.0

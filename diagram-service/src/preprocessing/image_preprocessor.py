import numpy as np
from typing import Optional
import cv2

from src.core.logger import app_logger
from src.core.config import settings
from src.core.exceptions import ImageProcessingError
from src.utils.image_utils import (
    resize_image,
    convert_to_rgb,
    enhance_contrast,
    denoise_image,
    get_image_info
)


class ImagePreprocessor:
    def __init__(self, max_size: Optional[int] = None):
        self.max_size = max_size or settings.max_image_size
        app_logger.info(f"ImagePreprocessor initialized with max_size={self.max_size}")
    
    def preprocess(self, image: np.ndarray, enhance: bool = True, denoise: bool = False) -> np.ndarray:
        try:
            app_logger.debug(f"Starting image preprocessing. Input shape: {image.shape}")
            
            original_info = get_image_info(image)
            app_logger.debug(f"Original image info: {original_info}")
            
            processed = image.copy()
            
            processed = convert_to_rgb(processed)
            app_logger.debug("Converted to RGB")
            
            processed = resize_image(processed, max_size=self.max_size, keep_aspect_ratio=True)
            app_logger.debug(f"Resized to: {processed.shape}")
            
            if enhance:
                processed = enhance_contrast(processed, clip_limit=2.0, tile_grid_size=(8, 8))
                app_logger.debug("Enhanced contrast")
            
            if denoise:
                processed = denoise_image(processed, strength=10)
                app_logger.debug("Applied denoising")
            
            final_info = get_image_info(processed)
            app_logger.info(f"Preprocessing complete. Final shape: {processed.shape}, size: {final_info['size_bytes']} bytes")
            
            return processed
            
        except Exception as e:
            app_logger.error(f"Image preprocessing failed: {str(e)}", exc_info=True)
            raise ImageProcessingError(f"Preprocessing failed: {str(e)}")
    
    def normalize_for_detection(self, image: np.ndarray) -> np.ndarray:
        try:
            normalized = image.astype(np.float32) / 255.0
            return normalized
        except Exception as e:
            raise ImageProcessingError(f"Normalization failed: {str(e)}")
    
    def prepare_for_ocr(self, image: np.ndarray) -> np.ndarray:
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            binary = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            
            app_logger.debug("Prepared image for OCR (grayscale + adaptive threshold)")
            return binary
            
        except Exception as e:
            app_logger.warning(f"OCR preparation failed, using original: {str(e)}")
            return image

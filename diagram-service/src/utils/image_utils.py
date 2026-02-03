import base64
import io
from typing import Union, Tuple
import numpy as np
from PIL import Image
import cv2

from src.core.logger import app_logger
from src.core.exceptions import ImageProcessingError


def decode_base64_image(base64_string: str) -> np.ndarray:
    try:
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        return np.array(image)
    except Exception as e:
        raise ImageProcessingError(f"Failed to decode base64 image: {str(e)}")


def encode_image_to_base64(image: Union[np.ndarray, Image.Image], format: str = "PNG") -> str:
    try:
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode('utf-8')
    except Exception as e:
        raise ImageProcessingError(f"Failed to encode image to base64: {str(e)}")


def bytes_to_numpy(image_bytes: bytes) -> np.ndarray:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        return np.array(image)
    except Exception as e:
        raise ImageProcessingError(f"Failed to convert bytes to numpy array: {str(e)}")


def numpy_to_bytes(image: np.ndarray, format: str = "PNG") -> bytes:
    try:
        pil_image = Image.fromarray(image)
        buffer = io.BytesIO()
        pil_image.save(buffer, format=format)
        buffer.seek(0)
        return buffer.read()
    except Exception as e:
        raise ImageProcessingError(f"Failed to convert numpy array to bytes: {str(e)}")


def resize_image(image: np.ndarray, max_size: int = 1920, keep_aspect_ratio: bool = True) -> np.ndarray:
    try:
        height, width = image.shape[:2]
        
        if height <= max_size and width <= max_size:
            return image
        
        if keep_aspect_ratio:
            scale = max_size / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
        else:
            new_width = max_size
            new_height = max_size
        
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        app_logger.debug(f"Resized image from {width}x{height} to {new_width}x{new_height}")
        
        return resized
    except Exception as e:
        raise ImageProcessingError(f"Failed to resize image: {str(e)}")


def convert_to_rgb(image: np.ndarray) -> np.ndarray:
    try:
        if len(image.shape) == 2:
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            return cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        elif image.shape[2] == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return image
    except Exception as e:
        raise ImageProcessingError(f"Failed to convert image to RGB: {str(e)}")


def enhance_contrast(image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: Tuple[int, int] = (8, 8)) -> np.ndarray:
    try:
        if len(image.shape) == 3:
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            return cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
        else:
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
            return clahe.apply(image)
    except Exception as e:
        app_logger.warning(f"Failed to enhance contrast: {str(e)}")
        return image


def denoise_image(image: np.ndarray, strength: int = 10) -> np.ndarray:
    try:
        if len(image.shape) == 3:
            return cv2.fastNlMeansDenoisingColored(image, None, strength, strength, 7, 21)
        else:
            return cv2.fastNlMeansDenoising(image, None, strength, 7, 21)
    except Exception as e:
        app_logger.warning(f"Failed to denoise image: {str(e)}")
        return image


def get_image_info(image: np.ndarray) -> dict:
    height, width = image.shape[:2]
    channels = image.shape[2] if len(image.shape) == 3 else 1
    
    return {
        "width": width,
        "height": height,
        "channels": channels,
        "dtype": str(image.dtype),
        "size_bytes": image.nbytes
    }

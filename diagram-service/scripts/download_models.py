import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.logger import app_logger
from src.core.config import settings


def download_yolo_model():
    app_logger.info("Downloading YOLOv8n model...")
    
    try:
        from ultralytics import YOLO
        
        model_path = settings.yolo_model_full_path
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        if model_path.exists():
            app_logger.info(f"YOLOv8n model already exists at {model_path}")
        else:
            model = YOLO('yolov8n.pt')
            app_logger.info(f"YOLOv8n model downloaded successfully")
        
        return True
    except Exception as e:
        app_logger.error(f"Failed to download YOLOv8n model: {e}")
        return False


def download_paddleocr_models():
    app_logger.info("Downloading PaddleOCR models...")
    
    try:
        from paddleocr import PaddleOCR
        
        langs = settings.paddle_ocr_lang.split(',')
        
        for lang in langs:
            lang = lang.strip()
            app_logger.info(f"Initializing PaddleOCR for language: {lang}")
            ocr = PaddleOCR(lang=lang, use_angle_cls=True, show_log=False)
            app_logger.info(f"PaddleOCR model for {lang} downloaded successfully")
        
        return True
    except Exception as e:
        app_logger.error(f"Failed to download PaddleOCR models: {e}")
        return False


def main():
    app_logger.info("Starting model download process...")
    
    yolo_success = download_yolo_model()
    paddle_success = download_paddleocr_models()
    
    if yolo_success and paddle_success:
        app_logger.info("All models downloaded successfully!")
        return 0
    else:
        app_logger.error("Some models failed to download")
        return 1


if __name__ == "__main__":
    sys.exit(main())

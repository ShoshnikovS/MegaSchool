from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Literal


class Settings(BaseSettings):
    app_name: str = "diagram-service"
    app_version: str = "0.1.0"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = False
    
    device: Literal["cpu", "cuda"] = "cpu"
    
    yolo_model_path: str = "models/yolov8/yolov8n.pt"
    paddle_ocr_lang: str = "ru,en"
    
    max_image_size: int = 1920
    confidence_threshold: float = 0.5
    ocr_confidence_threshold: float = 0.6
    
    max_upload_size: int = 10485760
    cors_origins: str = "*"
    api_prefix: str = "/api/v1"
    
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: str = "logs/app.log"
    
    template_dir: str = "templates"
    
    workers: int = 1
    timeout: int = 300
    
    @property
    def base_dir(self) -> Path:
        return Path(__file__).parent.parent.parent
    
    @property
    def models_dir(self) -> Path:
        return self.base_dir / "models"
    
    @property
    def templates_path(self) -> Path:
        return self.base_dir / self.template_dir
    
    @property
    def yolo_model_full_path(self) -> Path:
        return self.base_dir / self.yolo_model_path
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()

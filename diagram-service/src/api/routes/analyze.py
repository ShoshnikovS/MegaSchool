from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import time
import base64

from src.core.logger import app_logger
from src.core.exceptions import ImageProcessingError, ValidationError
from src.api.models.responses import UnifiedResponse, GraphRepresentation, Artifacts

router = APIRouter()


@router.post("/analyze", response_model=UnifiedResponse)
async def analyze_diagram(image: UploadFile = File(...)):
    start_time = time.time()
    
    app_logger.info(f"Received analyze request: {image.filename}")
    
    if not image.content_type.startswith("image/"):
        raise ValidationError(
            "Invalid file type. Only images are supported.",
            {"content_type": image.content_type}
        )
    
    try:
        image_bytes = await image.read()
        
        if len(image_bytes) > 10 * 1024 * 1024:
            raise ValidationError(
                "Image too large. Maximum size is 10MB.",
                {"size": len(image_bytes)}
            )
        
        app_logger.info(f"Image size: {len(image_bytes)} bytes")
        
        graph_representation = GraphRepresentation(
            nodes=[
                {
                    "id": "node_1",
                    "type": "start",
                    "label": "Начало",
                    "position": [100, 50]
                },
                {
                    "id": "node_2",
                    "type": "process",
                    "label": "Обработка данных",
                    "position": [100, 150]
                },
                {
                    "id": "node_3",
                    "type": "decision",
                    "label": "Условие выполнено?",
                    "position": [100, 250]
                },
                {
                    "id": "node_4",
                    "type": "process",
                    "label": "Действие A",
                    "position": [50, 350]
                },
                {
                    "id": "node_5",
                    "type": "process",
                    "label": "Действие B",
                    "position": [150, 350]
                },
                {
                    "id": "node_6",
                    "type": "end",
                    "label": "Конец",
                    "position": [100, 450]
                }
            ],
            edges=[
                {"source": "node_1", "target": "node_2", "label": None},
                {"source": "node_2", "target": "node_3", "label": None},
                {"source": "node_3", "target": "node_4", "label": "Да"},
                {"source": "node_3", "target": "node_5", "label": "Нет"},
                {"source": "node_4", "target": "node_6", "label": None},
                {"source": "node_5", "target": "node_6", "label": None}
            ]
        )
        
        description = (
            "Алгоритм начинается с начального узла. "
            "Затем выполняется обработка данных. "
            "После обработки проверяется условие. "
            "Если условие выполнено (Да), выполняется действие A. "
            "Если условие не выполнено (Нет), выполняется действие B. "
            "После выполнения одного из действий алгоритм завершается."
        )
        
        processing_time = time.time() - start_time
        
        response = UnifiedResponse(
            task_type="image_to_text",
            description=description,
            graph_representation=graph_representation,
            artifacts=Artifacts(),
            processing_time_sec=round(processing_time, 2),
            metadata={
                "image_filename": image.filename,
                "image_size_bytes": len(image_bytes)
            }
        )
        
        app_logger.info(f"Analysis completed in {processing_time:.2f}s")
        
        return response
        
    except ValidationError:
        raise
    except Exception as e:
        app_logger.error(f"Error processing image: {str(e)}", exc_info=True)
        raise ImageProcessingError(
            "Failed to process image",
            {"error": str(e)}
        )

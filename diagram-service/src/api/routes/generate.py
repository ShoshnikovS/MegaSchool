from fastapi import APIRouter
import time
import base64
from io import BytesIO

from src.core.logger import app_logger
from src.core.exceptions import TextParsingError, VisualizationError
from src.api.models.requests import GenerateRequest
from src.api.models.responses import UnifiedResponse, GraphRepresentation, Artifacts

router = APIRouter()


@router.post("/generate", response_model=UnifiedResponse)
async def generate_diagram(request: GenerateRequest):
    start_time = time.time()
    
    app_logger.info(f"Received generate request: format={request.output_format}, type={request.diagram_type}")
    app_logger.debug(f"Description: {request.description[:100]}...")
    
    try:
        graph_representation = GraphRepresentation(
            nodes=[
                {
                    "id": "start",
                    "type": "start",
                    "label": "Начало",
                    "position": [100, 50]
                },
                {
                    "id": "check",
                    "type": "decision",
                    "label": "Условие X",
                    "position": [100, 150]
                },
                {
                    "id": "action_a",
                    "type": "process",
                    "label": "Действие A",
                    "position": [50, 250]
                },
                {
                    "id": "action_b",
                    "type": "process",
                    "label": "Действие B",
                    "position": [150, 250]
                },
                {
                    "id": "end",
                    "type": "end",
                    "label": "Конец",
                    "position": [100, 350]
                }
            ],
            edges=[
                {"source": "start", "target": "check", "label": None},
                {"source": "check", "target": "action_a", "label": "Да"},
                {"source": "check", "target": "action_b", "label": "Нет"},
                {"source": "action_a", "target": "end", "label": None},
                {"source": "action_b", "target": "end", "label": None}
            ]
        )
        
        artifacts = Artifacts()
        
        if request.output_format in ["image", "both"]:
            dummy_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            artifacts.diagram_image_base64 = dummy_image_base64
        
        if request.output_format in ["code", "both"]:
            plantuml_code = """@startuml
start
if (Условие X?) then (Да)
  :Действие A;
else (Нет)
  :Действие B;
endif
stop
@enduml"""
            artifacts.diagram_code = plantuml_code
        
        processing_time = time.time() - start_time
        
        response = UnifiedResponse(
            task_type="text_to_diagram",
            description=request.description,
            graph_representation=graph_representation,
            artifacts=artifacts,
            processing_time_sec=round(processing_time, 2),
            metadata={
                "output_format": request.output_format,
                "diagram_type": request.diagram_type,
                "layout": request.layout
            }
        )
        
        app_logger.info(f"Generation completed in {processing_time:.2f}s")
        
        return response
        
    except Exception as e:
        app_logger.error(f"Error generating diagram: {str(e)}", exc_info=True)
        raise VisualizationError(
            "Failed to generate diagram",
            {"error": str(e)}
        )
